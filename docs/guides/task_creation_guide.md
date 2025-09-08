# Руководство по созданию и управлению задачами

## 🎯 Обзор

Это полное руководство по созданию, настройке и управлению задачами в PostgreSQL Reviewer. Система поддерживает 5 типов задач с гибкими параметрами конфигурации.

## 📋 Типы задач

### 1. 🔍 LOG_ANALYSIS - Анализ логов

**Что делает**: Извлекает данные из `pg_stat_statements`, анализирует медленные запросы с помощью AI

**Применение**:

- Мониторинг производительности
- Поиск проблемных запросов
- Анализ нагрузки на БД

### 2. ⚙️ CONFIG_CHECK - Проверка конфигурации

**Что делает**: Собирает настройки из `pg_settings`, анализирует конфигурацию с рекомендациями

**Применение**:

- Оптимизация настроек сервера
- Проверка best practices
- Аудит конфигурации

### 3. 📊 QUERY_ANALYSIS - Анализ запросов

**Что делает**: Собирает статистику производительности без AI обработки

**Применение**:

- Быстрый мониторинг производительности
- Сбор метрик для дашбордов
- Отслеживание трендов

### 4. 🛠️ CUSTOM_SQL - Кастомные запросы

**Что делает**: Выполняет любые SQL запросы, которые вы напишете

**Применение**:

- Кастомные проверки
- Сбор специфичных метрик
- Автоматизация операций

### 5. 📋 TABLE_ANALYSIS - Анализ таблиц

**Что делает**: Анализирует размер, структуру и статистику таблиц

**Применение**:

- Мониторинг роста данных
- Анализ фрагментации
- Планирование VACUUM

## 🚀 Создание задач

### Через API

#### Базовый пример

```bash
curl -X POST "http://localhost:8000/api/v1/scheduler/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "daily_log_check",
    "task_type": "log_analysis",
    "connection_id": 1,
    "cron_schedule": "0 2 * * *",
    "description": "Ежедневная проверка логов"
  }'
```

#### С параметрами

```bash
curl -X POST "http://localhost:8000/api/v1/scheduler/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "prod_config_audit",
    "task_type": "config_check",
    "connection_id": 1,
    "cron_schedule": "0 6 * * 1",
    "task_params": {
      "environment": "production",
      "config_sections": ["memory", "wal", "query_planning"],
      "check_performance": true,
      "check_security": true,
      "detailed_analysis": true
    },
    "description": "Еженедельный аудит конфигурации продакшн сервера"
  }'
```

### Через Python SDK

```python
import requests

def create_custom_sql_task():
    task_data = {
        "name": "user_growth_report",
        "task_type": "custom_sql",
        "connection_id": 2,
        "cron_schedule": "0 9 * * 1",  # Каждый понедельник в 9:00
        "task_params": {
            "custom_sql": """
                SELECT
                    DATE_TRUNC('week', created_at) as week,
                    COUNT(*) as new_users,
                    COUNT(*) FILTER (WHERE is_active = true) as active_users
                FROM users
                WHERE created_at >= NOW() - INTERVAL '4 weeks'
                GROUP BY DATE_TRUNC('week', created_at)
                ORDER BY week
            """,
            "query_timeout": 60,
            "output_format": "json"
        },
        "description": "Еженедельный отчет по росту пользователей"
    }

    response = requests.post(
        "http://localhost:8000/api/v1/scheduler/tasks",
        json=task_data
    )
    return response.json()
```

## ⏰ Настройка расписания (Cron)

### Примеры cron выражений

```bash
# Каждый день в 2:00
"0 2 * * *"

# Каждый час
"0 * * * *"

# Каждые 15 минут
"*/15 * * * *"

# По будням в 8:30
"30 8 * * 1-5"

# Первое число месяца в 3:00
"0 3 1 * *"

# Каждое воскресенье в 4:00
"0 4 * * 0"
```

### Полезные паттерны

```bash
# Мониторинг производительности
"*/5 * * * *"    # Каждые 5 минут - query_analysis
"0 * * * *"      # Каждый час - log_analysis (краткий)
"0 2 * * *"      # Ежедневно в 2:00 - log_analysis (полный)

# Проверки конфигурации
"0 6 * * 1"      # Еженедельно в понедельник - config_check
"0 3 1 * *"      # Ежемесячно - полный аудит

# Анализ таблиц
"0 4 * * 0"      # Еженедельно в воскресенье - table_analysis
"0 2 1 * *"      # Ежемесячно - полный анализ всех таблиц

# Кастомные отчеты
"0 9 * * 1"      # Еженедельные отчеты
"0 8 1 * *"      # Ежемесячные отчеты
```

## 🔧 Параметры задач (TaskParameters)

### Полная схема параметров

```json
{
  "analysis_target": "logs|config|performance|security|tables|queries",
  "environment": "production|staging|development",

  // Параметры анализа логов
  "log_level": "debug|info|warning|error",
  "log_source": "application|postgresql",
  "time_range_hours": 24,

  // Параметры проверки конфигурации
  "config_sections": ["memory", "wal", "query_planning", "autovacuum"],
  "check_performance": true,
  "check_security": true,

  // Параметры кастомного SQL
  "custom_sql": "SELECT * FROM custom_query",
  "query_timeout": 300,

  // Параметры анализа таблиц
  "target_tables": ["schema.table1", "schema.table2"],

  // Общие параметры
  "output_format": "json|csv",
  "detailed_analysis": false
}
```

## 📊 Примеры реальных сценариев

### 1. Мониторинг production БД

```json
{
  "name": "prod_health_check",
  "task_type": "log_analysis",
  "connection_id": 1,
  "cron_schedule": "0 */2 * * *",
  "task_params": {
    "environment": "production",
    "time_range_hours": 2,
    "log_level": "warning"
  }
}
```

### 2. Еженедельная очистка старых данных

```json
{
  "name": "cleanup_old_logs",
  "task_type": "custom_sql",
  "connection_id": 1,
  "cron_schedule": "0 3 * * 0",
  "task_params": {
    "custom_sql": "DELETE FROM application_logs WHERE created_at < NOW() - INTERVAL '30 days'",
    "query_timeout": 600
  }
}
```

### 3. Сбор бизнес-метрик

```json
{
  "name": "daily_business_metrics",
  "task_type": "custom_sql",
  "connection_id": 2,
  "cron_schedule": "0 8 * * *",
  "task_params": {
    "custom_sql": "SELECT DATE(created_at) as date, COUNT(*) as orders, SUM(total_amount) as revenue FROM orders WHERE created_at >= CURRENT_DATE - 1 GROUP BY DATE(created_at)",
    "query_timeout": 120,
    "output_format": "json"
  }
}
```

### 4. Мониторинг размера больших таблиц

```json
{
  "name": "large_tables_monitor",
  "task_type": "table_analysis",
  "connection_id": 1,
  "cron_schedule": "0 5 * * *",
  "task_params": {
    "target_tables": [
      "public.events",
      "public.user_actions",
      "public.audit_log"
    ],
    "detailed_analysis": false
  }
}
```

### 5. Проверка блокировок и долгих транзакций

```json
{
  "name": "locks_and_long_queries",
  "task_type": "custom_sql",
  "connection_id": 1,
  "cron_schedule": "*/15 * * * *",
  "task_params": {
    "custom_sql": "SELECT pid, now() - pg_stat_activity.query_start AS duration, query, state FROM pg_stat_activity WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes'",
    "query_timeout": 30
  }
}
```

## 🎛️ Управление задачами

### Просмотр задач

```bash
# Все задачи
curl "http://localhost:8000/api/v1/scheduler/tasks"

# Только активные
curl "http://localhost:8000/api/v1/scheduler/tasks?is_active=true"

# Конкретная задача
curl "http://localhost:8000/api/v1/scheduler/tasks/1"
```

### Обновление задачи

```bash
curl -X PUT "http://localhost:8000/api/v1/scheduler/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{
    "cron_schedule": "0 3 * * *",
    "is_active": false
  }'
```

### Запуск задачи вручную

```bash
curl -X POST "http://localhost:8000/api/v1/scheduler/tasks/1/execute"
```

### Удаление задачи

```bash
curl -X DELETE "http://localhost:8000/api/v1/scheduler/tasks/1"
```

## 📈 Мониторинг выполнения

### История выполнений

```bash
# Все выполнения
curl "http://localhost:8000/api/v1/scheduler/executions"

# Выполнения конкретной задачи
curl "http://localhost:8000/api/v1/scheduler/executions?task_id=1"

# Последние 10 выполнений
curl "http://localhost:8000/api/v1/scheduler/executions?limit=10"
```

### Статистика

```bash
# Общая статистика
curl "http://localhost:8000/api/v1/monitoring/tasks/stats"

# Активные задачи
curl "http://localhost:8000/api/v1/monitoring/tasks/active"

# Состояние очереди
curl "http://localhost:8000/api/v1/monitoring/queue/status"
```

## 🔄 Retry и обработка ошибок

### Автоматические повторы

- По умолчанию: 3 попытки
- Интервал между попытками: экспоненциальный (60s, 120s, 300s)
- После исчерпания попыток задача помечается как failed

### Настройка retry

```json
{
  "task_params": {
    "max_retries": 5,
    "retry_delay": 120
  }
}
```

### Обработка ошибок

```python
# Типичные ошибки и решения
{
  "connection_error": "Проверить данные подключения в Vault",
  "timeout_error": "Увеличить query_timeout",
  "sql_error": "Проверить синтаксис SQL в custom_sql",
  "permission_error": "Проверить права пользователя БД"
}
```

## 🔒 Безопасность

### Управление доступом

- Пароли БД хранятся только в Vault
- SQL выполняется с правами пользователя подключения
- Логирование всех операций для аудита

### Рекомендации

```bash
# Создавайте отдельного пользователя для анализа
CREATE USER analyzer WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE production TO analyzer;
GRANT USAGE ON SCHEMA public TO analyzer;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyzer;

# Для custom_sql с записью - дополнительные права
GRANT INSERT, UPDATE, DELETE ON specific_tables TO analyzer;
```

## 🛠️ Отладка и troubleshooting

### Проверка состояния

```bash
# Логи воркеров
docker-compose logs worker

# Состояние Redis
redis-cli INFO

# Проверка подключений
curl "http://localhost:8000/api/v1/monitoring/connections/health"
```

### Типичные проблемы

1. **Задача не запускается** → Проверить cron выражение и активность
2. **Ошибка подключения** → Проверить credentials в Vault
3. **SQL ошибка** → Проверить синтаксис и права пользователя
4. **Timeout** → Увеличить query_timeout или оптимизировать запрос

Это руководство покрывает все аспекты создания и управления задачами в PostgreSQL Reviewer!json
{
"name": "Название задачи",
"task*type": "тип*задачи",
"connection*id": 1,
"cron_schedule": "0 2 \* \* *",
"description": "Описание задачи (опционально)",
"task*params": {
"analysis_target": "logs|config|performance|security|tables|queries",
"custom_sql": "SELECT * FROM pg_stat_statements;",
"target_tables": ["table1", "table2"],
"query_timeout": 300,
"output_format": "json",
"detailed_analysis": true
},
"is_active": true
}

````

## Типы задач (task_type)

### 1. LOG_ANALYSIS - Анализ логов

Анализирует логи PostgreSQL сервера

```json
{
  "name": "Ежедневный анализ логов",
  "task_type": "log_analysis",
  "connection_id": 1,
  "cron_schedule": "0 2 * * *",
  "task_params": {
    "analysis_target": "logs",
    "detailed_analysis": true
  }
}
````

### 2. CONFIG_CHECK - Проверка конфигурации

Анализирует настройки PostgreSQL

```json
{
  "name": "Проверка конфигурации",
  "task_type": "config_check",
  "connection_id": 1,
  "cron_schedule": "0 6 * * 1",
  "task_params": {
    "analysis_target": "config",
    "detailed_analysis": true
  }
}
```

### 3. QUERY_ANALYSIS - Анализ запросов

Анализирует медленные и проблемные запросы

```json
{
  "name": "Анализ медленных запросов",
  "task_type": "query_analysis",
  "connection_id": 1,
  "cron_schedule": "0 */4 * * *",
  "task_params": {
    "analysis_target": "performance",
    "query_timeout": 300
  }
}
```

### 4. CUSTOM_SQL - Кастомный SQL

Выполняет пользовательский SQL запрос для анализа

```json
{
  "name": "Анализ блокировок",
  "task_type": "custom_sql",
  "connection_id": 1,
  "cron_schedule": "0 */2 * * *",
  "task_params": {
    "custom_sql": "SELECT blocked_locks.pid AS blocked_pid, blocked_activity.usename AS blocked_user, blocking_locks.pid AS blocking_pid, blocking_activity.usename AS blocking_user, blocked_activity.query AS blocked_statement, blocking_activity.query AS current_statement_in_blocking_process FROM pg_catalog.pg_locks blocked_locks JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation WHERE NOT blocked_locks.granted;",
    "analysis_target": "security",
    "output_format": "json"
  }
}
```

### 5. TABLE_ANALYSIS - Анализ таблиц

Анализирует конкретные таблицы

```json
{
  "name": "Анализ основных таблиц",
  "task_type": "table_analysis",
  "connection_id": 1,
  "cron_schedule": "0 3 * * 0",
  "task_params": {
    "target_tables": ["users", "orders", "products"],
    "analysis_target": "tables",
    "detailed_analysis": true
  }
}
```

## Параметры cron_schedule

Cron выражения для планирования:

- `"0 2 * * *"` - каждый день в 2:00
- `"0 */4 * * *"` - каждые 4 часа
- `"0 6 * * 1"` - каждый понедельник в 6:00
- `"*/30 * * * *"` - каждые 30 минут
- `"0 0 1 * *"` - первого числа каждого месяца в полночь

## Настройки через .env файл

```env
# Количество воркеров для выполнения задач
SCHEDULER_WORKERS_COUNT=3

# Интервал проверки новых задач (секунды)
SCHEDULER_CHECK_INTERVAL=30

# URL API для анализа
SCHEDULER_API_URL=http://postgresql-reviewer:8000
```

## Примеры полных запросов

### Пример 1: Комплексный анализ производительности

```bash
curl -X POST "http://localhost:8000/scheduler/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ночной анализ производительности",
    "task_type": "custom_sql",
    "connection_id": 1,
    "cron_schedule": "0 1 * * *",
    "description": "Анализ производительности с кастомными метриками",
    "task_params": {
      "custom_sql": "SELECT schemaname, tablename, attname, n_distinct, correlation FROM pg_stats WHERE schemaname = '\''public'\'' ORDER BY n_distinct DESC LIMIT 20;",
      "analysis_target": "performance",
      "detailed_analysis": true,
      "query_timeout": 600
    }
  }'
```

### Пример 2: Мониторинг безопасности

```bash
curl -X POST "http://localhost:8000/scheduler/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Проверка подозрительной активности",
    "task_type": "custom_sql",
    "connection_id": 1,
    "cron_schedule": "*/15 * * * *",
    "task_params": {
      "custom_sql": "SELECT usename, count(*) as connection_count FROM pg_stat_activity WHERE state = '\''active'\'' GROUP BY usename HAVING count(*) > 10;",
      "analysis_target": "security"
    }
  }'
```

Задачи автоматически выполняются планировщиком согласно cron расписанию и результаты сохраняются в базе данных.
