# HARDCODED_VALUES

description: Использование хардкода вместо параметров или конфигураций.
severity_default: low
bad_example: |
SELECT _ FROM users WHERE status = 'active';
good_example: |
SELECT _ FROM users WHERE status = $1;
notes: Повышает переиспользуемость и безопасность.
