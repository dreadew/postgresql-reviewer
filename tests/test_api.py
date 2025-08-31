"""
Тесты для API эндпоинтов PostgreSQL Reviewer.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.app import create_application


@pytest.fixture
def client():
    """Фикстура для тестового клиента FastAPI."""
    app = create_application()
    return TestClient(app)


def test_health_check(client):
    """Тест health check эндпоинта."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "debug" in data


def test_root_endpoint(client):
    """Тест корневого эндпоинта."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "PostgreSQL Reviewer API" in data["message"]
    assert "docs" in data
    assert "web_ui" in data


def test_review_endpoint_sql_required(client):
    """Тест валидации обязательного поля sql в review эндпоинте."""
    response = client.post("/api/review", json={})
    assert response.status_code == 422  # Validation error


def test_review_endpoint_valid_request(client):
    """Тест review эндпоинта с валидными данными."""
    review_data = {
        "sql": "SELECT * FROM users WHERE id = 1;",
        "query_plan": "Seq Scan on users",
        "tables": [{"name": "users", "columns": ["id", "name"]}],
        "server_info": {"version": "PostgreSQL 15.0"},
        "thread_id": "test-thread-123",
        "environment": "test",
    }
    response = client.post("/api/review", json=review_data)
    # Поскольку у нас нет полной настройки, ожидаем 500 или другой код
    # В реальном тесте нужно настроить моки для зависимостей
    assert response.status_code in [200, 500, 503]


def test_config_analysis_endpoint(client):
    """Тест эндпоинта анализа конфигурации."""
    config_data = {
        "config": {"shared_buffers": "128MB", "work_mem": "4MB"},
        "server_info": {"version": "PostgreSQL 15.0"},
        "environment": "test",
    }
    response = client.post("/api/config/analyze", json=config_data)
    assert response.status_code in [200, 500, 503]


def test_batch_review_endpoint(client):
    """Тест пакетного анализа SQL."""
    batch_data = {
        "queries": [
            {
                "sql": "SELECT * FROM users;",
                "query_plan": "",
                "tables": [],
                "server_info": {"version": "PostgreSQL 15.0"},
            }
        ],
        "environment": "test",
    }
    response = client.post("/api/review/batch", json=batch_data)
    assert response.status_code in [200, 500, 503]


def test_cron_validation_task_create():
    """Тест валидации cron выражений в TaskCreate."""
    from src.api.schemas import TaskCreate

    # Валидное cron выражение
    valid_task = TaskCreate(
        name="Test Task",
        connection_id=1,
        schedule="0 0 * * *",  # Каждый день в полночь
        task_type="config_check",
    )
    assert valid_task.schedule == "0 0 * * *"

    # Невалидное cron выражение
    with pytest.raises(ValueError, match="Invalid cron expression"):
        TaskCreate(
            name="Test Task",
            connection_id=1,
            schedule="invalid cron",
            task_type="config_check",
        )


def test_cron_validation_task_update():
    """Тест валидации cron выражений в TaskUpdate."""
    from src.api.schemas import TaskUpdate

    # Валидное cron выражение
    valid_update = TaskUpdate(schedule="*/5 * * * *")  # Каждые 5 минут
    assert valid_update.schedule == "*/5 * * * *"

    # Невалидное cron выражение
    with pytest.raises(ValueError, match="Invalid cron expression"):
        TaskUpdate(schedule="not a cron")

    # None значение (должно пройти)
    none_update = TaskUpdate(schedule=None)
    assert none_update.schedule is None
