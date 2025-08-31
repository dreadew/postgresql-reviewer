# ENVIRONMENT_APPROPRIATENESS

description: Соответствие запроса среде выполнения.
severity_default: high
bad_example: |
-- Environment: Production
SELECT _ FROM large_table; -- 10M rows
good_example: |
-- Environment: Production
SELECT _ FROM large_table WHERE indexed_column = 'value' LIMIT 1000;
notes: В production запрещены: SELECT \* без WHERE/LIMIT на таблицах > 100K строк, длительные блокирующие операции в рабочее время.
