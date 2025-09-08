# Review API Documentation

## Overview

API для анализа и проверки SQL запросов PostgreSQL. Позволяет анализировать отдельные запросы или пакеты запросов на предмет производительности, безопасности и соответствия best practices.

**Base URL:** `/api/v1/review`  
**Legacy URL:** `/api/review` (redirect to v1)

---

## Endpoints

### 1. Review Single SQL Query

**POST** `/review/`

Анализ одиночного SQL запроса.

#### Request Body

```json
{
  "sql": "SELECT u.id, u.name, COUNT(o.id) as order_count FROM users u LEFT JOIN orders o ON u.id = o.user_id WHERE u.created_at > '2024-01-01' GROUP BY u.id, u.name ORDER BY order_count DESC",
  "query_plan": {
    "Plan": {
      "Node Type": "Sort",
      "Sort Key": ["order_count"],
      "Total Cost": 1234.56,
      "Plans": [
        {
          "Node Type": "HashAggregate",
          "Group Key": ["u.id", "u.name"]
        }
      ]
    }
  },
  "tables": [
    {
      "name": "users",
      "schema": "public",
      "row_count": 100000,
      "indexes": ["users_pkey", "idx_users_created_at"]
    },
    {
      "name": "orders",
      "schema": "public",
      "row_count": 500000,
      "indexes": ["orders_pkey", "idx_orders_user_id"]
    }
  ],
  "server_info": {
    "version": "15.4",
    "host": "prod-db.example.com",
    "database": "myapp"
  },
  "thread_id": "thread_123",
  "environment": "production"
}
```

#### Response

```json
{
  "overall_score": 85,
  "environment": "production",
  "thread_id": "thread_123",
  "timestamp": "2024-01-01T12:00:00",
  "analysis_results": [
    {
      "category": "Performance",
      "severity": "medium",
      "score": 75,
      "title": "Index Usage",
      "description": "Query uses indexes effectively for most operations",
      "details": "The query leverages idx_users_created_at for filtering and idx_orders_user_id for joins",
      "recommendation": "Consider adding composite index on (user_id, created_at) for better performance",
      "sql_suggestion": "CREATE INDEX idx_orders_user_created ON orders(user_id, created_at);",
      "impact": "medium"
    },
    {
      "category": "Security",
      "severity": "low",
      "score": 95,
      "title": "SQL Injection Risk",
      "description": "No SQL injection vulnerabilities detected",
      "details": "Query uses proper parameterized approach",
      "recommendation": "Continue using parameterized queries",
      "impact": "low"
    },
    {
      "category": "Best Practices",
      "severity": "low",
      "score": 90,
      "title": "Query Structure",
      "description": "Well-structured query following PostgreSQL best practices",
      "details": "Proper use of LEFT JOIN and GROUP BY clauses",
      "recommendation": "Consider adding LIMIT clause for large result sets",
      "impact": "low"
    }
  ],
  "query_plan_analysis": {
    "execution_time_estimate": "~500ms",
    "cost_estimate": 1234.56,
    "operations": [
      {
        "operation": "Sort",
        "cost": 200.45,
        "rows": 1000,
        "optimization": "Consider using index for sorting"
      },
      {
        "operation": "HashAggregate",
        "cost": 800.12,
        "rows": 1000,
        "optimization": "Aggregation is efficient"
      }
    ],
    "bottlenecks": [
      {
        "operation": "Sort",
        "issue": "Expensive sort operation",
        "suggestion": "Add index on order_count or use different ordering"
      }
    ]
  },
  "recommendations": [
    {
      "priority": "medium",
      "category": "Performance",
      "title": "Add Composite Index",
      "description": "Create composite index to improve query performance",
      "sql": "CREATE INDEX idx_orders_user_created ON orders(user_id, created_at);"
    },
    {
      "priority": "low",
      "category": "Best Practices",
      "title": "Add Result Limit",
      "description": "Consider adding LIMIT clause for pagination",
      "sql": "-- Add at the end: LIMIT 100 OFFSET 0"
    }
  ],
  "metadata": {
    "analysis_duration_ms": 150,
    "rules_applied": 15,
    "confidence": "high"
  }
}
```

#### Status Codes

- `200` - Analysis completed successfully
- `400` - Invalid SQL or request data
- `500` - Internal server error

---

### 2. Review Multiple SQL Queries (Batch)

**POST** `/review/batch`

Анализ нескольких SQL запросов в пакетном режиме.

#### Request Body

```json
{
  "queries": [
    {
      "sql": "SELECT * FROM users WHERE id = 1",
      "query_plan": null,
      "tables": [
        {
          "name": "users",
          "schema": "public",
          "row_count": 100000
        }
      ],
      "server_info": {
        "version": "15.4",
        "host": "prod-db.example.com"
      },
      "thread_id": "batch_query_1"
    },
    {
      "sql": "UPDATE users SET last_login = NOW() WHERE id = 1",
      "query_plan": null,
      "tables": [
        {
          "name": "users",
          "schema": "public",
          "row_count": 100000
        }
      ],
      "server_info": {
        "version": "15.4",
        "host": "prod-db.example.com"
      },
      "thread_id": "batch_query_2"
    }
  ],
  "environment": "production"
}
```

#### Response

```json
{
  "results": [
    {
      "overall_score": 90,
      "environment": "production",
      "thread_id": "batch_query_1",
      "timestamp": "2024-01-01T12:00:00",
      "analysis_results": [
        {
          "category": "Performance",
          "severity": "low",
          "score": 95,
          "title": "Primary Key Lookup",
          "description": "Efficient primary key lookup",
          "recommendation": "Query is well optimized"
        }
      ],
      "recommendations": []
    },
    {
      "overall_score": 85,
      "environment": "production",
      "thread_id": "batch_query_2",
      "timestamp": "2024-01-01T12:00:01",
      "analysis_results": [
        {
          "category": "Performance",
          "severity": "medium",
          "score": 80,
          "title": "Index Usage",
          "description": "UPDATE uses primary key efficiently",
          "recommendation": "Consider adding WHERE clause validation"
        }
      ],
      "recommendations": [
        {
          "priority": "low",
          "category": "Security",
          "title": "Add Input Validation",
          "description": "Ensure proper input validation for user ID"
        }
      ]
    }
  ],
  "overall_score": 87.5,
  "passed": true,
  "summary": {
    "total_queries": 2,
    "passed_queries": 2,
    "failed_queries": 0,
    "average_score": 87.5,
    "issues_found": {
      "critical": 0,
      "high": 0,
      "medium": 1,
      "low": 2
    }
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

#### Status Codes

- `200` - Batch analysis completed successfully
- `400` - Invalid request data
- `500` - Internal server error

---

## Analysis Categories

### Performance Analysis

Анализ производительности запросов:

#### Index Usage

- Проверка использования индексов
- Анализ планов выполнения
- Рекомендации по созданию индексов

#### Query Optimization

- Структура запросов
- Эффективность JOIN'ов
- Оптимизация подзапросов

#### Resource Usage

- Оценка потребления памяти
- Анализ I/O операций
- CPU утилизация

### Security Analysis

Проверка безопасности:

#### SQL Injection Detection

- Поиск потенциальных SQL инъекций
- Анализ динамических запросов
- Проверка параметризации

#### Permission Validation

- Проверка прав доступа
- Анализ операций с данными
- Валидация схем доступа

#### Data Exposure

- Поиск потенциальных утечек данных
- Анализ SELECT \* запросов
- Проверка фильтрации данных

### Best Practices

Соответствие best practices:

#### Query Structure

- Стиль написания запросов
- Использование алиасов
- Читаемость кода

#### PostgreSQL Specific

- Использование PostgreSQL функций
- Специфичные оптимизации
- Версионная совместимость

---

## Scoring System

### Score Ranges

- **90-100**: Отличный запрос, оптимизации не требуются
- **70-89**: Хороший запрос, незначительные улучшения
- **50-69**: Средний запрос, рекомендуются оптимизации
- **30-49**: Плохой запрос, требуются значительные изменения
- **0-29**: Критические проблемы, запрос нуждается в переработке

### Severity Levels

- **Critical**: Критические проблемы безопасности или производительности
- **High**: Серьезные проблемы, требующие внимания
- **Medium**: Умеренные проблемы, рекомендуется исправление
- **Low**: Незначительные улучшения

---

## Examples

### Analyze Simple SELECT Query

```bash
curl -X POST "http://localhost:8000/review/" \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "SELECT id, name FROM users WHERE email = $1",
    "tables": [
      {
        "name": "users",
        "schema": "public",
        "row_count": 50000,
        "indexes": ["users_pkey", "idx_users_email"]
      }
    ],
    "server_info": {
      "version": "15.4",
      "database": "myapp"
    },
    "environment": "production"
  }'
```

### Analyze Complex JOIN Query

```bash
curl -X POST "http://localhost:8000/review/" \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "SELECT u.name, COUNT(o.id) FROM users u LEFT JOIN orders o ON u.id = o.user_id WHERE u.created_at > $1 GROUP BY u.id, u.name HAVING COUNT(o.id) > 5",
    "query_plan": {
      "Plan": {
        "Node Type": "HashAggregate",
        "Total Cost": 5000.00
      }
    },
    "tables": [
      {
        "name": "users",
        "schema": "public",
        "row_count": 100000
      },
      {
        "name": "orders",
        "schema": "public",
        "row_count": 500000
      }
    ],
    "environment": "production"
  }'
```

### Batch Analysis for Migration

```bash
curl -X POST "http://localhost:8000/review/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "queries": [
      {
        "sql": "CREATE INDEX CONCURRENTLY idx_users_email ON users(email)",
        "tables": [{"name": "users", "row_count": 100000}]
      },
      {
        "sql": "ALTER TABLE orders ADD COLUMN status VARCHAR(20) DEFAULT '\''pending'\''",
        "tables": [{"name": "orders", "row_count": 500000}]
      }
    ],
    "environment": "production"
  }'
```

---

## Integration Examples

### CI/CD Integration

```bash
#!/bin/bash
# Проверка SQL миграций в CI/CD

MIGRATION_FILES=$(find migrations/ -name "*.sql" -newer last_check.timestamp)

for file in $MIGRATION_FILES; do
  SQL_CONTENT=$(cat "$file")

  RESPONSE=$(curl -s -X POST "http://localhost:8000/review/" \
    -H "Content-Type: application/json" \
    -d "{
      \"sql\": \"$SQL_CONTENT\",
      \"environment\": \"production\"
    }")

  SCORE=$(echo "$RESPONSE" | jq '.overall_score')

  if [ "$SCORE" -lt 70 ]; then
    echo "FAILED: Migration $file has low score: $SCORE"
    exit 1
  fi
done

echo "All migrations passed review"
```

### Development Environment Integration

```python
# Python integration example
import requests

def review_query(sql, environment="development"):
    response = requests.post(
        "http://localhost:8000/review/",
        json={
            "sql": sql,
            "environment": environment,
            "server_info": {"version": "15.4"}
        }
    )

    result = response.json()

    if result["overall_score"] < 70:
        print(f"Query needs optimization (Score: {result['overall_score']})")
        for rec in result.get("recommendations", []):
            print(f"- {rec['title']}: {rec['description']}")

    return result

# Usage
query = "SELECT * FROM users WHERE email LIKE '%gmail%'"
review_result = review_query(query)
```
