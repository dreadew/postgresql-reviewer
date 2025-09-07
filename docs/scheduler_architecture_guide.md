# Архитектура планировщика задач PostgreSQL Reviewer

## 🏗️ Обзор архитектуры

PostgreSQL Reviewer использует распределенную архитектуру планировщика задач на основе Redis и воркеров для выполнения анализа баз данных.

## 📊 Компоненты системы

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Scheduler     │    │   Redis Queue   │    │   Task Workers  │
│                 │    │                 │    │                 │
│ • Сканирует     │───▶│ • task_queue    │───▶│ • Worker 1      │
│   расписание    │    │ • Приоритеты    │    │ • Worker 2      │
│ • Создает       │    │ • Retry логика  │    │ • Worker N      │
│   задачи        │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       ▼
         │                       │              ┌─────────────────┐
         │                       │              │   PostgreSQL    │
         │                       │              │   Instances     │
         │                       │              │                 │
         │                       │              │ • DB1 (conn_1)  │
         │                       │              │ • DB2 (conn_2)  │
         │                       │              │ • DB3 (conn_3)  │
         │                       │              └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   Database      │    │   Vault         │
│   (Analytics)   │    │   (Credentials) │
│                 │    │                 │
│ • Tasks         │    │ • DB Passwords  │
│ • Executions    │    │ • Connection    │
│ • Results       │    │   Details       │
└─────────────────┘    └─────────────────┘
```

## 🔄 Жизненный цикл задачи

### 1. Создание запланированной задачи

```python
# API: POST /scheduler/tasks
{
  "name": "daily_analysis",
  "task_type": "log_analysis",
  "connection_id": 1,  # Конкретная БД
  "cron_schedule": "0 2 * * *",
  "task_params": {...}
}
```

### 2. Планировщик обрабатывает расписание

```python
# scheduler.py: start_scheduler_loop()
due_tasks = get_due_tasks()  # Задачи готовые к выполнению
for task in due_tasks:
    execution_id = create_task_execution(task)
    queue_item = TaskQueueItem(...)
    redis.lpush("task_queue", queue_item)
```

### 3. Воркер получает и выполняет задачу

```python
# worker.py: start_worker()
task_data = redis.brpop("task_queue")
task = TaskQueueItem.parse(task_data)

# Получение данных подключения из Vault
connection_data = get_connection_data(task.connection_id)

# Выполнение в зависимости от типа
if task.task_type == "log_analysis":
    result = process_log_analysis(connection_data, task.parameters)
elif task.task_type == "custom_sql":
    result = process_custom_sql(connection_data, task.parameters)
```

### 4. Сохранение результата

```python
# Результат сохраняется в analysis_results
save_analysis_result(connection_id, analysis_type, result)
mark_task_completed(execution_id, result)
```

## 🗄️ Структура базы данных

### Таблицы планировщика

```sql
-- Запланированные задачи
CREATE TABLE scheduled_tasks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    task_type VARCHAR(100) NOT NULL,
    connection_id INTEGER REFERENCES connections(id),
    cron_schedule VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    last_run_at TIMESTAMP,
    next_run_at TIMESTAMP,
    task_params JSONB DEFAULT '{}',
    description TEXT
);

-- Выполнения задач
CREATE TABLE task_executions (
    id SERIAL PRIMARY KEY,
    scheduled_task_id INTEGER REFERENCES scheduled_tasks(id),
    task_type VARCHAR(100),
    connection_id INTEGER REFERENCES connections(id),
    status VARCHAR(50) NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    result JSONB DEFAULT '{}',
    error_message TEXT,
    parameters JSONB DEFAULT '{}'
);

-- Результаты анализа
CREATE TABLE analysis_results (
    id SERIAL PRIMARY KEY,
    connection_id INTEGER REFERENCES connections(id),
    analysis_type VARCHAR(50) NOT NULL,
    result JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    execution_id INTEGER REFERENCES task_executions(id)
);
```

## 🔐 Безопасность и подключения

### Управление подключениями

1. **Метаданные подключений** хранятся в таблице `connections`
2. **Пароли и учетные данные** хранятся в HashiCorp Vault
3. **Путь в Vault**: `secret/database/connections/{connection_id}`

### Пример получения подключения

```python
# worker.py: get_connection_data()
async def get_connection_data(connection_id: int):
    # Получаем метаданные из БД
    connection = await db_service.fetch_one(
        "SELECT * FROM connections WHERE id = %s",
        connection_id
    )

    # Получаем credentials из Vault
    vault_path = f"database/connections/{connection_id}"
    credentials = vault_service.get_secret(vault_path)

    return {
        "host": credentials.get("host"),
        "port": credentials.get("port", 5432),
        "database": credentials.get("database"),
        "username": credentials.get("username"),
        "password": credentials.get("password")
    }
```

## ⚡ Redis и очередь задач

### Структура элемента очереди

```python
class TaskQueueItem(BaseModel):
    execution_id: int
    task_type: TaskType
    connection_id: int
    scheduled_task_id: Optional[int]
    parameters: Dict[str, Any] = {}
    priority: int = 0
    retry_count: int = 0
    max_retries: int = 3
```

### Retry логика

```python
# При ошибке выполнения
if task.retry_count < task.max_retries:
    task.retry_count += 1
    await asyncio.sleep(min(task.retry_count * 60, 300))  # Exponential backoff
    await redis_client.lpush("task_queue", task.model_dump_json())
else:
    await mark_task_failed(task.execution_id, error_message)
```

## 🚀 Масштабирование

### Горизонтальное масштабирование воркеров

```yaml
# docker-compose.yml
services:
  worker-1:
    build: .
    command: python -m src.scheduler.worker
    environment:
      - WORKER_ID=worker-1

  worker-2:
    build: .
    command: python -m src.scheduler.worker
    environment:
      - WORKER_ID=worker-2

  worker-3:
    build: .
    command: python -m src.scheduler.worker
    environment:
      - WORKER_ID=worker-3
```

### Настройки производительности

```bash
# .env
SCHEDULER_WORKERS_COUNT=3
REDIS_POOL_SIZE=10
TASK_TIMEOUT=300
MAX_CONCURRENT_TASKS=5
```

## 📊 Мониторинг и логирование

### Метрики системы

- Количество активных воркеров
- Размер очереди задач в Redis
- Время выполнения задач
- Процент успешных/неудачных выполнений

### Логирование

```python
# Каждый этап жизненного цикла логируется
logger.info(f"Задача {task.execution_id} получена воркером {self.worker_id}")
logger.info(f"Подключение к БД {connection_data['host']} установлено")
logger.info(f"Задача {task.execution_id} успешно выполнена за {execution_time}s")
```

## 🛠️ Отладка и troubleshooting

### Проверка состояния системы

```bash
# Состояние Redis очереди
redis-cli LLEN task_queue

# Активные задачи
curl "http://localhost:8000/api/v1/monitoring/tasks/active"

# Логи воркеров
docker-compose logs worker-1

# Статистика выполнения
curl "http://localhost:8000/api/v1/monitoring/tasks/stats"
```

### Типичные проблемы

1. **Воркер не может подключиться к БД**

   - Проверить credentials в Vault
   - Проверить сетевую доступность

2. **Задачи накапливаются в очереди**

   - Увеличить количество воркеров
   - Проверить производительность БД

3. **Задачи падают с timeout**
   - Увеличить `query_timeout` в параметрах
   - Оптимизировать SQL запросы

## 🔄 Диаграмма потока данных

```
1. Cron Schedule → 2. Task Creation → 3. Redis Queue → 4. Worker Execution
        ↓                  ↓              ↓               ↓
   ┌──────────┐   ┌─────────────────┐  ┌─────────┐  ┌──────────────┐
   │ scheduled│   │ task_executions │  │  Redis  │  │ PostgreSQL   │
   │ _tasks   │   │                 │  │  Queue  │  │ Target DB    │
   └──────────┘   └─────────────────┘  └─────────┘  └──────────────┘
                           │                               │
                           ▼                               ▼
                  ┌─────────────────┐              ┌──────────────┐
                  │ analysis_results│              │ SQL Analysis │
                  │                 │              │ AI Processing│
                  └─────────────────┘              └──────────────┘
```

Эта архитектура обеспечивает надежное, масштабируемое и безопасное выполнение задач анализа PostgreSQL с полной трассировкой и мониторингом.
