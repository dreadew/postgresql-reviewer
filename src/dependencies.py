"""
Зависимости для репозиториев SQLAlchemy.
"""

from typing import Generator
from sqlalchemy.orm import Session
from .models.base import get_db
from .repositories.connections import ConnectionRepository, ConnectionStatusRepository
from .repositories.tasks import ScheduledTaskRepository, TaskExecutionRepository


def get_connection_repository(db: Session = get_db()) -> ConnectionRepository:
    """Получить репозиторий подключений."""
    return ConnectionRepository(db)


def get_connection_status_repository(
    db: Session = get_db(),
) -> ConnectionStatusRepository:
    """Получить репозиторий статусов подключений."""
    return ConnectionStatusRepository(db)


def get_scheduled_task_repository(db: Session = get_db()) -> ScheduledTaskRepository:
    """Получить репозиторий запланированных задач."""
    return ScheduledTaskRepository(db)


def get_task_execution_repository(db: Session = get_db()) -> TaskExecutionRepository:
    """Получить репозиторий выполнений задач."""
    return TaskExecutionRepository(db)
