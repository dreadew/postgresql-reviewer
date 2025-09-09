# AUTOVACUUM_ISSUES

description: Проблемы с автовакуумом
severity_default: medium
bad_example: |
2024-01-01 10:00:01 UTC WARNING: database "mydb" must be vacuumed within 1000000 transactions
2024-01-01 10:00:02 UTC ERROR: canceling autovacuum task
good_example: |
2024-01-01 10:00:01 UTC LOG: automatic vacuum of table "mydb.public.users": index scans: 1
notes: Проблемы с автовакуумом могут привести к деградации производительности и проблемам с transaction ID wraparound. Проверьте настройки autovacuum.
