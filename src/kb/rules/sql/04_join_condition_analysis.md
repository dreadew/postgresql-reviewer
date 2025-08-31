# JOIN_CONDITION_ANALYSIS

description: Проверка корректности и эффективности условий JOIN.
severity_default: high
bad_example: |
EXPLAIN ANALYZE SELECT _ FROM users u JOIN orders o ON u.name = o.customer_name;
-- Join on non-indexed text columns
good_example: |
EXPLAIN ANALYZE SELECT _ FROM users u JOIN orders o ON u.id = o.user_id;
-- Join on indexed integer columns
notes: Проверять план на использование Hash Join/Merge Join. Text joins без индексов - критично.
