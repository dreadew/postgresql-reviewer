-- PostgreSQL Reviewer Database Schema
-- This file initializes the database with required tables

-- Create database if it doesn't exist
-- Note: This is handled by POSTGRES_DB environment variable

-- Create connections table
CREATE TABLE IF NOT EXISTS connections (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    host VARCHAR(255) NOT NULL,
    port INTEGER DEFAULT 5432,
    database VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    vault_path VARCHAR(500) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    connection_id INTEGER REFERENCES connections(id) ON DELETE CASCADE,
    schedule VARCHAR(100) NOT NULL, -- cron format
    task_type VARCHAR(50) NOT NULL CHECK (task_type IN ('config_check', 'query_analysis', 'log_analysis')),
    parameters JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    last_run TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_connections_active ON connections(is_active);
CREATE INDEX IF NOT EXISTS idx_tasks_connection_id ON tasks(connection_id);
CREATE INDEX IF NOT EXISTS idx_tasks_active ON tasks(is_active);
CREATE INDEX IF NOT EXISTS idx_tasks_type ON tasks(task_type);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_connections_updated_at
    BEFORE UPDATE ON connections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data (optional, for development)
-- You can remove this in production
INSERT INTO connections (name, host, port, database, username, vault_path, is_active)
VALUES
    ('Local PostgreSQL', 'localhost', 5432, 'postgres', 'postgres', 'database/creds/local', true),
    ('Production DB', 'prod-db.example.com', 5432, 'app_db', 'app_user', 'database/creds/prod', true)
ON CONFLICT (vault_path) DO NOTHING;

INSERT INTO tasks (name, connection_id, schedule, task_type, parameters, is_active)
SELECT
    'Daily Config Check',
    c.id,
    '0 2 * * *',
    'config_check',
    '{"check_critical": true}',
    true
FROM connections c
WHERE c.name = 'Local PostgreSQL'
AND NOT EXISTS (SELECT 1 FROM tasks WHERE name = 'Daily Config Check')
LIMIT 1;

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO analyzer;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO analyzer;
