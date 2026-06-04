#!/usr/bin/env python3
"""Test script for GigaChat OAuth token fetch."""

import sys
import os

# Add project to path
sys.path.insert(0, '/home/hermes/projects/hermes-agent')

# Load .env file
from hermes_cli.config import get_env_value

print("=" * 60)
print("GigaChat OAuth Token Fetch Test")
print("=" * 60)

# Read credentials from .env
client_id = get_env_value("GIGACHAT_CLIENT_ID") or os.getenv("GIGACHAT_CLIENT_ID", "")
client_secret = get_env_value("GIGACHAT_CLIENT_SECRET") or os.getenv("GIGACHAT_CLIENT_SECRET", "")
api_token = get_env_value("GIGACHAT_API_TOKEN") or os.getenv("GIGACHAT_API_TOKEN", "")
ssl_verify = os.getenv("GIGACHAT_SSL_VERIFY", "false").lower() in ("1", "true", "yes", "on")

print(f"\nCredentials status:")
print(f"  GIGACHAT_CLIENT_ID:     {'✓' + client_id[:8] + '...' if client_id else '✗ NOT SET'}")
print(f"  GIGACHAT_CLIENT_SECRET: {'✓' + client_secret[:8] + '...' if client_secret else '✗ NOT SET'}")
print(f"  GIGACHAT_API_TOKEN:     {'✓' + api_token[:8] + '...' if api_token else '✗ NOT SET'}")
print(f"  GIGACHAT_SSL_VERIFY:    {ssl_verify}")

if not client_id or not client_secret:
    print("\n❌ ERROR: Client ID and Client Secret are required for OAuth flow")
    sys.exit(1)

# Test 1: Import plugin and call _get_gigachat_token()
print("\n" + "=" * 60)
print("Test 1: Direct plugin token fetch")
print("=" * 60)

try:
    from plugins.model_providers.gigachat import _get_gigachat_token
    print("✓ Plugin imported successfully")
    
    token = _get_gigachat_token()
    if token:
        print(f"✓ Token received: {token[:20]}...")
        print(f"  Token length: {len(token)} chars")
    else:
        print("❌ Token is None - OAuth fetch failed")
except Exception as e:
    print(f"❌ Exception: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Call resolve_gigachat_runtime_credentials()
print("\n" + "=" * 60)
print("Test 2: resolve_gigachat_runtime_credentials()")
print("=" * 60)

try:
    from hermes_cli.auth import resolve_gigachat_runtime_credentials
    print("✓ resolve_gigachat_runtime_credentials imported")
    
    creds = resolve_gigachat_runtime_credentials()
    print(f"✓ Credentials resolved:")
    print(f"  provider: {creds.get('provider')}")
    print(f"  base_url: {creds.get('base_url')}")
    print(f"  api_key:  {creds.get('api_key', '')[:20]}...")
    print(f"  source:   {creds.get('source')}")
    print(f"  auth_mode: {creds.get('auth_mode')}")
except Exception as e:
    print(f"❌ Exception: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Test actual API call with token
print("\n" + "=" * 60)
print("Test 3: API call to /chat/completions")
print("=" * 60)

try:
    import json
    import urllib.request
    
    # Get fresh token
    token = _get_gigachat_token()
    if not token:
        print("❌ Cannot test API - no token")
    else:
        url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        data = json.dumps({
            "model": "GigaChat-Pro",
            "messages": [{"role": "user", "content": "Hi"}],
        }).encode()
        
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        
        # SSL context
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
            result = json.loads(response.read().decode())
            print(f"✓ API call successful!")
            print(f"  Status: {response.status}")
            if "choices" in result:
                print(f"  Response: {result['choices'][0].get('message', {}).get('content', '')[:100]}")
            else:
                print(f"  Response: {json.dumps(result, indent=2)[:200]}")
                
except urllib.error.HTTPError as e:
    print(f"❌ HTTP Error {e.code}: {e.reason}")
    try:
        body = json.loads(e.read().decode())
        print(f"  Response: {json.dumps(body, indent=2)}")
    except:
        print(f"  Response: {e.read().decode()[:200]}")
except Exception as e:
    print(f"❌ Exception: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test complete")
print("=" * 60)
