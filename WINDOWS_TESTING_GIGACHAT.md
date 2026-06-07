# Testing GigaChat Provider on Windows

This guide covers testing the GigaChat provider changes in native Windows and WSL2 environments.

## Changes Overview

The `gigachat-plugin` branch adds live model discovery for GigaChat provider. When running `hermes model` and selecting GigaChat, the CLI now:

1. Calls the GigaChat plugin's native `fetch_models()` method
2. Displays the live list of available models from the API
3. Falls back to curated list if API is unavailable

**File modified:** `hermes_cli/main.py` (lines 5975-5991)

---

## Option 1: Native Windows (PowerShell)

### Quick Setup

```powershell
# 1. Clone the repository
git clone https://github.com/golem84/hermes-gigachat_api.git
cd hermes-gigachat_api

# 2. Checkout the gigachat-plugin branch
git checkout gigachat-plugin

# 3. Install uv (Python package manager), or don't if already done it before!
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 4. Create virtual environment
uv venv .venv --python 3.11

# 5. Activate the environment
.\.venv\Scripts\Activate.ps1

# 6. Bootstrap pip if the venv was created without it
.\.venv\Scripts\python.exe -m ensurepip --upgrade

# 7. Install the project in development mode
.\.venv\Scripts\python.exe -m pip install -e .

# 8. Verify installation
hermes version
```

### Testing the Changes

```powershell
# 1. Configure GigaChat API credentials
$env:GIGACHAT_CLIENT_ID="your_client_id"
$env:GIGACHAT_CLIENT_SECRET="your_client_secret"

# 2. Run the model picker
hermes model

# 3. Select 'gigachat' from the provider list
# Expected: List of models loaded from API:
#   - GigaChat-Max
#   - GigaChat-Plus
#   - GigaChat-Pro
#   - GigaChat-Max-Turbo
#   - GigaChat-Plus-0920
#   - GigaChat-Max-0920
```

### Running Tests

```powershell
# Activate venv
.\.venv\Scripts\Activate.ps1

# Install pytest
.\.venv\Scripts\python.exe -m pip install pytest pytest-xdist

# Run tests (single-threaded on Windows)
pytest tests/ -v -n 0
```

---

## Option 2: WSL2 (Recommended for Development)

```bash
# 1. Install WSL2 (if not already installed)
wsl --install

# 2. In WSL terminal (Ubuntu):
git clone https://github.com/golem84/hermes-gigachat_api.git
cd hermes-gigachat_api
git checkout gigachat-plugin

# 3. Install via script
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# 4. Activate environment
source .venv/bin/activate

# 5. Reinstall with changes
uv pip install -e ".[all]"

# 6. Test
hermes model
```

---

## Verification Steps

After installation, verify the changes are working:

### 1. Check Python syntax

```bash
python3 -m py_compile hermes_cli/main.py && echo "Syntax OK"
```

### 2. Verify fetch_models method exists

```bash
python3 -c "from providers import get_provider_profile; p = get_provider_profile('gigachat'); print('Has fetch_models:', hasattr(p, 'fetch_models'))"
```

### 3. Test model list retrieval

```bash
python3 -c "
from providers import get_provider_profile
import os
os.environ['GIGACHAT_CLIENT_ID'] = 'your_id'
os.environ['GIGACHAT_CLIENT_SECRET'] = 'your_secret'
p = get_provider_profile('gigachat')
models = p.fetch_models(api_key=None, timeout=8.0)
print('Models from API:', models)
"
```

### 4. Check curated fallback list

```bash
python3 -c "from hermes_cli.models import _PROVIDER_MODELS; print('Curated:', _PROVIDER_MODELS.get('gigachat', []))"
```

---

## Debugging

If the model list doesn't load:

### If `.venv` has no `pip`

Some Windows venvs are created without bundled `pip`. Bootstrap it once:

```powershell
.\.venv\Scripts\python.exe -m ensurepip --upgrade
.\.venv\Scripts\python.exe -m pip install -e .
```

### Enable verbose logging

```bash
# Set verbose mode
export HERMES_VERBOSE=1

# Or run with debug flag
hermes --verbose
```

### Check logs

```bash
# Follow logs in real-time
hermes logs --follow

# Check for errors
grep -i "gigachat\|error" ~/.hermes/logs/agent.log | tail -20
```

### Check cache

```bash
# View models.dev cache (if exists)
cat ~/.hermes/models_dev_cache.json 2>/dev/null || echo "No cache"
```

### Test API connectivity

```bash
# Test token retrieval manually
python3 -c "
import os
import base64
import urllib.request
import json

client_id = os.getenv('GIGACHAT_CLIENT_ID')
client_secret = os.getenv('GIGACHAT_CLIENT_SECRET')

if not client_id or not client_secret:
    print('Missing credentials')
    exit(1)

credentials = f'{client_id}:{client_secret}'
encoded = base64.b64encode(credentials.encode()).decode()

import uuid
url = 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth'
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'Authorization': f'Basic {encoded}',
    'RqUID': str(uuid.uuid4()),
}
data = b'scope=GIGACHAT_API_PERS'

req = urllib.request.Request(url, data=data, headers=headers, method='POST')
with urllib.request.urlopen(req, timeout=10) as response:
    result = json.loads(response.read().decode())
    print('Token obtained:', bool(result.get('access_token')))
"
```

---

## Windows-Specific Notes

### Git Bash

Native Windows uses Git Bash for shell commands. The installer automatically provisions PortableGit to `%LOCALAPPDATA%\hermes\git` if Git is not already installed.

### Dashboard Limitation

The web dashboard's embedded PTY terminal pane (`/chat` tab) requires WSL2. However, the CLI and gateway both work natively on Windows.

### Path Separators

When debugging path issues, remember Windows uses backslashes. The code should use `pathlib.Path` throughout.

### Encoding

Files are opened with `encoding="utf-8"` explicitly to avoid Windows locale issues (cp1252, etc.).

---

## Expected Output

When running `hermes model` with valid GigaChat credentials:

```
  Current model:    (not set)
  Active provider:  none

  Select a provider:
    1. OpenRouter ▸ (200+ models)
    2. Nous Portal ▸ (30+ models)
    3. Anthropic
    ...
    N. GigaChat  ← currently active
    ...

  Found 6 model(s) from GigaChat API
  Select a model:
    1. GigaChat-Max
    2. GigaChat-Plus
    3. GigaChat-Pro
    4. GigaChat-Max-Turbo
    5. GigaChat-Plus-0920
    6. GigaChat-Max-0920
    7. Enter custom model name
    8. Cancel
```

If API is unavailable, falls back to:

```
  Showing 6 curated models — use "Enter custom model name" for others.
```

---

## Common Issues

### Issue: "No module named 'providers'"

**Solution:** Ensure you're in the project directory and the venv is activated:

```powershell
cd hermes-gigachat_api
.\.venv\Scripts\Activate.ps1
```

### Issue: "401 Unauthorized" from GigaChat API

**Solution:** Check credentials:

```bash
hermes config env-path  # Check .env location
cat ~/.hermes/.env | grep GIGACHAT  # Verify keys are set
```

### Issue: Models list empty

**Solution:** Check network connectivity and API endpoint:

```bash
curl -I https://gigachat.devices.sberbank.ru/api/v1/models
```

### Issue: Tests fail on Windows

**Solution:** Some tests require POSIX primitives. Run with single thread:

```powershell
pytest tests/ -v -n 0
```

---

## References

- [Contributing Guide](website/docs/developer-guide/contributing.md)
- [Windows Native Guide](website/docs/user-guide/windows-native.md)
- [GigaChat Provider Plugin](plugins/model-providers/gigachat/__init__.py)
- [Model Selection Flow](hermes_cli/main.py#L5975-L5991)
