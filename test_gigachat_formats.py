"""Extended test for GigaChat function calling - multiple format attempts."""

import os
import requests, uuid
import json


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


def test_different_tool_formats():
    """Test different tool format variations."""
    
    token = get_gigachat_token()
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json', 
        'Authorization': f'Bearer {token}'
    }
    
    simple_function = {
        "name": "get_weather",
        "description": "Get current weather for a specific location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city name"
                }
            },
            "required": ["location"]
        }
    }
    
    tests = [
        {
            "name": "OpenAI format: tools array",
            "tools": [simple_function]
        },
        {
            "name": "OpenAI nested format",
            "tools": [{"type": "function", "function": simple_function}]
        },
        {
            "name": "functions parameter (legacy)",
            "functions": [simple_function]
        },
        {
            "name": "No tools (baseline)",
        }
    ]
    
    user_message = "What's the temperature in Moscow in Celsius?"
    
    for test in tests:
        print(f"\n{'='*60}")
        print(f"Testing: {test['name']}")
        print(f"{'='*60}")
        
        chat_data = {
            "model": "GigaChat",
            "messages": [
                {"role": "user", "content": user_message}
            ],
            "stream": False,
            "temperature": 0.7
        }
        
        # Add whichever tool format we're testing
        if 'tools' in test:
            chat_data['tools'] = test['tools']
        elif 'functions' in test:
            chat_data['functions'] = test['functions']
        
        try:
            response = requests.post('https://gigachat.devices.sberbank.ru/api/v1/chat/completions', 
                                   headers=headers, json=chat_data, verify=False, timeout=10)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                message = result['choices'][0]['message']
                
                print(f"Content: {message.get('content', 'N/A')[:100]}")
                
                if 'tool_calls' in message:
                    print(f"✅ Tool calls detected: {json.dumps(message['tool_calls'], indent=2)}")
                elif 'function_call' in message:
                    print(f"✅ Function call detected: {json.dumps(message['function_call'], indent=2)}")
                else:
                    print("⚠️ No function calls in response")
            else:
                print(f"❌ Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")


if __name__ == "__main__":
    test_different_tool_formats()