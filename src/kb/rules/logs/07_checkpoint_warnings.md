# CHECKPOINT_WARNINGS

description: Предупреждения о слишком частых checkpoint'ах
severity_default: medium
bad_example: |
2024-01-01 10:00:01 UTC LOG: checkpoints are occurring too frequently (24 seconds apart)
2024-01-01 10:00:01 UTC HINT: Consider increasing the configuration parameter "max_wal_size"
good_example: |
2024-01-01 10:00:01 UTC LOG: checkpoint complete: wrote 1000 buffers (6.1%); 0 WAL file(s) added, 0 removed, 1 recycled
notes: Слишком частые checkpoint'ы могут снижать производительность. Рассмотрите увеличение max_wal_size или checkpoint_timeout.
