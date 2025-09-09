# INDEX_SELECTIVITY

description: Использование индексов с низкой селективностью.
severity_default: medium
bad_example: |
-- Column status has 2 values: 'active', 'inactive' (50/50 distribution)
CREATE INDEX idx_users_status ON users(status);
EXPLAIN SELECT \* FROM users WHERE status = 'active';
-- Index not used due to low selectivity
good_example: |
-- Composite index with high-selectivity column
CREATE INDEX idx_users_status_created_at ON users(status, created_at);
EXPLAIN SELECT \* FROM users WHERE status = 'active' AND created_at > '2024-01-01';
-- Index used effectively
notes: Индексы по колонкам с cardinality < 5% от общего числа строк - проверять эффективность.
