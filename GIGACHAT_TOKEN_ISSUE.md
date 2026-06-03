# GigaChat OAuth Token Issue Analysis

## Problem
Companion support for GigaChat plugin is blocked by OAuth token acquisition failure.

## Error Details
- **Endpoint**: `https://ngw.devices.sberbank.ru:9443/api/v2/oauth`
- **Method**: POST
- **Response**: HTTP 400 Bad Request
- **Error Message**: `{"code":4,"message":"Can't decode 'Authorization' header"}`
- **Credentials**: Valid client_id and client_secret confirmed (base64 decodes correctly)

## Attempted Solutions (All Failed)

### 1. Basic Authorization Header (recommended in docs)
```
Authorization: Basic <base64(client_id:client_secret)>
Content-Type: application/x-www-form-urlencoded
Body: scope=GIGACHAT_API_PERS
```
Result: HTTP 400

### 2. Request Body Credentials (without Authorization header)
```
Content-Type: application/x-www-form-urlencoded
Body: scope=GIGACHAT_API_PERS&client_id=<id>&client_secret=<secret>
```
Result: HTTP 400

### 3. Client Credentials Grant Type
```
Authorization: Basic <base64(client_id:client_secret)>
Content-Type: application/x-www-form-urlencoded
Body: grant_type=client_credentials&scope=GIGACHAT_API_PERS
```
Result: HTTP 400

### 4. Different RqUID Formats
- Tested: UUID4, UUID without dashes, 16 hex characters
Result: HTTP 400 for all formats

### 5. Different Content Types
- Tested: JSON vs x-www-form-urlencoded
Result: HTTP 400 (or HTTP 415 for unsupported type)

### 6. Header Variations
- Tested: Bearer instead of Basic
- Tested: No Authorization header at all
Result: HTTP 400

### 7. Base URL Variations for API Access
- Tested multiple API endpoints with static token
Result: HTTP 401 (Unauthorized) or HTTP 403 (Forbidden)

## Analysis
The OAuth endpoint consistently returns HTTP 400 with "Can't decode 'Authorization' header", despite:
- Correct base64 encoding of client_id:client_secret
- Proper header formatting ("Authorization: Basic <token>")
- Valid credentials

This suggests a possible issue with:
1. The GigaChat OAuth endpoint expectations have changed
2. The OAuth endpoint requires additional parameters not documented
3. The OAuth endpoint is misconfigured or has server-side issues
4. The OAuth endpoint expects a different authentication flow

## Next Steps Required
1. **Check GigaChat documentation**: Verify current OAuth requirements from official docs
2. **Examine existing implementations**: Look for other open source projects that successfully authenticate with GigaChat
3. **Contact GigaChat support**: May need to reach out to Sberbank for OAuth endpoint issue
4. **Alternative approaches**: Consider if the plugin can use a different authentication method or API endpoint

## Notes
- SSL certificate issue temporarily bypassed with verify=False for testing
- Static token from environment variable returns HTTP 401/403 when used directly
- All variations of request formatting have been exhausted

