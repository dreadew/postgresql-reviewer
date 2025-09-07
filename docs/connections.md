# Подключения к БД API

Управление подключениями к PostgreSQL базам данных через интеграцию с HashiCorp Vault.

## Базовый путь: `/connections`

---

## 🔗 Управление подключениями

### POST `/connections/` - Создать подключение

Создает новое подключение к базе данных. Credentials хранятся в Vault, в базе данных сохраняются только метаданные.

**Запрос:**

```bash
curl -X POST http://localhost:8000/connections/ \
  -H "Content-Type: application/json" \
  -d '{
    "vault_path": "database/postgresql/prod-main",
    "environment": "production",
    "description": "Основная продакшн база данных",
    "tags": ["production", "main", "critical"],
    "host": "prod-db.company.com",
    "port": 5432,
    "database": "main_app",
    "username": "app_user",
    "password": "secure_password123"
  }'
```

**Поля запроса:**

- `vault_path` - путь в Vault для хранения credentials
- `environment` - окружение (production, staging, development)
- `description` - описание подключения
- `tags` - теги для категоризации
- `host`, `port`, `database`, `username`, `password` - данные подключения (сохраняются в Vault)

**Ответ:**

```json
{
  "id": 1,
  "vault_path": "database/postgresql/prod-main",
  "environment": "production",
  "description": "Основная продакшн база данных",
  "tags": ["production", "main", "critical"],
  "created_at": "2025-09-07T15:30:00",
  "updated_at": "2025-09-07T15:30:00"
}
```

---

### GET `/connections/` - Список подключений

Получает список всех подключений (только метаданные, без credentials).

**Запрос:**

```bash
curl http://localhost:8000/connections/
```

**Ответ:**

```json
[
  {
    "id": 1,
    "vault_path": "database/postgresql/prod-main",
    "environment": "production",
    "description": "Основная продакшн база данных",
    "tags": ["production", "main", "critical"],
    "created_at": "2025-09-07T15:30:00",
    "updated_at": "2025-09-07T15:30:00"
  },
  {
    "id": 2,
    "vault_path": "database/postgresql/staging",
    "environment": "staging",
    "description": "Тестовая база данных",
    "tags": ["staging", "test"],
    "created_at": "2025-09-07T14:20:00",
    "updated_at": "2025-09-07T14:20:00"
  }
]
```

---

### GET `/connections/{connection_id}` - Получить подключение

Получает информацию о конкретном подключении по ID.

**Запрос:**

```bash
curl http://localhost:8000/connections/1
```

**Ответ:**

```json
{
  "id": 1,
  "vault_path": "database/postgresql/prod-main",
  "environment": "production",
  "description": "Основная продакшн база данных",
  "tags": ["production", "main", "critical"],
  "created_at": "2025-09-07T15:30:00",
  "updated_at": "2025-09-07T15:30:00"
}
```

**Ошибки:**

- `404` - подключение не найдено

---

### PUT `/connections/{connection_id}` - Обновить подключение

Обновляет метаданные подключения и/или credentials в Vault.

**Запрос (обновление только метаданных):**

```bash
curl -X PUT http://localhost:8000/connections/1 \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Обновленное описание продакшн БД",
    "tags": ["production", "main", "critical", "updated"]
  }'
```

**Запрос (обновление credentials):**

```bash
curl -X PUT http://localhost:8000/connections/1 \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Основная продакшн база данных",
    "host": "new-prod-db.company.com",
    "port": 5432,
    "database": "main_app",
    "username": "app_user",
    "password": "new_secure_password456"
  }'
```

**Поля для обновления:**

- `vault_path` - новый путь в Vault
- `environment` - окружение
- `description` - описание
- `tags` - теги
- `host`, `port`, `database`, `username`, `password` - новые credentials

**Ответ:**

```json
{
  "id": 1,
  "vault_path": "database/postgresql/prod-main",
  "environment": "production",
  "description": "Обновленное описание продакшн БД",
  "tags": ["production", "main", "critical", "updated"],
  "created_at": "2025-09-07T15:30:00",
  "updated_at": "2025-09-07T16:45:00"
}
```

---

### DELETE `/connections/{connection_id}` - Удалить подключение

Удаляет подключение из системы. ⚠️ **Внимание:** также удаляет все связанные задачи и результаты анализа.

**Запрос:**

```bash
curl -X DELETE http://localhost:8000/connections/1
```

**Ответ:** 204 No Content

**Ошибки:**

- `404` - подключение не найдено
- `409` - есть активные задачи, использующие это подключение

---

## 🏷 Фильтрация и поиск

### Поиск по тегам

```bash
# Поиск подключений с тегом "production"
curl "http://localhost:8000/connections/?tags=production"

# Поиск по нескольким тегам
curl "http://localhost:8000/connections/?tags=production,critical"
```

### Фильтрация по окружению

```bash
# Только продакшн подключения
curl "http://localhost:8000/connections/?environment=production"

# Только тестовые
curl "http://localhost:8000/connections/?environment=staging"
```

---

## 🔒 Безопасность и Vault интеграция

### Как работает интеграция с Vault

1. **При создании подключения:**

   - Credentials (`host`, `port`, `database`, `username`, `password`) сохраняются в Vault по указанному пути
   - В базе данных сохраняются только метаданные (`vault_path`, `environment`, `description`, `tags`)

2. **При использовании подключения:**

   - Система получает credentials из Vault по `vault_path`
   - Устанавливает соединение с базой данных

3. **Структура в Vault:**

```json
{
  "host": "prod-db.company.com",
  "port": 5432,
  "database": "main_app",
  "username": "app_user",
  "password": "secure_password123"
}
```

---

## 📋 Примеры использования

### Настройка подключения к тестовой БД

```bash
curl -X POST http://localhost:8000/connections/ \
  -H "Content-Type: application/json" \
  -d '{
    "vault_path": "database/postgresql/test",
    "environment": "development",
    "description": "Локальная база данных для разработки",
    "tags": ["development", "local", "testing"],
    "host": "localhost",
    "port": 5432,
    "database": "test_db",
    "username": "test_user",
    "password": "test_password"
  }'
```

### Настройка подключения к аналитической БД

```bash
curl -X POST http://localhost:8000/connections/ \
  -H "Content-Type: application/json" \
  -d '{
    "vault_path": "database/postgresql/analytics",
    "environment": "production",
    "description": "База данных для аналитики и отчетов",
    "tags": ["production", "analytics", "readonly"],
    "host": "analytics-db.company.com",
    "port": 5432,
    "database": "analytics",
    "username": "analytics_reader",
    "password": "analytics_password"
  }'
```

### Обновление credentials для подключения

```bash
curl -X PUT http://localhost:8000/connections/2 \
  -H "Content-Type: application/json" \
  -d '{
    "password": "new_updated_password123"
  }'
```

### Изменение окружения подключения

```bash
curl -X PUT http://localhost:8000/connections/2 \
  -H "Content-Type: application/json" \
  -d '{
    "environment": "staging",
    "tags": ["staging", "pre-prod", "testing"]
  }'
```

---

## ⚠️ Важные замечания

1. **Безопасность credentials:** Все пароли и чувствительные данные хранятся только в Vault, не в базе данных системы.

2. **Удаление подключений:** При удалении подключения также удаляются все связанные задачи планировщика и результаты анализа.

3. **Vault пути:** Рекомендуется использовать понятную структуру путей, например: `database/postgresql/environment-purpose`.

4. **Теги:** Используйте теги для удобной категоризации и поиска подключений.

5. **Окружения:** Стандартные значения: `development`, `staging`, `production`.
