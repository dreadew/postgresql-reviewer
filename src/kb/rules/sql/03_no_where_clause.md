# WHERE_CLAUSE_NECESSITY

description: Отсутствие WHERE clause в запросах к большим таблицам.
severity_default: high
bad_example: |
SELECT _ FROM orders; -- orders has 1M+ rows
good_example: |
SELECT _ FROM orders WHERE created_at > '2024-01-01';
notes: Запрещено в production для таблиц > 100K строк. В development - warning при > 10K строк.
