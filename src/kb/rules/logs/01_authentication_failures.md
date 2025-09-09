# AUTHENTICATION_FAILURES

description: Обнаружение множественных неудачных попыток аутентификации
severity_default: high
bad_example: |
2024-01-01 10:00:01 UTC ERROR: password authentication failed for user "admin"
2024-01-01 10:00:02 UTC ERROR: password authentication failed for user "admin"
2024-01-01 10:00:03 UTC ERROR: password authentication failed for user "admin"
good_example: |
2024-01-01 10:00:01 UTC LOG: connection authorized: user=admin database=mydb
notes: Множественные неудачные попытки аутентификации могут указывать на атаку типа brute force. Рекомендуется проверить источник подключений и рассмотреть блокировку IP-адресов.
