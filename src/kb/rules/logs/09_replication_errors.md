# REPLICATION_ERRORS

description: Ошибки репликации
severity_default: high
bad_example: |
2024-01-01 10:00:01 UTC ERROR: could not connect to the primary server: connection refused
2024-01-01 10:00:02 UTC WARNING: replication connection lost
good_example: |
2024-01-01 10:00:01 UTC LOG: started streaming WAL from primary at 0/3000000 on timeline 1
notes: Ошибки репликации могут привести к потере данных и нарушению отказоустойчивости. Немедленно проверьте состояние репликации.
