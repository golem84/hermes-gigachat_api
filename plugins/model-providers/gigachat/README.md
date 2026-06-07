# GigaChat Provider Plugin for Hermes Agent

Интеграция GigaChat API в Hermes Agent с поддержкой function calling.

## Официальная документация

- **Основная документация**: https://developers.sber.ru/docs/ru/gigachat
- **API Reference**: https://developers.sber.ru/docs/ru/gigachat/reference
- **Быстрый старт**: https://developers.sber.ru/docs/ru/gigachat/guides/quickstart
- **Авторизация и токены**: https://developers.sber.ru/docs/ru/gigachat/guides/auth
- **Function Calling**: https://developers.sber.ru/docs/ru/gigachat/guides/functions
- **Ограничения и квоты**: https://developers.sber.ru/docs/ru/gigachat/guides/limits

## Установка и настройка

### 0. Установка зависимости (опционально)

Для расширенных функций (embeddings, vision, файлы) установите официальный Python SDK:

```bash
uv pip install gigachat==0.2.2a1
```

**Примечание:** Базовый чат и function calling работают без этой зависимости — плагин использует прямой HTTP API.

### 1. Получение учётных данных

1. Зарегистрируйтесь на [GigaChat Developer Portal](https://developers.sber.ru/)
2. Создайте приложение в личном кабинете
3. Получите `Client ID` и `Client Secret` (статические ключи, не меняются)

### 2. Настройка через `hermes model` (рекомендуется)

Запустите интерактивный мастер настройки:

```bash
hermes model
```

1. В списке провайдеров выберите `gigachat`
2. Введите `Client ID` (или нажмите Enter для использования текущего значения)
3. Введите `Client Secret` (или нажмите Enter для использования текущего значения)
4. Плагин проверит credentials и загрузит список доступных моделей
5. Выберите модель из списка (текущая модель отмечается маркером `←`)
6. Настройка завершена

**Преимущества:**
- ✅ Интерактивный ввод с маской для секрета
- ✅ Автоматическая проверка credentials
- ✅ Загрузка актуального списка моделей из API
- ✅ Сохранение в `~/.hermes/.env` и `~/.hermes/config.yaml`

### 3. Ручная настройка (альтернатива)

**Режим 1: Client credentials (автономная работа, рекомендуется)**

```bash
# Через Hermes CLI
hermes config set GIGACHAT_CLIENT_ID ваш_client_id
hermes config set GIGACHAT_CLIENT_SECRET ваш_client_secret

# Или через переменные окружения
export GIGACHAT_CLIENT_ID=ваш_client_id
export GIGACHAT_CLIENT_SECRET=ваш_client_secret
```

- ✅ Автономно: плагин автоматически получает новый access token при каждом запросе
- ✅ Client ID + Client Secret **не меняются** — выдаются один раз при создании приложения
- 💡 Подходит для постоянной работы, не требует ручного обновления токена

**Режим 2: Прямой API токен (опционально, для разовых сессий)**

```bash
# Через Hermes CLI
hermes config set GIGACHAT_API_TOKEN ваш_access_token

# Или через переменные окружения
export GIGACHAT_API_TOKEN=ваш_access_token
```

- ✅ Просто: скопируйте токен из кабинета разработчика
- ⚠️ Access token действует **30 минут** — после истечения нужно получить новый вручную
- 💡 Подходит для разовых сессий, тестирования

**Режим 3: Base64-encoded credentials (альтернатива)**

```bash
# Закодировать credentials: echo -n "client_id:client_secret" | base64
export GIGACHAT_API_TOKEN=base64(client_id:client_secret)
```

- Эквивалентно режиму 1, но в одной переменной
- Плагин автоматически распознаёт формат и запускает OAuth flow

### 4. SSL-верификация

GigaChat использует самоподписанные сертификаты. По умолчанию SSL-верификация отключена.

```bash
# По умолчанию (SSL отключен)
# Работает сразу после установки

# Для production (требуется добавить CA в trust store)
export GIGACHAT_SSL_VERIFY=true
```

## Механизм ротации токенов

### Срок действия токена

**Access token действует 30 минут** (согласно официальной документации).

### Автоматическая ротация

Плагин автоматически получает новый токен при каждом запросе к API:

1. **При инициализации клиента**: `_get_gigachat_token()` вызывается для получения свежего токена
2. **При 401 ошибке**: Hermes credential pool автоматически ротирует токен
3. **Кэширование**: Токен не кэшируется намеренно — каждый запрос получает свежий токен

### Почему не кэшируем?

- Простота реализации
- Избегаем edge cases с истёкшими токенами
- OAuth-запрос быстрый (~200-500ms)
- GigaChat не имеет rate limits на OAuth endpoint

### Схема работы

```
Hermes Agent запрос
    ↓
_get_gigachat_token()
    ↓
POST https://ngw.devices.sberbank.ru:9443/api/v2/oauth
    ↓
Получение access_token (30 мин)
    ↓
Использование в API запросе
    ↓
GigaChat API ответ
```

## Поддерживаемые модели

- `GigaChat` — базовая модель
- `GigaChat-2` — второе поколение
- `GigaChat-2-Max` — максимальная производительность
- `GigaChat-2-Pro` — продвинутая версия
- `GigaChat-Max` — флагманская модель
- `GigaChat-Plus` — сбалансированная
- `GigaChat-Pro` — профессиональная

## Function Calling

GigaChat использует **нативный `functions` формат**, а не OpenAI `tools`.

### Преобразование форматов

Плагин автоматически преобразует:

| Hermes (OpenAI) | GigaChat (Native) |
|-----------------|-------------------|
| `tools[]` | `functions[]` |
| `tool_calls[]` | `function_call` |
| `tool.role: "tool"` | `function.role: "function"` |

### Пример function call

```json
{
  "model": "GigaChat-Max",
  "messages": [{"role": "user", "content": "Погода в Москве"}],
  "functions": [{
    "name": "get_weather",
    "description": "Получить погоду",
    "parameters": {
      "type": "object",
      "properties": {
        "location": {"type": "string"}
      },
      "required": ["location"]
    }
  }]
}
```

## Готовность к релизу

Плагин готов к релизу для проверенных сценариев Hermes Agent:

- аутентификация через `Client ID` / `Client Secret`
- выбор модели из `hermes model` и `/model`
- загрузка актуального списка моделей из API, без захардкоженного каталога
- `function calling` для обычных инструментов Hermes
- работа с MCP-инструментами через Hermes (`mcp_time_get_current_time`, `mcp_time_convert_time`)

### Выполненные проверки

| Проверка | Результат |
|----------|-----------|
| `python -m pytest tests\\hermes_cli\\test_gigachat_model_flow.py -q -p no:timeout -p no:cacheprovider -o addopts=""` | `8/8 passed` |
| `hermes mcp test time` | `1/1 passed` (`✓ Connected`, `2` инструмента обнаружены) |
| `python -m py_compile hermes_cli\\mcp_startup.py` | `1/1 passed` |

### Что ещё не покрыто полностью

- все MCP-серверы, кроме `time`
- TUI, desktop, gateway и cron-режимы
- медленные или падающие MCP-серверы
- полный регресс по всем провайдерам моделей, не только GigaChat

## API Endpoints

| Endpoint | Назначение | SSL |
|----------|------------|-----|
| `https://ngw.devices.sberbank.ru:9443/api/v2/oauth` | OAuth токен | Self-signed |
| `https://gigachat.devices.sberbank.ru/api/v1/models` | Список моделей | Self-signed |
| `https://gigachat.devices.sberbank.ru/api/v1/chat/completions` | Chat API | Self-signed |
| `https://gigachat.devices.sberbank.ru/api/v1/embeddings` | Embeddings | Self-signed |

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `GIGACHAT_API_TOKEN` | Pre-computed токен (base64) | - |
| `GIGACHAT_CLIENT_ID` | Client ID из кабинета | - |
| `GIGACHAT_CLIENT_SECRET` | Client Secret | - |
| `GIGACHAT_SSL_VERIFY` | Включить SSL-верификацию | `false` |
| `GIGACHAT_BASE_URL` | Кастомный base URL | `https://gigachat.devices.sberbank.ru/api/v1` |

## Troubleshooting

### 401 Unauthorized

- Проверьте правильность `CLIENT_ID` и `CLIENT_SECRET`
- Убедитесь, что приложение активно в личном кабинете
- Проверьте квоты и лимиты

### Connection error

- SSL-сертификаты: установите `GIGACHAT_SSL_VERIFY=false`
- Проверьте доступность endpoints из вашей сети
- Возможно нужен прокси

### Function calling не работает

- Убедитесь, что модель поддерживает functions (Max, Pro)
- Используйте правильный формат `functions` (не `tools`)
- Проверьте `finish_reason: "function_call"` в ответе

## Ссылки

- [GigaChat API Docs](https://developers.sber.ru/docs/ru/gigachat)
- [ai-forever/gigachat](https://github.com/ai-forever/gigachat) — Python SDK
- [Hermes Agent Docs](https://hermes-agent.nousresearch.com/docs)

## Лицензия

MIT
