# MEMORY_ERRORS

description: Ошибки связанные с нехваткой памяти
severity_default: high
bad_example: |
2024-01-01 10:00:01 UTC ERROR: out of memory
2024-01-01 10:00:02 UTC DETAIL: Failed on request of size 1073741824
good_example: |
2024-01-01 10:00:01 UTC LOG: temporary file: path "base/pgsql_tmp/pgsql_tmp12345.0", size 104857600
notes: Ошибки памяти могут указывать на недостаточную конфигурацию памяти или неоптимальные запросы. Проверьте настройки work_mem и shared_buffers.
