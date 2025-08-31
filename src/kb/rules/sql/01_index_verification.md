# INDEXING_VERIFICATION

description: Проверка наличия и эффективности индексов по колонкам, используемым в WHERE/JOIN/ORDER BY.
severity_default: high
bad_example: |
EXPLAIN ANALYZE SELECT \* FROM orders WHERE customer_id = 123;
-- Seq Scan detected
good_example: |
CREATE INDEX CONCURRENTLY idx_orders_customer_id ON orders(customer_id);
-- Index Scan after creation
notes: Анализировать план выполнения. При Seq Scan на таблицах > 10K строк - критично. Учитывать cardinality и частоту использования фильтров.
