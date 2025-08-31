# N_PLUS_ONE_DETECTION

description: Выявление потенциальных N+1 проблем в запросах.
severity_default: high
bad_example: |
SELECT _ FROM users; -- 1000 users
-- Application makes 1000 individual queries for orders
good_example: |
SELECT u._, o.\* FROM users u LEFT JOIN orders o ON u.id = o.user_id;
notes: Анализировать количество вызовов одного и того же запроса с разными параметрами.
