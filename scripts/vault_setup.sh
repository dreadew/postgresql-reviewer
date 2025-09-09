#!/bin/bash

set -e

echo "Пример настройки Vault"

if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

if ! docker ps | grep -q "vault"; then
    echo "Запуск Vault контейнера..."
    docker-compose up -d vault
    
    echo "Ожидание готовности Vault..."
    sleep 5
fi

vault_exec() {
    docker exec -e VAULT_ADDR=http://localhost:8200 -e VAULT_TOKEN="$VAULT_TOKEN" vault vault "$@"
}

echo "Vault контейнер запущен"

echo "Настройка KV secrets engine..."
vault_exec secrets enable -path=secret kv-v2 2>/dev/null || echo "KV engine уже включен"

echo "Создание тестовых credentials для разработки..."

vault_exec kv put secret/database/connections/local-dev \
    host="postgres" \
    port="5432" \
    database="${POSTGRES_DB}" \
    username="${POSTGRES_USER}" \
    password="${POSTGRES_PASSWORD}"

vault_exec kv put secret/database/connections/prod-main \
    host="prod-db.example.com" \
    port="5432" \
    database="production_app" \
    username="app_user" \
    password="change_me_in_production"

vault_exec kv put secret/database/connections/staging \
    host="staging-db.example.com" \
    port="5432" \
    database="staging_app" \
    username="staging_user" \
    password="change_me_in_staging"

echo ""
echo "Проверяем созданные credentials:"
vault_exec kv list secret/database/connections/

echo ""
echo "Vault настроен успешно!"
echo ""
echo "Созданные подключения:"
echo "  • local-dev    - для локальной разработки"
echo "  • prod-main    - пример продакшн БД (нужно изменить)"
echo "  • staging      - пример staging БД (нужно изменить)"
echo ""
echo "Для изменения credentials используйте:"
echo "  docker exec -it vault vault kv put secret/database/connections/your-connection \\"
echo "    host='your-host' port='5432' database='your-db' username='user' password='pass'"
