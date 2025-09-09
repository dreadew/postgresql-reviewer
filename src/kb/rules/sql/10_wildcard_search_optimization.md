# WILDCARD_SEARCH_OPTIMIZATION

description: Неэффективный поиск по подстроке без индексов.
severity_default: medium
bad_example: |
EXPLAIN ANALYZE SELECT \* FROM users WHERE name LIKE '%smith%';
-- Seq Scan on 1M rows
good_example: |
CREATE INDEX idx_users_name_trgm ON users USING gin (name gin_trgm_ops);
EXPLAIN ANALYZE SELECT \* FROM users WHERE name LIKE '%smith%';
-- Bitmap Index Scan
notes: Для текстового поиска использовать pg_trgm или полнотекстовый поиск.
