# WINDOW_FUNCTION_WITHOUT_PARTITION

description: Использование оконных функций без PARTITION BY может быть неэффективным.
severity_default: low
bad_example: |
SELECT user_id, ROW_NUMBER() OVER (ORDER BY created_at) FROM orders;
good_example: |
SELECT user_id, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at) FROM orders;
notes: Используйте PARTITION BY для ускорения оконных функций.
