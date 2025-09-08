# Connections API Documentation

## Overview

API для управления подключениями к базам данных PostgreSQL. Позволяет создавать, просматривать, обновлять и удалять подключения с безопасным хранением учетных данных в HashiCorp Vault.

**🔒 Безопасность:** Все учетные данные (host, port, database, username, password) хранятся только в Vault. В базе данных сохраняются только метаданные подключения.

**Base URL:** `/api/v1/connections`  
**Legacy URL:** `/api/connections` (redirect to v1)

---

## ⚠️ Важные изменения

**С версии 2.0+** изменена архитектура хранения данных:

- **База данных:** хранит только метаданные (name, vault_path, environment, description, tags)
- **Vault:** хранит все учетные данные (host, port, database, username, password)
- **Безопасность:** credentials никогда не сохраняются в основной БД

---

## Endpoints

### 1. Create Connection

**POST** `/api/v1/connections/`

Создать новое подключение к базе данных PostgreSQL.

#### Request Body

```json
{
  "name": "Production DB",
  "vault_path": "secret/database/connections/prod-main",
  "environment": "production",
  "description": "Основная продакшн база данных",
  "tags": ["production", "critical", "main"],
  "is_active": true,

  // Поля для сохранения в Vault (не сохраняются в БД)
  "host": "prod-db.company.com",
  "port": 5432,
  "database": "main_app",
  "username": "app_user",
  "password": "secure_password_123"
}
```

#### Response

```json
{
  "id": 1,
  "name": "Production DB",
  "vault_path": "secret/database/connections/prod-main",
  "environment": "production",
  "description": "Основная продакшн база данных",
  "tags": ["production", "critical", "main"],
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

#### Status Codes

- `201` - Connection created successfully
- `500` - Error creating connection or storing credentials in Vault

#### Notes

- Учетные данные (host, port, database, username, password) автоматически сохраняются в Vault
- В ответе credentials не возвращаются (только vault_path)
- Vault path должен быть уникальным

---

### 2. Get All Connections

**GET** `/connections/`

Получить список всех подключений (только метаданные).

#### Response

```json
[
  {
    "id": 1,
    "name": "Production DB",
    "vault_path": "secret/database/connections/prod-main",
    "environment": "production",
    "description": "Основная продакшн база данных",
    "tags": ["production", "critical", "main"],
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  },
  {
    "id": 2,
    "name": "Staging DB",
    "vault_path": "secret/database/connections/staging",
    "environment": "staging",
    "description": "Тестовая среда",
    "tags": ["staging", "test"],
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

#### Status Codes

- `200` - Success
- `500` - Error retrieving connections

---

### 3. Get Connection by ID

**GET** `/connections/{connection_id}`

Получить подключение по ID (только метаданные).

#### Path Parameters

- `connection_id`: integer - ID подключения

#### Response

```json
{
  "id": 1,
  "name": "Production DB",
  "vault_path": "secret/database/connections/prod-main",
  "environment": "production",
  "description": "Основная продакшн база данных",
  "tags": ["production", "critical", "main"],
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

#### Status Codes

- `200` - Success
- `404` - Connection not found
- `500` - Error retrieving connection

---

### 4. Update Connection

**PUT** `/connections/{connection_id}`

Обновить подключение и/или его учетные данные в Vault.

#### Path Parameters

- `connection_id`: integer - ID подключения

#### Request Body

```json
{
  // Метаданные (сохраняются в БД)
  "name": "Updated Production DB",
  "environment": "production",
  "description": "Обновленное описание",
  "tags": ["production", "critical", "updated"],
  "is_active": true,

  // Учетные данные (обновляются в Vault)
  "host": "new-prod-db.company.com",
  "port": 5433,
  "database": "updated_app",
  "username": "new_app_user",
  "password": "new_secure_password"
}
```

#### Response

```json
{
  "id": 1,
  "name": "Updated Production DB",
  "vault_path": "secret/database/connections/prod-main",
  "environment": "production",
  "description": "Обновленное описание",
  "tags": ["production", "critical", "updated"],
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

#### Status Codes

- `200` - Connection updated successfully
- `404` - Connection not found
- `500` - Error updating connection

#### Notes

- Все поля опциональны - можно обновлять только нужные поля
- При обновлении username или password, учетные данные автоматически обновляются в Vault
- Пароль не возвращается в ответе из соображений безопасности

---

### 5. Delete Connection

**DELETE** `/connections/{connection_id}`

Удалить подключение.

#### Path Parameters

- `connection_id`: integer - ID подключения

#### Response

```json
{
  "message": "Подключение удалено"
}
```

#### Status Codes

- `200` - Connection deleted successfully
- `404` - Connection not found
- `500` - Error deleting connection

#### Notes

- При удалении подключения автоматически удаляются учетные данные из Vault
- Удаление подключения не влияет на связанные задачи (они станут неактивными)

---

## Security Notes

### Vault Integration

- Все пароли автоматически сохраняются в HashiCorp Vault
- Пароли никогда не хранятся в основной базе данных
- Vault путь генерируется автоматически: `database/creds/connection_{name}`
- При удалении подключения учетные данные автоматически удаляются из Vault

### Authentication

- Все endpoints требуют валидной аутентификации
- Операции логируются для аудита

---

## Examples

### Create a New Connection

```bash
curl -X POST "http://localhost:8000/api/v1/connections/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production Database",
    "host": "prod-db.example.com",
    "port": 5432,
    "database": "myapp_prod",
    "username": "app_user",
    "password": "secure_password_123",
    "is_active": true
  }'
```

### Get All Connections

```bash
curl "http://localhost:8000/api/v1/connections/"
```

### Update Connection (Change Only Host)

```bash
curl -X PUT "http://localhost:8000/api/v1/connections/1" \
  -H "Content-Type: application/json" \
  -d '{
    "host": "new-prod-db.example.com"
  }'
```

### Test Connection Before Creating Task

```bash
# 1. Create connection
curl -X POST "http://localhost:8000/api/v1/connections/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Connection",
    "host": "localhost",
    "port": 5432,
    "database": "testdb",
    "username": "testuser",
    "password": "testpass",
    "is_active": true
  }'

# 2. Use connection_id in scheduler task
curl -X POST "http://localhost:8000/api/v1/scheduler/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Task",
    "task_type": "log_analysis",
    "connection_id": 1,
    "cron_schedule": "0 2 * * *"
  }'
```

### Delete Connection

```bash
curl -X DELETE "http://localhost:8000/api/v1/connections/1"
```
