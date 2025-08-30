"""
Инъекция зависимостей для FastAPI.
"""

from typing import Generator
from fastapi import HTTPException, status
from src.services.review_service import ReviewService
import os


def get_review_service() -> Generator[ReviewService, None, None]:
    """Зависимость для ReviewService."""
    api_key = os.getenv("GIGACHAT_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GIGACHAT_API_KEY не найден.",
        )

    service = ReviewService(api_key=api_key)
    yield service


def get_environment() -> str:
    """Получить текущее окружение."""
    return os.getenv("ENVIRONMENT", "test")
