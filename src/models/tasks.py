"""
SQLAlchemy модели для планировщика задач.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    JSON,
)
from sqlalchemy.sql import func
from .base import Base


class ScheduledTask(Base):
    """Модель запланированной задачи."""

    __tablename__ = "scheduled_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    task_type = Column(String(50), nullable=False)
    connection_id = Column(Integer, nullable=False)
    cron_schedule = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime(timezone=True))
    next_run_at = Column(DateTime(timezone=True))
    task_params = Column(JSON)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<ScheduledTask(id={self.id}, name='{self.name}', task_type='{self.task_type}')>"

    def to_dict(self):
        """Преобразовать в словарь."""
        return {
            "id": self.id,
            "name": self.name,
            "task_type": self.task_type,
            "connection_id": self.connection_id,
            "cron_schedule": self.cron_schedule,
            "is_active": self.is_active,
            "last_run_at": self.last_run_at,
            "next_run_at": self.next_run_at,
            "task_params": self.task_params,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class TaskExecution(Base):
    """Модель выполнения задачи."""

    __tablename__ = "task_executions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scheduled_task_id = Column(Integer, nullable=False)
    task_type = Column(String(50), nullable=False)
    connection_id = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    parameters = Column(JSON)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    result = Column(JSON)
    error_message = Column(Text)

    def __repr__(self):
        return f"<TaskExecution(id={self.id}, scheduled_task_id={self.scheduled_task_id}, status='{self.status}')>"

    def to_dict(self):
        """Преобразовать в словарь."""
        return {
            "id": self.id,
            "scheduled_task_id": self.scheduled_task_id,
            "task_type": self.task_type,
            "connection_id": self.connection_id,
            "status": self.status,
            "parameters": self.parameters,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "result": self.result,
            "error_message": self.error_message,
        }
