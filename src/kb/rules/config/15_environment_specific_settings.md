# ENVIRONMENT_SPECIFIC_SETTINGS

description: Проверка соответствия настроек среде окружения.
severity_default: high
bad_example: |
log_statement = 'all'
log_min_duration_statement = 0
-- Production environment
good_example: |
log_statement = 'ddl'
log_min_duration_statement = 1000
-- Production environment
notes: Development: подробное логирование допустимо. Production: минимизировать логи. Test: баланс между информативностью и производительностью.
