# Плагин GigaChat для Hermes Agent

Плагин GigaChat для Hermes Agent с поддержкой чата, выбора модели и `function calling`.

Этот плагин нужен как отдельный адаптер, потому что GigaChat использует нативный формат `functions`, а Hermes должен общаться с ним через привычный OpenAI-совместимый контракт. Общий provider-путь недостаточно точен для этого сценария: здесь нужно отдельно переводить `tools` / `tool_calls` / `tool.role="tool"` в формат GigaChat и обратно.

## Кратко

- Работает в `hermes chat`, `hermes model`, `hermes mcp`, а также в общей цепочке Hermes gateway/TUI/Desktop.
- Подходит для Linux, macOS, Windows и WSL2.
- Для обычного чата и `function calling` официальный Python SDK не нужен.
- SDK можно поставить отдельно, если нужны расширенные возможности.

## Официальная документация GigaChat

- [Основная документация](https://developers.sber.ru/docs/ru/gigachat)
- [API Reference](https://developers.sber.ru/docs/ru/gigachat/reference)
- [Быстрый старт](https://developers.sber.ru/docs/ru/gigachat/guides/quickstart)
- [Авторизация и токены](https://developers.sber.ru/docs/ru/gigachat/guides/auth)
- [Function Calling](https://developers.sber.ru/docs/ru/gigachat/guides/functions)
- [Ограничения и квоты](https://developers.sber.ru/docs/ru/gigachat/guides/limits)

## Быстрый старт

### 1. Получите учётные данные

1. Зарегистрируйтесь в [GigaChat Developer Portal](https://developers.sber.ru/).
2. Создайте приложение.
3. Скопируйте `Client ID` и `Client Secret`.

### 2. Настройте через `hermes model`

Это рекомендуемый путь для большинства пользователей:

```bash
hermes model
```

Дальше:

1. Выберите `gigachat`.
2. Введите `Client ID`.
3. Введите `Client Secret`.
4. Дождитесь проверки учётных данных.
5. Выберите модель из списка.

### 3. Запустите чат

```bash
hermes chat
```

Если настройка завершена, Hermes будет использовать GigaChat из CLI.

## Где запускать

### Linux / macOS / WSL2

- Используйте обычный POSIX shell: `bash`, `zsh`, `fish` и т. д.
- В WSL2 используйте Linux-инструкции внутри WSL, а не Windows PowerShell.
- Если Hermes запущен в WSL2, настраивайте плагин внутри WSL2-профиля Hermes.

Пример через переменные окружения:

```bash
export GIGACHAT_CLIENT_ID="your_client_id"
export GIGACHAT_CLIENT_SECRET="your_client_secret"
```

### Windows native

- Используйте PowerShell.
- Для временного задания переменных окружения:

```powershell
$env:GIGACHAT_CLIENT_ID="your_client_id"
$env:GIGACHAT_CLIENT_SECRET="your_client_secret"
```

- Если вы не используете WSL2, следуйте Windows-инструкциям, а не POSIX-примерам с `export`.

## Варианты настройки

### Рекомендуемый вариант: client credentials

```bash
hermes config set GIGACHAT_CLIENT_ID your_client_id
hermes config set GIGACHAT_CLIENT_SECRET your_client_secret
```

Почему это лучше:

- access token обновляется автоматически;
- не нужен ручной 30-минутный цикл обновления;
- подходит для постоянной работы.

### Альтернатива: прямой access token

```bash
hermes config set GIGACHAT_API_TOKEN your_access_token
```

Подходит для разовых сессий и тестов. Учитывайте, что access token истекает.

### Альтернатива: base64 credentials

```bash
export GIGACHAT_API_TOKEN=base64(client_id:client_secret)
```

Плагин распознаёт такой формат и автоматически запускает OAuth flow.

### SSL-верификация

GigaChat использует self-signed сертификаты, поэтому SSL-верификация по умолчанию выключена.

```bash
export GIGACHAT_SSL_VERIFY=true
```

Включайте это только если CA уже добавлен в trust store.

## Что поддерживается

- Hermes-чат через GigaChat;
- выбор модели через `hermes model` и `/model`;
- загрузка живого списка моделей из API;
- `function calling` через native `functions` формат GigaChat;
- MCP-инструменты Hermes;
- работа в CLI, TUI, gateway и desktop-сценариях поверх общего backend.

## Поддерживаемые модели

- `GigaChat`
- `GigaChat-2`
- `GigaChat-2-Max`
- `GigaChat-2-Pro`
- `GigaChat-Max`
- `GigaChat-Plus`
- `GigaChat-Pro`

## Технические детали

### Токены

- Access token живёт около 30 минут.
- Плагин получает свежий токен на каждый запрос.
- При `401` Hermes может ротировать credentials через credential pool.
- Токены намеренно не кэшируются.

### Function calling

GigaChat использует нативный формат `functions`, а не OpenAI `tools`. Поэтому плагин нужен не только как "ещё один provider", а как слой совместимости, который переводит Hermes/OpenAI-формат в GigaChat-формат и обратно.

Сопоставление форматов:

| Hermes | GigaChat |
|---|---|
| `tools[]` | `functions[]` |
| `tool_calls[]` | `function_call` |
| `tool.role="tool"` | `function.role="function"` |

### API endpoints

| Endpoint | Назначение |
|---|---|
| `https://ngw.devices.sberbank.ru:9443/api/v2/oauth` | OAuth token |
| `https://gigachat.devices.sberbank.ru/api/v1/models` | Список моделей |
| `https://gigachat.devices.sberbank.ru/api/v1/chat/completions` | Chat API |
| `https://gigachat.devices.sberbank.ru/api/v1/embeddings` | Embeddings |

### Переменные окружения

| Переменная | Назначение | По умолчанию |
|---|---|---|
| `GIGACHAT_API_TOKEN` | Прямой токен или base64 credentials | - |
| `GIGACHAT_CLIENT_ID` | Client ID из кабинета | - |
| `GIGACHAT_CLIENT_SECRET` | Client Secret | - |
| `GIGACHAT_SSL_VERIFY` | Включить SSL-верификацию | `false` |
| `GIGACHAT_BASE_URL` | Кастомный base URL | `https://gigachat.devices.sberbank.ru/api/v1` |

## Проверка

Релизные сценарии Hermes проверены:

| Проверка | Результат |
|---|---|
| `python -m pytest tests\\hermes_cli\\test_gigachat_model_flow.py -q -p no:timeout -p no:cacheprovider -o addopts=""` | `8/8 passed` |
| `hermes mcp test time` | `1/1 passed` |
| `python -m py_compile hermes_cli\\mcp_startup.py` | `1/1 passed` |
| `python -m pytest tests\\cron\\test_cron_profile.py -q -p no:timeout -p no:cacheprovider -o addopts=""` | `20/20 passed` |
| `python -m pytest tests\\cron\\test_cron_script.py -q -p no:timeout -p no:cacheprovider -o addopts=""` | `35 passed, 1 skipped` |
| provider-regression (all model providers, Windows) | `1359/1359 passed`, `0 failed` |

Что это подтверждает:

- GigaChat-specific flow остаётся зелёным;
- `function calling` и выбор модели работают через живой каталог;
- cron-режим и script injection покрыты отдельными тестами;
- общий provider-regression на Windows остаётся зелёным.

## Troubleshooting

### 401 Unauthorized

- Проверьте `Client ID` и `Client Secret`.
- Убедитесь, что приложение активно в кабинете.
- Проверьте квоты и права доступа.

### Connection error

- Для локального теста оставьте `GIGACHAT_SSL_VERIFY=false`.
- Для production добавьте CA в trust store и включите SSL-верификацию.

### Function calling не работает

- Проверьте, что модель поддерживает `functions`.
- Используйте примеры Hermes `tools`, а не только OpenAI-only snippets.
- Убедитесь, что ответ завершился `finish_reason: "function_call"`.

## Ссылки

- [GigaChat API Docs](https://developers.sber.ru/docs/ru/gigachat)
- [Hermes Agent Docs](https://hermes-agent.nousresearch.com/docs)
- [ai-forever/gigachat](https://github.com/ai-forever/gigachat) — Python SDK

## Открытые вопросы

- Полный набор MCP-серверов, кроме `time`, здесь не проверялся.
- TUI, desktop и gateway покрыты только на уровне совместимости общего Hermes backend, без отдельного расширенного регресса именно для GigaChat.
- Новые provider-regression сценарии сверх уже зелёного набора требуют отдельного прогона и фиксации результата.

## Лицензия

MIT
