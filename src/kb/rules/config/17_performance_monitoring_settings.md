# PERFORMANCE_MONITORING_SETTINGS

description: Проверка настроек для сбора метрик производительности.
severity_default: medium
bad_example: |
track_activities = off
track_counts = off
track_io_timing = off
good_example: |
track_activities = on
track_counts = on
track_io_timing = on
pg_stat_statements.track = all
notes: track_io_timing = on требует поддержки от ОС. pg_stat_statements обязательна для мониторинга. track_counts = on для статистики таблиц.
