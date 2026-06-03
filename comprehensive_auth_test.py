"""Test different authorization methods for GigaChat OAuth."""

import os, requests, uuid, json, base64


def get_credentials():
    """Get available credentials from environment."""
    client_id = os.getenv("GIGACHAT_CLIENT_ID")
    client_secret = os.getenv("GIGACHAT_CLIENT_SECRET")
    api_token = os.getenv("GIGACHAT_API_TOKEN")
    
    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "api_token": api_token,
        "has_client_credentials": bool(client_id and client_secret),
        "has_api_token": bool(api_token)
    }


def test_auth_method(method_name, auth_value, auth_type="Basic"):
    """Test a specific authorization method."""
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json', 
        'RqUID': str(uuid.uuid4()),
        'Authorization': f'{auth_type} {auth_value}'
    }
    
    data = b'scope=GIGACHAT_API_PERS'
    
    print(f"\n🧪 Testing: {method_name}")
    print(f"   Auth Type: {auth_type}")
    print(f"   Value: {auth_value[:20]}...")
    
    try:
        req = requests.post(url, headers=headers, data=data, verify=False, timeout=10)
        
        if req.status_code == 200:
            result = req.json()
            print(f"   ✅ SUCCESS!")
            print(f"   Token: {result.get('access_token', 'N/A')[:20]}...")
            return True
        else:
            print(f"   ❌ FAILED: {req.status_code}")
            print(f"   Error: {req.text[:100]}")
            return False
            
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
        return False


def comprehensive_auth_test():
    """Test all possible authorization methods."""
    creds = get_credentials()
    
    print("="*70)
    print("🔍 COMPREHENSIVE AUTHORIZATION METHOD TESTING")
    print("="*70)
    
    print(f"\n📋 Available Credentials:")
    print(f"   Client ID: {'✅' if creds['client_id'] else '❌'}")
    print(f"   Client Secret: {'✅' if creds['client_secret'] else '❌'}")
    print(f"   API Token: {'✅' if creds['api_token'] else '❌'}")
    
    results = {}
    
    # Method 1: Client ID + Client Secret → Base64 → Basic Auth
    if creds['has_client_credentials']:
        basic_token = base64.b64encode(
            f"{creds['client_id']}:{creds['client_secret']}".encode()
        ).decode()
        results['Method 1: Basic (Derived from Client ID/Secret)'] = test_auth_method(
            "Method 1: Basic (Derived from Client ID/Secret)",
            basic_token,
            "Basic"
        )
    
    # Method 2: GIGACHAT_API_TOKEN as Basic Auth
    if creds['has_api_token']:
        results['Method 2: Basic (GIGACHAT_API_TOKEN)'] = test_auth_method(
            "Method 2: Basic (GIGACHAT_API_TOKEN)",
            creds['api_token'],
            "Basic"
        )
    
    # Method 3: GIGACHAT_API_TOKEN as Bearer Auth
    if creds['has_api_token']:
        results['Method 3: Bearer (GIGACHAT_API_TOKEN)'] = test_auth_method(
            "Method 3: Bearer (GIGACHAT_API_TOKEN)",
            creds['api_token'],
            "Bearer"
        )
    
    # Method 4: Client ID + Client Secret → Base64 → Bearer Auth (unlikely but test)
    if creds['has_client_credentials']:
        basic_token = base64.b64encode(
            f"{creds['client_id']}:{creds['client_secret']}".encode()
        ).decode()
        results['Method 4: Bearer (Derived from Client ID/Secret)'] = test_auth_method(
            "Method 4: Bearer (Derived from Client ID/Secret)",
            basic_token,
            "Bearer"
        )
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 TEST SUMMARY")
    print(f"{'='*70}")
    
    for method, result in results.items():
        status = "✅ SUCCESS" if result else "❌ FAILED"
        print(f"{status} - {method}")
    
    successful = sum(1 for r in results.values() if r)
    print(f"\n🎯 Success Rate: {successful}/{len(results)} ({successful/len(results)*100:.0f}%)")
    
    return results


if __name__ == "__main__":
    results = comprehensive_auth_test()
    
    # Based on docs check what's expected
    print(f"\n📝 OFFICIAL DOCS REQUIRE:")
    print(f"   Authorization: Basic authorization_key")
    print(f"   Where authorization_key should be Client ID + Secret")
    
    working_methods = [m for m, r in results.items() if r]
    if working_methods:
        print(f"\n✅ WORKING METHOD(S): {', '.join(working_methods)}")
    else:
        print(f"\n❌ NO WORKING METHODS FOUND")