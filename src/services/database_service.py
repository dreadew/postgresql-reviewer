import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from src.core.config import settings

logger = logging.getLogger(__name__)


class DatabaseService:
    """Сервис для работы с PostgreSQL."""

    def __init__(self):
        self.pool = None
        self._init_connection_pool()

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
        """Создать новое подключение."""
        query = """
            INSERT INTO connections (name, vault_path, environment, description, tags, is_active)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, name, vault_path, environment, description, tags, is_active,
                     created_at, updated_at
        """
        params = (
            connection_data["name"],
            connection_data["vault_path"],
            connection_data.get("environment", "development"),
            connection_data.get("description"),
            connection_data.get("tags", []),
            connection_data["is_active"],
        )

        result = self.execute_query(query, params)
        if result:
            return result[0]
        raise ValueError("Не удалось создать подключение")

    def get_connections(self) -> List[Dict[str, Any]]:
        """Получить все подключения."""
        query = "SELECT * FROM connections ORDER BY created_at DESC"
        return self.execute_query(query)

    def get_connection_by_id(self, connection_id: int) -> Optional[Dict[str, Any]]:
        """Получить подключение по ID."""
        query = "SELECT * FROM connections WHERE id = %s"
        result = self.execute_query(query, (connection_id,))
        return result[0] if result else None

    def update_connection(
        self, connection_id: int, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Обновить подключение."""
        set_parts = []
        params = []
        for key, value in update_data.items():
            if key != "id":
                set_parts.append(f"{key} = %s")
                params.append(value)

        if not set_parts:
            return self.get_connection_by_id(connection_id)

        set_parts.append("updated_at = CURRENT_TIMESTAMP")
        query = (
            f"UPDATE connections SET {', '.join(set_parts)} WHERE id = %s RETURNING *"
        )
        params.append(connection_id)

        result = self.execute_query(query, tuple(params))
        return result[0] if result else None

    def delete_connection(self, connection_id: int) -> bool:
        """Удалить подключение."""
        query = "DELETE FROM connections WHERE id = %s"
        try:
            self.execute_query(query, (connection_id,), fetch=False)
            return True
        except Exception:
            return False

    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создать новую задачу."""
        query = """
            INSERT INTO scheduled_tasks (name, connection_id, schedule, task_type, parameters, is_active)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, name, connection_id, schedule, task_type, parameters, is_active,
                     last_run, created_at, updated_at
        """
        params = (
            task_data["name"],
            task_data["connection_id"],
            task_data["schedule"],
            task_data["task_type"],
            task_data.get("parameters", {}),
            task_data["is_active"],
        )

        result = self.execute_query(query, params)
        if result:
            return result[0]
        raise ValueError("Не удалось создать задачу")

    def get_tasks(self) -> List[Dict[str, Any]]:
        """Получить все задачи."""
        query = "SELECT * FROM scheduled_tasks ORDER BY created_at DESC"
        return self.execute_query(query)

    def get_task_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Получить задачу по ID."""
        query = "SELECT * FROM scheduled_tasks WHERE id = %s"
        result = self.execute_query(query, (task_id,))
        return result[0] if result else None

    def update_task(
        self, task_id: int, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Обновить задачу."""
        set_parts = []
        params = []
        for key, value in update_data.items():
            if key != "id":
                set_parts.append(f"{key} = %s")
                params.append(value)

        if not set_parts:
            return self.get_task_by_id(task_id)

        set_parts.append("updated_at = CURRENT_TIMESTAMP")
        query = f"UPDATE scheduled_tasks SET {', '.join(set_parts)} WHERE id = %s RETURNING *"
        params.append(task_id)

        result = self.execute_query(query, tuple(params))
        return result[0] if result else None

    def delete_task(self, task_id: int) -> bool:
        """Удалить задачу."""
        query = "DELETE FROM scheduled_tasks WHERE id = %s"
        try:
            self.execute_query(query, (task_id,), fetch=False)
            return True
        except Exception:
            return False

    def update_task_last_run(self, task_id: int) -> bool:
        """Обновить время последнего запуска задачи."""
        query = "UPDATE scheduled_tasks SET last_run = CURRENT_TIMESTAMP WHERE id = %s"
        try:
            self.execute_query(query, (task_id,), fetch=False)
            return True
        except Exception:
            return False

    def create_task_execution(self, task_id: int) -> Dict[str, Any]:
        """Создать новое выполнение задачи."""
        query = """
            INSERT INTO task_executions (task_id, status, started_at)
            VALUES (%s, 'running', CURRENT_TIMESTAMP)
            RETURNING id, task_id, status, started_at, completed_at, duration_ms, result, error_message
        """
        result = self.execute_query(query, (task_id,))
        if result:
            return result[0]
        raise ValueError("Не удалось создать выполнение задачи")

    def update_task_execution(
        self,
        execution_id: int,
        status: str,
        result: Dict[str, Any] = None,
        error_message: str = None,
    ) -> bool:
        """Обновить выполнение задачи."""
        query = """
            UPDATE task_executions 
            SET status = %s, completed_at = CURRENT_TIMESTAMP, 
                duration_ms = EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - started_at)) * 1000,
                result = %s, error_message = %s
            WHERE id = %s
        """
        try:
            self.execute_query(
                query, (status, result, error_message, execution_id), fetch=False
            )
            return True
        except Exception:
            return False

    def get_task_executions(
        self, task_id: int = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Получить историю выполнения задач."""
        if task_id:
            query = """
                SELECT * FROM task_executions 
                WHERE scheduled_task_id = %s 
                ORDER BY started_at DESC LIMIT %s
            """
            params = (task_id, limit)
        else:
            query = """
                SELECT te.*, st.name as task_name 
                FROM task_executions te 
                LEFT JOIN scheduled_tasks st ON te.scheduled_task_id = st.id 
                ORDER BY te.started_at DESC LIMIT %s
            """
            params = (limit,)

        return self.execute_query(query, params)

    def update_connection_status(
        self,
        connection_id: int,
        is_healthy: bool,
        error_message: str = None,
        response_time_ms: int = None,
        server_version: str = None,
    ) -> bool:
        """Обновить статус подключения."""
        query = """
            INSERT INTO connection_status (connection_id, is_healthy, last_check, error_message, response_time_ms, server_version)
            VALUES (%s, %s, CURRENT_TIMESTAMP, %s, %s, %s)
            ON CONFLICT (connection_id) 
            DO UPDATE SET 
                is_healthy = EXCLUDED.is_healthy,
                last_check = EXCLUDED.last_check,
                error_message = EXCLUDED.error_message,
                response_time_ms = EXCLUDED.response_time_ms,
                server_version = EXCLUDED.server_version
        """
        try:
            self.execute_query(
                query,
                (
                    connection_id,
                    is_healthy,
                    error_message,
                    response_time_ms,
                    server_version,
                ),
                fetch=False,
            )
            return True
        except Exception:
            return False

    def get_connection_status(self, connection_id: int = None) -> List[Dict[str, Any]]:
        """Получить статус подключений."""
        if connection_id:
            query = """
                SELECT cs.*, c.name as connection_name, c.vault_path, c.environment
                FROM connection_status cs
                JOIN connections c ON cs.connection_id = c.id
                WHERE cs.connection_id = %s
            """
            params = (connection_id,)
        else:
            query = """
                SELECT cs.*, c.name as connection_name, c.vault_path, c.environment
                FROM connection_status cs
                JOIN connections c ON cs.connection_id = c.id
                ORDER BY cs.last_check DESC
            """
            params = ()

        return self.execute_query(query, params)

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

    async def create_task_execution(
        self,
        task_type: str,
        connection_id: int,
        scheduled_task_id: int = None,
        parameters: Dict[str, Any] = None,
    ) -> int:
        """Создать новое выполнение задачи (асинхронная версия)."""
        query = """
            INSERT INTO task_executions (scheduled_task_id, task_type, connection_id, status, parameters, started_at)
            VALUES (%s, %s, %s, 'pending', %s, %s)
            RETURNING id
        """

        result = await self.execute_query_async(
            query,
            scheduled_task_id,
            task_type,
            connection_id,
            json.dumps(parameters) if parameters else "{}",
            datetime.now(),
        )

        if result:
            return result[0]["id"]
        raise ValueError("Не удалось создать выполнение задачи")


database_service = DatabaseService()
