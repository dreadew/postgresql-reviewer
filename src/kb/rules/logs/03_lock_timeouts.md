# LOCK_TIMEOUTS

description: Превышение времени ожидания блокировок
severity_default: high
bad_example: |
2024-01-01 10:00:01 UTC ERROR: canceling statement due to lock timeout
2024-01-01 10:00:02 UTC WARNING: could not acquire lock on relation "users"
good_example: |
2024-01-01 10:00:01 UTC LOG: process 12345 acquired ShareLock on relation 16384
notes: Длительные блокировки могут привести к деградации производительности. Необходимо анализировать долго выполняющиеся запросы и оптимизировать их.
