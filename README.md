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

   ```
    GIGACHAT_API_KEY=<gigachat-api-key>

    LANGSMITH_TRACING=true
    LANGSMITH_ENDPOINT=https://api.smith.langchain.com
    LANGSMITH_API_KEY=<langsmith-api-key>
    LANGSMITH_PROJECT=<langsmith-project>

    VECTOR_STORE=faiss
    FAISS_PERSIST_DIR=./data/faiss
    KB_RULES_DIR=./src/kb/rules
    MAX_RULES_TO_RETRIEVE=6
    TOKENIZERS_PARALLELISM=false
   ```

4. Загрузите правила:
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

## CI/CD Интеграция

Для интеграции в CI/CD пайплайн используйте скрипт `ci_cd_review.sh`:

```bash
./examples/ci_cd_review.sh
```

Скрипт:

- Собирает SQL-файлы из коммита
- Отправляет их на ревью через `/review/batch`
- Проверяет общий скор (порог: 70)
- Выходит с кодом 1 при неудаче

Пример использования в GitHub Actions:

```yaml
- name: SQL Review
  run: ./ci_cd_review.sh
  env:
    API_URL: ${{ secrets.API_URL }}
```

## Docker

Соберите и запустите с Docker Compose:

```bash
docker-compose up --build
```

Или запустите напрямую:

```bash
docker build -t postgresql-reviewer .
docker run -p 8000:8000 --env-file .env postgresql-reviewer
```

## Конфигурация

Все чувствительные данные хранятся в `.env`. См. `.env` для необходимых переменных.
