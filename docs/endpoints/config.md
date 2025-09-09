# Config API Documentation

## Overview

API для анализа конфигурации PostgreSQL. Позволяет анализировать настройки базы данных и получать рекомендации по оптимизации.

**Base URL:** `/config`

---

## Endpoints

### 1. Analyze PostgreSQL Configuration

**POST** `/config/analyze`

Анализировать конфигурацию PostgreSQL сервера.

#### Request Body

```json
{
  "config": {
    "shared_buffers": "128MB",
    "effective_cache_size": "4GB",
    "maintenance_work_mem": "64MB",
    "checkpoint_completion_target": "0.7",
    "wal_buffers": "16MB",
    "default_statistics_target": "100",
    "random_page_cost": "4",
    "effective_io_concurrency": "1",
    "work_mem": "4MB",
    "min_wal_size": "1GB",
    "max_wal_size": "4GB"
  },
  "environment": "production",
  "server_info": {
    "version": "15.4",
    "host": "prod-db.example.com",
    "database": "myapp"
  }
}
```

#### Response

```json
{
  "overall_score": 75.5,
  "environment": "production",
  "timestamp": "2024-01-01T12:00:00",
  "analysis_results": [
    {
      "category": "Memory Configuration",
      "parameter": "shared_buffers",
      "current_value": "128MB",
      "recommended_value": "256MB",
      "severity": "medium",
      "score": 60,
      "description": "Shared buffers should be increased for better performance",
      "impact": "Performance improvement for read operations",
      "recommendation": "Increase shared_buffers to 25% of available RAM"
    },
    {
      "category": "WAL Configuration",
      "parameter": "checkpoint_completion_target",
      "current_value": "0.7",
      "recommended_value": "0.9",
      "severity": "low",
      "score": 80,
      "description": "Checkpoint completion target can be optimized",
      "impact": "Reduced I/O spikes during checkpoints",
      "recommendation": "Increase to 0.9 for smoother checkpoint distribution"
    }
  ],
  "recommendations": [
    {
      "priority": "high",
      "category": "Memory",
      "title": "Increase shared_buffers",
      "description": "Your shared_buffers is set to 128MB, which is quite low for a production system. Consider increasing it to 25% of your available RAM.",
      "sql_command": "ALTER SYSTEM SET shared_buffers = '256MB'; SELECT pg_reload_conf();"
    },
    {
      "priority": "medium",
      "category": "WAL",
      "title": "Optimize checkpoint settings",
      "description": "Adjusting checkpoint_completion_target can help reduce I/O spikes.",
      "sql_command": "ALTER SYSTEM SET checkpoint_completion_target = 0.9; SELECT pg_reload_conf();"
    }
  ],
  "summary": {
    "total_parameters_analyzed": 11,
    "high_priority_issues": 1,
    "medium_priority_issues": 2,
    "low_priority_issues": 1,
    "configuration_grade": "B"
  },
  "server_info": {
    "version": "15.4",
    "host": "prod-db.example.com",
    "database": "myapp"
  }
}
```

#### Status Codes

- `200` - Analysis completed successfully
- `400` - Invalid configuration data
- `500` - Internal server error

#### Notes

- Анализ основан на best practices для PostgreSQL
- Рекомендации учитывают указанную среду (development/staging/production)
- Оценка производится по шкале от 0 до 100
- Возвращаются конкретные SQL команды для применения рекомендаций

---

## Configuration Parameters

### Supported Parameters

#### Memory Configuration

- `shared_buffers` - Размер разделяемых буферов
- `effective_cache_size` - Предполагаемый размер кеша ОС
- `work_mem` - Память для операций сортировки
- `maintenance_work_mem` - Память для операций обслуживания

#### WAL Configuration

- `wal_buffers` - Размер буферов WAL
- `checkpoint_completion_target` - Цель завершения контрольных точек
- `min_wal_size` - Минимальный размер WAL
- `max_wal_size` - Максимальный размер WAL

#### Query Planning

- `default_statistics_target` - Цель статистики по умолчанию
- `random_page_cost` - Стоимость случайного доступа к странице
- `effective_io_concurrency` - Эффективная параллельность I/O

#### Connection Settings

- `max_connections` - Максимальное количество подключений
- `superuser_reserved_connections` - Зарезервированные подключения

#### Logging

- `log_statement` - Уровень логирования операторов
- `log_min_duration_statement` - Минимальная длительность для логирования

---

## Response Structure

### Analysis Results

Каждый результат анализа содержит:

- `category` - Категория параметра
- `parameter` - Имя параметра
- `current_value` - Текущее значение
- `recommended_value` - Рекомендуемое значение
- `severity` - Уровень важности (low/medium/high/critical)
- `score` - Оценка от 0 до 100
- `description` - Описание проблемы
- `impact` - Влияние на производительность
- `recommendation` - Рекомендация по исправлению

### Recommendations

Каждая рекомендация содержит:

- `priority` - Приоритет (low/medium/high/critical)
- `category` - Категория
- `title` - Заголовок рекомендации
- `description` - Подробное описание
- `sql_command` - SQL команда для применения

### Summary

- `total_parameters_analyzed` - Общее количество проанализированных параметров
- `high_priority_issues` - Количество проблем высокого приоритета
- `medium_priority_issues` - Количество проблем среднего приоритета
- `low_priority_issues` - Количество проблем низкого приоритета
- `configuration_grade` - Общая оценка конфигурации (A/B/C/D/F)

---

## Examples

### Analyze Production Configuration

```bash
curl -X POST "http://localhost:8000/config/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "shared_buffers": "128MB",
      "effective_cache_size": "4GB",
      "work_mem": "4MB",
      "maintenance_work_mem": "64MB",
      "checkpoint_completion_target": "0.5",
      "wal_buffers": "16MB",
      "max_connections": "100",
      "default_statistics_target": "100"
    },
    "environment": "production",
    "server_info": {
      "version": "15.4",
      "host": "prod-db.example.com",
      "database": "myapp"
    }
  }'
```

### Analyze Development Configuration

```bash
curl -X POST "http://localhost:8000/config/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "shared_buffers": "64MB",
      "effective_cache_size": "1GB",
      "work_mem": "2MB",
      "maintenance_work_mem": "32MB"
    },
    "environment": "development",
    "server_info": {
      "version": "15.4",
      "host": "localhost",
      "database": "testdb"
    }
  }'
```

### Get Configuration from PostgreSQL

```sql
-- SQL для получения текущей конфигурации
SELECT
  name,
  setting,
  unit,
  category,
  short_desc
FROM pg_settings
WHERE category IN (
  'Resource Usage / Memory',
  'Resource Usage / Disk',
  'Write Ahead Log',
  'Query Planning'
)
ORDER BY category, name;
```

### Apply Recommendations

```sql
-- Применение рекомендаций
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET work_mem = '8MB';

-- Перезагрузка конфигурации
SELECT pg_reload_conf();

-- Для некоторых параметров требуется перезапуск сервера
-- ALTER SYSTEM SET shared_buffers = '256MB'; -- требует перезапуска
```

---

## Environment-Specific Analysis

### Development Environment

- Менее строгие требования к производительности
- Упор на удобство разработки
- Меньшие значения буферов и кешей

### Staging Environment

- Конфигурация близкая к production
- Тестирование производительности
- Умеренные требования к ресурсам

### Production Environment

- Максимальная производительность
- Оптимизация под нагрузку
- Строгие требования к стабильности

### Testing Environment

- Быстрое выполнение тестов
- Минимальное потребление ресурсов
- Упрощенная конфигурация
