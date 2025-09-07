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

    async def update_scheduled_task(
        self, task_id: int, task_data: ScheduledTaskUpdate
    ) -> Optional[ScheduledTaskResponse]:
        """Обновить запланированную задачу."""
        try:
            current_task = await self.get_scheduled_task(task_id)
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
            query = "SELECT * FROM scheduled_tasks WHERE id = %s"
            result = self.db_service.fetch_one(query, task_id)

            if result:
                task_dict = dict(result)
                task_params = task_dict.get("task_params", "{}")
                if isinstance(task_params, str):
                    task_dict["task_params"] = json.loads(task_params)
                elif task_params is None:
                    task_dict["task_params"] = {}
                return ScheduledTaskResponse(**task_dict)
            return None

        except Exception as e:
            logger.error(f"Ошибка получения задачи {task_id}: {e}")
            raise

    def get_scheduled_tasks(
        self, is_active: Optional[bool] = None
    ) -> List[ScheduledTaskResponse]:
        """Получить список запланированных задач."""
        try:
            if is_active is not None:
                query = "SELECT * FROM scheduled_tasks WHERE is_active = %s ORDER BY created_at DESC"
                results = self.db_service.fetch_all(query, is_active)
            else:
                query = "SELECT * FROM scheduled_tasks ORDER BY created_at DESC"
                results = self.db_service.fetch_all(query)

            tasks = []
            for result in results:
                task_dict = dict(result)
                task_params = task_dict.get("task_params", "{}")
                if isinstance(task_params, str):
                    task_dict["task_params"] = json.loads(task_params)
                elif task_params is None:
                    task_dict["task_params"] = {}
                tasks.append(ScheduledTaskResponse(**task_dict))

            return tasks

        except Exception as e:
            logger.error(f"Ошибка получения списка задач: {e}")
            raise

    def get_due_tasks(self) -> List[ScheduledTaskResponse]:
        """Получить задачи, готовые к выполнению."""
        try:
            now = datetime.now()
            query = """
                SELECT * FROM scheduled_tasks 
                WHERE is_active = true 
                AND next_run_at <= %s
                ORDER BY next_run_at ASC
            """

            results = self.db_service.fetch_all(query, now)
            tasks = []

            for result in results:
                task_dict = dict(result)
                task_params = task_dict.get("task_params", "{}")
                if isinstance(task_params, str):
                    task_dict["task_params"] = json.loads(task_params)
                elif task_params is None:
                    task_dict["task_params"] = {}
                tasks.append(ScheduledTaskResponse(**task_dict))

            return tasks

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
                due_tasks = await self.get_due_tasks()

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
