# UNION_ALL_PREFERENCE

description: Использование UNION вместо UNION ALL без необходимости.
severity_default: low
bad_example: |
EXPLAIN ANALYZE (SELECT id FROM users) UNION (SELECT user_id FROM orders);
-- Unique node for duplicate removal
good_example: |
EXPLAIN ANALYZE (SELECT id FROM users) UNION ALL (SELECT user_id FROM orders);
-- Direct Append
notes: UNION ALL на 20%+ быстрее. Использовать UNION только при реальной необходимости.
