# SELECT_STAR

description: Использование SELECT _ даёт лишнюю ширину строки и IO.
severity_default: low
bad_example: |
SELECT _ FROM orders;
good_example: |
SELECT id, total_amount, created_at FROM orders WHERE ...;
notes: В аналитических запросах projection менее критичен, но всё равно
рекомендуется.
