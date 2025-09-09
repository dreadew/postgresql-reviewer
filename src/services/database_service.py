import logging
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from sqlalchemy.orm import Session
from src.core.config import settings
from src.models.base import get_db
from src.repositories.connections import (
    ConnectionRepository,
    ConnectionStatusRepository,
)
from src.repositories.tasks import ScheduledTaskRepository, TaskExecutionRepository

logger = logging.getLogger(__name__)


class DatabaseService:
    """Сервис для работы с PostgreSQL (миграция на SQLAlchemy)."""

    def __init__(self, db: Session = None):
        self.pool = None
        self._init_connection_pool()
        self.db = db or next(get_db())

        self.connection_repo = ConnectionRepository(self.db)
        self.connection_status_repo = ConnectionStatusRepository(self.db)
        self.task_repo = ScheduledTaskRepository(self.db)
        self.execution_repo = TaskExecutionRepository(self.db)

    def _parse_database_url(self, database_url: str) -> Dict[str, Any]:
        """Парсинг database URL для получения параметров подключения."""
        if database_url and database_url.startswith("postgresql://"):
            from urllib.parse import urlparse

            parsed = urlparse(database_url)
            return {
                "host": parsed.hostname or "postgres",
                "port": parsed.port or 5432,
                "database": parsed.path.lstrip("/") or settings.postgres_db,
                "user": parsed.username or settings.postgres_user,
                "password": parsed.password or settings.postgres_password,
            }
        else:
            return {
                "host": "postgres",
                "port": 5432,
                "database": settings.postgres_db,
                "user": settings.postgres_user,
                "password": settings.postgres_password,
            }

    def _init_connection_pool(self):
        """Инициализация пула соединений."""
        try:
            database_url = settings.database_url
            db_params = self._parse_database_url(database_url)

            self.pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=db_params["host"],
                port=db_params["port"],
                database=db_params["database"],
                user=db_params["user"],
                password=db_params["password"],
            )
            logger.info("Пул соединений с PostgreSQL инициализирован")
        except Exception as e:
            logger.error(f"Ошибка инициализации пула соединений: {e}")
            raise

    def get_connection(self):
        """Получить соединение из пула."""
        if not self.pool:
            raise RuntimeError("Пул соединений не инициализирован")
        return self.pool.getconn()

    def release_connection(self, conn):
        """Вернуть соединение в пул."""
        if self.pool:
            self.pool.putconn(conn)

    def execute_query(
        self, query: str, params: tuple = None, fetch: bool = True
    ) -> List[Dict[str, Any]]:
        """Выполнить SQL запрос."""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params or ())
                if fetch:
                    result = cursor.fetchall()
                    return [dict(row) for row in result]
                else:
                    conn.commit()
                    return []
        except Exception as e:
            logger.error(f"Ошибка выполнения запроса: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                self.release_connection(conn)

    def create_connection(self, connection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создать новое подключение (SQLAlchemy)."""
        try:
            connection = self.connection_repo.create(connection_data)
            return connection.to_dict()
        except ValueError as e:
            logger.error(f"Ошибка создания подключения: {e}")
            raise

    def get_connections(self) -> List[Dict[str, Any]]:
        """Получить все подключения (SQLAlchemy)."""
        connections = self.connection_repo.get_all()
        return [conn.to_dict() for conn in connections]

    def get_connection_by_id(self, connection_id: int) -> Optional[Dict[str, Any]]:
        """Получить подключение по ID (SQLAlchemy)."""
        connection = self.connection_repo.get_by_id(connection_id)
        return connection.to_dict() if connection else None

    def update_connection(
        self, connection_id: int, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Обновить подключение (SQLAlchemy)."""
        try:
            connection = self.connection_repo.update(connection_id, update_data)
            return connection.to_dict() if connection else None
        except ValueError as e:
            logger.error(f"Ошибка обновления подключения: {e}")
            raise

    def delete_connection(self, connection_id: int) -> bool:
        """Удалить подключение (SQLAlchemy)."""
        return self.connection_repo.delete(connection_id)

    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создать новую задачу (SQLAlchemy)."""
        try:
            sqlalchemy_data = {
                "name": task_data["name"],
                "connection_id": task_data["connection_id"],
                "cron_schedule": task_data.get(
                    "schedule", task_data.get("cron_schedule")
                ),
                "task_type": task_data["task_type"],
                "task_params": task_data.get(
                    "parameters", task_data.get("task_params", {})
                ),
                "is_active": task_data.get("is_active", True),
                "description": task_data.get("description"),
            }
            task = self.task_repo.create(sqlalchemy_data)
            return task.to_dict()
        except ValueError as e:
            logger.error(f"Ошибка создания задачи: {e}")
            raise

    def get_tasks(self) -> List[Dict[str, Any]]:
        """Получить все задачи (SQLAlchemy)."""
        tasks = self.task_repo.get_all()
        return [task.to_dict() for task in tasks]

    def get_task_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Получить задачу по ID (SQLAlchemy)."""
        task = self.task_repo.get_by_id(task_id)
        return task.to_dict() if task else None

    def update_task(
        self, task_id: int, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Обновить задачу (SQLAlchemy)."""
        try:
            sqlalchemy_data = {}
            if "schedule" in update_data:
                sqlalchemy_data["cron_schedule"] = update_data["schedule"]
            if "parameters" in update_data:
                sqlalchemy_data["task_params"] = update_data["parameters"]

            for key, value in update_data.items():
                if key not in ["schedule", "parameters", "id"]:
                    sqlalchemy_data[key] = value

            task = self.task_repo.update(task_id, sqlalchemy_data)
            return task.to_dict() if task else None
        except ValueError as e:
            logger.error(f"Ошибка обновления задачи: {e}")
            raise

    def delete_task(self, task_id: int) -> bool:
        """Удалить задачу (SQLAlchemy)."""
        return self.task_repo.delete(task_id)

    def update_task_last_run(self, task_id: int, last_run_at: datetime = None) -> bool:
        """Обновить время последнего запуска задачи (SQLAlchemy)."""
        return self.task_repo.update_last_run(task_id, last_run_at)

    def create_task_execution(
        self, task_id: int, connection_id: int = None, task_type: str = None
    ) -> Dict[str, Any]:
        """Создать новое выполнение задачи (SQLAlchemy)."""
        try:
            if not connection_id or not task_type:
                task = self.task_repo.get_by_id(task_id)
                if not task:
                    raise ValueError(f"Задача с ID {task_id} не найдена")
                connection_id = connection_id or task.connection_id
                task_type = task_type or task.task_type

            execution_data = {
                "scheduled_task_id": task_id,
                "connection_id": connection_id,
                "task_type": task_type,
                "status": "running",
                "started_at": datetime.now(timezone.utc),
            }
            execution = self.execution_repo.create(execution_data)
            return execution.to_dict()
        except Exception as e:
            logger.error(f"Ошибка создания выполнения задачи: {e}")
            raise

    def update_task_execution(
        self,
        execution_id: int,
        status: str,
        result: Dict[str, Any] = None,
        error_message: str = None,
    ) -> bool:
        """Обновить выполнение задачи (SQLAlchemy)."""
        try:
            completed_at = (
                datetime.now(timezone.utc)
                if status in ["completed", "failed"]
                else None
            )
            execution = self.execution_repo.update_status(
                execution_id, status, completed_at, result, error_message
            )
            return execution is not None
        except Exception as e:
            logger.error(f"Ошибка обновления выполнения задачи: {e}")
            return False

    def get_task_executions(
        self, task_id: int = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Получить историю выполнения задач (SQLAlchemy)."""
        if task_id:
            executions = self.execution_repo.get_by_task_id(task_id, limit)
        else:
            executions = self.execution_repo.get_all(limit)

        return [execution.to_dict() for execution in executions]

    def update_connection_status(
        self,
        connection_id: int,
        is_healthy: bool,
        error_message: str = None,
        response_time_ms: int = None,
        server_version: str = None,
    ) -> bool:
        """Обновить статус подключения (SQLAlchemy)."""
        try:
            status_data = {
                "connection_id": connection_id,
                "is_healthy": is_healthy,
                "last_check": datetime.now(timezone.utc),
                "error_message": error_message,
                "response_time_ms": response_time_ms,
                "server_version": server_version,
            }

            existing_status = self.connection_status_repo.get_by_connection_id(
                connection_id
            )

            if existing_status:
                self.connection_status_repo.update(existing_status.id, status_data)
            else:
                self.connection_status_repo.create(status_data)

            return True
        except Exception as e:
            logger.error(f"Ошибка обновления статуса подключения: {e}")
            return False

    def get_connection_status(self, connection_id: int = None) -> List[Dict[str, Any]]:
        """Получить статус подключений (SQLAlchemy)."""
        if connection_id:
            status = self.connection_status_repo.get_by_connection_id(connection_id)
            return [status.to_dict()] if status else []
        else:
            statuses = self.connection_status_repo.get_all()
            return [status.to_dict() for status in statuses]

    def fetch_one(self, query: str, *params) -> Optional[Dict[str, Any]]:
        """Выполнение запроса с получением одной записи."""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params if params else ())
                conn.commit()
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"Ошибка выполнения запроса: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                self.release_connection(conn)

    def fetch_all(self, query: str, *params) -> List[Dict[str, Any]]:
        """Выполнение запроса с получением всех записей."""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params if params else ())
                result = cursor.fetchall()
                return [dict(row) for row in result]
        except Exception as e:
            logger.error(f"Ошибка выполнения запроса: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                self.release_connection(conn)

    def execute_query_async(self, query: str, *params) -> bool:
        """Выполнение запроса без возврата данных."""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, params if params else ())
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка выполнения запроса: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                self.release_connection(conn)

    def update_task_execution(self, execution_id: int, **kwargs):
        """Обновить запись выполнения задачи."""
        if not kwargs:
            return

        update_fields = []
        values = []

        for field, value in kwargs.items():
            if field == "status":
                update_fields.append("status = %s")
                values.append(value)
            elif field == "started_at":
                update_fields.append("started_at = %s")
                values.append(value)
            elif field == "completed_at":
                update_fields.append("completed_at = %s")
                values.append(value)
            elif field == "result":
                update_fields.append("result = %s")
                values.append(json.dumps(value) if isinstance(value, dict) else value)
            elif field == "error_message":
                update_fields.append("error_message = %s")
                values.append(value)
            elif field == "duration_ms":
                update_fields.append("duration_ms = %s")
                values.append(value)

        if update_fields:
            values.append(execution_id)
            query = f"""
                UPDATE task_executions 
                SET {', '.join(update_fields)}
                WHERE id = %s
            """

            self.execute_query_async(query, *values)

    def create_task_execution(
        self,
        task_type: str,
        connection_id: int,
        scheduled_task_id: int = None,
        parameters: Dict[str, Any] = None,
    ) -> int:
        """Создать новое выполнение задачи."""
        query = """
            INSERT INTO task_executions (scheduled_task_id, task_type, connection_id, status, parameters, started_at)
            VALUES (%s, %s, %s, 'pending', %s, %s)
            RETURNING id
        """

        result = self.fetch_one(
            query,
            scheduled_task_id,
            task_type,
            connection_id,
            json.dumps(parameters) if parameters else "{}",
            datetime.now(),
        )

        if result:
            return result["id"]
        raise ValueError("Не удалось создать выполнение задачи")


database_service = DatabaseService()
