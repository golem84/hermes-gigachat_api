# GigaChat Function Calling Implementation

## Overview
Complete function calling support for GigaChat provider, bridging the gap between GigaChat's legacy function format and Hermes' modern OpenAI-compatible tool system.

## Format Differences

### Hermes/OpenAI Format (Modern)
**Request:**
```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Get weather information",
        "parameters": {
          "type": "object",
          "properties": { ... },
          "required": ["location"]
        }
      }
    }
  ]
}
```

**Response:**
```json
{
  "choices": [
    {
      "message": {
        "tool_calls": [
          {
            "id": "call_abc123",
            "type": "function", 
            "function": {
              "name": "get_weather",
              "arguments": "{\"location\": \"Moscow\"}"
            }
          }
        ]
      }
    }
  ]
}
```

### GigaChat Format (Legacy)
**Request:**
```json
{
  "functions": [
    {
      "name": "get_weather",
      "description": "Get weather information", 
      "parameters": {
        "type": "object",
        "properties": { ... },
        "required": ["location"]
      }
    }
  ]
}
```

**Response:**
```json
{
  "choices": [
    {
      "message": {
        "function_call": {
          "name": "get_weather",
          "arguments": {
            "location": "Moscow"
          }
        }
      },
      "finish_reason": "function_call"
    }
  ]
}
```

## Implementation Details

### 1. Request Transformation (`build_api_kwargs_extras`)
- Converts Hermes `tools` format to GigaChat `functions` format
- Handles both modern OpenAI format and already-converted legacy format
- Maintains backward compatibility

### 2. Message Preprocessing (`prepare_messages`)
- Converts modern `tool_calls` to legacy `function_call`
- Transforms `tool` role messages to `function` role
- Preserves message structure for GigaChat compatibility

### 3. Response Transformation (`_transform_gigachat_response_to_openai`)
- Converts GigaChat `function_call` responses back to OpenAI `tool_calls`
- Generates proper tool call IDs for Hermes tracking
- Maintains dual format support (both legacy and modern)

## Key Features
- ✅ Bidirectional transformation (Hermes ⇄ GigaChat)
- ✅ Support for multiple functions in single request
- ✅ Proper handling of function response messages
- ✅ Maintains finish_reason for function calls
- ✅ Preserves GigaChat-specific fields (functions_state_id)

## Testing Results
- ✅ Single function calls work correctly
- ✅ Multiple function definitions handled
- ✅ Response format fully compatible with Hermes tool system
- ✅ Argument serialization/deserialization correct
- ✅ Tool call ID generation for tracking

## Usage Example
```python
# Hermes provides tools in standard format
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                }
            }
        }
    }
]

# Provider automatically handles transformation
response = profile.build_api_kwargs_extras(tools=tools)
# Result: {"functions": [{"name": "get_weather", "parameters": {...}}]}
```

## Technical Notes
1. **GigaChat Limitations**: Uses older function calling API, may have limited support for advanced features like streaming function calls
2. **Arguments Format**: GigaChat uses dict objects for arguments, OpenAI uses JSON strings - conversion handled automatically
3. **Finish Reason**: GigaChat uses `"function_call"`, matches OpenAI expected value
4. **Tool Call IDs**: Generated from function name (`<call_<function_name>`) for Hermes compatibility

## Performance Considerations
- Transformation overhead minimal (simple JSON manipulation)
- No extra API calls required
- Transformation happens in-memory
- Compatible with large tool sets (tested with 10+ functions)

## Future Enhancements
- Support for GigaChat-specific function calling features
- Advanced error handling for malformed function calls  
- Streaming support for function call responses
- Function state tracking (functions_state_id field)