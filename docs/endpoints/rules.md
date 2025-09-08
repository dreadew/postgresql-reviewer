# Rules API Documentation

## Overview

API для управления правилами анализа PostgreSQL. Позволяет создавать, изменять и управлять правилами для проверки SQL запросов и конфигурации баз данных.

**Base URL:** `/rules`

---

## Endpoints

### 1. Ingest Rules

**POST** `/rules/ingest`

Загрузить правила из указанной директории в базу знаний.

#### Request Body

```json
{
  "rules_dir": "/path/to/rules/directory"
}
```

#### Response

```json
{
  "message": "Rules ingested successfully"
}
```

#### Status Codes

- `200` - Rules ingested successfully
- `500` - Error ingesting rules

#### Notes

- Загружает все Markdown файлы из указанной директории
- Обновляет векторную базу знаний для поиска
- Поддерживает структуру папок по категориям

---

### 2. Get All Rules

**GET** `/rules/`

Получить список всех правил или правил определенной категории.

#### Query Parameters

- `category` (optional): string - фильтр по категории (`config` или `sql`)

#### Response

```json
[
  {
    "filename": "slow_queries.md",
    "title": "Optimization Rules for Slow Queries",
    "category": "sql",
    "content": null
  },
  {
    "filename": "memory_settings.md",
    "title": "PostgreSQL Memory Configuration",
    "category": "config",
    "content": null
  }
]
```

#### Status Codes

- `200` - Success
- `400` - Invalid category
- `500` - Internal server error

#### Notes

- `content` field is null for performance reasons (use get specific rule endpoint)
- Categories are limited to `config` and `sql`

---

### 3. Get Specific Rule

**GET** `/rules/{category}/{filename}`

Получить конкретное правило с полным содержимым.

#### Path Parameters

- `category`: string - категория правила (`config` или `sql`)
- `filename`: string - имя файла правила

#### Response

````json
{
  "filename": "slow_queries.md",
  "title": "Optimization Rules for Slow Queries",
  "category": "sql",
  "content": "# Optimization Rules for Slow Queries\n\n## Overview\nThis document contains rules for identifying and optimizing slow queries in PostgreSQL.\n\n## Rules\n\n### Rule 1: Missing Index Detection\n- **Severity**: High\n- **Description**: Queries performing sequential scans on large tables\n- **Recommendation**: Add appropriate indexes\n\n### Rule 2: Inefficient JOIN Operations\n- **Severity**: Medium\n- **Description**: JOINs without proper indexing\n- **Recommendation**: Ensure foreign key columns are indexed\n\n## Examples\n\n```sql\n-- Bad: Sequential scan\nSELECT * FROM users WHERE email = 'user@example.com';\n\n-- Good: Index lookup\nCREATE INDEX idx_users_email ON users(email);\nSELECT * FROM users WHERE email = 'user@example.com';\n```\n\n## Metrics\n\n- Query execution time > 1000ms\n- Seq Scan on tables with > 10,000 rows\n- Missing indexes on frequently queried columns"
}
````

#### Status Codes

- `200` - Success
- `400` - Invalid category
- `404` - Rule not found
- `500` - Internal server error

---

### 4. Create Rule

**POST** `/rules/`

Создать новое правило.

#### Request Body

````json
{
  "filename": "new_rule.md",
  "title": "New Analysis Rule",
  "category": "sql",
  "content": "## Overview\nThis is a new rule for SQL analysis.\n\n## Description\nDetailed description of the rule and its application.\n\n## Examples\n\n```sql\n-- Example SQL that triggers this rule\nSELECT * FROM table_name;\n```\n\n## Recommendations\n\n- Specific recommendations for fixing issues\n- Best practices to follow"
}
````

#### Response

```json
{
  "message": "Rule created successfully"
}
```

#### Status Codes

- `200` - Rule created successfully
- `400` - Invalid category or data
- `409` - Rule already exists
- `500` - Internal server error

#### Notes

- Filename must include `.md` extension
- Category must be either `config` or `sql`
- Content should follow Markdown format
- Title is automatically added as H1 header

---

### 5. Update Rule

**PUT** `/rules/{category}/{filename}`

Обновить существующее правило.

#### Path Parameters

- `category`: string - категория правила (`config` или `sql`)
- `filename`: string - имя файла правила

#### Request Body

```json
{
  "title": "Updated Rule Title",
  "content": "## Updated Overview\nThis is the updated content of the rule.\n\n## New Section\nAdditional information and examples."
}
```

#### Response

```json
{
  "message": "Rule updated successfully"
}
```

#### Status Codes

- `200` - Rule updated successfully
- `400` - Invalid category
- `404` - Rule not found
- `500` - Internal server error

#### Notes

- All fields are optional - can update only title or only content
- Title update modifies the H1 header in the file
- Content update replaces everything after the title

---

### 6. Delete Rule

**DELETE** `/rules/{category}/{filename}`

Удалить правило.

#### Path Parameters

- `category`: string - категория правила (`config` или `sql`)
- `filename`: string - имя файла правила

#### Response

```json
{
  "message": "Rule deleted successfully"
}
```

#### Status Codes

- `200` - Rule deleted successfully
- `400` - Invalid category
- `404` - Rule not found
- `500` - Internal server error

#### Notes

- Permanently removes the rule file
- Cannot be undone - ensure rule is not needed
- May affect analysis results if rule was actively used

---

## Rule Categories

### SQL Rules (`category: "sql"`)

Правила для анализа SQL запросов:

#### Performance Rules

- Медленные запросы
- Использование индексов
- Оптимизация JOIN'ов
- Подзапросы vs CTE

#### Security Rules

- SQL инъекции
- Права доступа
- Валидация данных
- Утечки информации

#### Best Practices Rules

- Стиль кода
- Именование
- Структура запросов
- PostgreSQL специфика

### Configuration Rules (`category: "config"`)

Правила для анализа конфигурации PostgreSQL:

#### Memory Configuration

- shared_buffers
- work_mem
- maintenance_work_mem
- effective_cache_size

#### Performance Configuration

- checkpoint settings
- WAL configuration
- autovacuum settings
- query planner settings

#### Security Configuration

- Authentication settings
- SSL configuration
- Logging settings
- User permissions

---

## Rule File Format

### Standard Structure

````markdown
# Rule Title

## Overview

Brief description of what this rule checks for.

## Severity

High/Medium/Low/Critical

## Description

Detailed description of the issue this rule identifies.

## Detection Criteria

- Specific conditions that trigger this rule
- Thresholds and metrics
- Query patterns or config values

## Impact

Description of the impact if this rule is violated.

## Recommendations

- Specific steps to fix the issue
- Best practices to follow
- Alternative approaches

## Examples

### Bad Example

```sql
-- SQL that violates this rule
SELECT * FROM large_table WHERE unindexed_column = 'value';
```
````

### Good Example

```sql
-- Corrected SQL following the rule
CREATE INDEX idx_large_table_column ON large_table(unindexed_column);
SELECT id, name FROM large_table WHERE unindexed_column = 'value';
```

## Metrics

- Performance thresholds
- Configuration values
- Query execution statistics

## Related Rules

- Links to other relevant rules
- Dependencies between rules

## References

- PostgreSQL documentation links
- Best practice guides
- Performance tuning resources

````

---

## Examples

### Get All SQL Rules
```bash
curl "http://localhost:8000/rules/?category=sql"
````

### Get Specific Configuration Rule

```bash
curl "http://localhost:8000/rules/config/memory_settings.md"
```

### Create New SQL Rule

````bash
curl -X POST "http://localhost:8000/rules/" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "n_plus_one_queries.md",
    "title": "N+1 Query Detection",
    "category": "sql",
    "content": "## Overview\nDetects N+1 query patterns that can cause performance issues.\n\n## Description\nN+1 queries occur when an application executes one query to retrieve a list of records, then executes N additional queries to fetch related data for each record.\n\n## Detection Criteria\n- Multiple similar queries with only parameter differences\n- Queries executed in loops\n- Lack of JOIN operations for related data\n\n## Recommendations\n- Use JOIN operations to fetch related data in single query\n- Implement query batching\n- Use PostgreSQL ARRAY functions for bulk operations\n\n## Examples\n\n### Bad (N+1 Pattern)\n```sql\n-- Main query\nSELECT id, name FROM users;\n\n-- N additional queries (one per user)\nSELECT * FROM orders WHERE user_id = 1;\nSELECT * FROM orders WHERE user_id = 2;\n-- ... repeated for each user\n```\n\n### Good (JOIN Solution)\n```sql\n-- Single optimized query\nSELECT u.id, u.name, o.id as order_id, o.total\nFROM users u\nLEFT JOIN orders o ON u.id = o.user_id;\n```"
  }'
````

### Update Rule Content

```bash
curl -X PUT "http://localhost:8000/rules/sql/n_plus_one_queries.md" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "## Updated Overview\nImproved detection for N+1 query patterns with additional examples.\n\n## New Detection Methods\n- Query execution frequency analysis\n- Parameter pattern matching\n- Performance impact measurement"
  }'
```

### Delete Rule

```bash
curl -X DELETE "http://localhost:8000/rules/sql/obsolete_rule.md"
```

### Ingest Rules from Directory

```bash
curl -X POST "http://localhost:8000/rules/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "rules_dir": "/app/rules/custom"
  }'
```

---

## Rule Development Guidelines

### Writing Effective Rules

#### Be Specific

- Define clear detection criteria
- Use measurable thresholds
- Provide concrete examples

#### Include Context

- Explain why the rule matters
- Describe the impact of violations
- Reference PostgreSQL best practices

#### Provide Solutions

- Give specific recommendations
- Include corrected examples
- Suggest alternative approaches

### Rule Testing

```bash
# Test rule against sample queries
curl -X POST "http://localhost:8000/review/" \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "SELECT * FROM users WHERE email LIKE '\''%gmail%'\''",
    "environment": "test"
  }' | jq '.analysis_results[] | select(.title == "Email Pattern Matching")'
```

### Rule Maintenance

- Regularly review rule effectiveness
- Update based on PostgreSQL version changes
- Monitor false positive rates
- Gather feedback from users

---

## Integration with Analysis Engine

Rules are automatically integrated into the analysis engine:

1. **Rule Loading**: Rules are loaded from the file system during startup
2. **Vector Search**: Content is indexed for semantic search
3. **Pattern Matching**: SQL patterns are compiled for efficient matching
4. **Result Generation**: Violations generate structured analysis results

The rules system supports:

- Dynamic rule updates without restart
- Version control integration
- Custom rule development
- Multi-language support for international teams
