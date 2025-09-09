# Конфигурация API

Анализ и проверка конфигурации PostgreSQL серверов.

## Базовый путь: `/config`

---

## ⚙️ Анализ конфигурации

### POST `/config/analyze` - Анализ конфигурации PostgreSQL

Выполняет комплексный анализ конфигурации PostgreSQL сервера с рекомендациями по оптимизации.

**Запрос:**

```bash
curl -X POST http://localhost:8000/config/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": 1,
    "check_performance": true,
    "check_security": true,
    "check_logging": true,
    "check_replication": false,
    "include_recommendations": true,
    "severity_level": "medium"
  }'
```

**Параметры запроса:**

- `connection_id` - ID подключения к базе данных
- `check_performance` - проверить настройки производительности
- `check_security` - проверить настройки безопасности
- `check_logging` - проверить настройки логирования
- `check_replication` - проверить настройки репликации
- `include_recommendations` - включить рекомендации по улучшению
- `severity_level` - минимальный уровень серьезности (low, medium, high, critical)

**Ответ:**

```json
{
  "analysis_id": "config_analysis_20250907_160000",
  "connection_id": 1,
  "server_info": {
    "version": "PostgreSQL 14.9",
    "server_uptime": "15 days, 8 hours, 23 minutes",
    "config_file": "/etc/postgresql/14/main/postgresql.conf",
    "data_directory": "/var/lib/postgresql/14/main",
    "server_encoding": "UTF8",
    "max_connections": 100,
    "shared_buffers": "128MB",
    "effective_cache_size": "4GB"
  },
  "overall_score": 7.2,
  "total_issues": 12,
  "summary": {
    "critical_issues": 1,
    "high_issues": 3,
    "medium_issues": 5,
    "low_issues": 3,
    "performance_score": 6.8,
    "security_score": 8.1,
    "logging_score": 7.5
  },
  "performance_analysis": {
    "score": 6.8,
    "issues": [
      {
        "parameter": "shared_buffers",
        "current_value": "128MB",
        "issue": "Слишком маленькое значение для сервера с 8GB RAM",
        "severity": "high",
        "recommended_value": "2GB",
        "impact": "Низкая эффективность кэширования",
        "explanation": "shared_buffers должен составлять 25% от общей памяти"
      },
      {
        "parameter": "effective_cache_size",
        "current_value": "4GB",
        "issue": "Неоптимальное значение",
        "severity": "medium",
        "recommended_value": "6GB",
        "impact": "Неточные оценки планировщика запросов",
        "explanation": "Должен отражать общий объем доступной памяти для кэширования"
      },
      {
        "parameter": "work_mem",
        "current_value": "4MB",
        "issue": "Слишком мало для сложных запросов",
        "severity": "medium",
        "recommended_value": "16MB",
        "impact": "Частое использование дискового сортировки",
        "explanation": "Увеличение work_mem ускорит сортировки и хеш-операции"
      }
    ],
    "recommendations": [
      {
        "category": "memory",
        "priority": "high",
        "title": "Оптимизация настроек памяти",
        "changes": [
          "shared_buffers = 2GB",
          "effective_cache_size = 6GB",
          "work_mem = 16MB"
        ],
        "estimated_improvement": "30-50% улучшение производительности"
      }
    ]
  },
  "security_analysis": {
    "score": 8.1,
    "issues": [
      {
        "parameter": "ssl",
        "current_value": "off",
        "issue": "SSL отключен",
        "severity": "critical",
        "recommended_value": "on",
        "impact": "Небезопасная передача данных",
        "explanation": "Включение SSL обязательно для продакшн серверов"
      },
      {
        "parameter": "log_connections",
        "current_value": "off",
        "issue": "Логирование подключений отключено",
        "severity": "medium",
        "recommended_value": "on",
        "impact": "Затрудненный аудит безопасности",
        "explanation": "Помогает отслеживать несанкционированные подключения"
      }
    ],
    "recommendations": [
      {
        "category": "encryption",
        "priority": "critical",
        "title": "Включение SSL шифрования",
        "changes": [
          "ssl = on",
          "ssl_cert_file = 'server.crt'",
          "ssl_key_file = 'server.key'"
        ]
      }
    ]
  },
  "logging_analysis": {
    "score": 7.5,
    "issues": [
      {
        "parameter": "log_min_duration_statement",
        "current_value": "-1",
        "issue": "Медленные запросы не логируются",
        "severity": "medium",
        "recommended_value": "1000",
        "impact": "Сложность выявления проблем производительности",
        "explanation": "Логирование запросов >1с поможет в оптимизации"
      },
      {
        "parameter": "log_checkpoints",
        "current_value": "off",
        "issue": "Checkpoint'ы не логируются",
        "severity": "low",
        "recommended_value": "on",
        "impact": "Затрудненная диагностика I/O проблем",
        "explanation": "Помогает отслеживать производительность записи"
      }
    ],
    "recommendations": [
      {
        "category": "monitoring",
        "priority": "medium",
        "title": "Улучшение логирования для мониторинга",
        "changes": [
          "log_min_duration_statement = 1000",
          "log_checkpoints = on",
          "log_lock_waits = on"
        ]
      }
    ]
  },
  "detailed_configuration": {
    "memory_settings": {
      "shared_buffers": "128MB",
      "effective_cache_size": "4GB",
      "work_mem": "4MB",
      "maintenance_work_mem": "64MB",
      "temp_buffers": "8MB"
    },
    "checkpoint_settings": {
      "checkpoint_timeout": "5min",
      "checkpoint_completion_target": "0.5",
      "wal_buffers": "16MB",
      "wal_writer_delay": "200ms"
    },
    "connection_settings": {
      "max_connections": "100",
      "superuser_reserved_connections": "3",
      "tcp_keepalives_idle": "0",
      "tcp_keepalives_interval": "0"
    },
    "logging_settings": {
      "logging_collector": "off",
      "log_destination": "stderr",
      "log_min_messages": "warning",
      "log_min_error_statement": "error"
    }
  },
  "optimization_suggestions": [
    {
      "area": "Performance Tuning",
      "impact": "High",
      "suggestions": [
        {
          "setting": "shared_buffers",
          "current": "128MB",
          "recommended": "2GB",
          "reason": "Увеличить кэш для лучшей производительности"
        },
        {
          "setting": "random_page_cost",
          "current": "4.0",
          "recommended": "1.1",
          "reason": "Оптимизация для SSD дисков"
        }
      ]
    },
    {
      "area": "Security Hardening",
      "impact": "Critical",
      "suggestions": [
        {
          "setting": "ssl",
          "current": "off",
          "recommended": "on",
          "reason": "Обязательно для продакшн среды"
        },
        {
          "setting": "password_encryption",
          "current": "md5",
          "recommended": "scram-sha-256",
          "reason": "Более безопасный алгоритм хеширования"
        }
      ]
    }
  ],
  "compliance_check": {
    "pci_dss": {
      "compliant": false,
      "issues": ["SSL не включен", "Логирование доступа отключено"],
      "recommendations": ["Включить SSL", "Настроить аудит логирование"]
    },
    "hipaa": {
      "compliant": false,
      "issues": ["Отсутствует шифрование данных в покое"],
      "recommendations": ["Настроить transparent data encryption"]
    }
  },
  "created_at": "2025-09-07T16:00:00"
}
```

---

## 📊 Категории проверок

### 1. Производительность (`performance`)

- **Настройки памяти**: shared_buffers, work_mem, effective_cache_size
- **Checkpoint настройки**: checkpoint_timeout, checkpoint_completion_target
- **WAL настройки**: wal_buffers, synchronous_commit
- **Планировщик запросов**: random*page_cost, seq_page_cost, cpu*\*\_cost

### 2. Безопасность (`security`)

- **Шифрование**: ssl, password_encryption
- **Аутентификация**: authentication настройки
- **Авторизация**: row level security, default privileges
- **Аудит**: log_connections, log_disconnections

### 3. Логирование (`logging`)

- **Уровни логирования**: log_min_messages, log_min_error_statement
- **Производительность**: log_min_duration_statement
- **Аудит**: log_statement, log_line_prefix
- **Ротация**: log_rotation_age, log_rotation_size

### 4. Репликация (`replication`)

- **Streaming replication**: wal_level, max_wal_senders
- **Архивирование**: archive_mode, archive_command
- **Standby настройки**: hot*standby, max_standby*\*\_delay

---

## 🔍 Специализированные анализы

### Анализ только производительности

```bash
curl -X POST http://localhost:8000/config/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": 1,
    "check_performance": true,
    "check_security": false,
    "check_logging": false,
    "severity_level": "low"
  }'
```

### Аудит безопасности

```bash
curl -X POST http://localhost:8000/config/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": 1,
    "check_performance": false,
    "check_security": true,
    "check_logging": true,
    "severity_level": "medium",
    "compliance_standards": ["pci_dss", "hipaa"]
  }'
```

### Проверка готовности к продакшн

```bash
curl -X POST http://localhost:8000/config/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": 1,
    "check_performance": true,
    "check_security": true,
    "check_logging": true,
    "check_replication": true,
    "production_readiness": true
  }'
```

---

## 📈 Интеграция с планировщиком

### Автоматическая проверка конфигурации

```bash
curl -X POST http://localhost:8000/scheduler/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily Config Check",
    "task_type": "config_check",
    "connection_id": 1,
    "cron_schedule": "0 2 * * *",
    "task_params": {
      "check_performance": true,
      "check_security": true,
      "severity_level": "medium"
    }
  }'
```

---

## 💡 Примеры использования

### Оптимизация нового сервера

```bash
# Полный анализ для нового PostgreSQL сервера
curl -X POST http://localhost:8000/config/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": 1,
    "check_performance": true,
    "check_security": true,
    "check_logging": true,
    "include_recommendations": true
  }' | jq '.optimization_suggestions'
```

### Проверка соответствия стандартам

```bash
# Проверка соответствия требованиям безопасности
curl -X POST http://localhost:8000/config/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": 1,
    "check_security": true,
    "severity_level": "high"
  }' | jq '.compliance_check'
```

### Поиск проблем производительности

```bash
# Фокус на настройках производительности
curl -X POST http://localhost:8000/config/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": 1,
    "check_performance": true
  }' | jq '.performance_analysis.issues[] | select(.severity == "high")'
```

---

## 🛠 Применение рекомендаций

### Генерация скрипта изменений

Система может генерировать SQL скрипт для применения рекомендуемых изменений:

```sql
-- Сгенерированный скрипт оптимизации
-- Основано на анализе от 2025-09-07T16:00:00

-- ПРОИЗВОДИТЕЛЬНОСТЬ
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '6GB';
ALTER SYSTEM SET work_mem = '16MB';
ALTER SYSTEM SET random_page_cost = 1.1;

-- БЕЗОПАСНОСТЬ
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET password_encryption = 'scram-sha-256';
ALTER SYSTEM SET log_connections = on;

-- ЛОГИРОВАНИЕ
ALTER SYSTEM SET log_min_duration_statement = 1000;
ALTER SYSTEM SET log_checkpoints = on;
ALTER SYSTEM SET log_lock_waits = on;

-- Применить изменения
SELECT pg_reload_conf();

-- ВНИМАНИЕ: Некоторые параметры требуют перезапуска сервера
-- Перезапуск необходим для: shared_buffers
```

### Пошаговое применение

1. **Анализ текущей конфигурации**
2. **Резервное копирование конфигурации**
3. **Применение изменений по приоритету**
4. **Мониторинг после изменений**
5. **Валидация улучшений**

---

## ⚠️ Важные замечания

1. **Перезапуск сервера**: Некоторые параметры требуют перезапуска PostgreSQL
2. **Тестирование**: Всегда тестируйте изменения на dev/staging среде
3. **Мониторинг**: Отслеживайте метрики после применения изменений
4. **Откат**: Подготовьте план отката на случай проблем
5. **Документирование**: Документируйте все изменения конфигурации
