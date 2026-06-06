import json
import uuid

import hermes_cli.config as config_mod
import hermes_cli.main as main_mod


class _OAuthResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps({"access_token": "token"}).encode()


def test_gigachat_credential_test_sends_uuid_rquid(monkeypatch):
    captured = {}

    def fake_urlopen(request, timeout, context):
        captured["request"] = request
        captured["timeout"] = timeout
        captured["context"] = context
        return _OAuthResponse()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    success, error = main_mod._test_gigachat_oauth_credentials("client-id", "client-secret")

    assert success is True
    assert error == ""
    assert captured["request"].full_url == "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    assert captured["request"].data == b"scope=GIGACHAT_API_PERS"
    assert captured["request"].get_header("Authorization") == "Basic Y2xpZW50LWlkOmNsaWVudC1zZWNyZXQ="

    rquid = captured["request"].get_header("Rquid")
    assert rquid
    assert uuid.UUID(rquid).version == 4


def test_gigachat_runtime_prefers_client_credentials_over_stale_api_token(monkeypatch):
    import importlib

    import hermes_cli.auth as auth_mod
    from providers import get_provider_profile

    get_provider_profile("gigachat")
    gigachat_mod = importlib.import_module("plugins.model_providers.gigachat")

    monkeypatch.setattr(
        config_mod,
        "get_env_value",
        lambda key: {
            "GIGACHAT_CLIENT_ID": "client-id",
            "GIGACHAT_CLIENT_SECRET": "client-secret",
            "GIGACHAT_API_TOKEN": "stale-token",
        }.get(key),
    )
    monkeypatch.setenv("GIGACHAT_API_TOKEN", "stale-token")

    captured = {}

    def fake_get_token():
        captured["client_id"] = gigachat_mod.os.getenv("GIGACHAT_CLIENT_ID")
        captured["client_secret"] = gigachat_mod.os.getenv("GIGACHAT_CLIENT_SECRET")
        captured["api_token"] = gigachat_mod.os.getenv("GIGACHAT_API_TOKEN")
        return "access-token"

    monkeypatch.setattr(gigachat_mod, "_get_gigachat_token", fake_get_token)

    creds = auth_mod.resolve_gigachat_runtime_credentials()

    assert creds["api_key"] == "access-token"
    assert captured == {
        "client_id": "client-id",
        "client_secret": "client-secret",
        "api_token": None,
    }


def test_gigachat_provider_plugin_resolves_for_model_switch():
    from hermes_cli.providers import resolve_provider_full

    provider = resolve_provider_full("gigachat")

    assert provider is not None
    assert provider.id == "gigachat"
    assert provider.auth_type == "oauth_external"
    assert provider.base_url == "https://gigachat.devices.sberbank.ru/api/v1"


def test_gigachat_model_switch_accepts_provider_plugin(monkeypatch):
    import hermes_cli.model_switch as model_switch

    monkeypatch.setattr(
        "hermes_cli.runtime_provider.resolve_runtime_provider",
        lambda requested, target_model=None: {
            "api_key": "access-token",
            "base_url": "https://gigachat.devices.sberbank.ru/api/v1",
            "api_mode": "chat_completions",
        },
    )
    monkeypatch.setattr(
        "hermes_cli.models.validate_requested_model",
        lambda model, provider, **kwargs: {
            "accepted": True,
            "persist": True,
            "recognized": True,
            "message": "",
        },
    )

    result = model_switch.switch_model(
        "GigaChat-Max",
        current_provider="openrouter",
        current_model="openai/gpt-oss-120b",
        explicit_provider="gigachat",
    )

    assert result.success is True
    assert result.target_provider == "gigachat"
    assert result.new_model == "GigaChat-Max"
    assert result.base_url == "https://gigachat.devices.sberbank.ru/api/v1"
