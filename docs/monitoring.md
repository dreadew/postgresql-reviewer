# Мониторинг API

Мониторинг состояния баз данных, выполнения задач и общего состояния системы.

## Базовый путь: `/monitoring`

---

## 📊 Мониторинг выполнения задач

### GET `/monitoring/tasks/executions` - Все выполнения задач

Получает список всех выполнений задач с возможностью фильтрации.

**Запрос:**

```bash
# Все выполнения
curl http://localhost:8000/monitoring/tasks/executions

# Фильтрация по статусу
curl "http://localhost:8000/monitoring/tasks/executions?status=failed"

# Ограничение количества
curl "http://localhost:8000/monitoring/tasks/executions?limit=50"

# Фильтрация по времени (последние 24 часа)
curl "http://localhost:8000/monitoring/tasks/executions?since=24h"
```

**Параметры:**

- `status` - фильтр по статусу (pending, running, completed, failed, cancelled)
- `limit` - максимальное количество записей
- `since` - временной диапазон (24h, 7d, 30d)

**Ответ:**

```json
[
  {
    "id": 1,
    "task_id": 5,
    "task_name": "Daily Config Check",
    "task_type": "config_check",
    "connection_id": 1,
    "connection_name": "Production Main DB",
    "status": "completed",
    "started_at": "2025-09-07T15:30:00",
    "completed_at": "2025-09-07T15:30:45",
    "duration_seconds": 45,
    "result": {
      "checks_performed": 25,
      "warnings": 2,
      "errors": 0
    },
    "error_message": null
  },
  {
    "id": 2,
    "task_id": 3,
    "task_name": "Query Analysis",
    "task_type": "query_analysis",
    "connection_id": 1,
    "connection_name": "Production Main DB",
    "status": "failed",
    "started_at": "2025-09-07T14:00:00",
    "completed_at": "2025-09-07T14:00:30",
    "duration_seconds": 30,
    "result": null,
    "error_message": "Connection timeout"
  }
]
```

---

### GET `/monitoring/tasks/{task_id}/executions` - Выполнения конкретной задачи

Получает историю выполнений для конкретной задачи.

**Запрос:**

```bash
curl http://localhost:8000/monitoring/tasks/5/executions
```

**Ответ:**

```json
[
  {
    "id": 1,
    "task_id": 5,
    "task_name": "Daily Config Check",
    "task_type": "config_check",
    "connection_id": 1,
    "status": "completed",
    "started_at": "2025-09-07T15:30:00",
    "completed_at": "2025-09-07T15:30:45",
    "duration_seconds": 45,
    "result": {
      "config_issues": [],
      "performance_recommendations": ["Consider increasing shared_buffers"]
    }
  }
]
```

---

### POST `/monitoring/tasks/{task_id}/execute` - Запустить задачу для мониторинга

Запускает задачу и возвращает результат выполнения для мониторинга.

**Запрос:**

```bash
curl -X POST http://localhost:8000/monitoring/tasks/5/execute
```

**Ответ:**

```json
{
  "execution_id": 15,
  "status": "running",
  "started_at": "2025-09-07T16:00:00",
  "message": "Task execution started"
}
```

---

### GET `/monitoring/tasks/running` - Текущие выполняющиеся задачи

Показывает задачи, которые выполняются в данный момент.

**Запрос:**

```bash
curl http://localhost:8000/monitoring/tasks/running
```

**Ответ:**

```json
[
  {
    "execution_id": 15,
    "task_id": 5,
    "task_name": "Daily Config Check",
    "task_type": "config_check",
    "connection_id": 1,
    "started_at": "2025-09-07T16:00:00",
    "duration_seconds": 45,
    "estimated_remaining_seconds": 15
  }
]
```

---

## 🔗 Мониторинг подключений

### GET `/monitoring/connections/status` - Статус всех подключений

Проверяет состояние всех подключений к базам данных.

**Запрос:**

```bash
curl http://localhost:8000/monitoring/connections/status
```

**Ответ:**

```json
[
  {
    "connection_id": 1,
    "connection_name": "Production Main DB",
    "environment": "production",
    "is_healthy": true,
    "response_time_ms": 45,
    "last_check": "2025-09-07T16:00:00",
    "server_version": "PostgreSQL 14.9",
    "database_size": "2.5 GB",
    "active_connections": 15,
    "max_connections": 100,
    "connection_usage_percent": 15.0,
    "error_message": null
  },
  {
    "connection_id": 2,
    "connection_name": "Analytics DB",
    "environment": "production",
    "is_healthy": false,
    "response_time_ms": null,
    "last_check": "2025-09-07T16:00:00",
    "server_version": null,
    "database_size": null,
    "active_connections": null,
    "max_connections": null,
    "connection_usage_percent": null,
    "error_message": "Connection refused: server is not responding"
  }
]
```

---

### GET `/monitoring/connections/{connection_id}/status` - Статус конкретного подключения

Проверяет состояние конкретного подключения с детальной информацией.

**Запрос:**

```bash
curl http://localhost:8000/monitoring/connections/1/status
```

**Ответ:**

```json
{
  "connection_id": 1,
  "connection_name": "Production Main DB",
  "environment": "production",
  "is_healthy": true,
  "response_time_ms": 45,
  "last_check": "2025-09-07T16:00:00",
  "server_version": "PostgreSQL 14.9",
  "database_size": "2.5 GB",
  "active_connections": 15,
  "max_connections": 100,
  "connection_usage_percent": 15.0,
  "uptime": "15 days, 8 hours",
  "cpu_usage_percent": 25.5,
  "memory_usage_percent": 67.2,
  "disk_usage_percent": 45.1,
  "slow_queries_count": 3,
  "locks_count": 0,
  "error_message": null,
  "detailed_metrics": {
    "transactions_per_second": 150.5,
    "cache_hit_ratio": 98.5,
    "index_usage_ratio": 95.2,
    "deadlocks_count": 0
  }
}
```

---

### POST `/monitoring/connections/{connection_id}/check` - Принудительная проверка подключения

Выполняет немедленную проверку состояния подключения.

**Запрос:**

```bash
curl -X POST http://localhost:8000/monitoring/connections/1/check
```

**Ответ:**

```json
{
  "connection_id": 1,
  "check_time": "2025-09-07T16:00:00",
  "is_healthy": true,
  "response_time_ms": 42,
  "message": "Connection check completed successfully"
}
```

---

## 📈 Агрегированная статистика

### Метрики производительности по временным интервалам

```bash
# Статистика за последний час
curl "http://localhost:8000/monitoring/connections/1/status?interval=1h"

# Статистика за день
curl "http://localhost:8000/monitoring/connections/1/status?interval=24h"

# Статистика за неделю
curl "http://localhost:8000/monitoring/connections/1/status?interval=7d"
```

---

## 🚨 Алерты и уведомления

### Критерии для алертов

**Проблемы с подключением:**

- `response_time_ms > 1000` - медленное соединение
- `is_healthy = false` - недоступная база данных
- `connection_usage_percent > 90` - превышение лимита подключений

**Проблемы с производительностью:**

- `cpu_usage_percent > 80` - высокая загрузка CPU
- `memory_usage_percent > 85` - высокое потребление памяти
- `cache_hit_ratio < 90` - низкий коэффициент попадания в кэш

**Проблемы с выполнением задач:**

- `status = "failed"` - неудачное выполнение задачи
- `duration_seconds > expected` - задача выполняется слишком долго

---

## 💡 Примеры использования

### Мониторинг ключевых метрик

```bash
# Проверка состояния всех продакшн баз
curl "http://localhost:8000/monitoring/connections/status" | \
  jq '.[] | select(.environment == "production")'

# Поиск медленных задач
curl "http://localhost:8000/monitoring/tasks/executions" | \
  jq '.[] | select(.duration_seconds > 60)'

# Проверка неудачных выполнений за последний день
curl "http://localhost:8000/monitoring/tasks/executions?status=failed&since=24h"
```

### Настройка автоматического мониторинга

```bash
# Скрипт для регулярной проверки
#!/bin/bash
for conn_id in 1 2 3; do
  health=$(curl -s "http://localhost:8000/monitoring/connections/$conn_id/status" | jq -r '.is_healthy')
  if [ "$health" != "true" ]; then
    echo "ALERT: Connection $conn_id is unhealthy!"
  fi
done
```

### Сбор метрик для дашборда

```bash
# Экспорт метрик в формате для Prometheus/Grafana
curl "http://localhost:8000/monitoring/connections/status" | \
  jq -r '.[] | "db_healthy{connection_id=\"\(.connection_id)\"} \(.is_healthy | if . then 1 else 0 end)"'
```
