# Scheduler API Documentation

## Overview

API для управления планировщиком задач PostgreSQL Reviewer. Позволяет создавать, управлять и мониторить автоматические задачи анализа.

**Base URL:** `/api/v1/scheduler`  
**Legacy URL:** `/api/scheduler` (redirect to v1)

---

## Endpoints

### 1. Create Scheduled Task

**POST** `/scheduler/tasks`

Создать новую запланированную задачу.

#### Request Body

```json
{
  "name": "string",
  "task_type": "log_analysis|config_check|query_analysis|custom_sql|table_analysis",
  "connection_id": 1,
  "cron_schedule": "0 2 * * *",
  "description": "string (optional)",
  "task_params": {
    "analysis_target": "logs|config|performance|security|tables|queries",
    "custom_sql": "string (optional)",
    "target_tables": ["table1", "table2"] (optional),
    "query_timeout": 300,
    "output_format": "json",
    "detailed_analysis": true
  },
  "is_active": true
}
```

#### Response

```json
{
  "id": 1,
  "name": "string",
  "task_type": "log_analysis",
  "connection_id": 1,
  "cron_schedule": "0 2 * * *",
  "description": "string",
  "task_params": {},
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

#### Status Codes

- `201` - Task created successfully
- `400` - Invalid request data
- `500` - Internal server error

---

### 2. Get Scheduled Tasks

**GET** `/scheduler/tasks`

Получить список всех запланированных задач.

#### Query Parameters

- `is_active` (optional): `true|false` - фильтр по активности

#### Response

```json
[
  {
    "id": 1,
    "name": "string",
    "task_type": "log_analysis",
    "connection_id": 1,
    "cron_schedule": "0 2 * * *",
    "description": "string",
    "task_params": {},
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

---

### 3. Get Scheduled Task by ID

**GET** `/scheduler/tasks/{task_id}`

Получить запланированную задачу по ID.

#### Path Parameters

- `task_id`: integer - ID задачи

#### Response

```json
{
  "id": 1,
  "name": "string",
  "task_type": "log_analysis",
  "connection_id": 1,
  "cron_schedule": "0 2 * * *",
  "description": "string",
  "task_params": {},
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

#### Status Codes

- `200` - Success
- `404` - Task not found
- `500` - Internal server error

---

### 4. Update Scheduled Task

**PUT** `/scheduler/tasks/{task_id}`

Обновить запланированную задачу.

#### Path Parameters

- `task_id`: integer - ID задачи

#### Request Body

```json
{
  "name": "string (optional)",
  "cron_schedule": "string (optional)",
  "description": "string (optional)",
  "task_params": {} (optional),
  "is_active": true (optional)
}
```

#### Response

```json
{
  "id": 1,
  "name": "string",
  "task_type": "log_analysis",
  "connection_id": 1,
  "cron_schedule": "0 2 * * *",
  "description": "string",
  "task_params": {},
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

#### Status Codes

- `200` - Task updated successfully
- `400` - Invalid request data
- `404` - Task not found
- `500` - Internal server error

---

### 5. Delete Scheduled Task

**DELETE** `/scheduler/tasks/{task_id}`

Удалить запланированную задачу.

#### Path Parameters

- `task_id`: integer - ID задачи

#### Status Codes

- `204` - Task deleted successfully
- `404` - Task not found
- `500` - Internal server error

---

### 6. Run Task Now

**POST** `/scheduler/tasks/{task_id}/run`

Запустить задачу немедленно.

#### Path Parameters

- `task_id`: integer - ID задачи

#### Response

```json
{
  "message": "Задача запущена",
  "execution_id": 123
}
```

#### Status Codes

- `200` - Task started successfully
- `400` - Task is inactive
- `404` - Task not found
- `500` - Internal server error

---

### 7. Get Task Executions

**GET** `/scheduler/executions`

Получить историю выполнения задач.

#### Query Parameters

- `connection_id` (optional): integer - фильтр по подключению
- `task_type` (optional): string - фильтр по типу задачи
- `status_filter` (optional): string - фильтр по статусу
- `limit` (optional): integer - лимит записей (default: 100)

#### Response

```json
[
  {
    "id": 1,
    "scheduled_task_id": 1,
    "connection_id": 1,
    "task_type": "log_analysis",
    "status": "completed",
    "started_at": "2024-01-01T00:00:00",
    "completed_at": "2024-01-01T00:05:00",
    "result": {},
    "error_message": null
  }
]
```

---

### 8. Get Task Execution by ID

**GET** `/scheduler/executions/{execution_id}`

Получить информацию о конкретном выполнении задачи.

#### Path Parameters

- `execution_id`: integer - ID выполнения

#### Response

```json
{
  "id": 1,
  "scheduled_task_id": 1,
  "connection_id": 1,
  "task_type": "log_analysis",
  "status": "completed",
  "started_at": "2024-01-01T00:00:00",
  "completed_at": "2024-01-01T00:05:00",
  "result": {},
  "error_message": null
}
```

#### Status Codes

- `200` - Success
- `404` - Execution not found
- `500` - Internal server error

---

### 9. Get Queue Status

**GET** `/scheduler/queue/status`

Получить статус очереди задач.

#### Response

```json
{
  "queue_length": 5,
  "timestamp": "2024-01-01T00:00:00"
}
```

#### Status Codes

- `200` - Success
- `503` - Redis unavailable
- `500` - Internal server error

---

### 10. Get Scheduler Statistics

**GET** `/scheduler/stats`

Получить статистику планировщика.

#### Response

```json
{
  "tasks": {
    "total_tasks": 10,
    "active_tasks": 8,
    "inactive_tasks": 2
  },
  "executions_24h": {
    "total_executions": 24,
    "completed": 20,
    "failed": 2,
    "running": 2
  },
  "timestamp": "2024-01-01T00:00:00"
}
```

---

### 11. Queue Task for Execution

**POST** `/scheduler/tasks/{task_id}/queue`

Поставить задачу в очередь для немедленного выполнения.

#### Path Parameters

- `task_id`: integer - ID задачи

#### Response

```json
{
  "message": "Задача 1 добавлена в очередь",
  "task_id": 1
}
```

#### Status Codes

- `200` - Task queued successfully
- `404` - Task not found
- `500` - Internal server error

---

## Examples

### Create a Custom SQL Task

```bash
curl -X POST "http://localhost:8000/api/v1/scheduler/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily Security Check",
    "task_type": "custom_sql",
    "connection_id": 1,
    "cron_schedule": "0 2 * * *",
    "task_params": {
      "custom_sql": "SELECT usename, count(*) FROM pg_stat_activity WHERE state = '\''active'\'' GROUP BY usename;",
      "analysis_target": "security"
    }
  }'
```

### Get All Active Tasks

```bash
curl "http://localhost:8000/api/v1/scheduler/tasks?is_active=true"
```

### Run Task Immediately

```bash
curl -X POST "http://localhost:8000/api/v1/scheduler/tasks/1/run"
```

---

## Additional Endpoints

### 12. Get Scheduler Status

**GET** `/api/v1/scheduler/status`

Получить общий статус планировщика и базовую статистику.

#### Response

```json
{
  "scheduler_running": false,
  "redis_status": "connected",
  "stats": {
    "total_tasks": 16,
    "active_tasks": 16,
    "executions_24h": 6,
    "failed_executions_24h": 2
  },
  "timestamp": "2025-09-08T08:25:23.421150"
}
```

#### Status Codes

- `200` - Success
- `500` - Internal server error

---

### 13. Get Detailed Statistics

**GET** `/api/v1/scheduler/stats`

Получить детальную статистику работы планировщика.

#### Response

```json
{
  "task_types": [
    {
      "task_type": "log_analysis",
      "total_count": 4,
      "active_count": 4
    }
  ],
  "daily_stats": [
    {
      "date": "2025-09-07",
      "total_executions": 6,
      "successful": 0,
      "failed": 2,
      "avg_duration_seconds": 5.043716
    }
  ],
  "top_tasks": [
    {
      "name": "Log Analysis Task v2",
      "task_type": "log_analysis",
      "execution_count": 4,
      "avg_duration_seconds": 10.085566
    }
  ],
  "timestamp": "2025-09-08T08:25:12.435283"
}
```

#### Status Codes

- `200` - Success
- `500` - Internal server error

---

### 14. Get Queue Status

**GET** `/api/v1/scheduler/queue`

Получить статус очереди задач и текущие выполнения.

#### Response

```json
{
  "queue_length": 0,
  "pending_tasks": [],
  "running_tasks": [
    {
      "execution_id": 5,
      "task_name": "Custom Health Check - Analytics DB",
      "task_type": "custom_sql",
      "started_at": "2025-09-07T18:06:28.820479+00:00",
      "status": "running"
    }
  ],
  "redis_connected": true,
  "timestamp": "2025-09-08T08:25:17.970332"
}
```

#### Status Codes

- `200` - Success
- `500` - Internal server error

---

### 15. Start Scheduler

**POST** `/api/v1/scheduler/start`

Запустить планировщик задач.

#### Response

```json
{
  "message": "Планировщик запущен"
}
```

#### Status Codes

- `200` - Success
- `500` - Internal server error

---

### 16. Stop Scheduler

**POST** `/api/v1/scheduler/stop`

Остановить планировщик задач.

#### Response

```json
{
  "message": "Планировщик остановлен"
}
```

#### Status Codes

- `200` - Success
- `500` - Internal server error

---

## Examples

### Get Scheduler Status

```bash
curl "http://localhost:8000/api/v1/scheduler/status"
```

### Get Detailed Statistics

```bash
curl "http://localhost:8000/api/v1/scheduler/stats"
```

### Get Queue Status

```bash
curl "http://localhost:8000/api/v1/scheduler/queue"
```

### Start/Stop Scheduler

```bash
# Start scheduler
curl -X POST "http://localhost:8000/api/v1/scheduler/start"

# Stop scheduler
curl -X POST "http://localhost:8000/api/v1/scheduler/stop"
```
