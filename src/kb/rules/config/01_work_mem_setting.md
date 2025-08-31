# WORK_MEM_SETTING

description: Проверка корректности настройки work_mem для эффективной сортировки и хеширования.
severity_default: high
bad_example: |
work_mem = 4MB
-- Server RAM: 16GB, max_connections: 200
good_example: |
work_mem = 64MB
-- Calculated as (16GB _ 0.25) / max_connections = 64MB
notes: work_mem должен быть рассчитан как (total_memory _ 0.25) / max_connections. Минимум 16MB в production. Высокие значения временных файлов (> 100MB) указывают на недостаток.
