# WAL_SETTINGS

description: Проверка настроек Write-Ahead Logging для производительности и надежности.
severity_default: medium
bad_example: |
wal_buffers = 64kB
-- Server RAM: 16GB
good_example: |
wal_buffers = 16MB
-- 0.125% of shared_buffers, max 16MB
notes: wal_buffers = 0.125% от shared_buffers, максимум 16MB. sync_method = 'open_sync' на ext4, 'fsync' на XFS. wal_writer_delay = 200ms в production.
