-- Тестовые данные для PostgreSQL Reviewer
-- V002: Test Data

-- Пример подключений (credentials должны быть созданы в Vault отдельно)
INSERT INTO connections (name, vault_path, environment, description, tags, is_active)
VALUES
    ('Local Development', 'secret/database/connections/local-dev', 'development', 'Локальная БД для разработки', ARRAY['local', 'dev'], true),
    ('Production Main', 'secret/database/connections/prod-main', 'production', 'Основная продакшн БД', ARRAY['prod', 'critical'], true),
    ('Staging Environment', 'secret/database/connections/staging', 'staging', 'Тестовая среда', ARRAY['staging', 'test'], true),
    ('Analytics DB', 'secret/database/connections/analytics', 'production', 'База данных аналитики', ARRAY['analytics', 'readonly'], true)
ON CONFLICT (vault_path) DO NOTHING;

-- Пример запланированных задач
INSERT INTO scheduled_tasks (name, task_type, connection_id, cron_schedule, is_active, task_params, description)
SELECT
    'Daily Config Check - ' || c.name,
    'config_check',
    c.id,
    '0 2 * * *',  -- каждый день в 2:00
    true,
    '{"check_critical": true, "include_performance": true}',
    'Ежедневная проверка конфигурации PostgreSQL'
FROM connections c
WHERE c.environment IN ('production', 'staging')
ON CONFLICT (name) DO NOTHING;

INSERT INTO scheduled_tasks (name, task_type, connection_id, cron_schedule, is_active, task_params, description)
SELECT
    'Weekly Log Analysis - ' || c.name,
    'log_analysis',
    c.id,
    '0 1 * * 1',  -- каждый понедельник в 1:00
    true,
    '{"log_level": "WARNING", "last_hours": 168}',
    'Еженедельный анализ логов PostgreSQL'
FROM connections c
WHERE c.environment = 'production'
ON CONFLICT (name) DO NOTHING;

INSERT INTO scheduled_tasks (name, task_type, connection_id, cron_schedule, is_active, task_params, description)
SELECT
    'Hourly Query Analysis - ' || c.name,
    'query_analysis',
    c.id,
    '0 * * * *',  -- каждый час
    true,
    '{"analyze_slow_queries": true, "min_duration_ms": 1000}',
    'Почасовой анализ медленных запросов'
FROM connections c
WHERE c.environment = 'production'
ON CONFLICT (name) DO NOTHING;

-- Пример задач анализа таблиц
INSERT INTO scheduled_tasks (name, task_type, connection_id, cron_schedule, is_active, task_params, description)
SELECT
    'Daily Table Analysis - ' || c.name,
    'table_analysis',
    c.id,
    '0 3 * * *',  -- каждый день в 3:00
    true,
    '{"target_tables": ["public.*"], "include_indexes": true, "check_bloat": true}',
    'Ежедневный анализ таблиц и индексов'
FROM connections c
WHERE c.environment IN ('production', 'staging')
ON CONFLICT (name) DO NOTHING;

-- Пример пользовательской SQL задачи
INSERT INTO scheduled_tasks (name, task_type, connection_id, cron_schedule, is_active, task_params, description)
SELECT
    'Custom Health Check - ' || c.name,
    'custom_sql',
    c.id,
    '*/15 * * * *',  -- каждые 15 минут
    true,
    '{"custom_sql": "SELECT COUNT(*) as active_connections FROM pg_stat_activity WHERE state = ''active'';", "alert_threshold": 100}',
    'Проверка количества активных соединений'
FROM connections c
WHERE c.environment = 'production'
ON CONFLICT (name) DO NOTHING;
