# SLOW_QUERIES

description: Медленно выполняющиеся запросы
severity_default: medium
bad_example: |
2024-01-01 10:00:01 UTC LOG: duration: 5000.123 ms statement: SELECT \* FROM large_table WHERE complex_condition
good_example: |
2024-01-01 10:00:01 UTC LOG: duration: 50.123 ms statement: SELECT id, name FROM users WHERE id = 123
notes: Медленные запросы (более 1000ms) требуют оптимизации. Проверьте наличие индексов, план выполнения и статистики таблиц.
