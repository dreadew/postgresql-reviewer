# EXTENSION_AUTOLOADING

description: Проверка корректной загрузки расширений через shared_preload_libraries.
severity_default: high
bad_example: |
shared_preload_libraries = ''
-- pg_stat_statements needed
good_example: |
shared_preload_libraries = 'pg_stat_statements,pg_buffercache'
notes: Расширения типа pg_stat_statements, auto_explain требуют перезапуска. Проверять доступность расширений в системе.
