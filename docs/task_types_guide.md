# Типы задач планировщика PostgreSQL Reviewer

## 🎯 Обзор типов задач

PostgreSQL Reviewer поддерживает 5 типов задач, которые можно выполнять автоматически по расписанию или запускать вручную:

1. **LOG_ANALYSIS** - Анализ логов PostgreSQL
2. **CONFIG_CHECK** - Проверка конфигурации сервера
3. **QUERY_ANALYSIS** - Анализ производительности запросов
4. **CUSTOM_SQL** - Выполнение кастомных SQL запросов
5. **TABLE_ANALYSIS** - Анализ структуры и статистики таблиц

## 📊 1. Анализ логов (LOG_ANALYSIS)

### Что выполняется:

- Извлечение медленных запросов из `pg_stat_statements`
- Анализ времени выполнения и частоты вызовов
- Отправка данных в AI для анализа и рекомендаций

### Пример создания задачи:

```bash
curl -X POST "http://localhost:8000/api/v1/scheduler/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "daily_log_analysis",
    "task_type": "log_analysis",
    "connection_id": 1,
    "cron_schedule": "0 2 * * *",
    "task_params": {
      "environment": "production",
      "time_range_hours": 24,
      "log_level": "warning"
    },
    "description": "Ежедневный анализ логов продакшн БД"
  }'
```

### Результат выполнения:

```json
{
  "issues": [...],
  "overall_score": 85.5,
  "analyzed_queries": 15,
  "recommendations": [...]
}
```

## ⚙️ 2. Проверка конфигурации (CONFIG_CHECK)

### Что выполняется:

- Сбор параметров конфигурации из `pg_settings`
- Анализ настроек памяти, дисков, WAL
- AI-анализ конфигурации с рекомендациями

### Пример создания задачи:

```bash
curl -X POST "http://localhost:8000/api/v1/scheduler/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "weekly_config_check",
    "task_type": "config_check",
    "connection_id": 1,
    "cron_schedule": "0 6 * * 1",
    "task_params": {
      "environment": "production",
      "config_sections": ["memory", "wal", "query_planning"],
      "check_performance": true,
      "check_security": true
    },
    "description": "Еженедельная проверка конфигурации"
  }'
```

### Результат выполнения:

```json
{
  "issues": [
    {
      "content": "shared_buffers слишком мал для production",
      "criticality": "high",
      "recommendation": "Увеличить до 25% RAM"
    }
  ],
  "overall_score": 75.0,
  "config_details": {...}
}
```

## 🔍 3. Анализ запросов (QUERY_ANALYSIS)

### Что выполняется:

- Сбор статистики из `pg_stat_statements`
- Поиск медленных и частых запросов
- Анализ производительности без AI

### Пример создания задачи:

```bash
curl -X POST "http://localhost:8000/api/v1/scheduler/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "hourly_query_analysis",
    "task_type": "query_analysis",
    "connection_id": 1,
    "cron_schedule": "0 * * * *",
    "task_params": {
      "environment": "production",
      "detailed_analysis": true
    },
    "description": "Почасовой анализ производительности запросов"
  }'
```

### Результат выполнения:

```json
{
  "message": "Анализ запросов выполнен",
  "analyzed_queries": 20,
  "queries": [
    {
      "query": "SELECT * FROM users WHERE ...",
      "calls": 1500,
      "total_exec_time": 2500.5,
      "mean_exec_time": 1.67
    }
  ]
}
```

## 🛠️ 4. Кастомные SQL запросы (CUSTOM_SQL)

### Что выполняется:

- Выполнение любого SQL запроса на указанной БД
- Возврат результатов SELECT запросов
- Информация о затронутых строках для DML операций

### Пример создания задачи:

```bash
curl -X POST "http://localhost:8000/api/v1/scheduler/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "daily_cleanup_old_logs",
    "task_type": "custom_sql",
    "connection_id": 1,
    "cron_schedule": "0 3 * * *",
    "task_params": {
      "custom_sql": "DELETE FROM application_logs WHERE created_at < NOW() - INTERVAL '\''30 days'\''",
      "query_timeout": 600,
      "output_format": "json"
    },
    "description": "Ежедневная очистка старых логов приложения"
  }'
```

### Пример SELECT запроса:

```bash
curl -X POST "http://localhost:8000/api/v1/scheduler/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "daily_user_stats",
    "task_type": "custom_sql",
    "connection_id": 1,
    "cron_schedule": "0 8 * * *",
    "task_params": {
      "custom_sql": "SELECT DATE(created_at) as date, COUNT(*) as new_users FROM users WHERE created_at >= CURRENT_DATE - INTERVAL '\''7 days'\'' GROUP BY DATE(created_at) ORDER BY date",
      "query_timeout": 60,
      "output_format": "json"
    },
    "description": "Ежедневная статистика новых пользователей"
  }'
```

### Результат выполнения SELECT:

```json
{
  "message": "Кастомный SQL запрос выполнен успешно",
  "sql": "SELECT DATE(created_at) as date, COUNT(*) as new_users FROM users...",
  "execution_time_seconds": 0.15,
  "query_type": "SELECT",
  "rows_returned": 7,
  "data": [
    { "date": "2025-09-01", "new_users": 25 },
    { "date": "2025-09-02", "new_users": 18 }
  ],
  "columns": ["date", "new_users"]
}
```

### Результат выполнения DML:

```json
{
  "message": "Кастомный SQL запрос выполнен успешно",
  "sql": "DELETE FROM application_logs WHERE created_at < NOW() - INTERVAL '30 days'",
  "execution_time_seconds": 2.45,
  "query_type": "DML/DDL",
  "rows_affected": 1250,
  "operation": "completed"
}
```

## 📋 5. Анализ таблиц (TABLE_ANALYSIS)

### Что выполняется:

- Сбор информации о размере таблиц и индексов
- Статистика по количеству строк (живых/мертвых)
- Информация о последнем VACUUM и ANALYZE
- Опционально: детальная информация о колонках и индексах

### Пример создания задачи:

```bash
curl -X POST "http://localhost:8000/api/v1/scheduler/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "weekly_table_analysis",
    "task_type": "table_analysis",
    "connection_id": 1,
    "cron_schedule": "0 4 * * 0",
    "task_params": {
      "target_tables": ["public.users", "public.orders", "public.products"],
      "detailed_analysis": true,
      "environment": "production"
    },
    "description": "Еженедельный анализ основных таблиц"
  }'
```

### Анализ всех таблиц:

```bash
curl -X POST "http://localhost:8000/api/v1/scheduler/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "monthly_full_table_analysis",
    "task_type": "table_analysis",
    "connection_id": 1,
    "cron_schedule": "0 2 1 * *",
    "task_params": {
      "detailed_analysis": false,
      "environment": "production"
    },
    "description": "Ежемесячный анализ всех таблиц (краткий)"
  }'
```

### Результат выполнения:

```json
{
  "message": "Анализ таблиц выполнен",
  "analyzed_tables_count": 3,
  "tables": [
    {
      "table": "public.users",
      "schema": "public",
      "owner": "app_user",
      "total_size": "45 MB",
      "table_size": "32 MB",
      "indexes_size": "13 MB",
      "estimated_rows": 125000,
      "dead_rows": 1250,
      "has_indexes": true,
      "has_triggers": false,
      "last_vacuum": "2025-09-05T14:30:00",
      "last_analyze": "2025-09-05T14:30:05",
      "columns": [...],  // если detailed_analysis = true
      "indexes": [...]   // если detailed_analysis = true
    }
  ],
  "detailed_analysis": true
}
```

## 🚀 Запуск задач вручную

Любую запланированную задачу можно запустить немедленно:

```bash
curl -X POST "http://localhost:8000/api/v1/scheduler/tasks/{task_id}/execute"
```

## ⚡ Мониторинг выполнения

Проверка статуса выполнения задач:

```bash
# Все выполнения задач
curl "http://localhost:8000/api/v1/scheduler/executions"

# Выполнения конкретной задачи
curl "http://localhost:8000/api/v1/scheduler/executions?task_id=1"

# Статистика выполнения
curl "http://localhost:8000/api/v1/monitoring/tasks/stats"
```

## 📝 Примеры параметров задач

### TaskParameters - полный набор опций:

```json
{
  "analysis_target": "logs|config|performance|security|tables|queries",
  "environment": "production|staging|development",

  // Для log_analysis
  "log_level": "debug|info|warning|error",
  "log_source": "application|postgresql",
  "time_range_hours": 24,

  // Для config_check
  "config_sections": ["memory", "wal", "query_planning"],
  "check_performance": true,
  "check_security": true,

  // Для custom_sql
  "custom_sql": "SELECT * FROM pg_stat_activity",
  "query_timeout": 300,

  // Для table_analysis
  "target_tables": ["schema.table1", "schema.table2"],

  // Общие параметры
  "output_format": "json|csv",
  "detailed_analysis": false
}
```

## 🔒 Безопасность

- Все пароли хранятся в HashiCorp Vault
- Кастомные SQL запросы выполняются с правами пользователя подключения
- Установлен timeout для защиты от долгих запросов
- Логирование всех операций для аудита

## 📊 Интеграция с мониторингом

Результаты всех задач сохраняются в таблице `analysis_results` и доступны через API для интеграции с системами мониторинга и дашбордами.
