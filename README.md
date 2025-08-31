# PostgreSQL Reviewer

ИИ-агент для ревью SQL-запросов PostgreSQL с использованием LangGraph и GigaChat.

## Архитектура проекта

Проект следует принципам чистой архитектуры и разделен на следующие слои:

```
src/
├── api/                    # API слой
│   ├── main.py            # Основное приложение FastAPI
│   ├── dependencies.py    # Зависимости для DI
│   ├── schemas/           # Pydantic схемы запросов/ответов
│   └── routes/            # API роуты по доменам
├── core/                  # Бизнес-логика
│   ├── agents/            # ИИ агенты
│   │   ├── base.py        # Базовые классы агентов
│   │   ├── gigachat_agent.py  # Основной агент
│   │   └── prompt_templates.py # Шаблоны промптов
│   ├── workflows/         # Рабочие процессы LangGraph
│   ├── types/             # TypeScript-подобные типы
│   ├── constants.py       # Константы приложения
│   ├── scoring.py         # Логика подсчета оценок
│   └── utils/             # Утилиты
├── services/              # Сервисный слой
├── store/                 # Слой хранения данных
└── kb/                    # База знаний и правила
```

## Установка

1. Клонируйте репозиторий:

   ```bash
   git clone <repository-url>
   cd postgresql-reviewer
   ```

2. Установите зависимости:

   ```bash
   pip install .
   ```

3. Настройте переменные окружения в `.env`:

   ```bash
   # GigaChat Configuration
   GIGACHAT_API_KEY=<gigachat-api-key>
   GIGACHAT_MODEL_NAME=GigaChat

   # LangSmith Configuration (опционально)
   LANGSMITH_TRACING=true
   LANGSMITH_ENDPOINT=https://api.smith.langchain.com
   LANGSMITH_API_KEY=<langsmith-api-key>
   LANGSMITH_PROJECT=postgresql-reviewer

   # Database Configuration
   DATABASE_URL=postgresql://analyzer:analyzer_password@localhost:5432/analyzer_db

   # Vault Configuration
   VAULT_ADDR=http://localhost:8200
   VAULT_TOKEN=<vault-token>

   # Redis Configuration
   REDIS_URL=redis://localhost:6379

   # Vector Store Configuration
   VECTOR_STORE=faiss
   FAISS_PERSIST_DIR=./data/faiss
   KB_RULES_DIR=./src/kb/rules
   EMBEDDINGS_MODEL=all-MiniLM-L6-v2
   TOKENIZERS_PARALLELISM=false
   CHUNK_SIZE=1500
   CHUNK_OVERLAP=200
   MAX_RULES_TO_RETRIEVE=6

   # Application Settings
   DEBUG=false
   LOG_LEVEL=INFO
   LOG_FILE=./logs/postgresql-reviewer.log

   # Rate Limiting
   RATE_LIMIT_REQUESTS=100
   RATE_LIMIT_WINDOW=60

   # File Paths
   STATIC_DIR=./src/api/static
   LOGS_DIR=./logs
   ```

4. Создайте необходимые директории:

   ```bash
   mkdir -p logs data/faiss
   ```

5. Загрузите правила:

   ```bash
   python -c "from src.kb.ingest import ingest_rules; ingest_rules('./src/kb/rules')"
   ```

## Использование

### API

Запустите сервер:

```bash
uvicorn src.api.main:app --reload
```

Эндпоинты:

- `POST /review`: Ревью SQL-запроса.

  - Тело: `{"sql": "SELECT * FROM table", "query_plan": "...", "tables": [...], "server_info": {...}, "environment": "test|production"}`
  - Возвращает: `{"issues": [...], "overall_score": 85.5, "thread_id": "..."}`

- `POST /config/analyze`: Анализ конфигурации PostgreSQL с использованием LLM.

  - Тело: `{"config": {"shared_buffers": "128MB", ...}, "environment": "test|production"}`
  - Возвращает: `{"issues": [...], "overall_score": 75.0}`

- `POST /review/batch`: Пакетное ревью нескольких SQL-запросов (для CI/CD).

  - Тело: `{"queries": [{"sql": "...", ...}], "environment": "test|production"}`
  - Возвращает: `{"results": [...], "overall_score": 80.0, "passed": true}`

- `POST /ingest`: Загрузка правил из директории.
  - Тело: `{"rules_dir": "./src/kb/rules"}`

### Пример

```python
import requests

# Одиночное ревью
response = requests.post("http://localhost:8000/review", json={
    "sql": "SELECT * FROM orders WHERE customer_id = 123",
    "query_plan": "EXPLAIN output",
    "tables": [{"name": "orders", "columns": [{"name": "customer_id", "type": "int"}]}],
    "server_info": {"version": "15.0"},
    "environment": "production"
})
print(response.json())

# Анализ конфигурации
config_response = requests.post("http://localhost:8000/config/analyze", json={
    "config": {
        "shared_buffers": "128MB",
        "work_mem": "4MB",
        "maintenance_work_mem": "64MB"
    },
    "environment": "production"
})
print(config_response.json())

# Пакетное ревью
batch_response = requests.post("http://localhost:8000/review/batch", json={
    "queries": [
        {
            "sql": "SELECT * FROM orders WHERE customer_id = 123",
            "query_plan": "EXPLAIN output",
            "tables": [{"name": "orders", "columns": [{"name": "customer_id", "type": "int"}]}],
            "server_info": {"version": "15.0"}
        }
    ],
    "environment": "test"
})
print(batch_response.json())
```

## Тестирование

Запустите тесты:

```bash
pytest tests/
```

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
