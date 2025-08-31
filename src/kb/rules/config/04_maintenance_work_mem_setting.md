# MAINTENANCE_WORK_MEM_SETTING

description: Проверка размера maintenance_work_mem для операций обслуживания.
severity_default: medium
bad_example: |
maintenance_work_mem = 64MB
-- Server RAM: 16GB
good_example: |
maintenance_work_mem = 2GB
-- 12.5% of 16GB RAM (max 2GB)
notes: Рекомендуется 10-25% от RAM, но не более 2GB. Ускоряет VACUUM, CREATE INDEX, ALTER TABLE.
