# Monitoring API Documentation

## Overview

API для мониторинга состояния системы PostgreSQL Reviewer. Позволяет отслеживать выполнение задач, состояние подключений и общую производительность системы.

**Base URL:** `/api/v1/monitoring`  
**Legacy URL:** `/api/monitoring` (redirect to v1)

---

## Endpoints

### 1. Get Task Executions

**GET** `/monitoring/tasks/executions`

Получить историю выполнения задач.

#### Query Parameters

- `task_id` (optional): integer - фильтр по ID задачи
- `limit` (optional): integer - лимит записей (default: 50)

#### Response

```json
[
  {
    "id": 1,
    "task_id": 1,
    "status": "completed",
    "started_at": "2024-01-01T02:00:00",
    "completed_at": "2024-01-01T02:05:00",
    "duration_seconds": 300,
    "result": {
      "analyzed_logs": 1000,
      "issues_found": 5
    },
    "error_message": null
  }
]
```

#### Status Codes

- `200` - Success
- `500` - Internal server error

---

### 2. Get Task Executions by Task ID

**GET** `/monitoring/tasks/{task_id}/executions`

Получить историю выполнения конкретной задачи.

#### Path Parameters

- `task_id`: integer - ID задачи

#### Query Parameters

- `limit` (optional): integer - лимит записей (default: 20)

#### Response

```json
[
  {
    "id": 1,
    "task_id": 1,
    "status": "completed",
    "started_at": "2024-01-01T02:00:00",
    "completed_at": "2024-01-01T02:05:00",
    "duration_seconds": 300,
    "result": {
      "analyzed_logs": 1000,
      "issues_found": 5
    },
    "error_message": null
  }
]
```

#### Status Codes

- `200` - Success
- `404` - Task not found
- `500` - Internal server error

---

### 3. Execute Task Manually

**POST** `/monitoring/tasks/{task_id}/execute`

Запустить задачу вручную (немедленное выполнение).

#### Path Parameters

- `task_id`: integer - ID задачи

#### Response

```json
{
  "message": "Task executed successfully",
  "execution_id": 123
}
```

#### Status Codes

- `200` - Task started successfully
- `404` - Task not found
- `500` - Error executing task

#### Notes

- Задача добавляется в очередь Redis для немедленного выполнения
- Создается новая запись в таблице task_executions
- Если задача уже выполняется, будет создано новое выполнение

---

### 4. Get All Connections Status

**GET** `/monitoring/connections/status`

Получить статус всех подключений к базам данных.

#### Response

```json
[
  {
    "connection_id": 1,
    "name": "Production DB",
    "host": "prod-db.example.com",
    "port": 5432,
    "database": "myapp",
    "is_healthy": true,
    "last_check": "2024-01-01T12:00:00",
    "response_time_ms": 50,
    "server_version": "15.4",
    "error_message": null
  },
  {
    "connection_id": 2,
    "name": "Test DB",
    "host": "test-db.example.com",
    "port": 5432,
    "database": "testdb",
    "is_healthy": false,
    "last_check": "2024-01-01T11:55:00",
    "response_time_ms": 5000,
    "server_version": null,
    "error_message": "Connection timeout"
  }
]
```

#### Status Codes

- `200` - Success
- `500` - Error getting connection statuses

---

### 5. Get Connection Status by ID

**GET** `/monitoring/connections/{connection_id}/status`

Получить статус конкретного подключения.

#### Path Parameters

- `connection_id`: integer - ID подключения

#### Response

```json
{
  "connection_id": 1,
  "name": "Production DB",
  "host": "prod-db.example.com",
  "port": 5432,
  "database": "myapp",
  "is_healthy": true,
  "last_check": "2024-01-01T12:00:00",
  "response_time_ms": 50,
  "server_version": "15.4",
  "error_message": null
}
```

#### Status Codes

- `200` - Success
- `404` - Connection not found
- `500` - Error getting connection status

#### Notes

- Если статус подключения не найден, автоматически выполняется проверка здоровья
- Данные кешируются для повышения производительности

---

### 6. Check Connection Health

**POST** `/monitoring/connections/{connection_id}/check`

Выполнить проверку состояния подключения к базе данных.

#### Path Parameters

- `connection_id`: integer - ID подключения

#### Response

```json
{
  "connection_id": 1,
  "is_healthy": true,
  "response_time_ms": 45,
  "server_version": "PostgreSQL 15.4"
}
```

**Error Response:**

```json
{
  "connection_id": 1,
  "is_healthy": false,
  "error_message": "FATAL: password authentication failed for user \"postgres\"",
  "response_time_ms": 1500
}
```

#### Status Codes

- `200` - Health check completed (regardless of result)
- `404` - Connection not found
- `500` - Error performing health check

#### Notes

- Выполняет реальное подключение к базе данных
- Получает учетные данные из Vault
- Измеряет время отклика
- Определяет версию PostgreSQL сервера
- Результат сохраняется в таблице connection_status

---

### 7. Get Running Tasks

**GET** `/monitoring/tasks/running`

Получить список текущих выполняющихся задач.

#### Response

```json
[
  {
    "id": 1,
    "name": "Daily Log Analysis",
    "task_type": "log_analysis",
    "connection_id": 1,
    "execution_id": 123,
    "execution_started_at": "2024-01-01T02:00:00",
    "estimated_duration": "5 minutes"
  }
]
```

#### Status Codes

- `200` - Success
- `500` - Error getting running tasks

---

## Health Check Responses

### Successful Connection

```json
{
  "connection_id": 1,
  "is_healthy": true,
  "response_time_ms": 45,
  "server_version": "15.4",
  "last_check": "2024-01-01T12:00:00"
}
```

### Failed Connection - Authentication Error

```json
{
  "connection_id": 1,
  "is_healthy": false,
  "error_message": "FATAL: password authentication failed for user \"postgres\"",
  "response_time_ms": 1200,
  "last_check": "2024-01-01T12:00:00"
}
```

### Failed Connection - Network Error

```json
{
  "connection_id": 1,
  "is_healthy": false,
  "error_message": "could not connect to server: Connection refused",
  "response_time_ms": 5000,
  "last_check": "2024-01-01T12:00:00"
}
```

---

## Examples

### Monitor Task Execution

```bash
# Get all recent task executions
curl "http://localhost:8000/monitoring/tasks/executions?limit=10"

# Get executions for specific task
curl "http://localhost:8000/monitoring/tasks/1/executions"

# Execute task manually
curl -X POST "http://localhost:8000/monitoring/tasks/1/execute"
```

### Monitor Database Connections

```bash
# Check all connection statuses
curl "http://localhost:8000/monitoring/connections/status"

# Check specific connection
curl "http://localhost:8000/monitoring/connections/1/status"

# Force health check
curl -X POST "http://localhost:8000/monitoring/connections/1/check"
```

### Monitor Running Tasks

```bash
# Get currently running tasks
curl "http://localhost:8000/monitoring/tasks/running"
```

---

## Integration with Alerting

### Connection Health Monitoring

```bash
#!/bin/bash
# Health check script for monitoring systems

RESPONSE=$(curl -s "http://localhost:8000/monitoring/connections/status")
UNHEALTHY_COUNT=$(echo $RESPONSE | jq '[.[] | select(.is_healthy == false)] | length')

if [ "$UNHEALTHY_COUNT" -gt 0 ]; then
    echo "ALERT: $UNHEALTHY_COUNT unhealthy database connections detected"
    exit 1
fi

echo "OK: All database connections are healthy"
exit 0
```

### Task Execution Monitoring

```bash
#!/bin/bash
# Monitor for failed tasks in the last hour

FAILED_TASKS=$(curl -s "http://localhost:8000/monitoring/tasks/executions?limit=100" | \
    jq '[.[] | select(.status == "failed" and (.started_at | fromdateiso8601) > (now - 3600))] | length')

if [ "$FAILED_TASKS" -gt 0 ]; then
    echo "WARNING: $FAILED_TASKS failed tasks in the last hour"
    exit 1
fi

echo "OK: No failed tasks in the last hour"
exit 0
```
