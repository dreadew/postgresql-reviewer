# TEMPORARY_FILES_USAGE

description: Использование временных файлов для сортировки/агрегации.
severity_default: high
bad_example: |
EXPLAIN (ANALYZE, BUFFERS) SELECT _ FROM orders ORDER BY created_at;
-- Sort Method: external merge Disk: 5000kB
good_example: |
EXPLAIN (ANALYZE, BUFFERS) SELECT _ FROM orders WHERE customer_id = 123 ORDER BY created_at;
-- Sort Method: quicksort Memory: 25kB
notes: Disk sort > 1MB в production - критично. Проверять work_mem и индексы.
