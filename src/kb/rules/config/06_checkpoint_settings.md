# CHECKPOINT_SETTINGS

description: Проверка настроек контрольных точек для оптимальной производительности.
severity_default: high
bad_example: |
checkpoint_segments = 3
checkpoint_timeout = 5min
checkpoint_completion_target = 0.5
good_example: |
max_wal_size = 4GB
checkpoint_timeout = 30min
checkpoint_completion_target = 0.9
notes: checkpoint_completion_target = 0.7-0.9. Частые контрольные точки (меньше 10min) вызывают I/O spikes. max_wal_size = 25% от дискового пространства.
