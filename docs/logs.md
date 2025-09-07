# Логи API

Анализ и просмотр логов PostgreSQL и системных логов.

## Базовый путь: `/logs`

---

## 🔍 Анализ логов

### POST `/logs/analyze` - Анализ логов PostgreSQL

Выполняет анализ логов PostgreSQL для поиска проблем, ошибок и рекомендаций по оптимизации.

**Запрос:**

```bash
curl -X POST http://localhost:8000/logs/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": 1,
    "log_level": "WARNING",
    "time_range_hours": 24,
    "log_source": "postgresql",
    "filters": {
      "include_patterns": ["ERROR", "FATAL", "SLOW QUERY"],
      "exclude_patterns": ["DEBUG", "INFO"]
    }
  }'
```

**Параметры запроса:**

- `connection_id` - ID подключения к базе данных
- `log_level` - минимальный уровень логов (DEBUG, INFO, WARNING, ERROR, FATAL)
- `time_range_hours` - временной диапазон анализа в часах
- `log_source` - источник логов (postgresql, system, application)
- `filters` - фильтры для включения/исключения определенных паттернов

**Ответ:**

```json
{
  "analysis_id": "log_analysis_20250907_160000",
  "connection_id": 1,
  "time_range": {
    "start": "2025-09-06T16:00:00",
    "end": "2025-09-07T16:00:00",
    "duration_hours": 24
  },
  "summary": {
    "total_entries": 15420,
    "error_count": 23,
    "warning_count": 156,
    "fatal_count": 0,
    "slow_query_count": 45
  },
  "categories": {
    "connection_issues": {
      "count": 8,
      "severity": "medium",
      "examples": [
        "connection to server was lost",
        "could not receive from client"
      ]
    },
    "slow_queries": {
      "count": 45,
      "severity": "high",
      "examples": [
        "SELECT * FROM large_table took 15.2 seconds",
        "complex JOIN query took 8.7 seconds"
      ]
    },
    "lock_issues": {
      "count": 12,
      "severity": "medium",
      "examples": ["deadlock detected", "lock timeout exceeded"]
    },
    "checkpoint_warnings": {
      "count": 34,
      "severity": "low",
      "examples": ["checkpoints are occurring too frequently"]
    }
  },
  "recommendations": [
    {
      "category": "performance",
      "priority": "high",
      "message": "Consider optimizing slow queries identified in analysis",
      "affected_queries": 45,
      "suggested_actions": [
        "Add missing indexes",
        "Rewrite complex queries",
        "Increase work_mem for complex sorts"
      ]
    },
    {
      "category": "configuration",
      "priority": "medium",
      "message": "Checkpoint frequency is too high",
      "suggested_actions": [
        "Increase checkpoint_timeout",
        "Increase checkpoint_completion_target"
      ]
    }
  ],
  "top_errors": [
    {
      "message": "relation 'missing_table' does not exist",
      "count": 12,
      "first_seen": "2025-09-07T10:30:00",
      "last_seen": "2025-09-07T15:45:00"
    },
    {
      "message": "insufficient privilege for table sensitive_data",
      "count": 8,
      "first_seen": "2025-09-07T09:15:00",
      "last_seen": "2025-09-07T14:20:00"
    }
  ],
  "performance_insights": {
    "slowest_queries": [
      {
        "query": "SELECT * FROM orders o JOIN customers c ON o.customer_id = c.id WHERE o.created_at > '2025-01-01'",
        "avg_duration_ms": 15200,
        "execution_count": 25,
        "total_time_ms": 380000
      }
    ],
    "most_frequent_errors": [
      {
        "error_type": "syntax_error",
        "count": 15,
        "percentage": 65.2
      }
    ]
  },
  "created_at": "2025-09-07T16:00:00"
}
```

---

## 📊 Виды анализа логов

### 1. Анализ ошибок и предупреждений

```bash
curl -X POST http://localhost:8000/logs/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": 1,
    "log_level": "ERROR",
    "time_range_hours": 24,
    "filters": {
      "include_patterns": ["ERROR", "FATAL", "PANIC"]
    }
  }'
```

### 2. Анализ производительности

```bash
curl -X POST http://localhost:8000/logs/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": 1,
    "log_level": "INFO",
    "time_range_hours": 6,
    "filters": {
      "include_patterns": ["duration:", "slow query", "checkpoint"]
    }
  }'
```

### 3. Анализ подключений

```bash
curl -X POST http://localhost:8000/logs/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": 1,
    "log_level": "WARNING",
    "time_range_hours": 12,
    "filters": {
      "include_patterns": ["connection", "authentication", "SSL"]
    }
  }'
```

### 4. Анализ блокировок и дедлоков

```bash
curl -X POST http://localhost:8000/logs/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": 1,
    "log_level": "INFO",
    "time_range_hours": 48,
    "filters": {
      "include_patterns": ["deadlock", "lock", "waiting"]
    }
  }'
```

---

## 🚨 Типы проблем, выявляемых анализом

### Критические проблемы (FATAL/PANIC)

- Сбои сервера базы данных
- Критические ошибки в конфигурации
- Проблемы с файловой системой
- Коррупция данных

### Проблемы производительности

- Медленные запросы (> 1 секунды)
- Частые checkpoint'ы
- Высокое потребление памяти
- Проблемы с планировщиком запросов

### Проблемы безопасности

- Неудачные попытки аутентификации
- Нарушения прав доступа
- Подозрительная активность
- SSL/TLS проблемы

### Проблемы подключений

- Превышение лимита подключений
- Обрывы соединений
- Таймауты подключений
- DNS проблемы

---

## 📈 Интеграция с мониторингом

### Автоматический анализ логов

```bash
# Создание задачи для регулярного анализа логов
curl -X POST http://localhost:8000/scheduler/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hourly Log Analysis",
    "task_type": "log_analysis",
    "connection_id": 1,
    "cron_schedule": "0 * * * *",
    "task_params": {
      "log_level": "WARNING",
      "time_range_hours": 1
    }
  }'
```

### Экспорт результатов анализа

```bash
# Получение результатов в JSON для дальнейшей обработки
curl -X POST http://localhost:8000/logs/analyze \
  -H "Content-Type: application/json" \
  -d '{"connection_id": 1, "time_range_hours": 24}' | \
  jq '.recommendations[] | select(.priority == "high")'
```

---

## 💡 Примеры использования

### Расследование инцидента

```bash
# Анализ логов во время известного инцидента
curl -X POST http://localhost:8000/logs/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": 1,
    "log_level": "ERROR",
    "time_range_hours": 2,
    "filters": {
      "include_patterns": ["ERROR", "FATAL", "timeout", "connection"]
    }
  }'
```

### Еженедельный анализ производительности

```bash
# Поиск паттернов производительности за неделю
curl -X POST http://localhost:8000/logs/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": 1,
    "log_level": "INFO",
    "time_range_hours": 168,
    "filters": {
      "include_patterns": ["duration:", "slow", "checkpoint", "vacuum"]
    }
  }'
```

### Анализ безопасности

```bash
# Поиск проблем безопасности
curl -X POST http://localhost:8000/logs/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": 1,
    "log_level": "WARNING",
    "time_range_hours": 24,
    "filters": {
      "include_patterns": ["authentication", "privilege", "SSL", "unauthorized"]
    }
  }'
```

---

## 🔧 Настройка логирования PostgreSQL

Для эффективного анализа логов рекомендуется настроить PostgreSQL для записи детальной информации:

```sql
-- Рекомендуемые настройки логирования в postgresql.conf
log_destination = 'csvlog,stderr'
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB

-- Уровень детализации
log_min_duration_statement = 1000  -- Логировать запросы > 1 секунды
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_statement = 'mod'  -- Логировать DDL и модификации данных
log_temp_files = 0
```

Эти настройки обеспечат детальное логирование для качественного анализа.
