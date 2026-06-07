# GigaChat Provider Plugin for Hermes Agent

GigaChat provider plugin for Hermes Agent with chat, model selection, and `function calling` support.

This plugin exists as a dedicated adapter because GigaChat uses a native `functions` format and Hermes needs a custom compatibility layer to speak it in the usual OpenAI-shaped contract. The generic provider path is not precise enough here: `tools` / `tool_calls` / `tool.role="tool"` need explicit translation to and from GigaChat's format.

## Quick Summary

- Works in `hermes chat`, `hermes model`, `hermes mcp`, and the shared Hermes gateway/TUI/Desktop stack.
- Supports Linux, macOS, Windows, and WSL2.
- No official Python SDK is required for standard chat and `function calling`.
- The official SDK is optional for advanced features.

## Official GigaChat Docs

- [Main docs](https://developers.sber.ru/docs/ru/gigachat)
- [API reference](https://developers.sber.ru/docs/ru/gigachat/reference)
- [Quick start](https://developers.sber.ru/docs/ru/gigachat/guides/quickstart)
- [Auth and tokens](https://developers.sber.ru/docs/ru/gigachat/guides/auth)
- [Function calling](https://developers.sber.ru/docs/ru/gigachat/guides/functions)
- [Limits](https://developers.sber.ru/docs/ru/gigachat/guides/limits)

## Getting Started

### 1. Get credentials

1. Register at the [GigaChat Developer Portal](https://developers.sber.ru/).
2. Create an application.
3. Copy `Client ID` and `Client Secret`.

### 2. Configure with `hermes model`

This is the recommended path for most users:

```bash
hermes model
```

Then:

1. Choose `gigachat`.
2. Enter `Client ID`.
3. Enter `Client Secret`.
4. Wait for credential verification.
5. Pick a model from the live list.

### 3. Start chatting

```bash
hermes chat
```

If setup is complete, Hermes will use GigaChat normally from the CLI.

## Where to Run It

### Linux / macOS / WSL2

- Use a POSIX shell: `bash`, `zsh`, `fish`, etc.
- In WSL2, use the Linux instructions inside WSL, not Windows PowerShell.
- If Hermes runs in WSL2, configure the plugin inside the WSL2 Hermes profile.

Example with environment variables:

```bash
export GIGACHAT_CLIENT_ID="your_client_id"
export GIGACHAT_CLIENT_SECRET="your_client_secret"
```

### Windows native

- Use PowerShell.
- Temporary environment variables:

```powershell
$env:GIGACHAT_CLIENT_ID="your_client_id"
$env:GIGACHAT_CLIENT_SECRET="your_client_secret"
```

- If you are not using WSL2, follow the Windows instructions instead of POSIX `export` examples.

## Configuration Options

### Recommended: client credentials

```bash
hermes config set GIGACHAT_CLIENT_ID your_client_id
hermes config set GIGACHAT_CLIENT_SECRET your_client_secret
```

Why this is preferred:

- the access token refreshes automatically;
- no manual 30-minute token refresh loop;
- best for continuous use.

### Alternative: direct access token

```bash
hermes config set GIGACHAT_API_TOKEN your_access_token
```

Good for one-off sessions and testing. Keep in mind that access tokens expire.

### Alternative: base64 credentials

```bash
export GIGACHAT_API_TOKEN=base64(client_id:client_secret)
```

The plugin detects this format and performs the OAuth flow automatically.

### SSL verification

GigaChat uses self-signed certificates, so SSL verification is off by default.

```bash
export GIGACHAT_SSL_VERIFY=true
```

Enable this only if the CA is already in your trust store.

## What It Supports

- Hermes chat through GigaChat;
- model selection through `hermes model` and `/model`;
- live model catalog loading from the API;
- GigaChat-native `function calling`;
- Hermes MCP tools;
- CLI, TUI, gateway, and desktop scenarios through the shared backend.

## Supported Models

- `GigaChat`
- `GigaChat-2`
- `GigaChat-2-Max`
- `GigaChat-2-Pro`
- `GigaChat-Max`
- `GigaChat-Plus`
- `GigaChat-Pro`

## Technical Notes

### Tokens

- Access tokens live for about 30 minutes.
- The plugin fetches a fresh token for each request.
- On `401`, Hermes can rotate credentials through the credential pool.
- Tokens are not cached on purpose.

### Function calling

GigaChat uses the native `functions` format, not OpenAI `tools`. That is why this plugin is more than "just another provider": it is the compatibility layer that translates Hermes/OpenAI-shaped requests and responses to GigaChat and back.

Format mapping:

| Hermes | GigaChat |
|---|---|
| `tools[]` | `functions[]` |
| `tool_calls[]` | `function_call` |
| `tool.role="tool"` | `function.role="function"` |

### API endpoints

| Endpoint | Purpose |
|---|---|
| `https://ngw.devices.sberbank.ru:9443/api/v2/oauth` | OAuth token |
| `https://gigachat.devices.sberbank.ru/api/v1/models` | Model list |
| `https://gigachat.devices.sberbank.ru/api/v1/chat/completions` | Chat API |
| `https://gigachat.devices.sberbank.ru/api/v1/embeddings` | Embeddings |

### Environment variables

| Variable | Purpose | Default |
|---|---|---|
| `GIGACHAT_API_TOKEN` | Direct token or base64 credentials | - |
| `GIGACHAT_CLIENT_ID` | Client ID from the portal | - |
| `GIGACHAT_CLIENT_SECRET` | Client secret | - |
| `GIGACHAT_SSL_VERIFY` | Enable SSL verification | `false` |
| `GIGACHAT_BASE_URL` | Custom base URL | `https://gigachat.devices.sberbank.ru/api/v1` |

## Validation

Release-relevant Hermes scenarios were verified:

| Check | Result |
|---|---|
| `python -m pytest tests\\hermes_cli\\test_gigachat_model_flow.py -q -p no:timeout -p no:cacheprovider -o addopts=""` | `8/8 passed` |
| `hermes mcp test time` | `1/1 passed` |
| `python -m py_compile hermes_cli\\mcp_startup.py` | `1/1 passed` |
| `python -m pytest tests\\cron\\test_cron_profile.py -q -p no:timeout -p no:cacheprovider -o addopts=""` | `20/20 passed` |
| `python -m pytest tests\\cron\\test_cron_script.py -q -p no:timeout -p no:cacheprovider -o addopts=""` | `35 passed, 1 skipped` |
| provider-regression (all model providers, Windows) | `1359/1359 passed`, `0 failed` |

What this confirms:

- the GigaChat-specific flow stays green;
- `function calling` and model selection work against the live catalog;
- cron mode and script injection have separate coverage;
- the wider provider regression remains green on Windows.

## Troubleshooting

### 401 Unauthorized

- Check `Client ID` and `Client Secret`.
- Make sure the application is active in the portal.
- Verify quotas and permissions.

### Connection error

- For local testing, keep `GIGACHAT_SSL_VERIFY=false`.
- For production, add the CA to your trust store and enable SSL verification.

### Function calling does not work

- Make sure the selected model supports `functions`.
- Use Hermes `tools` examples, not OpenAI-only snippets.
- Check that the response ends with `finish_reason: "function_call"`.

## Links

- [GigaChat API Docs](https://developers.sber.ru/docs/ru/gigachat)
- [Hermes Agent Docs](https://hermes-agent.nousresearch.com/docs)
- [ai-forever/gigachat](https://github.com/ai-forever/gigachat) — Python SDK

## Open Questions

- The full set of MCP servers, except `time`, has not been validated here.
- TUI, desktop, and gateway are covered at the level of shared Hermes backend compatibility, but not by a separate GigaChat-specific regression.
- Any new provider-regression scenario beyond the already green set requires a separate run and result capture.

## License

MIT
