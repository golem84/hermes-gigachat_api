"""GigaChat provider plug-in.

GigaChat is a Russian large language model developed by Sberbank.
It supports function calling via its native "functions" format (not OpenAI tools).
"""

from __future__ import annotations

import json
import os
import time
import base64
import urllib.request
from typing import Any

from providers import register_provider
from providers.base import ProviderProfile

logger = __import__("logging").getLogger(__name__)


def _get_gigachat_token() -> str | None:
    """Fetch GigaChat access token.

    Supports two modes:
    1. Direct API token (GIGACHAT_API_TOKEN) — user-provided access token from developer portal
    2. Client credentials (GIGACHAT_CLIENT_ID + GIGACHAT_CLIENT_SECRET) — auto-fetch access token via OAuth

    Priority:
    - If GIGACHAT_API_TOKEN is set and NOT base64-encoded credentials: use it directly
    - If GIGACHAT_API_TOKEN is base64-encoded (client_id:client_secret): fetch access token via OAuth
    - If GIGACHAT_CLIENT_ID + GIGACHAT_CLIENT_SECRET are set: fetch access token via OAuth
    - Otherwise: return None

    Returns:
        Access token string or None if failed.
    """
    # Check SSL verification setting (default: False for GigaChat's self-signed cert)
    # GIGACHAT_SSL_VERIFY=true enables verification (requires CA in trust store)
    _ssl_verify = os.getenv("GIGACHAT_SSL_VERIFY", "false").lower() in ("1", "true", "yes", "on")
    
    # Get credentials from environment variables
    api_token = os.getenv("GIGACHAT_API_TOKEN")

    # Mode 1: Direct API token (not base64-encoded credentials)
    # This is a pre-computed access token from the developer portal
    # Token expires after 30 minutes — user must refresh manually or use credentials mode
    if api_token:
        # Try to decode the token as base64 and see if it contains a colon (i.e., it's client_id:client_secret)
        try:
            decoded = base64.b64decode(api_token).decode("utf-8")
            if ":" in decoded:
                # It appears to be the base64 encoded client_id:client_secret
                # Use it to fetch an access token via the NGW endpoint (Mode 2a)
                return _fetch_token_oauth(api_token, _ssl_verify, "base64_credentials")
            else:
                # The token is not base64 encoded credentials, treat it as the direct access token (Mode 1)
                logger.debug("Using direct API token (GIGACHAT_API_TOKEN)")
                return api_token
        except Exception:
            # If we cannot decode it as base64, treat it as the direct access token (Mode 1)
            logger.debug("Using direct API token (non-base64 GIGACHAT_API_TOKEN)")
            return api_token

    # Mode 2a: Client credentials from GIGACHAT_API_TOKEN as base64(client_id:client_secret)
    # Already handled above via _fetch_token_oauth

    # Mode 2b: Client credentials from separate env vars (GIGACHAT_CLIENT_ID + GIGACHAT_CLIENT_SECRET)
    # This mode auto-fetches access token via OAuth — no manual refresh needed
    client_id = os.getenv("GIGACHAT_CLIENT_ID")
    client_secret = os.getenv("GIGACHAT_CLIENT_SECRET")
    
    if client_id and client_secret:
        logger.debug("Using client credentials (GIGACHAT_CLIENT_ID + GIGACHAT_CLIENT_SECRET)")
        credentials = f"{client_id}:{client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return _fetch_token_oauth(encoded_credentials, _ssl_verify, "client_credentials")
    
    logger.debug("GigaChat credentials not found in environment")
    return None


def _fetch_token_oauth(encoded_credentials: str, ssl_verify: bool, mode: str) -> str | None:
    """Fetch access token via OAuth client credentials flow.

    Args:
        encoded_credentials: Base64-encoded client_id:client_secret
        ssl_verify: Whether to verify SSL certificates
        mode: "base64_credentials" or "client_credentials" for logging

    Returns:
        Access token string or None if failed.
    """
    import uuid
    
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "Authorization": f"Basic {encoded_credentials}",
        "RqUID": str(uuid.uuid4()),  # UUID4 as per official documentation
    }
    data = b"scope=GIGACHAT_API_PERS"
    
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        # Create SSL context based on GIGACHAT_SSL_VERIFY setting
        # GigaChat uses self-signed certificates in their certificate chain,
        # so verification is disabled by default (GIGACHAT_SSL_VERIFY=false).
        # For production, set GIGACHAT_SSL_VERIFY=true and add GigaChat CA to trust store.
        if not ssl_verify:
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
                result = json.loads(response.read().decode())
                token = result.get("access_token")
                if token:
                    logger.debug("OAuth token fetched successfully (mode=%s)", mode)
                return token
        else:
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode())
                token = result.get("access_token")
                if token:
                    logger.debug("OAuth token fetched successfully (mode=%s, SSL verified)", mode)
                return token
    except Exception as e:
        logger.debug("Failed to fetch GigaChat token (mode=%s): %s", mode, e)
        return None


def _transform_gigachat_response_to_openai(response: dict) -> dict:
    """Transform GigaChat response to OpenAI-compatible format.

    GigaChat uses legacy function_call format, OpenAI uses modern tool_calls.
    This function converts the response for Hermes compatibility.
    """
    if "choices" not in response:
        return response
    
    for choice in response["choices"]:
        message = choice.get("message", {})
        
        # Convert legacy function_call to modern tool_calls
        if "function_call" in message:
            function_call = message["function_call"]
            
            # Create modern tool_calls structure
            tool_call = {
                "id": f"call_{function_call['name']}",  # Generate call ID
                "type": "function",
                "function": {
                    "name": function_call["name"],
                    "arguments": json.dumps(function_call.get("arguments", {}))
                }
            }
            
            message["tool_calls"] = [tool_call]
            
            # Keep legacy function_call for potential Hermes handling
            # but add modern tool_calls for compatibility
        
        # Keep all other GigaChat specific fields like functions_state_id
    return response


class GigaChatProfile(ProviderProfile):
    """GigaChat provider profile.

    GigaChat uses Bearer token authentication and supports function calling
    via its native "functions" format. It requires translation between
    OpenAI tools format and GigaChat functions format.
    """

    def prepare_messages(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Pre-process messages for GigaChat.

        GigaChat expects messages in OpenAI format but uses legacy function_call
        instead of modern tool_calls. Convert between formats as needed.
        """
        processed_messages = []
        
        for message in messages:
            processed_msg = message.copy()
            
            # Convert OpenAI tool_calls to GigaChat function_call
            if "tool_calls" in message:
                # Convert modern tool_calls to legacy function_call
                if len(message["tool_calls"]) > 0:
                    tool_call = message["tool_calls"][0]
                    if tool_call["type"] == "function":
                        processed_msg["function_call"] = {
                            "name": tool_call["function"]["name"],
                            "arguments": tool_call["function"]["arguments"]
                        }
                        # Remove tool_calls for GigaChat compatibility
                        del processed_msg["tool_calls"]
            
            # Convert tool response messages
            if message.get("role") == "tool":
                # Convert tool response to function response format
                processed_msg["role"] = "function"
                tool_name = message.get("name") or ""
                if not tool_name:
                    tool_call_id = str(message.get("tool_call_id", ""))
                    tool_name = tool_call_id[5:] if tool_call_id.startswith("call_") else tool_call_id
                processed_msg["name"] = tool_name
                processed_msg.pop("tool_call_id", None)
            
            processed_messages.append(processed_msg)
        
        return processed_messages

    def build_extra_body(
        self, *, session_id: str | None = None, **context: Any
    ) -> dict[str, Any]:
        """Build extra body parameters for GigaChat requests."""
        body: dict[str, Any] = {}

        # Add session ID if provided
        if session_id:
            body["session_id"] = session_id

        return body

    def build_api_kwargs_extras(
        self,
        *,
        reasoning_config: dict | None = None,
        tools: list[dict] | None = None,
        **context: Any,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Build API kwargs extras for GigaChat.

        GigaChat uses the legacy `functions` parameter instead of the newer
        `tools` format. We need to convert OpenAI tools format to GigaChat
        functions format.
        
        GigaChat expects:
        {
            "functions": [
                {
                    "name": "function_name",
                    "description": "description",
                    "parameters": {...}
                }
            ]
        }
        
        Instead of OpenAI's modern format:
        {
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "function_name",
                        ...
                    }
                }
            ]
        }
        """
        extra_body_additions = {}
        top_level_kwargs = {}
        
        # Convert OpenAI tools to GigaChat functions format
        if tools:
            gigachat_functions = []
            for tool in tools:
                # Handle both formats
                if isinstance(tool, dict):
                    if "type" in tool and tool["type"] == "function" and "function" in tool:
                        # Modern OpenAI format: {"type": "function", "function": {...}}
                        gigachat_functions.append(tool["function"])
                    elif "name" in tool:
                        # Legacy format or already GigaChat format: {"name": "...", ...}
                        gigachat_functions.append(tool)
            
            if gigachat_functions:
                extra_body_additions["functions"] = gigachat_functions
        
        # GigaChat doesn't need special handling for reasoning config
        # beyond what's handled in the standard API call
        return extra_body_additions, top_level_kwargs

    def fetch_models(
        self,
        *,
        api_key: str | None = None,
        timeout: float = 8.0,
    ) -> list[str] | None:
        """Fetch available GigaChat models.

        Uses the /models endpoint with Bearer token authentication.
        """
        if not api_key:
            # Try to fetch token if not provided
            api_key = _get_gigachat_token()
            if not api_key:
                return None

        # Try the models endpoint
        url = "https://gigachat.devices.sberbank.ru/api/v1/models"

        try:
            req = urllib.request.Request(url)
            req.add_header("Authorization", f"Bearer {api_key}")
            req.add_header("Accept", "application/json")

            # Add standard headers
            req.add_header("User-Agent", "hermes-cli")

            # GigaChat uses self-signed certificates in their certificate chain.
            # Disable verification by default (GIGACHAT_SSL_VERIFY=false).
            # For production, set GIGACHAT_SSL_VERIFY=true and add GigaChat CA to trust store.
            _ssl_verify = os.getenv("GIGACHAT_SSL_VERIFY", "false").lower() in ("1", "true", "yes", "on")
            if not _ssl_verify:
                import ssl
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                with urllib.request.urlopen(req, timeout=timeout, context=ssl_context) as response:
                    data = json.loads(response.read().decode())
            else:
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    data = json.loads(response.read().decode())

            # Extract model IDs from response
            models = []
            if isinstance(data, dict) and "data" in data:
                for item in data["data"]:
                    if isinstance(item, dict) and "id" in item:
                        models.append(item["id"])
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "id" in item:
                        models.append(item["id"])

            return models if models else None

        except Exception as exc:
            logger.debug("fetch_models(gigachat): %s", exc)
            return None


# Create the GigaChat provider instance
gigachat = GigaChatProfile(
    name="gigachat",
    aliases=("gigachat-pro", "gigachat-max", "gigachat-plus"),
    api_mode="chat_completions",  # Uses standard chat completions endpoint
    env_vars=("GIGACHAT_API_TOKEN", "GIGACHAT_CLIENT_ID", "GIGACHAT_CLIENT_SECRET"),
    base_url="https://gigachat.devices.sberbank.ru/api/v1",
    auth_type="oauth_external",  # OAuth token fetched via _get_gigachat_token()
    tool_format="functions_extra_body",
    # Note: We don't set default_aux_model as GigaChat models are all fairly capable
    # SSL verification: GigaChat uses self-signed certs. Set GIGACHAT_SSL_VERIFY=true for production.
)

# Register the provider
register_provider(gigachat)