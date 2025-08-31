"""
Общие фикстуры для тестов.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.app import create_application


@pytest.fixture
def client():
    """Фикстура для тестового клиента FastAPI."""
    app = create_application()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_review_request():
    """Фикстура с примером запроса на анализ SQL."""
    return {
        "sql": "SELECT * FROM users WHERE id = $1;",
        "query_plan": "Index Scan using users_pkey on users",
        "tables": [
            {
                "name": "users",
                "columns": [
                    {"name": "id", "type": "integer", "nullable": False},
                    {"name": "name", "type": "varchar", "nullable": False},
                    {"name": "email", "type": "varchar", "nullable": True},
                ],
            }
        ],
        "server_info": {
            "version": "PostgreSQL 15.0",
            "host": "localhost",
            "port": "5432",
        },
        "thread_id": "test-thread-123",
        "environment": "test",
    }


@pytest.fixture
def sample_config_request():
    """Фикстура с примером запроса на анализ конфигурации."""
    return {
        "config": {
            "shared_buffers": "256MB",
            "work_mem": "4MB",
            "maintenance_work_mem": "64MB",
            "effective_cache_size": "1GB",
            "max_connections": "100",
        },
        "server_info": {
            "version": "PostgreSQL 15.0",
            "host": "localhost",
            "port": "5432",
        },
        "environment": "test",
    }


@pytest.fixture
def sample_task_data():
    """Фикстура с примером данных задачи."""
    return {
        "name": "Daily Config Check",
        "connection_id": 1,
        "schedule": "0 2 * * *",  # Каждый день в 2:00
        "task_type": "config_check",
        "parameters": {"check_type": "full"},
        "is_active": True,
    }
