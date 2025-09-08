# Практические примеры использования планировщика

## 🎯 Реальные сценарии использования

Этот документ содержит готовые к использованию примеры задач для типичных сценариев мониторинга и анализа PostgreSQL.

## 🏥 Мониторинг health продакшн БД

### 1. Непрерывный мониторинг производительности

```json
{
  "name": "prod_performance_monitor",
  "task_type": "query_analysis",
  "connection_id": 1,
  "cron_schedule": "*/5 * * * *",
  "task_params": {
    "environment": "production"
  },
  "description": "Мониторинг производительности каждые 5 минут"
}
```

### 2. Поиск медленных запросов

```json
{
  "name": "slow_query_detector",
  "task_type": "custom_sql",
  "connection_id": 1,
  "cron_schedule": "*/10 * * * *",
  "task_params": {
    "custom_sql": "SELECT query, calls, total_exec_time, mean_exec_time, rows FROM pg_stat_statements WHERE mean_exec_time > 1000 ORDER BY total_exec_time DESC LIMIT 10",
    "query_timeout": 30
  },
  "description": "Поиск запросов с временем выполнения > 1 сек"
}
```

### 3. Мониторинг подключений

```json
{
  "name": "connection_monitor",
  "task_type": "custom_sql",
  "connection_id": 1,
  "cron_schedule": "*/2 * * * *",
  "task_params": {
    "custom_sql": "SELECT state, COUNT(*) as count FROM pg_stat_activity WHERE state IS NOT NULL GROUP BY state",
    "query_timeout": 15
  },
  "description": "Мониторинг состояния подключений"
}
```

### 4. Проверка блокировок

```json
{
  "name": "lock_monitor",
  "task_type": "custom_sql",
  "connection_id": 1,
  "cron_schedule": "*/3 * * * *",
  "task_params": {
    "custom_sql": "SELECT blocked_locks.pid AS blocked_pid, blocked_activity.usename AS blocked_user, blocking_locks.pid AS blocking_pid, blocking_activity.usename AS blocking_user, blocked_activity.query AS blocked_statement FROM pg_catalog.pg_locks blocked_locks JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype AND blocking_locks.DATABASE IS NOT DISTINCT FROM blocked_locks.DATABASE AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid AND blocking_locks.pid != blocked_locks.pid JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid WHERE NOT blocked_locks.GRANTED",
    "query_timeout": 30
  },
  "description": "Поиск заблокированных запросов"
}
```

## 📊 Регулярные отчеты и аналитика

### 5. Ежедневная сводка по БД

```json
{
  "name": "daily_db_summary",
  "task_type": "custom_sql",
  "connection_id": 1,
  "cron_schedule": "0 8 * * *",
  "task_params": {
    "custom_sql": "SELECT 'Database Size' as metric, pg_size_pretty(pg_database_size(current_database())) as value UNION ALL SELECT 'Active Connections', COUNT(*)::text FROM pg_stat_activity WHERE state = 'active' UNION ALL SELECT 'Total Queries Today', SUM(calls)::text FROM pg_stat_statements WHERE stats_reset::date = CURRENT_DATE UNION ALL SELECT 'Cache Hit Ratio', ROUND(100.0 * sum(blks_hit) / (sum(blks_hit) + sum(blks_read)), 2)::text || '%' FROM pg_stat_database WHERE datname = current_database()",
    "query_timeout": 60
  },
  "description": "Ежедневная сводка ключевых метрик БД"
}
```

### 6. Еженедельный отчет по росту данных

```json
{
  "name": "weekly_growth_report",
  "task_type": "table_analysis",
  "connection_id": 1,
  "cron_schedule": "0 9 * * 1",
  "task_params": {
    "target_tables": [
      "public.users",
      "public.orders",
      "public.products",
      "public.events"
    ],
    "detailed_analysis": true
  },
  "description": "Еженедельный анализ роста основных таблиц"
}
```

### 7. Месячный анализ конфигурации

```json
{
  "name": "monthly_config_audit",
  "task_type": "config_check",
  "connection_id": 1,
  "cron_schedule": "0 6 1 * *",
  "task_params": {
    "environment": "production",
    "check_performance": true,
    "check_security": true,
    "detailed_analysis": true
  },
  "description": "Ежемесячный аудит конфигурации продакшн сервера"
}
```

## 🧹 Автоматизация обслуживания

### 8. Очистка старых логов

```json
{
  "name": "cleanup_application_logs",
  "task_type": "custom_sql",
  "connection_id": 2,
  "cron_schedule": "0 2 * * 0",
  "task_params": {
    "custom_sql": "DELETE FROM application_logs WHERE created_at < NOW() - INTERVAL '30 days'",
    "query_timeout": 1800
  },
  "description": "Еженедельная очистка логов старше 30 дней"
}
```

### 9. Очистка временных данных

```json
{
  "name": "cleanup_temp_data",
  "task_type": "custom_sql",
  "connection_id": 2,
  "cron_schedule": "0 3 * * *",
  "task_params": {
    "custom_sql": "DELETE FROM temp_sessions WHERE created_at < NOW() - INTERVAL '24 hours'; DELETE FROM temp_files WHERE created_at < NOW() - INTERVAL '2 hours';",
    "query_timeout": 600
  },
  "description": "Ежедневная очистка временных данных"
}
```

### 10. Обновление статистики

```json
{
  "name": "update_table_statistics",
  "task_type": "custom_sql",
  "connection_id": 1,
  "cron_schedule": "0 4 * * 0",
  "task_params": {
    "custom_sql": "ANALYZE; SELECT 'Statistics updated for ' || count(*) || ' tables' as result FROM pg_stat_user_tables;",
    "query_timeout": 3600
  },
  "description": "Еженедельное обновление статистики таблиц"
}
```

## 📈 Бизнес-метрики и KPI

### 11. Ежедневные продажи

```json
{
  "name": "daily_sales_report",
  "task_type": "custom_sql",
  "connection_id": 2,
  "cron_schedule": "0 9 * * *",
  "task_params": {
    "custom_sql": "SELECT DATE(created_at) as date, COUNT(*) as orders_count, SUM(total_amount) as total_revenue, AVG(total_amount) as avg_order_value FROM orders WHERE created_at >= CURRENT_DATE - INTERVAL '1 day' GROUP BY DATE(created_at)",
    "query_timeout": 120
  },
  "description": "Ежедневный отчет по продажам"
}
```

### 12. Активность пользователей

```json
{
  "name": "user_activity_stats",
  "task_type": "custom_sql",
  "connection_id": 2,
  "cron_schedule": "0 10 * * *",
  "task_params": {
    "custom_sql": "SELECT 'Daily Active Users' as metric, COUNT(DISTINCT user_id) as value FROM user_sessions WHERE DATE(created_at) = CURRENT_DATE UNION ALL SELECT 'New Registrations', COUNT(*) FROM users WHERE DATE(created_at) = CURRENT_DATE UNION ALL SELECT 'Login Sessions', COUNT(*) FROM user_sessions WHERE DATE(created_at) = CURRENT_DATE",
    "query_timeout": 90
  },
  "description": "Ежедневная статистика активности пользователей"
}
```

### 13. Еженедельный retention анализ

```json
{
  "name": "weekly_retention_analysis",
  "task_type": "custom_sql",
  "connection_id": 2,
  "cron_schedule": "0 11 * * 1",
  "task_params": {
    "custom_sql": "WITH cohort_data AS (SELECT DATE_TRUNC('week', created_at) as cohort_week, user_id FROM users WHERE created_at >= NOW() - INTERVAL '8 weeks'), activity_data AS (SELECT DATE_TRUNC('week', login_date) as activity_week, user_id FROM user_logins WHERE login_date >= NOW() - INTERVAL '8 weeks') SELECT c.cohort_week, COUNT(DISTINCT c.user_id) as cohort_size, COUNT(DISTINCT a.user_id) as active_users, ROUND(100.0 * COUNT(DISTINCT a.user_id) / COUNT(DISTINCT c.user_id), 2) as retention_rate FROM cohort_data c LEFT JOIN activity_data a ON c.user_id = a.user_id AND a.activity_week = c.cohort_week + INTERVAL '1 week' GROUP BY c.cohort_week ORDER BY c.cohort_week",
    "query_timeout": 180
  },
  "description": "Еженедельный анализ удержания пользователей"
}
```

## 🔍 Специализированные проверки

### 14. Поиск дублей в критичных таблицах

```json
{
  "name": "duplicate_check",
  "task_type": "custom_sql",
  "connection_id": 1,
  "cron_schedule": "0 12 * * *",
  "task_params": {
    "custom_sql": "SELECT 'users' as table_name, email, COUNT(*) as duplicate_count FROM users GROUP BY email HAVING COUNT(*) > 1 UNION ALL SELECT 'products', sku, COUNT(*) FROM products GROUP BY sku HAVING COUNT(*) > 1",
    "query_timeout": 300
  },
  "description": "Ежедневная проверка дублей в критичных таблицах"
}
```

### 15. Мониторинг размера индексов

```json
{
  "name": "index_size_monitor",
  "task_type": "custom_sql",
  "connection_id": 1,
  "cron_schedule": "0 5 * * 1",
  "task_params": {
    "custom_sql": "SELECT schemaname, tablename, indexname, pg_size_pretty(pg_relation_size(indexrelid)) as index_size FROM pg_stat_user_indexes JOIN pg_index ON pg_stat_user_indexes.indexrelid = pg_index.indexrelid WHERE pg_relation_size(indexrelid) > 100 * 1024 * 1024 ORDER BY pg_relation_size(indexrelid) DESC",
    "query_timeout": 120
  },
  "description": "Еженедельный мониторинг размера больших индексов"
}
```

### 16. Проверка неиспользуемых индексов

```json
{
  "name": "unused_indexes_check",
  "task_type": "custom_sql",
  "connection_id": 1,
  "cron_schedule": "0 6 * * 0",
  "task_params": {
    "custom_sql": "SELECT schemaname, tablename, indexname, idx_scan FROM pg_stat_user_indexes WHERE idx_scan = 0 AND NOT indisunique AND indexname NOT LIKE '%_pkey'",
    "query_timeout": 60
  },
  "description": "Еженедельная проверка неиспользуемых индексов"
}
```

## 🚨 Алерты и уведомления

### 17. Критический мониторинг дискового пространства

```json
{
  "name": "disk_space_alert",
  "task_type": "custom_sql",
  "connection_id": 1,
  "cron_schedule": "*/30 * * * *",
  "task_params": {
    "custom_sql": "SELECT 'Database Size' as metric, pg_size_pretty(pg_database_size(current_database())) as current_size, CASE WHEN pg_database_size(current_database()) > 50*1024*1024*1024 THEN 'WARNING: Database size > 50GB' ELSE 'OK' END as status",
    "query_timeout": 30
  },
  "description": "Мониторинг размера БД каждые 30 минут"
}
```

### 18. Мониторинг долгих транзакций

```json
{
  "name": "long_transactions_alert",
  "task_type": "custom_sql",
  "connection_id": 1,
  "cron_schedule": "*/15 * * * *",
  "task_params": {
    "custom_sql": "SELECT pid, now() - xact_start AS duration, state, query FROM pg_stat_activity WHERE state != 'idle' AND (now() - xact_start) > interval '10 minutes' ORDER BY duration DESC",
    "query_timeout": 30
  },
  "description": "Поиск транзакций длиннее 10 минут"
}
```

## 🔧 Кастомизация под ваши нужды

### Шаблон для создания собственных задач

```json
{
  "name": "your_custom_task",
  "task_type": "custom_sql",
  "connection_id": YOUR_CONNECTION_ID,
  "cron_schedule": "CRON_EXPRESSION",
  "task_params": {
    "custom_sql": "YOUR_SQL_QUERY",
    "query_timeout": TIMEOUT_IN_SECONDS,
    "output_format": "json"
  },
  "description": "Description of what this task does"
}
```

### Полезные SQL запросы для мониторинга

#### Топ медленных запросов

```sql
SELECT query, calls, total_exec_time, mean_exec_time
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
```

#### Размер таблиц

```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

#### Hit ratio кэша

```sql
SELECT
    datname,
    ROUND(100.0 * blks_hit / (blks_hit + blks_read), 2) AS cache_hit_ratio
FROM pg_stat_database
WHERE blks_read > 0;
```

Эти примеры покрывают большинство типичных сценариев использования планировщика PostgreSQL Reviewer. Адаптируйте их под свои специфические потребности!
