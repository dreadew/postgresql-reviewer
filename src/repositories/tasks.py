"""
Репозиторий для работы с задачами через SQLAlchemy.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, desc
from datetime import datetime, timezone
from .base import BaseRepository
from ..models.tasks import ScheduledTask, TaskExecution
import logging

logger = logging.getLogger(__name__)


class ScheduledTaskRepository(BaseRepository[ScheduledTask]):
    """Репозиторий для работы с запланированными задачами."""

    def __init__(self, db: Session):
        super().__init__(db, ScheduledTask)

    def create(self, task_data: Dict[str, Any]) -> ScheduledTask:
        """Создать новую запланированную задачу с валидацией."""
        try:
            existing = self.get_by_name(task_data["name"])
            if existing:
                raise ValueError(f"Task with name '{task_data['name']}' already exists")

            return super().create(task_data)

        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Failed to create task: {e}")
            raise ValueError(f"Task with name '{task_data['name']}' already exists")

    def get_by_name(self, name: str) -> Optional[ScheduledTask]:
        """Получить задачу по имени."""
        return self.db.query(ScheduledTask).filter(ScheduledTask.name == name).first()

    def get_filtered(self, filters: Dict[str, Any]) -> List[ScheduledTask]:
        """Получить отфильтрованные задачи."""
        query = self.db.query(ScheduledTask)
        query = self._apply_filters(query, filters)
        return query.order_by(ScheduledTask.created_at.desc()).all()

    def get_active_tasks(self) -> List[ScheduledTask]:
        """Получить все активные задачи."""
        return self.get_filtered({"is_active": True})

    def get_tasks_ready_to_run(self, current_time: datetime) -> List[ScheduledTask]:
        """Получить задачи готовые к выполнению."""
        return (
            self.db.query(ScheduledTask)
            .filter(
                and_(
                    ScheduledTask.is_active == True,
                    ScheduledTask.next_run_at <= current_time,
                )
            )
            .all()
        )

    def update_last_run(self, task_id: int, last_run_at: datetime = None) -> bool:
        """Обновить время последнего запуска задачи."""
        try:
            task = self.get_by_id(task_id)
            if not task:
                return False

            task.last_run_at = last_run_at or datetime.now(timezone.utc)
            self.db.commit()

            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update last run for task {task_id}: {e}")
            return False


class TaskExecutionRepository(BaseRepository[TaskExecution]):
    """Репозиторий для работы с выполнениями задач."""

    def __init__(self, db: Session):
        super().__init__(db, TaskExecution)

    def get_filtered(self, filters: Dict[str, Any]) -> List[TaskExecution]:
        """Получить отфильтрованные выполнения задач."""
        query = self.db.query(TaskExecution)
        query = self._apply_filters(query, filters)
        return query.order_by(desc(TaskExecution.started_at)).all()

    def get_by_task_id(self, task_id: int, limit: int = 50) -> List[TaskExecution]:
        """Получить выполнения для конкретной задачи."""
        return (
            self.db.query(TaskExecution)
            .filter(TaskExecution.scheduled_task_id == task_id)
            .order_by(desc(TaskExecution.started_at))
            .limit(limit)
            .all()
        )

    def get_running_executions(self) -> List[TaskExecution]:
        """Получить все выполняющиеся задачи."""
        return self.get_filtered({"status": "running"})

    def update_status(
        self,
        execution_id: int,
        status: str,
        completed_at: datetime = None,
        result: Dict[str, Any] = None,
        error_message: str = None,
    ) -> Optional[TaskExecution]:
        """Обновить статус выполнения."""
        try:
            execution = self.get_by_id(execution_id)
            if not execution:
                return None

            execution.status = status
            if completed_at:
                execution.completed_at = completed_at
            if result:
                execution.result = result
            if error_message:
                execution.error_message = error_message

            self.db.commit()
            self.db.refresh(execution)

            return execution

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update task execution {execution_id}: {e}")
            return None

    def mark_running(self, execution_id: int) -> bool:
        """Отметить выполнение как запущенное."""
        return self.update_status(execution_id, "running") is not None

    def mark_completed(self, execution_id: int, result: Dict[str, Any] = None) -> bool:
        """Отметить выполнение как завершенное."""
        return (
            self.update_status(
                execution_id,
                "completed",
                completed_at=datetime.now(timezone.utc),
                result=result,
            )
            is not None
        )

    def mark_failed(self, execution_id: int, error_message: str) -> bool:
        """Отметить выполнение как неудачное."""
        return (
            self.update_status(
                execution_id,
                "failed",
                completed_at=datetime.now(timezone.utc),
                error_message=error_message,
            )
            is not None
        )
