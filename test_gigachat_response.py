"""Test GigaChat function call response format."""

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


def analyze_function_call_response():
    """Analyze the structure of function call responses from GigaChat."""
    
    token = get_gigachat_token()
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json', 
        'Authorization': f'Bearer {token}'
    }
    
    # Define multiple functions to test
    functions = [
        {
            "name": "get_weather",
            "description": "Get current weather for a specific location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"},
                },
                "required": ["location"]
            }
        },
        {
            "name": "get_time", 
            "description": "Get current time in a specific timezone",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {"type": "string", "description": "Timezone like 'Europe/Moscow'"},
                },
                "required": ["timezone"]
            }
        }
    ]
    
    chat_data = {
        "model": "GigaChat",
        "messages": [
            {"role": "user", "content": "What time is it in Moscow?"}
        ],
        "functions": functions,
        "stream": False,
        "temperature": 0.1
    }
    
    print("Testing function call response structure...")
    response = requests.post('https://gigachat.devices.sberbank.ru/api/v1/chat/completions', 
                           headers=headers, json=chat_data, verify=False, timeout=10)
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ Full Response Structure:")
        print(json.dumps(result, indent=2))
        
        message = result['choices'][0]['message']
        print(f"\n🔍 Message structure:")
        print(json.dumps(message, indent=2))
        
        # Check for both possible formats
        if 'tool_calls' in message:
            print(f"\n✅ Modern 'tool_calls' format found:")
            print(json.dumps(message['tool_calls'], indent=2))
        elif 'function_call' in message:
            print(f"\n✅ Legacy 'function_call' format found:")
            print(json.dumps(message['function_call'], indent=2))
        else:
            print(f"\n⚠️ No function call found in response")
            print(f"Message content: {message.get('content', 'N/A')}")
            
        # Check finish reason
        print(f"\n🔍 Finish reason: {result['choices'][0].get('finish_reason', 'unknown')}")
        
    else:
        print(f"❌ Error: {response.status_code}")


if __name__ == "__main__":
    analyze_function_call_response()