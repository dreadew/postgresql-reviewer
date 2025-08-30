# Индексирование

description: Отсутствие индексов по колонкам, используемым в WHERE/JOIN/ORDER
BY.
severity_default: high
bad_example: |
SELECT \* FROM orders WHERE customer_id = 123;
good_example: |
CREATE INDEX CONCURRENTLY idx_orders_customer_id ON orders(customer_id);
notes: Проверять cardinality и статистики таблиц. Если cardinality низкая —
индекс может не помочь.
