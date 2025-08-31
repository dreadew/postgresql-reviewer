# LOCK_CONTENTION_ANALYSIS

description: Запросы, которые могут вызвать блокировки или быть заблокированными.
severity_default: high
bad_example: |
UPDATE users SET last_login = NOW() WHERE id = 1;
-- In high-concurrency environment
good_example: |
UPDATE users SET last_login = NOW() WHERE id = 1 AND last_login < NOW() - INTERVAL '1 hour';
-- Conditional update to reduce contention
notes: В production при concurrency > 10 - критично. Проверять pg_stat_activity на блокировки.
