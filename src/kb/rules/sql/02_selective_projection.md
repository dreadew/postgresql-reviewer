# SELECTIVE_PROJECTION

description: Использование SELECT _ вместо явного перечисления нужных колонок.
severity_default: medium
bad_example: |
SELECT _ FROM orders WHERE customer_id = 123;
good_example: |
SELECT id, total_amount, created_at FROM orders WHERE customer_id = 123;
notes: Особенно важно для таблиц с большим количеством колонок (>20) или большими полями (JSON, TEXT). Проверять ширину строки в плане. SELECT \* может привести к избыточной передаче данных и снижению производительности.
