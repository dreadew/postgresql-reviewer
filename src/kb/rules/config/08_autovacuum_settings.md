# AUTOVACUUM_SETTINGS

description: Проверка настроек автоочистки для предотвращения bloat.
severity_default: high
bad_example: |
autovacuum = off
-- Large write-heavy tables
good_example: |
autovacuum = on
autovacuum_vacuum_scale_factor = 0.05
autovacuum_analyze_scale_factor = 0.02
notes: Обязательно включено в production. scale_factor = 0.02-0.05 для активных таблиц. log_autovacuum_min_duration = 0 для мониторинга.
