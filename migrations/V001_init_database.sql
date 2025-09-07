-- PostgreSQL Reviewer Database Schema
-- Инициализация БД с финальной структурой (без дублирования данных)

-- 1. Таблица подключений (метаданные, credentials в Vault)
CREATE TABLE IF NOT EXISTS connections (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    vault_path VARCHAR(500) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    environment VARCHAR(50) DEFAULT 'development',
    description TEXT,
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Таблица запланированных задач
CREATE TABLE IF NOT EXISTS scheduled_tasks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    task_type VARCHAR(100) NOT NULL CHECK (task_type IN ('log_analysis', 'config_check', 'query_analysis', 'custom_sql', 'table_analysis')),
    connection_id INTEGER REFERENCES connections(id) ON DELETE CASCADE,
    cron_schedule VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_run_at TIMESTAMP,
    next_run_at TIMESTAMP,
    task_params JSONB DEFAULT '{}',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Таблица выполнений задач
CREATE TABLE IF NOT EXISTS task_executions (
    id SERIAL PRIMARY KEY,
    scheduled_task_id INTEGER REFERENCES scheduled_tasks(id) ON DELETE SET NULL,
    task_type VARCHAR(100),
    connection_id INTEGER REFERENCES connections(id) ON DELETE CASCADE,
    parameters JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_ms INTEGER,
    result JSONB,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Таблица результатов анализа
CREATE TABLE IF NOT EXISTS analysis_results (
    id SERIAL PRIMARY KEY,
    connection_id INTEGER REFERENCES connections(id) ON DELETE CASCADE,
    analysis_type VARCHAR(50) NOT NULL,
    result JSONB NOT NULL,
    execution_id INTEGER REFERENCES task_executions(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Таблица статуса подключений
CREATE TABLE IF NOT EXISTS connection_status (
    id SERIAL PRIMARY KEY,
    connection_id INTEGER REFERENCES connections(id) ON DELETE CASCADE,
    is_healthy BOOLEAN DEFAULT FALSE,
    last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT,
    response_time_ms INTEGER,
    server_version VARCHAR(100)
);

-- ИНДЕКСЫ для оптимизации запросов

-- Connections
CREATE INDEX IF NOT EXISTS idx_connections_active ON connections(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_connections_environment ON connections(environment);
CREATE UNIQUE INDEX IF NOT EXISTS idx_connections_name_env ON connections(name, environment);

-- Scheduled Tasks
CREATE INDEX IF NOT EXISTS idx_scheduled_tasks_active ON scheduled_tasks(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_scheduled_tasks_connection ON scheduled_tasks(connection_id);
CREATE INDEX IF NOT EXISTS idx_scheduled_tasks_type ON scheduled_tasks(task_type);
CREATE INDEX IF NOT EXISTS idx_scheduled_tasks_next_run ON scheduled_tasks(next_run_at) WHERE is_active = true;

-- Task Executions
CREATE INDEX IF NOT EXISTS idx_task_executions_scheduled_task ON task_executions(scheduled_task_id);
CREATE INDEX IF NOT EXISTS idx_task_executions_connection ON task_executions(connection_id);
CREATE INDEX IF NOT EXISTS idx_task_executions_status ON task_executions(status);
CREATE INDEX IF NOT EXISTS idx_task_executions_task_type ON task_executions(task_type);
CREATE INDEX IF NOT EXISTS idx_task_executions_started_at ON task_executions(started_at);

-- Analysis Results
CREATE INDEX IF NOT EXISTS idx_analysis_results_connection_id ON analysis_results(connection_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_type ON analysis_results(analysis_type);
CREATE INDEX IF NOT EXISTS idx_analysis_results_created_at ON analysis_results(created_at);
CREATE INDEX IF NOT EXISTS idx_analysis_results_execution_id ON analysis_results(execution_id);

-- Connection Status
CREATE INDEX IF NOT EXISTS idx_connection_status_connection_id ON connection_status(connection_id);
CREATE INDEX IF NOT EXISTS idx_connection_status_last_check ON connection_status(last_check);

-- ТРИГГЕРЫ для автоматического обновления timestamps

-- Функция обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Триггеры
CREATE TRIGGER update_connections_updated_at
    BEFORE UPDATE ON connections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_scheduled_tasks_updated_at
    BEFORE UPDATE ON scheduled_tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- КОММЕНТАРИИ для документации

COMMENT ON TABLE connections IS 'Метаданные подключений к PostgreSQL. Credentials хранятся в Vault.';
COMMENT ON COLUMN connections.vault_path IS 'Путь в Vault где хранятся учетные данные (host, port, dbname, username, password)';
COMMENT ON COLUMN connections.environment IS 'Окружение: development, staging, production';
COMMENT ON COLUMN connections.tags IS 'Теги для группировки и фильтрации подключений';
COMMENT ON COLUMN connections.description IS 'Описание подключения для пользователей';

COMMENT ON TABLE scheduled_tasks IS 'Запланированные задачи анализа PostgreSQL';
COMMENT ON COLUMN scheduled_tasks.task_type IS 'Тип задачи: log_analysis, config_check, query_analysis, custom_sql, table_analysis';
COMMENT ON COLUMN scheduled_tasks.cron_schedule IS 'Расписание в формате Cron';
COMMENT ON COLUMN scheduled_tasks.task_params IS 'JSON параметры задачи (custom_sql, target_tables и т.д.)';

COMMENT ON TABLE task_executions IS 'История выполнения задач';
COMMENT ON COLUMN task_executions.task_type IS 'Тип задачи: log_analysis, config_check, query_analysis, custom_sql, table_analysis';
COMMENT ON COLUMN task_executions.connection_id IS 'ID подключения к базе данных, на которой выполняется задача';
COMMENT ON COLUMN task_executions.parameters IS 'JSON параметры выполнения задачи (custom_sql, target_tables и т.д.)';

COMMENT ON TABLE analysis_results IS 'Результаты анализа PostgreSQL (конфигурация, логи, запросы, таблицы)';

COMMENT ON TABLE connection_status IS 'Статус подключений к PostgreSQL';
