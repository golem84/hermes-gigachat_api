# GigaChat Quick Integration Guide

## ⚡ One-Line Setup Options

### Option 1: Quick API Token Setup (Recommended)
```bash
# Using hermes config command
hermes config set GIGACHAT_API_TOKEN your_base64_token_here

# Using interactive setup script  
python setup_gigachat.py --quick
```

### Option 2: Client ID + Secret Setup
```bash
# Set credentials individually
hermes config set GIGACHAT_CLIENT_ID your_client_id
hermes config set GIGACHAT_CLIENT_SECRET your_secret

# Or use interactive setup  
python setup_gigachat.py --client-creds
```

## 🎯 What You Need

### Get Your Credentials
1. **Register** at [GigaChat Developer Portal](https://developers.sber.ru/)
2. **Create app** → Get Client ID and Secret
3. **Choose method:**
   - **A.** Use API Token (Client ID + Secret base64 encoded)
   - **B.** Use Client ID + Secret individually

### Generate API Token
```bash
# If you have Client ID + Secret, generate token:
echo -n "client_id:client_secret" | base64

# Output: your_api_token_to_use_with_hermes_config_set
```

## 🚀 Usage Examples

### Basic Chat
```bash
# Start interactive chat
hermes --model gigachat

# Ask a question directly
hermes --model gigachat "Привет, как дела?"

# Use specific model
hermes --model gigachat:GigaChat-2-Max "Анализ данных..."
```

### With Tools
```bash
# Enable function calling
hermes --model gigachat --enable-tools

# Use with specific tool
hermes --model gigachat --tool search_web "AI новости"
```

## 🔧 Configuration Options

### Environment Variables (Set via hermes config)
```env
# Method A: Pre-computed API token (recommended)
GIGACHAT_API_TOKEN=your_base64_token

# Method B: Client credentials (alternative)
GIGACHAT_CLIENT_ID=your_client_id
GIGACHAT_CLIENT_SECRET=your_secret
```

### Model Selection
```bash
# List available models
hermes models list --provider gigachat

# Use specific model variants
hermes --model gigachat         # Basic model
hermes --model gigachat:GigaChat-2-Max   # Advanced model
hermes --model gigachat:GigaChat-Pro    # Production model
```

## ⚙️ Advanced Configuration

### Token Refresh
Tokens expire after 30 minutes - handled automatically.

### SSL Verification
Currently disabled for testing. For production:
```bash
# Add GigaChat certificates to system trust store
sudo cp /path/to/gigachat/certs/*.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
```

### Function Calling
Automatically enabled when you use `--enable-tools` flag:
```bash
hermes --model gigachat --enable-tools "Покажи погоду в Москве"
```

## 🧪 Test Your Setup

### Verify Configuration
```bash
# Check if GigaChat is configured
hermes config show | grep GIGACHAT

# Test connection
python setup_gigachat.py --test
```

### Quick Test
```bash
# Simple test message
hermes --model gigachat "Тест"

# Check available models  
hermes models list --provider gigachat
```

## 📊 Available Models

| Model | Speed | Quality | Best For |
|-------|-------|---------|----------|
| `gigachat` | Fast | Good | Quick tasks |
| `gigachat:GigaChat-2` | Medium | Better | General use |
| `gigachat:GigaChat-2-Max` | Slower | Best | Complex reasoning |
| `gigachat:GigaChat-Pro` | Medium | Excellent | Production apps |
| `gigachat:GigaChat-2-Pro` | Medium | Excellent | Advanced features |
| `gigachat:GigaChat-Max` | Slower | Best | High-quality tasks |
| `gigachat:GigaChat-Plus` | Medium | Better | Balanced tasks |

## 🔍 Troubleshooting

### "Provider not found"
```bash
# Ensure plugin is installed
ls hermes-agent/plugins/model-providers/gigachat/

# Restart Hermes
# Plugin will be autoloaded
```

### "Connection failed"
```bash
# Check credentials
hermes config show | grep GIGACHAT

# Test manually
python setup_gigachat.py --test
```

### "SSL certificate error"
```bash
# Temporary (development)
# SSL verification is automatically disabled

# Production: Add certificates
sudo update-ca-certificates
```

## 🎯 Integration Checklist

- [ ] Register at GigaChat Developer Portal
- [ ] Get Client ID and/or Secret
- [ ] Generate API Token (Optional)
- [ ] Run `hermes config set GIGACHAT_API_TOKEN <token>`
- [ ] Test with `echo "test" | hermes --model gigachat`
- [ ] Verify models with `hermes models list --provider gigachat`
- [ ] Try with tools: `hermes --model gigachat --enable-tools`

## 🚀 Production Deployment

### Security
- [ ] Rotate credentials periodically
- [ ] Enable SSL verification
- [ ] Use environment variables for secrets
- [ ] Monitor usage via GigaChat Portal

### Performance
- [ ] Cache tokens where possible
- [ ] Use appropriate model for task complexity
- [ ] Implement rate limiting
- [ ] Monitor API costs

## 📞 Support & Resources

- **GigaChat Docs**: [developers.sber.ru](https://developers.sber.ru/docs/ru/gigachat)
- **Hermes Docs**: [GitHub Repository](https://github.com/NousResearch/hermes-agent)
- **Setup Help**: Run `python setup_gigachat.py` (interactive)

## 💡 Pro Tips

1. **Fastest setup**: Use API token method (`GIGACHAT_API_TOKEN`)
2. **Testing**: Start with basic model (`gigachat`) before advanced
3. **Function calling**: Just add `--enable-tools` - no extra config needed
4. **Best performance**: Use `GigaChat-2-Max` for complex tasks
5. **Production**: Enable SSL verification and monitor costs

---

## Summary: 30-Second Setup

```bash
# 1. Get API token from GigaChat Portal
# 2. Run one command:
hermes config set GIGACHAT_API_TOKEN your_token

# 3. Done! Start using:
hermes --model gigachat "Привет!"
```

🎉 That's it! Full GigaChat integration ready in one line of code!