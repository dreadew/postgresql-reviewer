# REPLICATION_SETTINGS

description: Проверка настроек репликации для отказоустойчивости.
severity_default: high
bad_example: |
wal_level = minimal
max_wal_senders = 0
-- High availability required
good_example: |
wal_level = replica
max_wal_senders = 5
hot_standby = on
notes: wal_level = replica или logical для репликации. max_wal_senders >= количество реплик. archive_mode = on для point-in-time recovery.
