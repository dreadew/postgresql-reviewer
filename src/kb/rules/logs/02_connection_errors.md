# CONNECTION_ERRORS

description: Ошибки подключения к базе данных
severity_default: medium
bad_example: |
2024-01-01 10:00:01 UTC FATAL: database "nonexistent_db" does not exist
2024-01-01 10:00:02 UTC FATAL: too many connections for role "user"
good_example: |
2024-01-01 10:00:01 UTC LOG: connection received: host=192.168.1.100 port=54321
notes: Ошибки подключения могут указывать на проблемы с конфигурацией, достижение лимитов подключений или попытки подключения к несуществующим базам данных.
