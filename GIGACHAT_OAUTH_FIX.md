# GigaChat OAuth Issue Resolution

## Problem
OAuth token acquisition was failing with HTTP 400 error and message: `{"code":4,"message":"Can't decode 'Authorization' header"}`

## Root Cause
The issue was in the format of the `RqUID` parameter. The code was using random 16 hex characters instead of UUIDv4 format as required by GigaChat official documentation.

## Solution
Changed `RqUID` generation from:
```python
"RqUID": os.urandom(16).hex()  # INCORRECT - random hex
```

To:
```python
import uuid
"RqUID": str(uuid.uuid4())  # CORRECT - UUIDv4 format
```

## Correct OAuth Request Format
Per GigaChat official documentation:
```
curl -L -X POST 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth' \
-H 'Content-Type: application/x-www-form-urlencoded' \
-H 'Accept: application/json' \
-H 'RqUID: <uuid4>' \
-H 'Authorization: Basic <base64(client_id:client_secret)>' \
--data-urlencode 'scope=GIGACHAT_API_PERS'
```

## Testing Results
After the fix:
- ✅ Token acquisition successful (HTTP 200)
- ✅ Models endpoint working (HTTP 200)
- ✅ Chat completions working (HTTP 200)
- ✅ Available models detected: GigaChat, GigaChat-2, GigaChat-2-Max, GigaChat-2-Pro, GigaChat-Max, GigaChat-Plus, GigaChat-Pro, etc.

## API Details
- **OAuth Endpoint**: `https://ngw.devices.sberbank.ru:9443/api/v2/oauth`
- **API Base URL**: `https://gigachat.devices.sberbank.ru/api/v1`
- **Authentication**: Bearer token (30-minute expiration)
- **Scope**: `GIGACHAT_API_PERS`

## Implementation Changes
1. Updated `_get_gigachat_token()` function to use UUIDv4 format for RqUID
2. Added proper imports and error handling
3. Maintained backward compatibility with both `GIGACHAT_API_TOKEN` (base64 encoded) and separate `GIGACHAT_CLIENT_ID`/`GIGACHAT_CLIENT_SECRET`

## Notes
- SSL verification disabled for testing (self-signed certificate)
- Token expiration is 30 minutes as per GigaChat documentation
- The provider is now fully functional and ready for testing with Hermes agent