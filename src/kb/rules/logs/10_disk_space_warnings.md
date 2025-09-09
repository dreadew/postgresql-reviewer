# DISK_SPACE_WARNINGS

description: Предупреждения о нехватке дискового пространства
severity_default: high
bad_example: |
2024-01-01 10:00:01 UTC ERROR: could not extend file "base/16384/123456": No space left on device
2024-01-01 10:00:02 UTC WARNING: database disk usage is 95% full
good_example: |
2024-01-01 10:00:01 UTC LOG: database disk usage is 60% full
notes: Нехватка дискового пространства может привести к остановке базы данных. Необходимо срочно освободить место или расширить хранилище.
