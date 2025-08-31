# MEMORY_CONFIGURATION_CONSISTENCY

description: Проверка согласованности всех memory-related параметров.
severity_default: high
bad_example: |
shared_buffers = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
effective_cache_size = 128MB
-- Server RAM: 16GB
good_example: |
shared_buffers = 4GB
work_mem = 64MB
maintenance_work_mem = 2GB
effective_cache_size = 12GB
notes: Общая сумма memory settings не должна превышать 80% RAM. effective_cache_size + shared_buffers не должна быть больше 100% RAM.
