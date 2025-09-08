"""
Дополнительные модели для нормализации базы данных (3НФ).
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from .base import Base

connection_tags = Table(
    "connection_tags",
    Base.metadata,
    Column("connection_id", Integer, ForeignKey("connections.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class Tag(Base):
    """Модель тега."""

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)

    connections = relationship(
        "Connection", secondary=connection_tags, back_populates="tag_objects"
    )

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"

    def to_dict(self):
        return {"id": self.id, "name": self.name}
