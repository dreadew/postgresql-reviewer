# BACKUP_CONFIGURATION

description: Проверка настроек для обеспечения возможности резервного копирования.
severity_default: high
bad_example: |
archive_mode = off
wal_level = minimal
good_example: |
archive_mode = on
wal_level = replica
archive_command = 'cp %p /var/lib/postgresql/archive/%f'
notes: archive_mode = on для WAL-архивации. wal_level >= replica. archive_command должен быть протестирован. wal_keep_segments или wal_keep_size для реплик.
