# FILE_SYSTEM_COMPATIBILITY

description: Проверка настроек в соответствии с файловой системой.
severity_default: medium
bad_example: |
fsync = off
-- ext4 file system
good_example: |
fsync = on
wal_sync_method = open_sync
-- ext4 file system
notes: fsync = on обязательно. Для ext4 использовать wal_sync_method = open_sync. Для XFS - fsync. data_directory и wal_directory на разных дисках для производительности.
