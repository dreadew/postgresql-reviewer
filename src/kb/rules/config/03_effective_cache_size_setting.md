# EFFECTIVE_CACHE_SIZE_SETTING

description: Проверка корректности effective_cache_size для планировщика.
severity_default: medium
bad_example: |
effective_cache_size = 128MB
-- Server RAM: 16GB
good_example: |
effective_cache_size = 12GB
-- 75% of 16GB RAM
notes: Должен быть равен 50-75% от общей памяти. Используется планировщиком для оценки стоимости кэшированных данных.
