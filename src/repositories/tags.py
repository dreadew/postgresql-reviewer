"""
Репозиторий для работы с тегами.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models.tags import Tag
from .base import BaseRepository
import logging

logger = logging.getLogger(__name__)


class TagRepository(BaseRepository[Tag]):
    """Репозиторий для работы с тегами."""

    def __init__(self, db: Session):
        super().__init__(db, Tag)

    def get_or_create(self, name: str) -> Tag:
        """Получить тег по имени или создать новый."""
        tag = self.db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name)
            self.db.add(tag)
            try:
                self.db.commit()
                self.db.refresh(tag)
                logger.info(f"Created new tag: {name}")
            except IntegrityError:
                self.db.rollback()
                # Возможно тег уже создан в другой транзакции
                tag = self.db.query(Tag).filter(Tag.name == name).first()
                if not tag:
                    raise
        return tag

    def get_by_name(self, name: str) -> Optional[Tag]:
        """Получить тег по имени."""
        return self.db.query(Tag).filter(Tag.name == name).first()

    def get_by_names(self, names: List[str]) -> List[Tag]:
        """Получить теги по списку имен."""
        return self.db.query(Tag).filter(Tag.name.in_(names)).all()

    def get_filtered(self, **filters) -> List[Tag]:
        """Получить теги с фильтрацией."""
        query = self.db.query(Tag)
        for key, value in filters.items():
            if hasattr(Tag, key) and value is not None:
                query = query.filter(getattr(Tag, key) == value)
        return query.all()

    def get_or_create_multiple(self, names: List[str]) -> List[Tag]:
        """Получить или создать несколько тегов."""
        tags = []
        for name in names:
            tag = self.get_or_create(name)
            tags.append(tag)
        return tags
