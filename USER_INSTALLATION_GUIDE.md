# GigaChat Plugin Installation Guide for Hermes

## 🚀 Quick Start

### 1. Install Dependencies
The GigaChat plugin requires Python libraries. Install them via your package manager:

```bash
# Using uv (recommended for Hermes)
uv pip install requests

# Or using pip
pip install requests
```

### 2. Configure Environment Variables
Add these variables to your Hermes `.env` file:

```env
# GigaChat OAuth Credentials (REQUIRED)
GIGACHAT_CLIENT_ID=your_client_id_here
GIGACHAT_CLIENT_SECRET=your_client_secret_here

# Pre-computed Basic Auth Token (alternative approach)
GIGACHAT_API_TOKEN=your_base64_encoded_token_here
```

### 3. Get GigaChat Credentials

#### Option A: Create New Credentials (Recommended)
1. Register at [GigaChat Developer Portal](https://developers.sber.ru/)
2. Create a new application
3. Copy your `Client ID` and `Client Secret`
4. Set them in your `.env` file

#### Option B: Manual Basic Auth Token
If you prefer to pre-compute the Basic Auth token:
```bash
# Generate token from client_id:client_secret
echo -n "your_client_id:your_client_secret" | base64
```

### 4. Verify Plugin Installation
The plugin should be automatically detected by Hermes. Check if it's available:

```bash
hermes models list | grep gigachat
```

Expected models:
- `GigaChat`, `GigaChat-2`, `GigaChat-2-Max`, `GigaChat-2-Pro`
- `GigaChat-Max`, `GigaChat-Plus`, `GigaChat-Pro`
- `GigaChat-2-Retriever`, `GigaChat2-Pro-Retriever`

## 🔧 Configuration Options

### SSL Verification (Production Security)
GigaChat uses self-signed certificates in their certificate chain. By default, SSL verification is disabled to allow immediate testing.

**Default (Development):**
```bash
# SSL verification disabled by default for GigaChat
# This allows connection despite self-signed certificates
```

**Production (Recommended):**
For production use, add GigaChat's CA certificate to your system trust store:
```bash
# Download GigaChat certificates and add to OS trust store
sudo cp gigachat_certs/*.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
# Then enable verification
export GIGACHAT_SSL_VERIFY=true
```

**Temporary Override:**
```bash
# Force SSL verification (will fail without proper CA certs)
export GIGACHAT_SSL_VERIFY=true

# Explicitly disable (default behavior)
export GIGACHAT_SSL_VERIFY=false
```

### Token Refresh Strategy
GigaChat tokens expire after 30 minutes. The plugin automatically obtains new tokens when needed.

## 📋 Usage Examples

### Basic Chat
```bash
hermes chat --model gigachat --message "Привет, как дела?"
```

### Interactive Session
```bash
hermes chat --model gigachat:GigaChat-2-Max
```

### Using with Tools
The plugin supports function calling automatically:
```bash
hermes chat --model gigachat --enable-tools
```

## 🔍 Troubleshooting

### "Provider not found" Error
Ensure the plugin files are in the correct location:
```
hermes-agent/plugins/model-providers/gigachat/__init__.py
hermes-agent/plugins/model-providers/__init__.py
```

### OAuth 400/401 Errors
1. Check credentials in `.env` file
2. Verify the RqUID format uses UUIDv4 (automatically handled)
3. Confirm network connectivity to GigaChat endpoints

### SSL Certificate Errors
- **Default behavior**: SSL verification is disabled by default for GigaChat (`GIGACHAT_SSL_VERIFY=false`)
- **Connection errors**: If you still see SSL errors, ensure `GIGACHAT_SSL_VERIFY=false` is set
- **Production**: Set `GIGACHAT_SSL_VERIFY=true` only after adding GigaChat CA to your system trust store
- **Temporary test**: `export GIGACHAT_SSL_VERIFY=false` to explicitly disable verification

### Model Not Available
1. Run `hermes models list --provider gigachat` to see available models
2. Check your GigaChat account permissions
3. Verify network connectivity to `gigachat.devices.sberbank.ru`

## 🔒 Security Best Practices

### Protect Your Credentials
- Never commit `.env` file to version control
- Use environment variables for all sensitive data
- Rotate Client Secrets periodically
- Monitor usage through GigaChat Developer Portal

### Network Security
- Enable SSL verification in production
- Use firewalls to restrict GigaChat API access
- Monitor API usage for anomalies
- Implement rate limiting at application level

## 🚀 Advanced Configuration

### Custom Model Selection
You can select specific GigaChat models:
```bash
# Basic model
hermes --model gigachat

# Advanced model (better reasoning)  
hermes --model gigachat:GigaChat-2-Max

# Production model (enhanced capabilities)
hermes --model gigachat:GigaChat-Pro
```

### Function Calling
The plugin handles function calling automatically. Just enable tools:
```bash
hermes --model gigachat --tools-enabled
```

Supported tool formats are automatically converted between Hermes and GigaChat.

## 📊 Performance Considerations

### Expected Latency
- **Token Acquisition**: ~200-500ms (cached for 30 min)
- **API Response**: 1-5 seconds depending on model
- **Function Calls**: Additional 100-200ms processing

### Model Performance
| Model | Speed | Quality | Best For |
|-------|-------|---------|----------|
| GigaChat | Fast | Good | Quick tasks |
| GigaChat-2 | Medium | Better | General use |
| GigaChat-2-Max | Slower | Best | Complex reasoning |
| GigaChat-Pro | Medium | Excellent | Production apps |

## 🌐 API Endpoints

The plugin uses these GigaChat endpoints:
- **OAuth**: `https://ngw.devices.sberbank.ru:9443/api/v2/oauth`
- **Chat**: `https://gigachat.devices.sberbank.ru/api/v1/chat/completions`
- **Models**: `https://gigachat.devices.sberbank.ru/api/v1/models`

Ensure firewall rules allow connectivity to these domains.

## 🎯 Next Steps

1. **Test Basic Functionality**:
   ```bash
   hermes --model gigachat --message "Test message"
   ```

2. **Configure Advanced Features**:
   Enable tools, SSL verification, and custom models

3. **Monitor Usage**:
   Check GigaChat Developer Portal for API usage statistics

4. **Production Deployment**:
   Update SSL certificates, configure rate limiting, set up monitoring

## 📞 Support & Resources

- **GigaChat Documentation**: [GigaChat API Guide](https://developers.sber.ru/docs/ru/gigachat)
- **Hermes Documentation**: [Hermes GitHub](https://github.com/NousResearch/hermes-agent)
- **Issues**: Report bugs via GitHub Issues

---

## Summary Checklist ✅

For production integration, users need to:

- [ ] Install Python `requests` library
- [ ] Register at GigaChat Developer Portal  
- [ ] Get Client ID and Client Secret
- [ ] Add credentials to Hermes `.env` file
- [ ] Test basic chat functionality
- [ ] Configure SSL verification (production)
- [ ] Enable tools/function calling if needed
- [ ] Monitor usage via GigaChat dashboard

**That's it!** The plugin handles all format transformations automatically once configured.