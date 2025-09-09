# DEADLOCKS

description: Обнаружение взаимных блокировок (deadlocks)
severity_default: high
bad_example: |
2024-01-01 10:00:01 UTC ERROR: deadlock detected
2024-01-01 10:00:01 UTC DETAIL: Process 12345 waits for ShareLock on transaction 987; blocked by process 67890
good_example: |
2024-01-01 10:00:01 UTC LOG: process 12345 acquired ShareLock on relation 16384
notes: Deadlocks указывают на проблемы с порядком блокировок в приложении. Необходимо пересмотреть логику транзакций и порядок обращения к ресурсам.
