# GigaChat Provider Implementation

## Overview
This implements a GigaChat provider plugin for Hermes Agent that enables:
- Authentication with Sberbank's GigaChat API
- Access to GigaChat models (GigaChat, GigaChat-2, GigaChat-Max, etc.)
- Support for GigaChat's native function calling format

## Key Implementation Details

### Authentication
The plugin supports two authentication methods:
1. Direct API token via `GIGACHAT_API_TOKEN` environment variable
2. Client credentials flow using `GIGACHAT_CLIENT_ID` and `GIGACHAT_CLIENT_SECRET` to fetch tokens from Sberbank's NGW endpoint

### Model Discovery
Implements `fetch_models()` to dynamically retrieve available models from:
```
https://gigachat.devices.sberbank.ru/api/v1/models
```

### Function Calling Support
Based on research from `/home/hermes/projects/gigachat/README.md`, GigaChat:
- Does NOT support OpenAI `tools` format
- DOES support native `functions` format
- Returns `function_call` in responses when functions are used

The actual translation between OpenAI tools format and GigaChat functions format will need to be handled in the transport layer or agent logic, as the provider profile mainly handles authentication and metadata.

## Configuration
Add to your `.env` file:
```
# Option 1: Direct token
GIGACHAT_API_TOKEN=your_token_here

# Option 2: Client credentials (for automatic token refresh)
GIGACHAT_CLIENT_ID=your_client_id
GIGACHAT_CLIENT_SECRET=your_client_secret
```

## Testing
To test the plugin:
1. Ensure credentials are set in environment
2. The plugin should appear in the provider list
3. Model fetching should work
4. Chat completions should function with supported models

## Known Limitations
- The current implementation assumes standard chat completions work
- Function calling translation layer needs to be implemented separately
- Streaming support needs to be verified