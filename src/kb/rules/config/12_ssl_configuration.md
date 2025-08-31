# SSL_CONFIGURATION

description: Проверка настроек SSL для безопасного соединения.
severity_default: high
bad_example: |
ssl = off
-- Production environment
good_example: |
ssl = on
ssl_cert_file = '/etc/ssl/postgresql/server.crt'
ssl_key_file = '/etc/ssl/postgresql/server.key'
notes: Обязательно включено в production и test средах. ssl_ciphers должен исключать уязвимые алгоритмы. ssl_prefer_server_ciphers = on.
