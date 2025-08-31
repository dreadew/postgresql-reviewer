# STATISTICS_FRESHNESS

description: Использование устаревшей статистики планировщиком.
severity_default: medium
bad_example: |
-- Table orders: 1M rows, but pg_statistic shows 10K rows
EXPLAIN SELECT _ FROM orders WHERE customer_id = 123;
-- Wrong estimation, chooses Seq Scan
good_example: |
ANALYZE orders;
EXPLAIN SELECT _ FROM orders WHERE customer_id = 123;
-- Correct estimation, chooses Index Scan
notes: Проверять разницу между actual rows и estimated rows > 10x. Таблицы с частыми изменениями - регулярный ANALYZE.
