import logging
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
            INSERT INTO connections (name, host, port, database, username, vault_path, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id, name, host, port, database, username, vault_path, is_active,
                     created_at, updated_at
        """
        params = (
            connection_data["name"],
            connection_data["host"],
            connection_data["port"],
            connection_data["database"],
            connection_data["username"],
            connection_data["vault_path"],
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
            if key != "id":  # Не обновляем ID
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
            INSERT INTO tasks (name, connection_id, schedule, task_type, parameters, is_active)
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
        query = "SELECT * FROM tasks ORDER BY created_at DESC"
        return self.execute_query(query)

    def get_task_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Получить задачу по ID."""
        query = "SELECT * FROM tasks WHERE id = %s"
        result = self.execute_query(query, (task_id,))
        return result[0] if result else None

    def update_task(
        self, task_id: int, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Обновить задачу."""
        set_parts = []
        params = []
        for key, value in update_data.items():
            if key != "id":  # Не обновляем ID
                set_parts.append(f"{key} = %s")
                params.append(value)

        if not set_parts:
            return self.get_task_by_id(task_id)

        set_parts.append("updated_at = CURRENT_TIMESTAMP")
        query = f"UPDATE tasks SET {', '.join(set_parts)} WHERE id = %s RETURNING *"
        params.append(task_id)

        result = self.execute_query(query, tuple(params))
        return result[0] if result else None

    def delete_task(self, task_id: int) -> bool:
        """Удалить задачу."""
        query = "DELETE FROM tasks WHERE id = %s"
        try:
            self.execute_query(query, (task_id,), fetch=False)
            return True
        except Exception:
            return False

    def update_task_last_run(self, task_id: int) -> bool:
        """Обновить время последнего запуска задачи."""
        query = "UPDATE tasks SET last_run = CURRENT_TIMESTAMP WHERE id = %s"
        try:
            self.execute_query(query, (task_id,), fetch=False)
            return True
        except Exception:
            return False
