# SUBQUERY_OPTIMIZATION

description: Неоптимальные подзапросы, которые можно заменить JOIN или CTE.
severity_default: medium
bad_example: |
EXPLAIN ANALYZE SELECT \* FROM users u WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id AND o.total > 1000);
-- SubPlan (correlated subquery)
good_example: |
EXPLAIN ANALYZE SELECT DISTINCT u.\* FROM users u JOIN orders o ON u.id = o.user_id WHERE o.total > 1000;
-- Hash Join
notes: Correlated subqueries с cost > 1000 - критично.
