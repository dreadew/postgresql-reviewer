# AGGREGATION_PERFORMANCE

description: Неэффективные агрегации без индексов по GROUP BY колонкам.
severity_default: medium
bad_example: |
EXPLAIN ANALYZE SELECT user_id, COUNT(_) FROM orders GROUP BY user_id;
-- GroupAggregate with Seq Scan
good_example: |
CREATE INDEX idx_orders_user_id ON orders(user_id);
EXPLAIN ANALYZE SELECT user_id, COUNT(_) FROM orders GROUP BY user_id;
-- HashAggregate with Index Scan
notes: GROUP BY по неиндексированным колонкам в таблицах > 100K строк - warning.
