# Tasks API Documentation

## Overview

API для управления задачами планировщика PostgreSQL Reviewer. Позволяет создавать, управлять и запускать задачи анализа баз данных.

**Base URL:** `/tasks`

---

## Endpoints

### 1. Create Task

**POST** `/tasks/`

Создать новую задачу планировщика.

#### Request Body

```json
{
  "name": "Daily Log Analysis",
  "connection_id": 1,
  "schedule": "0 2 * * *",
  "task_type": "log_analysis",
  "parameters": {
    "analysis_target": "logs",
    "detailed_analysis": true,
    "retention_days": 30
  },
  "is_active": true
}
```

#### Response

```json
{
  "id": 1,
  "name": "Daily Log Analysis",
  "connection_id": 1,
  "schedule": "0 2 * * *",
  "task_type": "log_analysis",
  "parameters": {
    "analysis_target": "logs",
    "detailed_analysis": true,
    "retention_days": 30
  },
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00",
  "last_run": null,
  "next_run": "2024-01-02T02:00:00"
}
```

#### Status Codes

- `200` - Task created successfully
- `400` - Invalid request data
- `500` - Internal server error

#### Notes

- Задача автоматически добавляется в очередь планировщика
- `schedule` использует cron формат
- Задача становится активной сразу после создания (если `is_active: true`)

---

### 2. Get All Tasks

**GET** `/tasks/`

Получить список всех задач.

#### Response

```json
[
  {
    "id": 1,
    "name": "Daily Log Analysis",
    "connection_id": 1,
    "schedule": "0 2 * * *",
    "task_type": "log_analysis",
    "parameters": {
      "analysis_target": "logs"
    },
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
    "last_run": "2024-01-01T02:00:00",
    "next_run": "2024-01-02T02:00:00"
  },
  {
    "id": 2,
    "name": "Config Check",
    "connection_id": 1,
    "schedule": "0 6 * * 1",
    "task_type": "config_check",
    "parameters": {},
    "is_active": false,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
    "last_run": null,
    "next_run": null
  }
]
```

#### Status Codes

- `200` - Success
- `500` - Internal server error

---

### 3. Get Task by ID

**GET** `/tasks/{task_id}`

Получить задачу по ID.

#### Path Parameters

- `task_id`: integer - ID задачи

#### Response

```json
{
  "id": 1,
  "name": "Daily Log Analysis",
  "connection_id": 1,
  "schedule": "0 2 * * *",
  "task_type": "log_analysis",
  "parameters": {
    "analysis_target": "logs",
    "detailed_analysis": true
  },
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00",
  "last_run": "2024-01-01T02:00:00",
  "next_run": "2024-01-02T02:00:00"
}
```

#### Status Codes

- `200` - Success
- `404` - Task not found
- `500` - Internal server error

---

### 4. Update Task

**PUT** `/tasks/{task_id}`

Обновить задачу.

#### Path Parameters

- `task_id`: integer - ID задачи

#### Request Body

```json
{
  "name": "Updated Daily Log Analysis",
  "schedule": "0 3 * * *",
  "parameters": {
    "analysis_target": "logs",
    "detailed_analysis": false,
    "retention_days": 60
  },
  "is_active": false
}
```

#### Response

```json
{
  "id": 1,
  "name": "Updated Daily Log Analysis",
  "connection_id": 1,
  "schedule": "0 3 * * *",
  "task_type": "log_analysis",
  "parameters": {
    "analysis_target": "logs",
    "detailed_analysis": false,
    "retention_days": 60
  },
  "is_active": false,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T12:00:00",
  "last_run": "2024-01-01T02:00:00",
  "next_run": null
}
```

#### Status Codes

- `200` - Task updated successfully
- `404` - Task not found
- `500` - Internal server error

#### Notes

- Все поля опциональны - можно обновлять только нужные поля
- При изменении `schedule` пересчитывается `next_run`
- При установке `is_active: false` задача исключается из планировщика

---

### 5. Delete Task

**DELETE** `/tasks/{task_id}`

Удалить задачу.

#### Path Parameters

- `task_id`: integer - ID задачи

#### Response

```json
{
  "message": "Задача удалена"
}
```

#### Status Codes

- `200` - Task deleted successfully
- `404` - Task not found
- `500` - Internal server error

#### Notes

- При удалении задачи также удаляется история её выполнений
- Текущие выполнения задачи завершаются

---

### 6. Run Task Now

**POST** `/tasks/{task_id}/run`

Запустить задачу немедленно.

#### Path Parameters

- `task_id`: integer - ID задачи

#### Response

```json
{
  "message": "Задача добавлена в очередь"
}
```

#### Status Codes

- `200` - Task queued successfully
- `404` - Task not found
- `500` - Error queuing task

#### Notes

- Задача добавляется в очередь Redis для немедленного выполнения
- Не влияет на обычное расписание задачи
- Обновляется время последнего запуска (`last_run`)

---

## Task Types

### Supported Task Types

#### 1. log_analysis

Анализ логов PostgreSQL сервера

```json
{
  "task_type": "log_analysis",
  "parameters": {
    "analysis_target": "logs",
    "detailed_analysis": true,
    "log_level": "ERROR",
    "retention_days": 30
  }
}
```

#### 2. config_check

Проверка конфигурации PostgreSQL

```json
{
  "task_type": "config_check",
  "parameters": {
    "analysis_target": "config",
    "check_recommendations": true,
    "environment": "production"
  }
}
```

#### 3. query_analysis

Анализ медленных запросов

```json
{
  "task_type": "query_analysis",
  "parameters": {
    "analysis_target": "performance",
    "min_duration_ms": 1000,
    "limit": 100
  }
}
```

#### 4. custom_sql

Выполнение кастомного SQL

```json
{
  "task_type": "custom_sql",
  "parameters": {
    "custom_sql": "SELECT * FROM pg_stat_statements WHERE total_exec_time > 1000",
    "analysis_target": "performance",
    "timeout_seconds": 300
  }
}
```

#### 5. table_analysis

Анализ конкретных таблиц

```json
{
  "task_type": "table_analysis",
  "parameters": {
    "target_tables": ["users", "orders", "products"],
    "analysis_target": "tables",
    "include_indexes": true
  }
}
```

---

## Schedule Format

### Cron Schedule Examples

- `"0 2 * * *"` - Каждый день в 2:00
- `"0 */4 * * *"` - Каждые 4 часа
- `"0 6 * * 1"` - Каждый понедельник в 6:00
- `"*/30 * * * *"` - Каждые 30 минут
- `"0 0 1 * *"` - Первого числа каждого месяца
- `"0 9-17 * * 1-5"` - Каждый час с 9 до 17 в рабочие дни

### Schedule Validation

API автоматически валидирует cron выражения и вычисляет следующее время запуска.

---

## Examples

### Create Log Analysis Task

```bash
curl -X POST "http://localhost:8000/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hourly Error Log Check",
    "connection_id": 1,
    "schedule": "0 * * * *",
    "task_type": "log_analysis",
    "parameters": {
      "analysis_target": "logs",
      "log_level": "ERROR",
      "detailed_analysis": true
    },
    "is_active": true
  }'
```

### Create Custom SQL Task

```bash
curl -X POST "http://localhost:8000/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Security Monitoring",
    "connection_id": 1,
    "schedule": "*/15 * * * *",
    "task_type": "custom_sql",
    "parameters": {
      "custom_sql": "SELECT usename, count(*) FROM pg_stat_activity WHERE state = '\''active'\'' GROUP BY usename HAVING count(*) > 10",
      "analysis_target": "security"
    },
    "is_active": true
  }'
```

### Update Task Schedule

```bash
curl -X PUT "http://localhost:8000/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{
    "schedule": "0 3 * * *",
    "is_active": true
  }'
```

### Run Task Immediately

```bash
curl -X POST "http://localhost:8000/tasks/1/run"
```

### Get Task Status

```bash
curl "http://localhost:8000/tasks/1"
```

### Disable Task

```bash
curl -X PUT "http://localhost:8000/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{
    "is_active": false
  }'
```

---

## Task Parameters Reference

### Common Parameters

- `analysis_target`: string - Цель анализа (logs/config/performance/security/tables)
- `detailed_analysis`: boolean - Детальный анализ
- `timeout_seconds`: integer - Таймаут выполнения (default: 300)
- `retention_days`: integer - Период хранения результатов

### Log Analysis Parameters

- `log_level`: string - Уровень логов (ERROR/WARNING/INFO/DEBUG)
- `pattern_filter`: string - Фильтр по паттерну
- `time_range_hours`: integer - Диапазон времени для анализа

### Config Check Parameters

- `environment`: string - Среда (development/staging/production)
- `check_recommendations`: boolean - Проверка рекомендаций
- `include_extensions`: boolean - Включить анализ расширений

### Query Analysis Parameters

- `min_duration_ms`: integer - Минимальная длительность запроса
- `limit`: integer - Лимит запросов для анализа
- `include_plan`: boolean - Включить план выполнения

### Custom SQL Parameters

- `custom_sql`: string - SQL запрос для выполнения
- `result_format`: string - Формат результата (json/csv)
- `max_rows`: integer - Максимальное количество строк результата

### Table Analysis Parameters

- `target_tables`: array - Список таблиц для анализа
- `include_indexes`: boolean - Включить анализ индексов
- `include_statistics`: boolean - Включить статистику таблиц
