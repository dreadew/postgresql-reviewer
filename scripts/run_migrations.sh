#!/bin/bash

set -e

echo "Запуск миграций..."

echo "Ожидание готовности PostgreSQL..."
while ! PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' > /dev/null 2>&1; do
  echo "⏳ PostgreSQL еще не готов, ожидание..."
  sleep 2
done

echo "PostgreSQL готов!"

MIGRATIONS_DIR="/app/migrations"

if [ -d "$MIGRATIONS_DIR" ]; then
    echo "Найдена папка с миграциями: $MIGRATIONS_DIR"
    
    for migration_file in $(find $MIGRATIONS_DIR -name "*.sql" | sort); do
        echo "Выполнение миграции: $(basename $migration_file)"
        
        PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$migration_file"
        
        if [ $? -eq 0 ]; then
            echo "Миграция $(basename $migration_file) выполнена успешно"
        else
            echo "Ошибка выполнения миграции $(basename $migration_file)"
            exit 1
        fi
    done
    
    echo "Все миграции выполнены успешно!"
else
    echo "Папка с миграциями не найдена: $MIGRATIONS_DIR"
fi
