"""
Базовый абстрактный класс для репозиториев.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Generic, TypeVar, Type
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BaseRepository(Generic[T], ABC):
    """Базовый абстрактный класс для всех репозиториев."""

    def __init__(self, db: Session, model_class: Type[T]):
        self.db = db
        self.model_class = model_class

    def create(self, data: Dict[str, Any]) -> T:
        """Создать новую запись."""
        try:
            instance = self.model_class(**data)
            self.db.add(instance)
            self.db.commit()
            self.db.refresh(instance)

            logger.info(f"Created {self.model_class.__name__}: {instance.id}")
            return instance

        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Failed to create {self.model_class.__name__}: {e}")
            raise ValueError(f"Failed to create {self.model_class.__name__}: {str(e)}")

    def get_by_id(self, record_id: int) -> Optional[T]:
        """Получить запись по ID."""
        return (
            self.db.query(self.model_class)
            .filter(self.model_class.id == record_id)
            .first()
        )

    def get_all(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[T]:
        """Получить все записи."""
        query = self.db.query(self.model_class)
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        return query.all()

    def update(self, record_id: int, update_data: Dict[str, Any]) -> Optional[T]:
        """Обновить запись."""
        try:
            instance = self.get_by_id(record_id)
            if not instance:
                return None

            for key, value in update_data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)

            self.db.commit()
            self.db.refresh(instance)

            logger.info(f"Updated {self.model_class.__name__}: {instance.id}")
            return instance

        except IntegrityError as e:
            self.db.rollback()
            logger.error(
                f"Failed to update {self.model_class.__name__} {record_id}: {e}"
            )
            raise ValueError(f"Update failed: {str(e)}")

    def delete(self, record_id: int) -> bool:
        """Удалить запись."""
        try:
            instance = self.get_by_id(record_id)
            if not instance:
                return False

            self.db.delete(instance)
            self.db.commit()

            logger.info(f"Deleted {self.model_class.__name__}: {record_id}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(
                f"Failed to delete {self.model_class.__name__} {record_id}: {e}"
            )
            return False

    def count(self) -> int:
        """Получить количество записей."""
        return self.db.query(self.model_class).count()

    def exists(self, record_id: int) -> bool:
        """Проверить существование записи."""
        return (
            self.db.query(self.model_class)
            .filter(self.model_class.id == record_id)
            .first()
            is not None
        )

    @abstractmethod
    def get_filtered(self, filters: Dict[str, Any]) -> List[T]:
        """
        Абстрактный метод для получения отфильтрованных записей.
        Должен быть реализован в каждом конкретном репозитории.
        """
        pass

    def _apply_filters(self, query, filters: Dict[str, Any]):
        """Вспомогательный метод для применения фильтров к запросу."""
        for key, value in filters.items():
            if hasattr(self.model_class, key) and value is not None:
                query = query.filter(getattr(self.model_class, key) == value)
        return query
