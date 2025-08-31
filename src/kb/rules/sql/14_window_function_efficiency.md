# WINDOW_FUNCTION_EFFICIENCY

description: Неэффективные оконные функции без индексов.
severity_default: medium
bad_example: |
EXPLAIN ANALYZE SELECT _, ROW_NUMBER() OVER (ORDER BY created_at) FROM orders;
-- WindowAgg node with full sort
good_example: |
CREATE INDEX idx_orders_created_at ON orders(created_at);
EXPLAIN ANALYZE SELECT _, ROW_NUMBER() OVER (ORDER BY created_at) FROM orders;
-- WindowAgg with index scan
notes: Window functions по неиндексированным колонкам в таблицах > 50K строк - warning.
