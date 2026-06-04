#!/usr/bin/env python3
"""Debug GigaChat OAuth token fetch with detailed logging."""

import sys
import os
import json
import base64
import urllib.request
import urllib.error
import ssl

# Load .env file
sys.path.insert(0, '/home/hermes/projects/hermes-agent')
from hermes_cli.config import get_env_value

print("=" * 60)
print("GigaChat OAuth Debug")
print("=" * 60)

# Read credentials
client_id = get_env_value("GIGACHAT_CLIENT_ID") or os.getenv("GIGACHAT_CLIENT_ID", "")
client_secret = get_env_value("GIGACHAT_CLIENT_SECRET") or os.getenv("GIGACHAT_CLIENT_SECRET", "")
api_token = get_env_value("GIGACHAT_API_TOKEN") or os.getenv("GIGACHAT_API_TOKEN", "")

print(f"\nCredentials:")
print(f"  CLIENT_ID:     {client_id[:8] + '...' if client_id else 'NOT SET'}")
print(f"  CLIENT_SECRET: {client_secret[:8] + '...' if client_secret else 'NOT SET'}")
print(f"  API_TOKEN:     {api_token[:20] + '...' if api_token else 'NOT SET'}")

# Check if API_TOKEN is base64-encoded credentials
if api_token:
    try:
        decoded = base64.b64decode(api_token).decode("utf-8")
        if ":" in decoded:
            print(f"  → API_TOKEN is base64(credentials): {decoded[:8]}...")
        else:
            print(f"  → API_TOKEN is direct access token")
    except:
        print(f"  → API_TOKEN is not base64")

if not client_id or not client_secret:
    print("\n❌ No credentials found")
    sys.exit(1)

# Manual OAuth token fetch
print("\n" + "=" * 60)
print("Manual OAuth Token Fetch")
print("=" * 60)

credentials = f"{client_id}:{client_secret}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

print(f"Credentials string: {credentials[:8]}...")
print(f"Base64 encoded:     {encoded_credentials[:20]}...")

url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json",
    "Authorization": f"Basic {encoded_credentials}",
    "RqUID": "test-uuid-1234-5678-90ab-cdef",
}
data = b"scope=GIGACHAT_API_PERS"

print(f"\nRequest:")
print(f"  URL:  {url}")
print(f"  Method: POST")
print(f"  Headers: {headers}")
print(f"  Data: {data}")

import uuid
headers["RqUID"] = str(uuid.uuid4())

try:
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    # SSL context (disable verification for GigaChat's self-signed certs)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    print(f"\nSending request...")
    with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
        result = json.loads(response.read().decode())
        print(f"✓ Response received!")
        print(f"  Status: {response.status}")
        print(f"  Body: {json.dumps(result, indent=2)}")
        
        if "access_token" in result:
            print(f"\n✓ SUCCESS: access_token = {result['access_token'][:20]}...")
        elif "error" in result:
            print(f"\n❌ ERROR: {result.get('error')} - {result.get('error_description', 'no description')}")
        else:
            print(f"\n❌ UNEXPECTED RESPONSE FORMAT")
            
except urllib.error.HTTPError as e:
    print(f"\n❌ HTTP Error {e.code}: {e.reason}")
    try:
        body = json.loads(e.read().decode())
        print(f"  Response: {json.dumps(body, indent=2)}")
    except:
        print(f"  Response: {e.read().decode()[:500]}")
except urllib.error.URLError as e:
    print(f"\n❌ URL Error: {e.reason}")
    if hasattr(e.reason, 'args'):
        print(f"  Details: {e.reason.args}")
except Exception as e:
    print(f"\n❌ Exception: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
