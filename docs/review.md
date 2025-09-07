# Анализ и ревью API

Выполнение анализа SQL запросов, конфигураций и структуры базы данных с рекомендациями по оптимизации.

## Базовый путь: `/review`

---

## 🔍 Анализ SQL запросов

### POST `/review/` - Анализ одного запроса

Выполняет комплексный анализ SQL запроса с рекомендациями по оптимизации.

**Запрос:**

```bash
curl -X POST http://localhost:8000/review/ \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": 1,
    "sql_query": "SELECT u.name, COUNT(o.id) as order_count FROM users u LEFT JOIN orders o ON u.id = o.user_id WHERE u.created_at > '\''2023-01-01'\'' GROUP BY u.id, u.name ORDER BY order_count DESC LIMIT 100",
    "analysis_type": "performance",
    "include_execution_plan": true,
    "check_security": true
  }'
```

**Параметры запроса:**

- `connection_id` - ID подключения к базе данных
- `sql_query` - SQL запрос для анализа
- `analysis_type` - тип анализа (performance, security, best_practices, all)
- `include_execution_plan` - включить план выполнения
- `check_security` - проверить на уязвимости безопасности

**Ответ:**

```json
{
  "analysis_id": "review_20250907_160000",
  "connection_id": 1,
  "sql_query": "SELECT u.name, COUNT(o.id) as order_count FROM users u LEFT JOIN orders o ON u.id = o.user_id WHERE u.created_at > '2023-01-01' GROUP BY u.id, u.name ORDER BY order_count DESC LIMIT 100",
  "analysis_type": "performance",
  "overall_score": 7.5,
  "severity": "medium",
  "execution_plan": {
    "plan_type": "Limit",
    "cost": {
      "startup_cost": 1234.56,
      "total_cost": 5678.9
    },
    "estimated_rows": 100,
    "estimated_width": 64,
    "actual_time": {
      "startup": 15.234,
      "total": 287.456
    },
    "operations": [
      {
        "operation": "Sort",
        "cost": 4567.89,
        "rows": 1500,
        "sort_key": ["order_count DESC"],
        "sort_method": "quicksort",
        "memory_used": "156kB"
      },
      {
        "operation": "HashAggregate",
        "cost": 3456.78,
        "rows": 1500,
        "group_key": ["u.id", "u.name"]
      },
      {
        "operation": "Hash Left Join",
        "cost": 2345.67,
        "rows": 5000,
        "join_condition": "u.id = o.user_id",
        "hash_buckets": 1024,
        "hash_batches": 1
      }
    ]
  },
  "performance_analysis": {
    "estimated_execution_time_ms": 287,
    "rows_examined": 15000,
    "rows_returned": 100,
    "selectivity": 0.67,
    "join_efficiency": 0.85,
    "index_usage": [
      {
        "table": "users",
        "index": "idx_users_created_at",
        "usage": "range_scan",
        "effectiveness": "good"
      },
      {
        "table": "orders",
        "index": "idx_orders_user_id",
        "usage": "eq_ref",
        "effectiveness": "excellent"
      }
    ],
    "bottlenecks": [
      {
        "type": "sort_operation",
        "description": "Expensive sort operation on large dataset",
        "impact": "medium",
        "cost_percentage": 35.2
      }
    ]
  },
  "security_analysis": {
    "sql_injection_risk": "none",
    "privilege_escalation_risk": "none",
    "data_exposure_risk": "low",
    "issues": [],
    "recommendations": [
      "Query appears safe from SQL injection",
      "Consider limiting data exposure with proper WHERE clauses"
    ]
  },
  "recommendations": [
    {
      "category": "performance",
      "priority": "high",
      "title": "Add composite index",
      "description": "Create composite index on (created_at, id) for better performance",
      "sql_suggestion": "CREATE INDEX idx_users_created_at_id ON users (created_at, id);",
      "estimated_improvement": "40-60% faster execution"
    },
    {
      "category": "query_optimization",
      "priority": "medium",
      "title": "Consider query rewrite",
      "description": "Use window functions instead of GROUP BY for better performance",
      "sql_suggestion": "SELECT u.name, COUNT(o.id) OVER (PARTITION BY u.id) as order_count FROM users u LEFT JOIN orders o ON u.id = o.user_id WHERE u.created_at > '2023-01-01' ORDER BY order_count DESC LIMIT 100",
      "estimated_improvement": "20-30% faster execution"
    },
    {
      "category": "best_practices",
      "priority": "low",
      "title": "Use explicit column list",
      "description": "Specify exact columns instead of implicit GROUP BY",
      "sql_suggestion": "Add all non-aggregate columns to GROUP BY clause explicitly"
    }
  ],
  "statistics": {
    "tables_involved": 2,
    "joins_count": 1,
    "subqueries_count": 0,
    "aggregate_functions": 1,
    "complexity_score": 6.5
  },
  "created_at": "2025-09-07T16:00:00"
}
```

---

### POST `/review/batch` - Пакетный анализ запросов

Анализирует множество SQL запросов за один вызов.

**Запрос:**

```bash
curl -X POST http://localhost:8000/review/batch \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": 1,
    "queries": [
      {
        "id": "query_1",
        "sql": "SELECT * FROM users WHERE email = '\''user@example.com'\''",
        "description": "User lookup by email"
      },
      {
        "id": "query_2",
        "sql": "SELECT COUNT(*) FROM orders WHERE created_at > CURRENT_DATE - INTERVAL '\''30 days'\''",
        "description": "Monthly order count"
      },
      {
        "id": "query_3",
        "sql": "UPDATE users SET last_login = NOW() WHERE id = 12345",
        "description": "Update user last login"
      }
    ],
    "analysis_options": {
      "include_execution_plan": false,
      "check_security": true,
      "analysis_type": "all"
    }
  }'
```

**Ответ:**

```json
{
  "batch_id": "batch_20250907_160000",
  "connection_id": 1,
  "total_queries": 3,
  "completed_queries": 3,
  "failed_queries": 0,
  "overall_score": 6.8,
  "summary": {
    "high_priority_issues": 2,
    "medium_priority_issues": 5,
    "low_priority_issues": 8,
    "security_issues": 1,
    "performance_issues": 6
  },
  "results": [
    {
      "query_id": "query_1",
      "sql": "SELECT * FROM users WHERE email = 'user@example.com'",
      "score": 4.5,
      "severity": "high",
      "issues": [
        {
          "type": "performance",
          "priority": "high",
          "message": "SELECT * can be expensive for tables with many columns",
          "recommendation": "Specify only needed columns"
        },
        {
          "type": "performance",
          "priority": "medium",
          "message": "Missing index on email column",
          "recommendation": "CREATE INDEX idx_users_email ON users (email);"
        }
      ]
    },
    {
      "query_id": "query_2",
      "sql": "SELECT COUNT(*) FROM orders WHERE created_at > CURRENT_DATE - INTERVAL '30 days'",
      "score": 8.5,
      "severity": "low",
      "issues": [
        {
          "type": "best_practices",
          "priority": "low",
          "message": "Consider using more specific time boundaries",
          "recommendation": "Use specific timestamps instead of relative dates for consistency"
        }
      ]
    },
    {
      "query_id": "query_3",
      "sql": "UPDATE users SET last_login = NOW() WHERE id = 12345",
      "score": 7.2,
      "severity": "medium",
      "issues": [
        {
          "type": "security",
          "priority": "medium",
          "message": "Direct ID usage in WHERE clause",
          "recommendation": "Ensure proper authorization before executing this update"
        }
      ]
    }
  ],
  "global_recommendations": [
    {
      "category": "indexing",
      "priority": "high",
      "message": "Several queries would benefit from additional indexes",
      "affected_queries": ["query_1"],
      "sql_suggestions": [
        "CREATE INDEX idx_users_email ON users (email);",
        "CREATE INDEX idx_orders_created_at ON orders (created_at);"
      ]
    }
  ],
  "created_at": "2025-09-07T16:00:00"
}
```

---

## 📊 Типы анализа

### 1. Анализ производительности (`performance`)

- Оценка плана выполнения
- Использование индексов
- Стоимость операций
- Рекомендации по оптимизации

### 2. Анализ безопасности (`security`)

- Поиск SQL injection уязвимостей
- Проверка прав доступа
- Выявление потенциальных угроз
- Рекомендации по безопасности

### 3. Лучшие практики (`best_practices`)

- Соответствие стандартам кодирования
- Читаемость запросов
- Поддерживаемость кода
- Соответствие конвенциям

### 4. Комплексный анализ (`all`)

- Все виды анализа одновременно
- Общая оценка качества
- Приоритизированные рекомендации

---

## 🎯 Специализированные анализы

### Анализ медленных запросов

```bash
curl -X POST http://localhost:8000/review/ \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": 1,
    "sql_query": "SELECT * FROM large_table WHERE complex_condition = true",
    "analysis_type": "performance",
    "include_execution_plan": true,
    "performance_threshold_ms": 1000
  }'
```

### Анализ безопасности запросов

```bash
curl -X POST http://localhost:8000/review/ \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": 1,
    "sql_query": "SELECT user_data FROM sensitive_table WHERE user_id = $1",
    "analysis_type": "security",
    "check_data_exposure": true,
    "check_privilege_escalation": true
  }'
```

### Анализ DDL операций

```bash
curl -X POST http://localhost:8000/review/ \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": 1,
    "sql_query": "CREATE INDEX CONCURRENTLY idx_name ON large_table (column_name)",
    "analysis_type": "best_practices",
    "check_ddl_safety": true
  }'
```

---

## 📈 Интеграция с планировщиком

### Автоматический анализ запросов

```bash
# Создание задачи для регулярного анализа медленных запросов
curl -X POST http://localhost:8000/scheduler/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily Query Review",
    "task_type": "query_analysis",
    "connection_id": 1,
    "cron_schedule": "0 2 * * *",
    "task_params": {
      "analysis_type": "performance",
      "min_duration_ms": 5000,
      "include_execution_plan": true
    }
  }'
```

---

## 💡 Примеры использования

### Код-ревью SQL в CI/CD

```bash
# Анализ SQL миграций перед деплоем
queries_file="migration_queries.json"
curl -X POST http://localhost:8000/review/batch \
  -H "Content-Type: application/json" \
  -d @$queries_file | \
  jq '.results[] | select(.severity == "high") | .issues[]'
```

### Аудит существующих запросов

```bash
# Анализ всех запросов приложения
curl -X POST http://localhost:8000/review/batch \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": 1,
    "queries": [...],
    "analysis_options": {
      "analysis_type": "all",
      "check_security": true
    }
  }' | jq '.global_recommendations'
```

### Оптимизация производительности

```bash
# Поиск проблемных запросов
curl -X POST http://localhost:8000/review/ \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": 1,
    "sql_query": "SELECT * FROM orders o JOIN customers c ON o.customer_id = c.id WHERE o.status = '\''pending'\''",
    "analysis_type": "performance"
  }' | jq '.recommendations[] | select(.priority == "high")'
```

---

## 🔧 Настройка анализа

### Конфигурация уровней серьезности

- **Критичный** (score < 4): Серьезные проблемы производительности или безопасности
- **Высокий** (score 4-6): Значимые проблемы, требующие внимания
- **Средний** (score 6-8): Умеренные проблемы, рекомендуется исправить
- **Низкий** (score 8-10): Незначительные улучшения, опционально

### Настройка правил анализа

Система использует встроенные правила анализа, которые можно настроить через модуль правил (`/rules` API).
