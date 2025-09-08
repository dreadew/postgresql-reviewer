# Logs API Documentation

## Overview

API для анализа логов PostgreSQL. Позволяет анализировать логи сервера, выявлять ошибки, проблемы производительности и потенциальные угрозы безопасности.

**Base URL:** `/logs`

---

## Endpoints

### 1. Analyze PostgreSQL Logs

**POST** `/logs/analyze`

Анализировать логи PostgreSQL сервера.

#### Request Body

```json
{
  "logs": "2024-01-01 12:00:01.123 UTC [12345] LOG: database system is ready to accept connections\n2024-01-01 12:00:05.456 UTC [12346] ERROR: relation \"missing_table\" does not exist at character 15\n2024-01-01 12:00:10.789 UTC [12347] WARNING: there is no transaction in progress\n2024-01-01 12:01:15.234 UTC [12348] LOG: duration: 15234.567 ms statement: SELECT * FROM large_table WHERE complex_condition = 'slow_query'",
  "server_info": {
    "version": "15.4",
    "host": "prod-db.example.com",
    "database": "myapp"
  },
  "environment": "production"
}
```

#### Response

```json
{
  "errors": [
    {
      "severity": "ERROR",
      "timestamp": "2024-01-01T12:00:05.456Z",
      "message": "relation \"missing_table\" does not exist at character 15",
      "category": "schema_error",
      "description": "Table or view does not exist",
      "impact": "high",
      "recommendation": "Verify table name and schema, or create missing table",
      "query": "SELECT * FROM missing_table",
      "line_number": 2
    }
  ],
  "overall_score": 65,
  "notes": "Found 1 error and 1 warning. Performance issues detected with slow queries.",
  "analysis_summary": {
    "total_log_lines": 4,
    "error_count": 1,
    "warning_count": 1,
    "slow_query_count": 1,
    "connection_events": 1,
    "performance_issues": [
      {
        "type": "slow_query",
        "duration_ms": 15234.567,
        "query": "SELECT * FROM large_table WHERE complex_condition = 'slow_query'",
        "recommendation": "Consider adding indexes or optimizing query"
      }
    ],
    "security_issues": [],
    "connection_issues": [],
    "categories": {
      "errors": 1,
      "warnings": 1,
      "performance": 1,
      "security": 0,
      "connections": 0
    },
    "time_range": {
      "start": "2024-01-01T12:00:01.123Z",
      "end": "2024-01-01T12:01:15.234Z",
      "duration_minutes": 1.23
    },
    "recommendations": [
      {
        "priority": "high",
        "category": "schema",
        "title": "Fix missing table reference",
        "description": "Application is trying to access non-existent table 'missing_table'"
      },
      {
        "priority": "medium",
        "category": "performance",
        "title": "Optimize slow queries",
        "description": "Query taking 15+ seconds should be optimized with proper indexing"
      }
    ]
  }
}
```

#### Status Codes

- `200` - Analysis completed successfully
- `400` - Invalid log data
- `500` - Internal server error

---

## Log Analysis Features

### Error Detection

Анализ выявляет различные типы ошибок:

#### Database Errors

- **Syntax Errors** - Неправильный SQL синтаксис
- **Schema Errors** - Отсутствующие таблицы, колонки
- **Permission Errors** - Недостаток прав доступа
- **Constraint Violations** - Нарушения ограничений

#### Connection Errors

- **Authentication Failures** - Ошибки аутентификации
- **Connection Timeouts** - Таймауты подключений
- **Too Many Connections** - Превышение лимита подключений

#### System Errors

- **Disk Space Issues** - Недостаток места на диске
- **Memory Issues** - Проблемы с памятью
- **Configuration Errors** - Ошибки конфигурации

### Performance Analysis

Анализ производительности включает:

#### Slow Queries

- Запросы с длительным временем выполнения
- Рекомендации по оптимизации
- Анализ планов выполнения

#### Lock Detection

- Блокировки и deadlock'и
- Долгие блокировки
- Конфликты доступа

#### Resource Usage

- Использование памяти
- Нагрузка на диск
- CPU утилизация

### Security Analysis

Проверка безопасности:

#### Authentication Issues

- Неудачные попытки входа
- Подозрительная активность
- Брутфорс атаки

#### Permission Violations

- Попытки доступа к запрещенным ресурсам
- Эскалация привилегий
- Подозрительные операции

#### SQL Injection Attempts

- Потенциальные SQL инъекции
- Подозрительные запросы
- Аномальная активность

---

## Response Structure

### Error Object

```json
{
  "severity": "ERROR|WARNING|NOTICE|INFO",
  "timestamp": "2024-01-01T12:00:00Z",
  "message": "Original error message",
  "category": "schema_error|performance|security|connection",
  "description": "Human-readable description",
  "impact": "low|medium|high|critical",
  "recommendation": "Specific recommendation",
  "query": "SQL query that caused the error (if applicable)",
  "line_number": 123
}
```

### Performance Issue Object

```json
{
  "type": "slow_query|lock|deadlock",
  "duration_ms": 15234.567,
  "query": "SELECT * FROM table",
  "recommendation": "Add index on column_name",
  "severity": "low|medium|high",
  "impact_description": "Description of performance impact"
}
```

### Analysis Summary

- `total_log_lines` - Общее количество строк лога
- `error_count` - Количество ошибок
- `warning_count` - Количество предупреждений
- `slow_query_count` - Количество медленных запросов
- `connection_events` - События подключений
- `time_range` - Временной диапазон логов
- `categories` - Распределение по категориям
- `recommendations` - Общие рекомендации

---

## Log Format Support

### Supported Log Formats

#### Standard PostgreSQL Log Format

```
2024-01-01 12:00:01.123 UTC [12345] LOG: message
2024-01-01 12:00:01.123 UTC [12345] ERROR: error message
```

#### CSV Log Format

```
2024-01-01 12:00:01.123,user,database,12345,host,LOG,00000,message
```

#### JSON Log Format

```json
{
  "timestamp": "2024-01-01T12:00:01.123Z",
  "level": "LOG",
  "message": "message",
  "detail": "additional details"
}
```

### Log Configuration Recommendations

```sql
-- Рекомендуемые настройки логирования для анализа
ALTER SYSTEM SET log_destination = 'stderr';
ALTER SYSTEM SET logging_collector = on;
ALTER SYSTEM SET log_directory = 'pg_log';
ALTER SYSTEM SET log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log';
ALTER SYSTEM SET log_rotation_age = '1d';
ALTER SYSTEM SET log_rotation_size = '100MB';

-- Детальное логирование
ALTER SYSTEM SET log_min_duration_statement = '1000'; -- медленные запросы >1сек
ALTER SYSTEM SET log_checkpoints = on;
ALTER SYSTEM SET log_connections = on;
ALTER SYSTEM SET log_disconnections = on;
ALTER SYSTEM SET log_lock_waits = on;
ALTER SYSTEM SET log_statement = 'all'; -- только для отладки

-- Перезагрузка конфигурации
SELECT pg_reload_conf();
```

---

## Examples

### Analyze Error Logs

```bash
curl -X POST "http://localhost:8000/logs/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "logs": "2024-01-01 12:00:01 UTC [1234] ERROR: syntax error at or near \"SELCT\"\n2024-01-01 12:00:02 UTC [1235] ERROR: relation \"users\" does not exist",
    "server_info": {
      "version": "15.4",
      "host": "prod-db.example.com",
      "database": "myapp"
    },
    "environment": "production"
  }'
```

### Analyze Performance Logs

```bash
curl -X POST "http://localhost:8000/logs/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "logs": "2024-01-01 12:00:01 UTC [1234] LOG: duration: 5000.123 ms statement: SELECT * FROM large_table\n2024-01-01 12:00:10 UTC [1235] LOG: process 1235 still waiting for ShareLock",
    "server_info": {
      "version": "15.4",
      "host": "prod-db.example.com",
      "database": "myapp"
    },
    "environment": "production"
  }'
```

### Analyze Security Logs

```bash
curl -X POST "http://localhost:8000/logs/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "logs": "2024-01-01 12:00:01 UTC [1234] FATAL: password authentication failed for user \"admin\"\n2024-01-01 12:00:02 UTC [1235] ERROR: permission denied for table sensitive_data",
    "server_info": {
      "version": "15.4",
      "host": "prod-db.example.com",
      "database": "myapp"
    },
    "environment": "production"
  }'
```

---

## Integration with Log Collection

### Collecting Logs from PostgreSQL

```bash
#!/bin/bash
# Сбор логов за последний час для анализа

LOG_FILE="/var/lib/postgresql/data/pg_log/postgresql-$(date +%Y-%m-%d).log"
LAST_HOUR_LOGS=$(tail -n 1000 "$LOG_FILE" | grep "$(date -d '1 hour ago' '+%Y-%m-%d %H')")

curl -X POST "http://localhost:8000/logs/analyze" \
  -H "Content-Type: application/json" \
  -d "{
    \"logs\": \"$LAST_HOUR_LOGS\",
    \"server_info\": {
      \"version\": \"15.4\",
      \"host\": \"$(hostname)\",
      \"database\": \"production\"
    },
    \"environment\": \"production\"
  }"
```

### Automated Log Analysis

```bash
#!/bin/bash
# Автоматический анализ логов с отправкой в мониторинг

RESPONSE=$(curl -s -X POST "http://localhost:8000/logs/analyze" \
  -H "Content-Type: application/json" \
  -d @log_data.json)

ERROR_COUNT=$(echo "$RESPONSE" | jq '.analysis_summary.error_count')
SCORE=$(echo "$RESPONSE" | jq '.overall_score')

if [ "$ERROR_COUNT" -gt 10 ] || [ "$SCORE" -lt 70 ]; then
  echo "ALERT: High error count ($ERROR_COUNT) or low score ($SCORE)"
  # Отправка в систему мониторинга
fi
```
