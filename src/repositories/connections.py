"""
Репозиторий для работы с подключениями к базам данных.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
import logging

from ..models.connections import Connection, ConnectionStatus
from .base import BaseRepository
from .tags import TagRepository

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)


class ConnectionRepository(BaseRepository[Connection]):
    """Репозиторий для работы с подключениями."""

    def __init__(self, db: Session):
        super().__init__(db, Connection)
        self.tag_repo = TagRepository(db)

    def create(self, connection_data: Dict[str, Any]) -> Connection:
        """Создать новое подключение с тегами."""
        try:
            existing = (
                self.db.query(Connection.id)
                .filter(Connection.name == connection_data["name"])
                .first()
            )
            if existing:
                raise ValueError(
                    f"Connection with name '{connection_data['name']}' already exists"
                )

            tags_data = connection_data.pop("tags", [])

            connection = Connection(
                name=connection_data["name"],
                vault_path=connection_data["vault_path"],
                environment=connection_data.get("environment", "development"),
                description=connection_data.get("description"),
                is_active=connection_data.get("is_active", True),
            )

            if tags_data:
                tag_objects = self.tag_repo.get_or_create_multiple(tags_data)
                connection.tag_objects = tag_objects

            self.db.add(connection)
            self.db.commit()
            self.db.refresh(connection)

            logger.info(f"Created connection: {connection.name}")
            return connection

        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Failed to create connection: {e}")
            raise ValueError(
                f"Connection with name '{connection_data['name']}' already exists"
            )

    def get_by_id(self, connection_id: int) -> Optional[Connection]:
        """Получить подключение по ID с загруженными тегами."""
        return (
            self.db.query(Connection)
            .options(joinedload(Connection.tag_objects))
            .filter(Connection.id == connection_id)
            .first()
        )

    def get_all(self) -> List[Connection]:
        """Получить все подключения с загруженными тегами."""
        return (
            self.db.query(Connection)
            .options(joinedload(Connection.tag_objects))
            .order_by(Connection.created_at.desc())
            .all()
        )

    def update(
        self, connection_id: int, update_data: Dict[str, Any]
    ) -> Optional[Connection]:
        """Обновить подключение с поддержкой тегов."""
        try:
            connection = self.get_by_id(connection_id)
            if not connection:
                return None

            if "tags" in update_data:
                tags_data = update_data.pop("tags")
                if isinstance(tags_data, list):
                    tag_objects = self.tag_repo.get_or_create_multiple(tags_data)
                    connection.tag_objects = tag_objects

            for key, value in update_data.items():
                if hasattr(connection, key):
                    setattr(connection, key, value)

            self.db.commit()
            self.db.refresh(connection)

            logger.info(f"Updated connection: {connection.name}")
            return connection

        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Failed to update connection {connection_id}: {e}")
            raise ValueError(f"Update failed: {str(e)}")

    def add_tag(self, connection_id: int, tag_name: str) -> bool:
        """Добавить тег к подключению."""
        try:
            connection = self.get_by_id(connection_id)
            if not connection:
                return False

            tag = self.tag_repo.get_or_create(tag_name)
            if tag not in connection.tag_objects:
                connection.tag_objects.append(tag)
                self.db.commit()
                logger.info(f"Added tag '{tag_name}' to connection {connection.name}")

            return True
        except Exception as e:
            self.db.rollback()
            logger.error(
                f"Failed to add tag {tag_name} to connection {connection_id}: {e}"
            )
            return False

    def remove_tag(self, connection_id: int, tag_name: str) -> bool:
        """Удалить тег у подключения."""
        try:
            connection = self.get_by_id(connection_id)
            if not connection:
                return False

            tag = self.tag_repo.get_by_name(tag_name)
            if tag and tag in connection.tag_objects:
                connection.tag_objects.remove(tag)
                self.db.commit()
                logger.info(
                    f"Removed tag '{tag_name}' from connection {connection.name}"
                )

            return True
        except Exception as e:
            self.db.rollback()
            logger.error(
                f"Failed to remove tag {tag_name} from connection {connection_id}: {e}"
            )
            return False

    def get_by_name(self, name: str) -> Optional[Connection]:
        """Получить подключение по имени."""
        return self.db.query(Connection).filter(Connection.name == name).first()

    def get_filtered(self, filters: Dict[str, Any]) -> List[Connection]:
        """Получить отфильтрованные подключения."""
        query = self.db.query(Connection)
        query = self._apply_filters(query, filters)
        return query.order_by(Connection.created_at.desc()).all()

    def get_active_connections(self) -> List[Connection]:
        """Получить все активные подключения."""
        return self.get_filtered({"is_active": True})

    def get_by_environment(self, environment: str) -> List[Connection]:
        """Получить подключения по окружению."""
        return self.get_filtered({"environment": environment})


class ConnectionStatusRepository(BaseRepository[ConnectionStatus]):
    """Репозиторий для работы со статусами подключений."""

    def __init__(self, db: Session):
        super().__init__(db, ConnectionStatus)

    def get_filtered(self, filters: Dict[str, Any]) -> List[ConnectionStatus]:
        """Получить отфильтрованные статусы подключений."""
        query = self.db.query(ConnectionStatus)
        query = self._apply_filters(query, filters)
        return query.order_by(ConnectionStatus.last_check.desc()).all()

    def upsert_status(
        self,
        connection_id: int,
        is_healthy: bool,
        error_message: str = None,
        response_time_ms: float = None,
        server_version: str = None,
    ) -> ConnectionStatus:
        """Создать или обновить статус подключения."""
        try:
            status = (
                self.db.query(ConnectionStatus)
                .filter(ConnectionStatus.connection_id == connection_id)
                .first()
            )

            if status:
                status.is_healthy = is_healthy
                status.error_message = error_message
                status.response_time_ms = response_time_ms
                status.server_version = server_version
            else:
                status = ConnectionStatus(
                    connection_id=connection_id,
                    is_healthy=is_healthy,
                    error_message=error_message,
                    response_time_ms=response_time_ms,
                    server_version=server_version,
                )
                self.db.add(status)

            self.db.commit()
            self.db.refresh(status)

            return status

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to upsert connection status {connection_id}: {e}")
            raise

    def get_by_connection_id(self, connection_id: int) -> Optional[ConnectionStatus]:
        """Получить статус подключения по ID подключения."""
        return (
            self.db.query(ConnectionStatus)
            .filter(ConnectionStatus.connection_id == connection_id)
            .first()
        )

    def get_all_healthy(self) -> List[ConnectionStatus]:
        """Получить все здоровые подключения."""
        return (
            self.db.query(ConnectionStatus)
            .filter(ConnectionStatus.is_healthy == True)
            .all()
        )

    def get_all_unhealthy(self) -> List[ConnectionStatus]:
        """Получить все нездоровые подключения."""
        return (
            self.db.query(ConnectionStatus)
            .filter(ConnectionStatus.is_healthy == False)
            .all()
        )
