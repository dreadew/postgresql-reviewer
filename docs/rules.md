# Правила анализа API

Управление правилами для анализа SQL запросов, конфигураций и выявления проблем.

## Базовый путь: `/rules`

---

## 📋 Управление правилами

### GET `/rules/` - Список всех правил

Получает список всех доступных правил анализа.

**Запрос:**

```bash
curl http://localhost:8000/rules/
```

**Ответ:**

```json
[
  {
    "id": "performance_001",
    "category": "performance",
    "filename": "slow_queries.yaml",
    "title": "Медленные запросы",
    "description": "Правила для выявления медленных SQL запросов",
    "severity": "high",
    "enabled": true,
    "tags": ["performance", "sql", "optimization"],
    "created_at": "2025-09-07T15:30:00",
    "updated_at": "2025-09-07T15:30:00"
  },
  {
    "id": "security_001",
    "category": "security",
    "filename": "sql_injection.yaml",
    "title": "SQL Injection",
    "description": "Правила для выявления потенциальных SQL injection уязвимостей",
    "severity": "critical",
    "enabled": true,
    "tags": ["security", "sql", "vulnerability"],
    "created_at": "2025-09-07T15:30:00",
    "updated_at": "2025-09-07T15:30:00"
  },
  {
    "id": "config_001",
    "category": "config",
    "filename": "postgresql_config.yaml",
    "title": "Конфигурация PostgreSQL",
    "description": "Правила для проверки настроек PostgreSQL",
    "severity": "medium",
    "enabled": true,
    "tags": ["configuration", "postgresql", "best_practices"],
    "created_at": "2025-09-07T15:30:00",
    "updated_at": "2025-09-07T15:30:00"
  }
]
```

---

### GET `/rules/{category}/{filename}` - Получить конкретное правило

Получает содержимое конкретного правила.

**Запрос:**

```bash
curl http://localhost:8000/rules/performance/slow_queries.yaml
```

**Ответ:**

```yaml
# Правило для выявления медленных запросов
id: performance_001
title: "Медленные запросы"
description: "Выявление SQL запросов с плохой производительностью"
category: performance
severity: high
enabled: true

# Условия срабатывания правила
conditions:
  - name: "execution_time"
    operator: ">"
    value: 1000
    unit: "ms"
    description: "Время выполнения больше 1 секунды"

  - name: "rows_examined"
    operator: ">"
    value: 10000
    description: "Просмотрено более 10000 строк"

  - name: "cost_estimate"
    operator: ">"
    value: 1000
    description: "Оценочная стоимость запроса высокая"

# Паттерны для поиска в SQL
patterns:
  - pattern: "SELECT \\* FROM"
    message: "Использование SELECT * может быть неэффективным"
    severity: medium

  - pattern: "WHERE.*LIKE '%.*%'"
    message: "LIKE с ведущим % препятствует использованию индексов"
    severity: high

  - pattern: "ORDER BY.*LIMIT [0-9]+"
    message: "ORDER BY + LIMIT может быть оптимизирован с помощью индексов"
    severity: medium

# Рекомендации при срабатывании
recommendations:
  - type: "index_suggestion"
    message: "Рассмотрите добавление индекса для улучшения производительности"
    action: "create_index"

  - type: "query_rewrite"
    message: "Попробуйте переписать запрос для лучшей производительности"
    action: "optimize_query"

  - type: "schema_optimization"
    message: "Проверьте структуру таблиц и нормализацию"
    action: "review_schema"

# Примеры проблемных запросов
examples:
  bad:
    - "SELECT * FROM large_table WHERE name LIKE '%search%'"
    - "SELECT COUNT(*) FROM orders WHERE created_at > '2020-01-01'"

  good:
    - "SELECT id, name, email FROM users WHERE email = 'user@example.com'"
    - "SELECT COUNT(*) FROM orders WHERE created_at >= '2025-01-01'::date"

# Метаданные
metadata:
  author: "PostgreSQL Reviewer Team"
  version: "1.0"
  last_updated: "2025-09-07"
  references:
    - "https://wiki.postgresql.org/wiki/Performance_Optimization"
    - "https://use-the-index-luke.com/"
```

---

### POST `/rules/` - Создать новое правило

Создает новое правило анализа.

**Запрос:**

```bash
curl -X POST http://localhost:8000/rules/ \
  -H "Content-Type: application/json" \
  -d '{
    "category": "custom",
    "filename": "my_rule.yaml",
    "content": "id: custom_001\ntitle: \"Мое правило\"\ndescription: \"Пользовательское правило анализа\"\ncategory: custom\nseverity: medium\nenabled: true\n\npatterns:\n  - pattern: \"SELECT.*FROM huge_table\"\n    message: \"Избегайте запросов к huge_table без WHERE\"\n    severity: high\n\nrecommendations:\n  - type: \"query_optimization\"\n    message: \"Добавьте WHERE условие для фильтрации\"\n    action: \"add_where_clause\""
  }'
```

**Ответ:**

```json
{
  "message": "Правило успешно создано",
  "rule_id": "custom_001",
  "category": "custom",
  "filename": "my_rule.yaml",
  "path": "/rules/custom/my_rule.yaml"
}
```

---

### PUT `/rules/{category}/{filename}` - Обновить правило

Обновляет существующее правило.

**Запрос:**

```bash
curl -X PUT http://localhost:8000/rules/custom/my_rule.yaml \
  -H "Content-Type: application/json" \
  -d '{
    "content": "id: custom_001\ntitle: \"Обновленное правило\"\ndescription: \"Обновленное пользовательское правило\"\ncategory: custom\nseverity: high\nenabled: true\n\npatterns:\n  - pattern: \"SELECT.*FROM huge_table\"\n    message: \"КРИТИЧНО: Избегайте запросов к huge_table без WHERE\"\n    severity: critical"
  }'
```

**Ответ:**

```json
{
  "message": "Правило успешно обновлено",
  "rule_id": "custom_001",
  "category": "custom",
  "filename": "my_rule.yaml",
  "updated_at": "2025-09-07T16:30:00"
}
```

---

### DELETE `/rules/{category}/{filename}` - Удалить правило

Удаляет правило из системы.

**Запрос:**

```bash
curl -X DELETE http://localhost:8000/rules/custom/my_rule.yaml
```

**Ответ:**

```json
{
  "message": "Правило успешно удалено",
  "rule_id": "custom_001",
  "category": "custom",
  "filename": "my_rule.yaml"
}
```

---

### POST `/rules/ingest` - Загрузка правил из файлов

Загружает правила из файловой системы в базу знаний.

**Запрос:**

```bash
curl -X POST http://localhost:8000/rules/ingest
```

**Ответ:**

```json
{
  "message": "Правила успешно загружены",
  "loaded_rules": 15,
  "categories": ["performance", "security", "config", "sql"],
  "details": [
    {
      "category": "performance",
      "rules_count": 5,
      "files": ["slow_queries.yaml", "index_usage.yaml"]
    },
    {
      "category": "security",
      "rules_count": 4,
      "files": ["sql_injection.yaml", "privilege_escalation.yaml"]
    }
  ]
}
```

---

## 📚 Категории правил

### 1. Производительность (`performance`)

- Медленные запросы
- Неэффективное использование индексов
- Проблемы с JOIN операциями
- Неоптимальные GROUP BY и ORDER BY

### 2. Безопасность (`security`)

- SQL injection уязвимости
- Утечка данных
- Проблемы с правами доступа
- Небезопасные функции

### 3. Конфигурация (`config`)

- Настройки PostgreSQL
- Параметры производительности
- Настройки безопасности
- Конфигурация логирования

### 4. SQL качество (`sql`)

- Стиль кодирования
- Лучшие практики
- Читаемость кода
- Поддерживаемость

---

## 🔧 Структура правил

### YAML формат правила

```yaml
# Метаданные правила
id: unique_rule_id
title: "Название правила"
description: "Подробное описание"
category: performance|security|config|sql
severity: low|medium|high|critical
enabled: true|false
tags: [tag1, tag2, tag3]

# Условия срабатывания
conditions:
  - name: "metric_name"
    operator: ">|<|=|!=|>=|<="
    value: numeric_value
    unit: "ms|mb|percent"
    description: "Описание условия"

# Паттерны поиска в SQL/конфиге
patterns:
  - pattern: "regex_pattern"
    message: "Сообщение при срабатывании"
    severity: low|medium|high|critical
    flags: [case_insensitive, multiline]

# Рекомендации
recommendations:
  - type: "recommendation_type"
    message: "Рекомендация"
    action: "suggested_action"
    sql_example: "EXAMPLE SQL"

# Примеры
examples:
  bad: ["плохой пример 1", "плохой пример 2"]
  good: ["хороший пример 1", "хороший пример 2"]

# Метаданные
metadata:
  author: "Автор правила"
  version: "1.0"
  last_updated: "2025-09-07"
  references: ["ссылка 1", "ссылка 2"]
```

---

## 💡 Примеры правил

### Правило для выявления SELECT \*

```yaml
id: sql_001
title: "Избегайте SELECT *"
description: "Использование SELECT * может негативно влиять на производительность"
category: sql
severity: medium
enabled: true

patterns:
  - pattern: "SELECT\\s+\\*\\s+FROM"
    message: "Использование SELECT * не рекомендуется"
    severity: medium

recommendations:
  - type: "query_optimization"
    message: "Укажите конкретные столбцы вместо *"
    action: "specify_columns"
    sql_example: "SELECT id, name, email FROM users"

examples:
  bad: ["SELECT * FROM users"]
  good: ["SELECT id, name, email FROM users"]
```

### Правило для безопасности

```yaml
id: security_002
title: "Потенциальная SQL injection"
description: "Выявление потенциальных SQL injection уязвимостей"
category: security
severity: critical
enabled: true

patterns:
  - pattern: "WHERE.*=.*\\$[^0-9]"
    message: "Возможная SQL injection через неэкранированные параметры"
    severity: critical

  - pattern: "WHERE.*LIKE.*'%.*'.*"
    message: "Потенциально небезопасное использование LIKE"
    severity: high

recommendations:
  - type: "security_fix"
    message: "Используйте параметризованные запросы"
    action: "use_parameters"
    sql_example: "WHERE id = $1"
```

### Правило для конфигурации

```yaml
id: config_002
title: "Неоптимальная настройка shared_buffers"
description: "Проверка правильности настройки shared_buffers"
category: config
severity: medium
enabled: true

conditions:
  - name: "shared_buffers_mb"
    operator: "<"
    value: 128
    unit: "mb"
    description: "shared_buffers слишком мал"

recommendations:
  - type: "config_optimization"
    message: "Увеличьте shared_buffers до 25% от RAM"
    action: "update_config"
    sql_example: "shared_buffers = 1GB"
```

---

## 🚀 Интеграция правил с анализом

Правила автоматически применяются при выполнении анализа через:

- `/review/` - анализ отдельных запросов
- `/review/batch` - пакетный анализ
- Автоматические задачи планировщика

### Настройка правил для задач

```bash
# Создание задачи с конкретными правилами
curl -X POST http://localhost:8000/scheduler/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Security Audit",
    "task_type": "query_analysis",
    "connection_id": 1,
    "cron_schedule": "0 2 * * *",
    "task_params": {
      "analysis_type": "security",
      "enabled_rules": ["security_001", "security_002"],
      "rule_categories": ["security"]
    }
  }'
```
