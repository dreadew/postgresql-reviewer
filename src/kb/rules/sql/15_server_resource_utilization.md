# SERVER_RESOURCE_UTILIZATION

description: Потенциальная перегрузка серверных ресурсов.
severity_default: high
bad_example: |
-- Server: 4GB RAM, work_mem=4MB
EXPLAIN ANALYZE SELECT \* FROM large_table ORDER BY text_column;
-- Disk sort: 2GB temporary files
good_example: |
-- Server: 16GB RAM, work_mem=64MB
EXPLAIN ANALYZE SELECT \* FROM large_table ORDER BY text_column;
-- Memory sort: 50MB
notes: Сравнивать размер временных файлов с доступной памятью. Disk sort > 10% RAM - критично.
