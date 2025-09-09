# PostgreSQL Reviewer

🚀 ИИ-агент для автоматического анализа и ревью PostgreSQL с использованием LangGraph и GigaChat.

PostgreSQL Reviewer - это комплексная система для мониторинга, анализа и оптимизации PostgreSQL баз данных. Система использует искусственный интеллект для автоматического обнаружения проблем производительности, безопасности и предоставляет рекомендации по оптимизации.

### Инструкция по запуску

1. Склонировать данный репозиторий
2. В корневой папке проекта создать файл `.env`, заполнить переменные в соответствие с `.env.example`
3. Запустить сервисы через `docker compose up -d` (Документация будет доступна по адресу http://localhost:8000/api/v1/docs)
4. Склонировать проект с фронтендом `https://github.com/dreadew/postgresql-reviewer-frontend`
5. Создать и заполнить файл `.env` в проекте с фронтендом в соответствии с файлом `.env.example` из репозитория с фронтендом
6. Запустить фронтенд командой `docker compose up -d` (Фронтенд запускается на порту 80 и будет доступен по адресу http://localhost)

### Добавление правил для ревью

Правила выбираются через косинусовое сходство векторов с помощью FAISS, выбирается top-k правил, параметром k можно управлять в файле `.env` - `MAX_RULES_TO_RETRIEVE`

Через создание файлов в проекте:

1. Создаем md файл в нужной папке `src/kb/rules/` в соответствии с шаблонами других файлов
2. При необходимости пересобираем индекс FAISS через эндпоинт `/api/v1/rules/ingest`

Через фронтенд:

1. Переходим на страницу `http://localhost:3000/rules`
2. Нажимаем на кнопку "Создать правило"
3. Заполняем необходимые поля и сохраняем правило
4. Обязательно пересобираем индекс FAISS через эндпоинт `/api/v1/rules/ingest`

## ✨ Основные возможности

- 🔍 **Автоматический анализ SQL запросов** - обнаружение медленных запросов и рекомендации по оптимизации
- ⚙️ **Анализ конфигурации PostgreSQL** - проверка настроек сервера и best practices
- 📊 **Мониторинг логов** - анализ ошибок, предупреждений и подозрительной активности
- 📅 **Планировщик задач** - автоматическое выполнение анализа по расписанию
- 🔒 **Безопасное хранение учетных данных** - интеграция с HashiCorp Vault
- 📈 **RESTful API** - полный набор API для интеграции с другими системами
- 🎯 **Кастомные правила анализа** - возможность создания собственных правил проверки

## 🏗️ Архитектура проекта

```
src/
├── api/                    # API слой
│   ├── main.py            # Основное приложение FastAPI
│   ├── dependencies.py    # Зависимости для DI
│   ├── schemas/           # Pydantic схемы запросов/ответов
│   └── routes/            # API роуты по доменам
│       ├── scheduler.py   # Планировщик задач
│       ├── connections.py # Управление подключениями
│       ├── monitoring.py  # Мониторинг системы
│       ├── config.py      # Анализ конфигурации
│       ├── logs.py        # Анализ логов
│       ├── review.py      # Ревью SQL запросов
│       ├── tasks.py       # Управление задачами
│       └── rules.py       # Управление правилами
├── core/                  # Бизнес-логика
│   ├── agents/            # ИИ агенты
│   │   ├── base.py        # Базовые классы агентов
│   │   ├── gigachat_agent.py  # Основной агент
│   │   └── prompt_templates.py # Шаблоны промптов
│   ├── workflows/         # Рабочие процессы LangGraph
│   ├── types/             # TypeScript-подобные типы
│   ├── constants.py       # Константы приложения
│   ├── scoring.py         # Логика подсчета оценок
│   ├── config.py          # Конфигурация приложения
│   └── utils/             # Утилиты
├── services/              # Сервисный слой
│   ├── database_service.py    # Работа с БД
│   ├── vault_service.py       # Интеграция с Vault
│   ├── review_service.py      # Сервис анализа
│   └── scheduler_service.py   # Сервис планировщика
├── scheduler/             # Планировщик задач
│   ├── main.py           # Основной процесс планировщика
│   ├── scheduler.py      # Логика планировщика
│   ├── worker.py         # Воркеры для выполнения задач
│   └── models.py         # Модели данных планировщика
├── store/                 # Слой хранения данных
│   ├── base.py           # Базовые классы хранилищ
│   ├── factory.py        # Фабрика хранилищ
│   └── faiss.py          # FAISS векторное хранилище
└── kb/                    # База знаний и правила
    ├── ingest.py         # Загрузка правил
    └── rules/            # Правила анализа
        ├── config/       # Правила для конфигурации
        └── sql/          # Правила для SQL
```

## 🚀 Быстрый старт

### 1. Клонирование и установка

```bash
git clone <repository-url>
cd postgresql-reviewer

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка окружения

```bash
# Копирование примера конфигурации
cp .env.example .env

# Редактирование конфигурации
nano .env  # или ваш любимый редактор
```

### 3. Обязательные настройки в .env

```bash
# Основная база данных для приложения
DATABASE_URL=postgresql://analyzer:analyzer_password@localhost:5432/analyzer_db

# HashiCorp Vault (для безопасного хранения паролей БД)
VAULT_ADDR=http://localhost:8200
VAULT_TOKEN=your_vault_token_here

# Redis (для очереди задач)
REDIS_URL=redis://localhost:6379

# GigaChat API (для ИИ анализа)
GIGACHAT_API_KEY=your_gigachat_api_key_here
```

### 4. Настройка инфраструктуры

```bash
# Запуск инфраструктуры через Docker
docker-compose up -d postgres redis vault

# Настройка учетных данных БД в Vault
chmod +x scripts/setup_vault_db_credentials.sh
./scripts/setup_vault_db_credentials.sh
```

### 5. Инициализация базы данных

```bash
# Применение миграций
python -m alembic upgrade head

# Или через Docker
docker-compose exec app python -m alembic upgrade head
```

### 6. Запуск приложения

```bash
# Запуск через Docker Compose (рекомендуется)
docker-compose up

# Или локально
python -m src.api.main
python -m src.scheduler.main  # В отдельном терминале
```

## 📖 Документация API

Подробная документация по всем эндпоинтам доступна в папке `docs/endpoints/`:

- [Scheduler API](docs/endpoints/scheduler.md) - Планировщик задач
- [Connections API](docs/endpoints/connections.md) - Управление подключениями к БД
- [Monitoring API](docs/endpoints/monitoring.md) - Мониторинг системы
- [Config API](docs/endpoints/config.md) - Анализ конфигурации PostgreSQL
- [Logs API](docs/endpoints/logs.md) - Анализ логов
- [Review API](docs/endpoints/review.md) - Ревью SQL запросов
- [Tasks API](docs/endpoints/tasks.md) - Управление задачами
- [Rules API](docs/endpoints/rules.md) - Управление правилами анализа

### 📋 Руководства

- [Типы задач и примеры использования](docs/task_types_guide.md) - Полное руководство по всем типам задач планировщика
- [Архитектура планировщика](docs/guides/scheduler_architecture_guide.md) - Техническая документация по архитектуре системы
- [Создание и управление задачами](docs/guides/task_creation_guide.md) - Подробное руководство по работе с задачами
- [Практические примеры](docs/guides/practical_examples.md) - Готовые примеры для реальных сценариев

### Swagger UI

После запуска приложения, интерактивная документация доступна по адресу:

- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## 🔧 Конфигурация

Полный пример конфигурации находится в файле `.env.example`. Основные группы настроек:

### 🔑 Обязательные настройки

```bash
# База данных приложения
DATABASE_URL=postgresql://analyzer:analyzer_password@localhost:5432/analyzer_db

# HashiCorp Vault
VAULT_ADDR=http://localhost:8200
VAULT_TOKEN=your_vault_token_here

# Redis для очереди задач
REDIS_URL=redis://localhost:6379

# GigaChat API
GIGACHAT_API_KEY=your_gigachat_api_key_here
```

### ⚙️ Настройки планировщика

```bash
# Настройки Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
SCHEDULER_ENABLED=true
SCHEDULER_TIMEZONE=Europe/Moscow
```

### 🔍 Настройки векторного поиска

```bash
VECTOR_STORE=faiss
FAISS_PERSIST_DIR=./data/faiss
EMBEDDINGS_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=1500
CHUNK_OVERLAP=200
MAX_RULES_TO_RETRIEVE=6
```

### 📊 Настройки мониторинга

```bash
LOG_LEVEL=INFO
LOG_FILE=./logs/postgresql-reviewer.log
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

## 🔒 Безопасность

### Настройка HashiCorp Vault

Для безопасного хранения паролей баз данных используется HashiCorp Vault:

```bash
# Запуск Vault в dev режиме
docker run --cap-add=IPC_LOCK -d --name=dev-vault -p 8200:8200 vault:latest

# Настройка через скрипт
./scripts/setup_vault_db_credentials.sh
```

### Хранение учетных данных

Пароли баз данных хранятся в Vault по пути `secret/databases/{connection_name}`:

```bash
# Пример записи в Vault
vault kv put secret/databases/production \
  host=prod-db.example.com \
  port=5432 \
  dbname=production_db \
  username=analyzer \
  password=secure_password
```

## 🚦 Использование

### Добавление подключения к БД

```bash
curl -X POST "http://localhost:8000/api/v1/connections" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "production",
    "host": "prod-db.example.com",
    "port": 5432,
    "database": "production_db",
    "description": "Production database",
    "tags": ["production", "critical"]
  }'
```

### Создание задачи анализа

```bash
curl -X POST "http://localhost:8000/api/v1/scheduler/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "daily_analysis",
    "task_type": "sql_review",
    "connection_name": "production",
    "schedule": "0 2 * * *",
    "parameters": {
      "analyze_slow_queries": true,
      "check_configuration": true
    }
  }'
```

## 🎯 Примеры интеграции

### CI/CD Pipeline

```bash
#!/bin/bash
# Пример интеграции в CI/CD pipeline
set -e

echo "🔍 Анализ SQL запросов в коммите..."

# Получение измененных SQL файлов
SQL_FILES=$(git diff --name-only HEAD~1 HEAD | grep -E '\.(sql)$' || true)

if [ -z "$SQL_FILES" ]; then
    echo "✅ SQL файлы не изменялись"
    exit 0
fi

# Анализ каждого файла
for file in $SQL_FILES; do
    echo "Анализ файла: $file"

    curl -X POST "http://postgresql-reviewer:8000/api/v1/review/analyze" \
        -H "Content-Type: application/json" \
        -d "{
            \"sql\": \"$(cat $file | sed 's/"/\\"/g')\",
            \"connection_name\": \"staging\"
        }" \
        --fail || exit 1
done

echo "✅ Все SQL запросы прошли проверку"
```

### Мониторинг интеграция

```python
# Пример интеграции с системой мониторинга
import requests
import time

def check_database_health():
    """Проверка здоровья всех подключений"""
    response = requests.get("http://localhost:8000/api/v1/monitoring/connections/health")

    for connection in response.json():
        if connection["status"] != "healthy":
            send_alert(f"Database {connection['name']} is unhealthy")

def get_task_metrics():
    """Получение метрик выполнения задач"""
    response = requests.get("http://localhost:8000/api/v1/monitoring/tasks/stats")
    metrics = response.json()

    # Отправка метрик в систему мониторинга
    send_metrics("postgresql_reviewer.tasks.total", metrics["total"])
    send_metrics("postgresql_reviewer.tasks.failed", metrics["failed"])
    send_metrics("postgresql_reviewer.tasks.success_rate", metrics["success_rate"])

# Запуск проверок каждые 5 минут
while True:
    check_database_health()
    get_task_metrics()
    time.sleep(300)
```

## 🛠️ Разработка

### Структура проекта

```
migrations/                 # Миграции базы данных
├── V001__initial_schema.sql
├── V002__add_task_history.sql
└── V003__add_scheduler_tables.sql

scripts/                    # Утилиты и скрипты
├── setup_vault_db_credentials.sh
└── ...

data/                       # Данные приложения
├── faiss/                  # FAISS векторная база
└── ...

docs/                       # Документация
├── endpoints/              # API документация
└── TASK_CREATION_GUIDE.md

examples/                   # Примеры использования
├── ci_cd_review.sh
└── test.py
```

### Добавление новых правил анализа

1. Создайте файл правила в `src/kb/rules/sql/` или `src/kb/rules/config/`
2. Определите правило в формате:

````markdown
# Название правила

## Описание

Подробное описание того, что проверяет правило.

## Проблема

Какую проблему решает это правило.

## Рекомендация

Как исправить найденную проблему.

## Пример

```sql
-- Плохо
SELECT * FROM large_table WHERE status = 'active';

-- Хорошо
SELECT id, name, created_at FROM large_table
WHERE status = 'active' AND created_at > NOW() - INTERVAL '1 day';
```
````

````

3. Перезагрузите правила:

```bash
curl -X POST "http://localhost:8000/api/v1/rules/reload"
````

### Запуск тестов

```bash
# Установка зависимостей для разработки
pip install -e ".[dev]"

# Запуск тестов
pytest tests/

# Запуск с покрытием
pytest --cov=src tests/

# Линтинг
black src/
isort src/
flake8 src/
```

### Локальная разработка

```bash
# Запуск только инфраструктуры
docker-compose up -d postgres redis vault

# Запуск приложения локально
python -m src.api.main

# Запуск планировщика
python -m src.scheduler.main
```

## 🔍 Troubleshooting

### Частые проблемы

1. **Ошибка подключения к Vault**

   ```bash
   # Проверьте статус Vault
   docker-compose logs vault

   # Убедитесь что Vault unsealed
   export VAULT_ADDR=http://localhost:8200
   vault status
   ```

2. **Redis недоступен**

   ```bash
   # Проверьте Redis
   docker-compose logs redis
   redis-cli ping
   ```

3. **Ошибки миграций**

   ```bash
   # Проверьте текущую версию
   python -m alembic current

   # Откат миграции
   python -m alembic downgrade -1
   ```

4. **Проблемы с FAISS индексом**
   ```bash
   # Пересоздание индекса
   rm -rf data/faiss/*
   python -c "from src.kb.ingest import ingest_rules; ingest_rules('./src/kb/rules')"
   ```

### Логи

```bash
# Просмотр логов приложения
tail -f logs/postgresql-reviewer.log

# Просмотр логов через Docker
docker-compose logs -f app

# Логи планировщика
docker-compose logs -f scheduler
```

### Мониторинг производительности

```bash
# Статистика задач
curl http://localhost:8000/api/v1/monitoring/tasks/stats

# Здоровье подключений
curl http://localhost:8000/api/v1/monitoring/connections/health

# Системные метрики
curl http://localhost:8000/api/v1/monitoring/system/health
```

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

## 🆘 Поддержка

- 📧 Email: support@postgresql-reviewer.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/postgresql-reviewer/issues)
- 📖 Wiki: [GitHub Wiki](https://github.com/your-org/postgresql-reviewer/wiki)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-org/postgresql-reviewer/discussions)

---

Сделано с ❤️ для сообщества PostgreSQL
"environment": "production"
})
print(config_response.json())

# Пакетное ревью

batch_response = requests.post("http://localhost:8000/review/batch", json={
"queries": [
{
"sql": "SELECT \* FROM orders WHERE customer_id = 123",
"query_plan": "EXPLAIN output",
"tables": [{"name": "orders", "columns": [{"name": "customer_id", "type": "int"}]}],
"server_info": {"version": "15.0"}
}
],
"environment": "test"
})
print(batch_response.json())

````

## Тестирование

Запустите тесты:

```bash
pytest tests/
````

Или с покрытием:

```bash
pytest tests/ --cov=src --cov-report=html
```

### Структура тестов

```
tests/
├── conftest.py          # Общие фикстуры
├── test_api.py          # Тесты API эндпоинтов
└── test_schemas.py      # Тесты Pydantic схем
```

## Безопасность

Проект использует следующие меры безопасности:

- **Rate Limiting**: Ограничение количества запросов (настраивается через `RATE_LIMIT_REQUESTS` и `RATE_LIMIT_WINDOW`)
- **Валидация входных данных**: Все входные данные валидируются с помощью Pydantic
- **Валидация Cron выражений**: Проверка корректности cron выражений в задачах
- **Логирование**: Все действия логируются в файл с ротацией
- **Хранение секретов**: Чувствительные данные хранятся в HashiCorp Vault

## 🚀 Быстрый запуск

```bash
# 1. Клонировать репозиторий
git clone <repository-url>
cd postgresql-reviewer

# 2. Запустить setup
./setup.sh

# 3. Отредактировать .env файл с реальными ключами API

# 4. Запустить приложение
uvicorn src.api.main:app --reload
```

## 📊 Production развертывание

### Docker Compose (рекомендуется)

```bash
docker-compose up --build -d
```

### Ручное развертывание

```bash
# Установка зависимостей
pip install -e .

# Запуск с Gunicorn (production)
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Конфигурация

Все чувствительные данные хранятся в `.env`. См. `.env` для необходимых переменных.
