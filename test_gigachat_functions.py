"""Test script for GigaChat function calling support."""

import os
import base64, requests, uuid
import json


def get_gigachat_token() -> str:
    """Get GigaChat access token using the working OAuth flow."""
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


def test_function_calling():
    """Test GigaChat function calling with a simple example."""
    
    # Get token first
    print("Getting GigaChat token...")
    token = get_gigachat_token()
    if not token:
        print("Failed to get token!")
        return
    
    print(f"Token: {token[:50]}...")
    
    # Test function calling schema
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json', 
        'Authorization': f'Bearer {token}'
    }
    
    # Define a simple function for testing
    function_schema = {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a specific location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city name, e.g. 'Moscow'"
                    },
                    "unit": {
                        "type": "string", 
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit"
                    }
                },
                "required": ["location"]
            }
        }
    }
    
    # Send request with function definition
    chat_data = {
        "model": "GigaChat",
        "messages": [
            {"role": "user", "content": "What's the weather in Moscow?"}
        ],
        "tools": [function_schema],
        "stream": False
    }
    
    print("\nSending function calling request...")
    try:
        response = requests.post('https://gigachat.devices.sberbank.ru/api/v1/chat/completions', 
                               headers=headers, json=chat_data, verify=False, timeout=10)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            result = response.json()
            print("\nFull response:")
            print(json.dumps(result, indent=2))
            
            # Check if function was called
            if 'choices' in result and result['choices']:
                message = result['choices'][0].get('message', {})
                if 'tool_calls' in message:
                    print("\n✅ Function calling supported!")
                    print(f"Tool calls: {json.dumps(message['tool_calls'], indent=2)}")
                elif 'function_call' in message:
                    print("\n✅ Function calling supported (legacy format)!")
                    print(f"Function call: {json.dumps(message['function_call'], indent=2)}")
                else:
                    print("\n⚠️ No function call in response")
                    print(f"Message content: {message.get('content', 'N/A')}")
        else:
            print(f"❌ Request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_function_calling()