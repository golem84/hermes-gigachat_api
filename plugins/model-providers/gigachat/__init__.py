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
    """Fetch GigaChat access token using client credentials from environment.

    Returns:
        Access token string or None if failed.
    """
    # Get credentials from environment variables
    client_id = os.getenv("GIGACHAT_CLIENT_ID")
    client_secret = os.getenv("GIGACHAT_CLIENT_SECRET")
    api_token = os.getenv("GIGACHAT_API_TOKEN")

    # If we have an API token, check if it's actually the base64 encoded credentials
    if api_token:
        # Try to decode the token as base64 and see if it contains a colon (i.e., it's client_id:client_secret)
        try:
            decoded = base64.b64decode(api_token).decode("utf-8")
            if ":" in decoded:
                # It appears to be the base64 encoded client_id:client_secret
                # Use it to fetch an access token via the NGW endpoint
                url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                    "Authorization": f"Basic {api_token}",
                    "RqUID": os.urandom(16).hex(),
                }
                data = b"scope=GIGACHAT_API_PERS"
                try:
                    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
                    with urllib.request.urlopen(req, timeout=10) as response:
                        result = json.loads(response.read().decode())
                        return result.get("access_token")
                except Exception as e:
                    logger.debug("Failed to fetch GigaChat token from base64 credentials: %s", e)
                    # Fall through to try the client credentials flow below
            else:
                # The token is not base64 encoded credentials, treat it as the direct token
                return api_token
        except Exception:
            # If we cannot decode it as base64, treat it as the direct token
            return api_token

    # If we don't have a usable API token, try the client credentials flow
    if not client_id or not client_secret:
        logger.debug("GigaChat credentials not found in environment")
        return None

    # Prepare basic auth
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    # Request token from Sberbank's NGW endpoint
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "Authorization": f"Basic {encoded_credentials}",
        "RqUID": os.urandom(16).hex(),
    }
    data = b"scope=GIGACHAT_API_PERS"

    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
            return result.get("access_token")
    except Exception as e:
        logger.debug("Failed to fetch GigaChat token: %s", e)
        return None


class GigaChatProfile(ProviderProfile):
    """GigaChat provider profile.

    GigaChat uses Bearer token authentication and supports function calling
    via its native "functions" format. It requires translation between
    OpenAI tools format and GigaChat functions format.
    """

    def prepare_messages(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Pre-process messages for GigaChat.

        GigaChat expects messages in OpenAI format but may have specific
        requirements for function calls.
        """
        # For now, pass through unchanged - we'll handle function conversion elsewhere
        return messages

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
        **context: Any,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Build API kwargs extras for GigaChat.

        GigaChat doesn't appear to have special reasoning config requirements
        beyond standard parameters, but we maintain the interface for compatibility.
        """
        # GigaChat doesn't need special handling for reasoning config
        # beyond what's handled in the standard API call
        return {}, {}

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
    auth_type="api_key",  # Will use Bearer token
    # Note: We don't set default_aux_model as GigaChat models are all fairly capable
)

# Register the provider
register_provider(gigachat)