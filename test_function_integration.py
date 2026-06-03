"""Comprehensive test for GigaChat function calling integration."""

import os, requests, uuid, json


def get_gigachat_token() -> str:
    """Get GigaChat access token."""
    api_token = os.getenv("GIGACHAT_API_TOKEN")
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json', 
        'RqUID': str(uuid.uuid4()),
        'Authorization': f'Basic {api_token}'
    }
    data = b'scope=GIGACHAT_API_PERS'
    
    req = requests.post(url, headers=headers, data=data, verify=False, timeout=10)
    result = req.json()
    return result.get('access_token')


def test_comprehensive_function_calling():
    """Test complete function calling workflow."""
    
    print("🧪 GigaChat Function Calling Integration Test")
    print("=" * 70)
    
    token = get_gigachat_token()
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json', 
        'Authorization': f'Bearer {token}'
    }
    
    # Define tool set simulating Hermes tool format
    hermes_tools = [
        {
            "type": "function",
            "function": {
                "name": "search_web",
                "description": "Search the web for information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function", 
            "function": {
                "name": "calculate_math",
                "description": "Perform mathematical calculations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "Math expression"},
                    },
                    "required": ["expression"]
                }
            }
        }
    ]
    
    # Transform from Hermes format to GigaChat format (simulating provider logic)
    gigachat_functions = [tool["function"] for tool in hermes_tools]
    
    test_cases = [
        {
            "user_message": "Search for 'AI news' and tell me about recent developments",
            "expected_function": "search_web",
            "description": "Tool calling with web search"
        },
        {
            "user_message": "Calculate 25 + 37 * 2",
            "expected_function": "calculate_math", 
            "description": "Tool calling with math calculation"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['description']}")
        print(f"📝 User: {test_case['user_message']}")
        
        chat_data = {
            "model": "GigaChat",
            "messages": [
                {"role": "user", "content": test_case["user_message"]}
            ],
            "functions": gigachat_functions,
            "stream": False,
            "temperature": 0.1
        }
        
        try:
            response = requests.post(
                'https://gigachat.devices.sberbank.ru/api/v1/chat/completions',
                headers=headers, json=chat_data, verify=False, timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                message = result['choices'][0]['message']
                finish_reason = result['choices'][0]['finish_reason']
                
                # Check response structure
                print(f"✅ Response received (finish_reason: {finish_reason})")
                
                if 'function_call' in message:
                    func_name = message['function_call']['name']
                    func_args = message['function_call']['arguments']
                    
                    # Simulate transformation back to Hermes format
                    tool_call = {
                        "id": f"call_{func_name}",
                        "type": "function",
                        "function": {
                            "name": func_name,
                            "arguments": json.dumps(func_args)
                        }
                    }
                    
                    print(f"🎯 Function called: {func_name}")
                    print(f"📦 Arguments: {json.dumps(func_args, indent=2)}")
                    print(f"🔄 Hermes format: {json.dumps(tool_call, indent=2)}")
                    
                    if func_name == test_case["expected_function"]:
                        print("✅ Correct function called!")
                        results.append(True)
                    else:
                        print(f"❌ Expected {test_case['expected_function']}, got {func_name}")
                        results.append(False)
                else:
                    print("⚠️ No function call in response")
                    print(f"💬 Content: {message.get('content', 'N/A')[:100]}")
                    results.append(None)
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"📄 Error details: {response.text[:200]}")
                results.append(False)
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            results.append(False)
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 TEST SUMMARY")
    print(f"{'='*70}")
    
    passed = sum(1 for r in results if r is True)
    failed = sum(1 for r in results if r is False)
    neutral = sum(1 for r in results if r is None)
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}") 
    print(f"⚠️  Neutral: {neutral}")
    print(f"📈 Success Rate: {passed/len(results)*100:.1f}%")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Function calling implementation is working correctly.")
    else:
        print(f"\n⚠️  Some tests failed. Review the results above.")
        
    return results


if __name__ == "__main__":
    test_comprehensive_function_calling()