# QUERY_COST_ANALYSIS

description: Анализ общего cost и времени выполнения запроса.
severity_default: high
bad_example: |
EXPLAIN (ANALYZE, BUFFERS) SELECT \* FROM orders WHERE customer_id = 123;
-- cost=0.00..100000.00, execution time > 1000ms
good_example: |
EXPLAIN (ANALYZE, BUFFERS) SELECT \* FROM orders WHERE customer_id = 123;
-- cost=0.00..100.00, execution time < 10ms
notes: В production: cost > 10000 или время > 100ms - критично. В development: cost > 1000 или время > 50ms - warning.
