# MAX_CONNECTIONS_SETTING

description: Проверка разумного ограничения максимального количества соединений.
severity_default: high
bad_example: |
max_connections = 1000
-- Application uses ~50 concurrent connections
good_example: |
max_connections = 200
-- 2-3x от реального использования + запас
notes: Высокие значения увеличивают потребление памяти. Рекомендуется использовать пулы соединений (PgBouncer). max_connections > 500 без пула - критично.
