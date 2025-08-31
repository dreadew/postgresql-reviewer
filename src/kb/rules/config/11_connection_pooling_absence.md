# CONNECTION_POOLING_ABSENCE

description: Проверка наличия пула соединений при высоких max_connections.
severity_default: critical
bad_example: |
max_connections = 500
-- No connection pooling
good_example: |
max_connections = 100
-- PgBouncer or PgPool-II used
notes: max_connections > 200 без пула соединений - критично. Рекомендуется использовать внешний пул (PgBouncer) для более 50 соединений.
