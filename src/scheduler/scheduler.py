"""
Планировщик задач с поддержкой cron расписания и интеграцией с Vault.
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import List, Optional
from croniter import croniter

from src.core.constants import ERROR_TASK_CREATION_FAILED
import redis.asyncio as redis
from src.core.config import settings
from src.services.database_service import DatabaseService
from src.services.vault_service import VaultService
from .models import (
    ScheduledTaskCreate,
    ScheduledTaskUpdate,
    ScheduledTaskResponse,
    TaskExecutionCreate,
    TaskQueueItem,
)

logger = logging.getLogger(__name__)


def _prepare_task_dict(task_dict: dict) -> dict:
    """Подготовить словарь задачи для ScheduledTaskResponse."""
    if isinstance(task_dict.get("task_params"), str):
        task_dict["task_params"] = json.loads(task_dict["task_params"])
    elif task_dict.get("task_params") is None:
        task_dict["task_params"] = {}
    return task_dict


class SchedulerService:
    """Сервис планировщика задач."""

    def __init__(self):
        self.db_service = DatabaseService()
        self.vault_service = VaultService()
        self.redis_client = None
        self.is_running = False

    async def initialize(self):
        """Инициализация сервиса."""
        try:
            redis_url = settings.redis_url or "redis://localhost:6379"
            self.redis_client = redis.from_url(redis_url)
            await self.redis_client.ping()
            logger.info("Подключение к Redis установлено")
            self.vault_service.initialize()
            logger.info("Vault инициализирован")

        except Exception as e:
            logger.error(f"Ошибка инициализации планировщика: {e}")
            raise

    async def close(self):
        """Закрытие соединений."""
        if self.redis_client:
            await self.redis_client.close()

    def create_scheduled_task(
        self, task_data: ScheduledTaskCreate
    ) -> ScheduledTaskResponse:
        """Создать запланированную задачу."""
        try:
            if not croniter.is_valid(task_data.cron_schedule):
                raise ValueError(
                    f"Некорректное cron выражение: {task_data.cron_schedule}"
                )

            cron = croniter(task_data.cron_schedule, datetime.now())
            next_run_at = cron.get_next(datetime)

            query = """
                INSERT INTO scheduled_tasks 
                (name, task_type, connection_id, cron_schedule, is_active, next_run_at, task_params, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """

            result = self.db_service.fetch_one(
                query,
                task_data.name,
                task_data.task_type.value,
                task_data.connection_id,
                task_data.cron_schedule,
                task_data.is_active,
                next_run_at,
                json.dumps(task_data.task_params),
                task_data.description,
            )

            if not result:
                raise ValueError(ERROR_TASK_CREATION_FAILED)

            logger.info(f"Создана запланированная задача: {task_data.name}")
            return ScheduledTaskResponse(**dict(result))

        except Exception as e:
            logger.error(f"Ошибка создания задачи: {e}")
            raise

    def update_scheduled_task(
        self, task_id: int, task_data: ScheduledTaskUpdate
    ) -> Optional[ScheduledTaskResponse]:
        """Обновить запланированную задачу."""
        try:
            current_task = self.get_scheduled_task(task_id)
            if not current_task:
                return None

            update_fields = []
            values = []

            if task_data.name is not None:
                update_fields.append("name = %s")
                values.append(task_data.name)

            if task_data.cron_schedule is not None:
                if not croniter.is_valid(task_data.cron_schedule):
                    raise ValueError(
                        f"Некорректное cron выражение: {task_data.cron_schedule}"
                    )

                update_fields.append("cron_schedule = %s")
                values.append(task_data.cron_schedule)

                cron = croniter(task_data.cron_schedule, datetime.now())
                next_run_at = cron.get_next(datetime)
                update_fields.append("next_run_at = %s")
                values.append(next_run_at)

            if task_data.task_params is not None:
                update_fields.append("task_params = %s")
                values.append(json.dumps(task_data.task_params))

            if task_data.description is not None:
                update_fields.append("description = %s")
                values.append(task_data.description)

            if task_data.is_active is not None:
                update_fields.append("is_active = %s")
                values.append(task_data.is_active)

            if not update_fields:
                return current_task

            values.append(task_id)
            query = f"""
                UPDATE scheduled_tasks 
                SET {', '.join(update_fields)}
                WHERE id = %s
                RETURNING *
            """

            result = self.db_service.fetch_one(query, *values)
            if result:
                logger.info(f"Обновлена задача ID: {task_id}")
                return ScheduledTaskResponse(**dict(result))

            return None

        except Exception as e:
            logger.error(f"Ошибка обновления задачи {task_id}: {e}")
            raise

    async def remove_task_from_schedule(self, task_id: int) -> bool:
        """Удалить задачу только из планировщика (без удаления из БД)."""
        try:
            removed_count = 0
            cancelled_executions = 0

            if self.redis_client:
                queue_tasks = await self.redis_client.lrange("task_queue", 0, -1)

                await self.redis_client.delete("task_queue")

                for task_json in queue_tasks:
                    try:
                        task_data = json.loads(task_json)
                        if task_data.get("scheduled_task_id") != task_id:
                            await self.redis_client.lpush("task_queue", task_json)
                        else:
                            removed_count += 1
                    except json.JSONDecodeError:
                        await self.redis_client.lpush("task_queue", task_json)

            try:
                cancel_query = """
                    UPDATE task_executions 
                    SET status = 'cancelled', completed_at = NOW()
                    WHERE scheduled_task_id = %s AND status IN ('running', 'pending')
                """
                await self.db_service.execute_query(cancel_query, task_id)

                count_query = """
                    SELECT COUNT(*) FROM task_executions 
                    WHERE scheduled_task_id = %s AND status = 'cancelled'
                """
                result = self.db_service.fetch_one(count_query, task_id)
                if result:
                    cancelled_executions = result[0] or 0

            except Exception as db_error:
                logger.warning(
                    f"Не удалось отменить выполнения задачи {task_id}: {db_error}"
                )

            logger.info(
                f"Задача ID: {task_id} удалена из планировщика. Удалено из очереди: {removed_count}, отменено выполнений: {cancelled_executions}"
            )
            return True

        except Exception as e:
            logger.error(f"Ошибка удаления задачи {task_id} из планировщика: {e}")
            raise

    async def delete_scheduled_task(self, task_id: int) -> bool:
        """Удалить запланированную задачу."""
        try:
            query = "DELETE FROM scheduled_tasks WHERE id = %s"
            result = await self.db_service.execute_query(query, task_id)

            if result:
                logger.info(f"Удалена задача ID: {task_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"Ошибка удаления задачи {task_id}: {e}")
            raise

    def get_scheduled_task(self, task_id: int) -> Optional[ScheduledTaskResponse]:
        """Получить запланированную задачу по ID."""
        try:
            from src.models.base import get_db
            from src.models.tasks import ScheduledTask

            db = next(get_db())
            try:
                task = (
                    db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()
                )

                if task:
                    task_dict = _prepare_task_dict(task.to_dict())
                    return ScheduledTaskResponse(**task_dict)
                return None
            finally:
                db.close()

        except Exception as e:
            logger.error(f"Ошибка получения задачи {task_id}: {e}")
            raise

    def get_scheduled_tasks(
        self, is_active: Optional[bool] = None
    ) -> List[ScheduledTaskResponse]:
        """Получить список запланированных задач."""
        try:
            from src.models.base import get_db
            from src.models.tasks import ScheduledTask

            db = next(get_db())
            try:
                query = db.query(ScheduledTask).order_by(
                    ScheduledTask.created_at.desc()
                )

                if is_active is not None:
                    query = query.filter(ScheduledTask.is_active == is_active)

                tasks = []
                for task in query.all():
                    task_dict = _prepare_task_dict(task.to_dict())
                    tasks.append(ScheduledTaskResponse(**task_dict))

                return tasks
            finally:
                db.close()

        except Exception as e:
            logger.error(f"Ошибка получения списка задач: {e}")
            raise

    def get_due_tasks(self) -> List[ScheduledTaskResponse]:
        """Получить задачи, готовые к выполнению."""
        try:
            from src.models.base import get_db
            from src.models.tasks import ScheduledTask

            now = datetime.now()
            db = next(get_db())
            try:
                tasks_query = (
                    db.query(ScheduledTask)
                    .filter(
                        ScheduledTask.is_active == True,
                        ScheduledTask.next_run_at <= now,
                    )
                    .order_by(ScheduledTask.next_run_at.asc())
                )

                tasks = []
                for task in tasks_query.all():
                    task_dict = _prepare_task_dict(task.to_dict())
                    tasks.append(ScheduledTaskResponse(**task_dict))

                return tasks
            finally:
                db.close()

        except Exception as e:
            logger.error(f"Ошибка получения готовых задач: {e}")
            raise

    async def schedule_task_execution(self, task: ScheduledTaskResponse) -> int:
        """Запланировать выполнение задачи."""
        try:
            execution_data = TaskExecutionCreate(
                task_type=task.task_type,
                connection_id=task.connection_id,
                scheduled_task_id=task.id,
                parameters=task.task_params,
            )

            execution_id = await self.db_service.create_task_execution(
                task_type=execution_data.task_type.value,
                connection_id=execution_data.connection_id,
                scheduled_task_id=execution_data.scheduled_task_id,
                parameters=execution_data.parameters,
            )

            queue_item = TaskQueueItem(
                execution_id=execution_id,
                task_type=task.task_type,
                connection_id=task.connection_id,
                scheduled_task_id=task.id,
                parameters=task.task_params,
                priority=1,
            )

            await self.redis_client.lpush("task_queue", queue_item.model_dump_json())

            cron = croniter(task.cron_schedule, datetime.now())
            next_run_at = cron.get_next(datetime)

            await self.db_service.execute_query(
                "UPDATE scheduled_tasks SET last_run_at = %s, next_run_at = %s WHERE id = %s",
                datetime.now(),
                next_run_at,
                task.id,
            )

            logger.info(
                f"Запланировано выполнение задачи {task.name} (execution_id: {execution_id})"
            )
            return execution_id

        except Exception as e:
            logger.error(f"Ошибка планирования выполнения задачи {task.id}: {e}")
            raise

    async def execute_task_manually(self, task_id: int) -> dict:
        """Запустить задачу вручную."""
        try:
            task = self.get_scheduled_task(task_id)
            if not task:
                raise ValueError(f"Задача {task_id} не найдена")

            if not task.is_active:
                raise ValueError(f"Задача {task_id} неактивна")

            execution_data = TaskExecutionCreate(
                task_type=task.task_type,
                connection_id=task.connection_id,
                scheduled_task_id=task.id,
                parameters=task.task_params.model_dump() if task.task_params else {},
            )

            execution_id = self.db_service.create_task_execution(
                task_type=execution_data.task_type.value,
                connection_id=execution_data.connection_id,
                scheduled_task_id=execution_data.scheduled_task_id,
                parameters=execution_data.parameters,
            )

            queue_item = TaskQueueItem(
                execution_id=execution_id,
                task_type=task.task_type,
                connection_id=task.connection_id,
                scheduled_task_id=task.id,
                parameters=task.task_params.model_dump() if task.task_params else {},
                priority=10,
            )

            await self.redis_client.lpush("task_queue", queue_item.model_dump_json())

            logger.info(
                f"Ручной запуск задачи {task.name} (execution_id: {execution_id})"
            )

            return {
                "id": execution_id,
                "task_id": task_id,
                "task_name": task.name,
                "status": "queued",
            }

        except Exception as e:
            logger.error(f"Ошибка ручного запуска задачи {task_id}: {e}")
            raise

    async def queue_task(self, task_id: int):
        """Добавить задачу в очередь для немедленного выполнения."""
        try:
            task = self.get_scheduled_task(task_id)
            if not task:
                raise ValueError(f"Задача {task_id} не найдена")

            execution_query = """
                INSERT INTO task_executions (scheduled_task_id, task_type, connection_id, status, parameters)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """

            execution_result = self.db_service.fetch_one(
                execution_query,
                task.id,
                task.task_type.value,
                task.connection_id,
                "running",
                json.dumps(task.task_params.model_dump() if task.task_params else {}),
            )

            if not execution_result:
                raise RuntimeError("Не удалось создать запись выполнения")

            execution_id = execution_result["id"]

            task_queue_item = TaskQueueItem(
                execution_id=execution_id,
                task_type=task.task_type,
                connection_id=task.connection_id,
                scheduled_task_id=task.id,
                parameters=task.task_params.model_dump() if task.task_params else {},
            )

            await self.redis_client.lpush(
                "task_queue", json.dumps(task_queue_item.model_dump())
            )

            logger.info(
                f"Задача {task_id} добавлена в очередь с execution_id {execution_id}"
            )

        except Exception as e:
            logger.error(f"Ошибка добавления задачи {task_id} в очередь: {e}")
            raise

    async def start_scheduler_loop(self):
        """Запустить основной цикл планировщика."""
        self.is_running = True
        logger.info("Запущен цикл планировщика")

        while self.is_running:
            try:
                due_tasks = self.get_due_tasks()

                for task in due_tasks:
                    try:
                        await self.schedule_task_execution(task)
                    except Exception as e:
                        logger.error(f"Ошибка при планировании задачи {task.id}: {e}")
                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Ошибка в цикле планировщика: {e}")
                await asyncio.sleep(60)

        logger.info("Цикл планировщика остановлен")

    def stop_scheduler(self):
        """Остановить планировщик."""
        self.is_running = False
        logger.info("Получен сигнал остановки планировщика")

    async def start(self):
        """Запустить планировщик (API метод)."""
        if not self.is_running:
            self.is_running = True
            task = asyncio.create_task(self.start_scheduler_loop())
            self._scheduler_task = task
            await asyncio.sleep(0.1)
            logger.info("Планировщик запущен через API")
        else:
            logger.info("Планировщик уже запущен")

    async def stop(self):
        """Остановить планировщик (API метод)."""
        self.stop_scheduler()
        if hasattr(self, "_scheduler_task"):
            try:
                self._scheduler_task.cancel()
                await self._scheduler_task
            except asyncio.CancelledError:
                logger.debug("Scheduler task cancelled")
                raise
        logger.info("Планировщик остановлен через API")

    async def get_status(self):
        """Получить статус планировщика."""
        try:
            from src.models.base import get_db
            from src.models.tasks import ScheduledTask, TaskExecution
            from sqlalchemy import func
            from datetime import datetime, timedelta

            db = next(get_db())
            try:
                total_tasks = db.query(ScheduledTask).count()
                active_tasks = (
                    db.query(ScheduledTask)
                    .filter(ScheduledTask.is_active == True)
                    .count()
                )

                last_24h = datetime.now() - timedelta(hours=24)
                recent_executions = (
                    db.query(TaskExecution)
                    .filter(TaskExecution.started_at >= last_24h)
                    .count()
                )

                failed_executions = (
                    db.query(TaskExecution)
                    .filter(
                        TaskExecution.status == "failed",
                        TaskExecution.started_at >= last_24h,
                    )
                    .count()
                )
            finally:
                db.close()

            redis_status = "connected" if self.redis_client else "disconnected"
            if self.redis_client:
                try:
                    await self.redis_client.ping()
                except Exception:
                    redis_status = "error"

            return {
                "scheduler_running": self.is_running,
                "redis_status": redis_status,
                "stats": {
                    "total_tasks": total_tasks or 0,
                    "active_tasks": active_tasks or 0,
                    "executions_24h": recent_executions or 0,
                    "failed_executions_24h": failed_executions or 0,
                },
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Ошибка получения статуса: {e}")
            return {
                "scheduler_running": self.is_running,
                "redis_status": "unknown",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def get_stats(self):
        """Получить детальную статистику планировщика."""
        try:
            from src.models.base import get_db
            from src.models.tasks import ScheduledTask, TaskExecution
            from sqlalchemy import func, case, extract, text
            from datetime import datetime, timedelta

            db = next(get_db())
            try:
                task_types_stats = (
                    db.query(
                        ScheduledTask.task_type,
                        func.count(ScheduledTask.id).label("count"),
                        func.sum(
                            case((ScheduledTask.is_active == True, 1), else_=0)
                        ).label("active_count"),
                    )
                    .group_by(ScheduledTask.task_type)
                    .all()
                )

                daily_stats = db.execute(
                    text(
                        """
                    SELECT DATE(started_at) as date, 
                           COUNT(*) as total_executions,
                           SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful,
                           SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                           AVG(EXTRACT(EPOCH FROM (completed_at - started_at))) as avg_duration_seconds
                    FROM task_executions 
                    WHERE started_at >= NOW() - INTERVAL '7 days'
                    GROUP BY DATE(started_at)
                    ORDER BY date DESC
                """
                    )
                ).fetchall()

                top_tasks = db.execute(
                    text(
                        """
                    SELECT st.name, st.task_type, COUNT(te.id) as execution_count,
                           AVG(EXTRACT(EPOCH FROM (te.completed_at - te.started_at))) as avg_duration
                    FROM scheduled_tasks st
                    LEFT JOIN task_executions te ON st.id = te.scheduled_task_id
                    WHERE te.started_at >= NOW() - INTERVAL '30 days'
                    GROUP BY st.id, st.name, st.task_type
                    ORDER BY execution_count DESC
                    LIMIT 10
                """
                    )
                ).fetchall()
            finally:
                db.close()

            return {
                "task_types": [
                    {
                        "task_type": row.task_type,
                        "total_count": row.count,
                        "active_count": row.active_count or 0,
                    }
                    for row in task_types_stats
                ],
                "daily_stats": [
                    {
                        "date": row[0].isoformat() if row[0] else None,
                        "total_executions": row[1] or 0,
                        "successful": row[2] or 0,
                        "failed": row[3] or 0,
                        "avg_duration_seconds": float(row[4]) if row[4] else 0,
                    }
                    for row in daily_stats
                ],
                "top_tasks": [
                    {
                        "name": row[0],
                        "task_type": row[1],
                        "execution_count": row[2] or 0,
                        "avg_duration_seconds": float(row[3]) if row[3] else 0,
                    }
                    for row in top_tasks
                ],
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def get_queue_status(self):
        """Получить статус очереди задач."""
        try:
            queue_length = 0
            pending_tasks = []

            if self.redis_client:
                queue_length = await self.redis_client.llen("task_queue")

                raw_tasks = await self.redis_client.lrange("task_queue", 0, 9)

                for raw_task in raw_tasks:
                    try:
                        task_data = json.loads(raw_task)
                        pending_tasks.append(
                            {
                                "task_id": task_data.get("task_id"),
                                "task_name": task_data.get("task_name"),
                                "task_type": task_data.get("task_type"),
                                "queued_at": task_data.get("queued_at"),
                                "priority": task_data.get("priority", 0),
                            }
                        )
                    except json.JSONDecodeError:
                        continue

            from src.models.base import get_db
            from src.models.tasks import ScheduledTask, TaskExecution

            db = next(get_db())
            try:
                running_tasks_query = (
                    db.query(
                        TaskExecution.id,
                        ScheduledTask.name,
                        ScheduledTask.task_type,
                        TaskExecution.started_at,
                        TaskExecution.status,
                    )
                    .join(
                        ScheduledTask,
                        TaskExecution.scheduled_task_id == ScheduledTask.id,
                    )
                    .filter(TaskExecution.status == "running")
                    .order_by(TaskExecution.started_at)
                )

                running_tasks = running_tasks_query.all()
            finally:
                db.close()

            return {
                "queue_length": queue_length,
                "pending_tasks": pending_tasks,
                "running_tasks": [
                    {
                        "execution_id": row.id,
                        "task_name": row.name,
                        "task_type": row.task_type,
                        "started_at": (
                            row.started_at.isoformat() if row.started_at else None
                        ),
                        "status": row.status,
                    }
                    for row in running_tasks
                ],
                "redis_connected": self.redis_client is not None,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Ошибка получения статуса очереди: {e}")
            return {
                "error": str(e),
                "queue_length": 0,
                "pending_tasks": [],
                "running_tasks": [],
                "redis_connected": False,
                "timestamp": datetime.now().isoformat(),
            }
