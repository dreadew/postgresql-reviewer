"""
Модели для работы с подключениями к базам данных.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from typing import List

from .base import Base


class Connection(Base):
    """Модель подключения к базе данных."""

    __tablename__ = "connections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    vault_path = Column(String(500), nullable=False)
    environment = Column(String(50), default="development")
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    tag_objects = relationship(
        "Tag", secondary="connection_tags", back_populates="connections"
    )
    status = relationship(
        "ConnectionStatus", back_populates="connection", uselist=False
    )

    @property
    def tags(self) -> List[str]:
        """Получить список имен тегов."""
        if hasattr(self, "tag_objects") and self.tag_objects is not None:
            return [tag.name for tag in self.tag_objects]
        return []

    def add_tag(self, tag_name: str) -> None:
        """Добавить тег к подключению."""
        from .tags import Tag

        existing_tag = next(
            (tag for tag in self.tag_objects if tag.name == tag_name), None
        )
        if not existing_tag:
            from sqlalchemy.orm import Session

            session = Session.object_session(self)
            if session:
                tag = session.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    session.add(tag)
                self.tag_objects.append(tag)

    def remove_tag(self, tag_name: str) -> None:
        """Удалить тег у подключения."""
        self.tag_objects = [tag for tag in self.tag_objects if tag.name != tag_name]

    def to_dict(self):
        """Преобразовать в словарь."""
        return {
            "id": self.id,
            "name": self.name,
            "vault_path": self.vault_path,
            "environment": self.environment,
            "description": self.description,
            "tags": self.tags,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def __repr__(self):
        return f"<Connection(id={self.id}, name='{self.name}', environment='{self.environment}')>"


class ConnectionStatus(Base):
    """Модель статуса подключения к базе данных."""

    __tablename__ = "connection_status"

    id = Column(Integer, primary_key=True, index=True)
    connection_id = Column(
        Integer, ForeignKey("connections.id"), nullable=False, unique=True
    )
    is_healthy = Column(Boolean, default=False)
    last_check = Column(DateTime(timezone=True), server_default=func.now())
    error_message = Column(Text)
    response_time_ms = Column(Float)
    server_version = Column(String(100))

    connection = relationship("Connection", back_populates="status")

    def to_dict(self):
        """Преобразовать в словарь."""
        return {
            "id": self.id,
            "connection_id": self.connection_id,
            "is_healthy": self.is_healthy,
            "last_check": self.last_check,
            "error_message": self.error_message,
            "response_time_ms": self.response_time_ms,
            "server_version": self.server_version,
        }

    def __repr__(self):
        return f"<ConnectionStatus(connection_id={self.connection_id}, is_healthy={self.is_healthy})>"
