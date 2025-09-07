# Планировщик задач API

Управление автоматизированными задачами анализа PostgreSQL баз данных.

## Базовый путь: `/scheduler`

---

## 📋 Управление задачами

### POST `/scheduler/tasks` - Создать задачу

Создает новую запланированную задачу для автоматического выполнения.

**Запрос:**

```bash
curl -X POST http://localhost:8000/scheduler/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ежедневная проверка конфигурации",
    "task_type": "config_check",
    "connection_id": 1,
    "cron_schedule": "0 2 * * *",
    "description": "Проверка настроек PostgreSQL каждый день в 02:00",
    "task_params": {
      "check_performance": true,
      "check_security": true,
      "environment": "production"
    },
    "is_active": true
  }'
```

**Типы задач (`task_type`):**

- `config_check` - Проверка конфигурации PostgreSQL
- `log_analysis` - Анализ логов
- `query_analysis` - Анализ медленных запросов
- `table_analysis` - Анализ таблиц и индексов
- `custom_sql` - Выполнение пользовательского SQL

**Формат cron (`cron_schedule`):**

- `0 2 * * *` - каждый день в 02:00
- `0 */6 * * *` - каждые 6 часов
- `0 1 * * 1` - каждый понедельник в 01:00

**Ответ:**

```json
{
  "id": 1,
  "name": "Ежедневная проверка конфигурации",
  "task_type": "config_check",
  "connection_id": 1,
  "cron_schedule": "0 2 * * *",
  "description": "Проверка настроек PostgreSQL каждый день в 02:00",
  "task_params": {
    "check_performance": true,
    "check_security": true,
    "environment": "production"
  },
  "is_active": true,
  "last_run_at": null,
  "next_run_at": "2025-09-08T02:00:00",
  "created_at": "2025-09-07T15:30:00"
}
```

---

### GET `/scheduler/tasks` - Список задач

Получает список всех запланированных задач.

**Запрос:**

```bash
# Все задачи
curl http://localhost:8000/scheduler/tasks

# Только активные задачи
curl "http://localhost:8000/scheduler/tasks?is_active=true"

# Только неактивные задачи
curl "http://localhost:8000/scheduler/tasks?is_active=false"
```

**Параметры:**

- `is_active` (optional) - фильтр по статусу активности

**Ответ:**

```json
[
  {
    "id": 1,
    "name": "Ежедневная проверка конфигурации",
    "task_type": "config_check",
    "connection_id": 1,
    "cron_schedule": "0 2 * * *",
    "is_active": true,
    "last_run_at": null,
    "next_run_at": "2025-09-08T02:00:00",
    "created_at": "2025-09-07T15:30:00"
  }
]
```

---

### GET `/scheduler/tasks/{task_id}` - Получить задачу

Получает информацию о конкретной задаче по ID.

**Запрос:**

```bash
curl http://localhost:8000/scheduler/tasks/1
```

**Ответ:**

```json
{
  "id": 1,
  "name": "Ежедневная проверка конфигурации",
  "task_type": "config_check",
  "connection_id": 1,
  "cron_schedule": "0 2 * * *",
  "description": "Проверка настроек PostgreSQL каждый день в 02:00",
  "task_params": {
    "check_performance": true,
    "check_security": true
  },
  "is_active": true,
  "last_run_at": null,
  "next_run_at": "2025-09-08T02:00:00",
  "created_at": "2025-09-07T15:30:00"
}
```

---

### PUT `/scheduler/tasks/{task_id}` - Обновить задачу

Обновляет существующую задачу.

**Запрос:**

```bash
curl -X PUT http://localhost:8000/scheduler/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Обновленная проверка конфигурации",
    "cron_schedule": "0 3 * * *",
    "is_active": false
  }'
```

**Поля для обновления:**

- `name` - название задачи
- `cron_schedule` - расписание cron
- `description` - описание
- `task_params` - параметры выполнения
- `is_active` - статус активности

---

### DELETE `/scheduler/tasks/{task_id}` - Удалить задачу

Удаляет задачу из системы.

**Запрос:**

```bash
curl -X DELETE http://localhost:8000/scheduler/tasks/1
```

**Ответ:** 204 No Content

---

### POST `/scheduler/tasks/{task_id}/run` - Запустить задачу немедленно

Добавляет задачу в очередь для немедленного выполнения.

**Запрос:**

```bash
curl -X POST http://localhost:8000/scheduler/tasks/1/run
```

**Ответ:**

```json
{
  "message": "Задача добавлена в очередь выполнения",
  "task_id": 1
}
```

---

## 📊 Мониторинг выполнения

### GET `/scheduler/executions` - История выполнений

Получает историю выполнения задач.

**Запрос:**

```bash
# Все выполнения (последние 100)
curl http://localhost:8000/scheduler/executions

# Выполнения конкретной задачи
curl "http://localhost:8000/scheduler/executions?task_id=1"

# Ограничить количество
curl "http://localhost:8000/scheduler/executions?limit=50"
```

**Параметры:**

- `task_id` (optional) - ID задачи для фильтрации
- `limit` (optional) - максимальное количество записей (по умолчанию 100)

**Ответ:**

```json
[
  {
    "id": 1,
    "task_type": "config_check",
    "connection_id": 1,
    "scheduled_task_id": 1,
    "status": "completed",
    "started_at": "2025-09-07T15:30:00",
    "completed_at": "2025-09-07T15:30:15",
    "result": {
      "checks_performed": 25,
      "warnings": 2,
      "errors": 0
    },
    "error_message": null,
    "parameters": {
      "check_performance": true,
      "check_security": true
    }
  }
]
```

**Статусы выполнения:**

- `pending` - ожидает выполнения
- `running` - выполняется
- `completed` - завершено успешно
- `failed` - завершено с ошибкой
- `cancelled` - отменено

---

### GET `/scheduler/executions/{execution_id}` - Детали выполнения

Получает подробную информацию о конкретном выполнении.

**Запрос:**

```bash
curl http://localhost:8000/scheduler/executions/1
```

**Ответ:**

```json
{
  "id": 1,
  "task_type": "config_check",
  "connection_id": 1,
  "scheduled_task_id": 1,
  "status": "completed",
  "started_at": "2025-09-07T15:30:00",
  "completed_at": "2025-09-07T15:30:15",
  "result": {
    "checks_performed": 25,
    "warnings": 2,
    "errors": 0,
    "recommendations": [
      "Увеличить shared_buffers до 1GB",
      "Настроить checkpoint_timeout"
    ]
  },
  "error_message": null,
  "parameters": {
    "check_performance": true,
    "check_security": true
  }
}
```

---

## 📈 Статистика и мониторинг

### GET `/scheduler/stats` - Статистика планировщика

Получает общую статистику работы планировщика.

**Запрос:**

```bash
curl http://localhost:8000/scheduler/stats
```

**Ответ:**

```json
{
  "tasks": {
    "total_tasks": 12,
    "active_tasks": 10,
    "inactive_tasks": 2
  },
  "executions_24h": {
    "total_executions": 45,
    "completed": 42,
    "failed": 2,
    "running": 1
  },
  "timestamp": "2025-09-07T15:30:00"
}
```

---

### GET `/scheduler/queue/status` - Статус очереди

Показывает текущее состояние очереди задач.

**Запрос:**

```bash
curl http://localhost:8000/scheduler/queue/status
```

**Ответ:**

```json
{
  "queue_length": 3,
  "timestamp": "2025-09-07T15:30:00"
}
```

---

## 🔧 Расширенные функции

### POST `/scheduler/tasks/{task_id}/queue` - Добавить в очередь

Добавляет задачу в очередь для выполнения (альтернатива `/run`).

**Запрос:**

```bash
curl -X POST http://localhost:8000/scheduler/tasks/1/queue
```

---

## Примеры использования

### Настройка еженедельного анализа логов

```bash
curl -X POST http://localhost:8000/scheduler/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Еженедельный анализ логов",
    "task_type": "log_analysis",
    "connection_id": 1,
    "cron_schedule": "0 1 * * 1",
    "description": "Анализ логов каждый понедельник",
    "task_params": {
      "log_level": "WARNING",
      "time_range_hours": 168
    }
  }'
```

### Ежечасный анализ медленных запросов

```bash
curl -X POST http://localhost:8000/scheduler/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Анализ медленных запросов",
    "task_type": "query_analysis",
    "connection_id": 1,
    "cron_schedule": "0 * * * *",
    "description": "Поиск медленных запросов каждый час"
  }'
```

### Пользовательская SQL проверка

```bash
curl -X POST http://localhost:8000/scheduler/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Проверка активных подключений",
    "task_type": "custom_sql",
    "connection_id": 1,
    "cron_schedule": "*/15 * * * *",
    "task_params": {
      "custom_sql": "SELECT COUNT(*) as active_connections FROM pg_stat_activity WHERE state = '\''active'\'';",
      "query_timeout": 30
    }
  }'
```
