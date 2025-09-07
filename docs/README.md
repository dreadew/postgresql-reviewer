# PostgreSQL Reviewer API Documentation

Документация по REST API системы анализа и мониторинга PostgreSQL баз данных.

## Базовый URL

```
http://localhost:8000
```

## Структура API

### 📊 [Планировщик задач](./scheduler.md) - `/scheduler/*`

Управление автоматизированными задачами анализа

### 🔗 [Подключения](./connections.md) - `/connections/*`

Управление подключениями к базам данных

### 📝 [Логи](./logs.md) - `/logs/*`

Просмотр и анализ системных логов

### 📈 [Мониторинг](./monitoring.md) - `/monitoring/*`

Мониторинг состояния баз данных и системы

### 🔍 [Анализ и ревью](./review.md) - `/review/*`

Выполнение анализа запросов и конфигураций

### ⚙️ [Правила](./rules.md) - `/rules/*`

Управление правилами анализа

### 🛠 [Конфигурация](./config.md) - `/config/*`

Системные настройки

## Быстрый старт

1. **Создание подключения к БД:**

```bash
curl -X POST http://localhost:8000/connections/ \
  -H "Content-Type: application/json" \
  -d '{
    "vault_path": "database/postgresql/test",
    "environment": "development",
    "description": "Test database connection",
    "tags": ["test", "development"]
  }'
```

2. **Создание задачи анализа:**

```bash
curl -X POST http://localhost:8000/scheduler/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily Config Check",
    "task_type": "config_check",
    "connection_id": 1,
    "cron_schedule": "0 2 * * *",
    "description": "Ежедневная проверка конфигурации"
  }'
```

3. **Запуск задачи:**

```bash
curl -X POST http://localhost:8000/scheduler/tasks/1/run
```

## Общие принципы

- Все запросы/ответы используют JSON формат
- Аутентификация через заголовки (если настроена)
- Стандартные HTTP коды ответов
- Пагинация для списочных эндпоинтов
- Единообразные схемы ошибок

## Схемы ответов

### Успешный ответ

```json
{
  "data": { ... },
  "status": "success"
}
```

### Ошибка

```json
{
  "detail": "Описание ошибки",
  "status": "error"
}
```
