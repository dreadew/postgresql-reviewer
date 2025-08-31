# LOGGING_CONFIGURATION

description: Проверка настроек логирования для мониторинга и отладки.
severity_default: medium
bad_example: |
log_statement = 'none'
log_min_duration_statement = -1
good_example: |
log_statement = 'ddl'
log_min_duration_statement = 1000
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
notes: log_statement = 'ddl' в production. log_min_duration_statement = 1000-5000ms для slow query logging. Логи должны включать контекст (user, db, app).
