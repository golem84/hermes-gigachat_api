"""Test GigaChat with API_KEY instead of Client ID/Secret."""

import os, requests, uuid, json


def test_with_api_key():
    """Test GigaChat OAuth using API_KEY instead of client_id:client_secret."""
    
    # Try using API_KEY if available
    api_key = os.getenv("GIGACHAT_API_KEY")
    
    if not api_key:
        print("❌ GIGACHAT_API_KEY not found in environment")
        print("Testing with existing GIGACHAT_API_TOKEN (client_id:client_secret base64)...")
        api_key = os.getenv("GIGACHAT_API_TOKEN")
        method = "using GIGACHAT_API_TOKEN"
    else:
        print("Testing with GIGACHAT_API_KEY...")
        method = "using GIGACHAT_API_KEY"
    
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json', 
        'RqUID': str(uuid.uuid4()),
        'Authorization': f'Bearer {api_key}'  # Try Bearer instead of Basic
    }
    
    data = b'scope=GIGACHAT_API_PERS'
    
    print(f"Method: {method}")
    print(f"Token: {api_key[:10]}...")
    
    try:
        req = requests.post(url, headers=headers, data=data, verify=False, timeout=10)
        print(f"Status: {req.status_code}")
        
        if req.status_code == 200:
            result = req.json()
            print(f"✅ Success with Bearer auth!")
            print(f"Access token: {result.get('access_token', 'N/A')[:20]}...")
            return True
        else:
            print(f"❌ Bearer auth failed: {req.text[:200]}")
            
            # Try Basic auth as fallback
            print("\nTrying Basic auth instead...")
            headers['Authorization'] = f'Basic {api_key}'
            
            req = requests.post(url, headers=headers, data=data, verify=False, timeout=10)
            print(f"Status: {req.status_code}")
            
            if req.status_code == 200:
                result = req.json()
                print(f"✅ Success with Basic auth!")
                print(f"Access token: {result.get('access_token', 'N/A')[:20]}...")
                return True
            else:
                print(f"❌ Basic auth also failed: {req.text[:200]}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def analyze_current_implementation():
    """Analyze what method we're currently using."""
    print("\n" + "="*60)
    print("🔍 ANALYZING CURRENT IMPLEMENTATION")
    print("="*60)
    
    # Check what environment variables we have
    client_id = os.getenv("GIGACHAT_CLIENT_ID")
    client_secret = os.getenv("GIGACHAT_CLIENT_SECRET")
    api_key = os.getenv("GIGACHAT_API_KEY")
    api_token = os.getenv("GIGACHAT_API_TOKEN")
    
    print(f"GIGACHAT_CLIENT_ID: {'✅ Set' if client_id else '❌ Not set'}")
    print(f"GIGACHAT_CLIENT_SECRET: {'✅ Set' if client_secret else '❌ Not set'}")
    print(f"GIGACHAT_API_KEY: {'✅ Set' if api_key else '❌ Not set'}")
    print(f"GIGACHAT_API_TOKEN: {'✅ Set' if api_token else '❌ Not set'}")
    
    # Decode the api_token to see what it contains
    if api_token:
        try:
            import base64
            decoded = base64.b64decode(api_token).decode('utf-8')
            print(f"\n📋 GIGACHAT_API_TOKEN content:")
            print(f"   Decoded: {decoded[:30]}...")
            
            if ':' in decoded:
                parts = decoded.split(':')
                print(f"   Structure: {parts[0][:20]}...:{parts[1][:20]}...")
                print(f"   ℹ️ Looks like client_id:client_secret format (⏱{30} basic auth)")
        except Exception as e:
            print(f"   ℹ️ Cannot decode: {e}")
    
    if api_key:
        print(f"\n📋 GIGACHAT_API_KEY content:")
        print(f"   Value: {api_key[:30]}...")
        
        if api_key.startswith('Bearer ') or api_key.startswith('Basic '):
            print(f"   ℹ️ Contains auth prefix")
        elif ':' in api_key[:20]:
            print(f"   ℹ️ Contains colon, possibly encoded")


def base64_decoder_test():
    """Test different base64 interpretations."""
    import base64, binascii
    
    api_token = os.getenv("GIGACHAT_API_TOKEN")
    if not api_token:
        return
    
    print("\n🧪 Testing different interpretations of GIGACHAT_API_TOKEN:")
    
    try:
        # Interpretation 1: It's already the Basic auth string
        decoded = base64.b64decode(api_token).decode('utf-8')
        print(f"1. Base64 decode → {decoded[:30]}...")
    except:
        print("1. ❌ Base64 decode failed")
    
    try:
        # Interpretation 2: It's the raw API key
        print(f"2. Raw API key → {api_token[:30]}...")
    except:
        print("2. ❌ Raw API key unavailable")


if __name__ == "__main__":
    analyze_current_implementation()
    base64_decoder_test()
    
    print("\n" + "="*60)
    print("🧪 API KEY TESTING")
    print("="*60)
    test_with_api_key()
    
    print("\n📝 CONCLUSION:")
    print("Based on docs, GigaChat supports:")
    print("• Client ID + Client Secret (→ Basic Auth Token)")
    print("• Pre-generated API Key (→ Authorization header)")
    print("\nOur implementation currently uses Method 1 (Client ID/Secret)")