"""
Схемы Pydantic для запросов и ответов сервера.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class ReviewRequest(BaseModel):
    """Модель запроса для SQL анализа."""

    sql: str
    query_plan: str = ""
    tables: List[Dict[str, Any]]
    server_info: Dict[str, str]
    thread_id: Optional[str] = None
    environment: Optional[str] = None


class ConfigRequest(BaseModel):
    """Модель запроса для анализа конфигурации."""

    config: Dict[str, Any]
    environment: str = "test"


class BatchReviewRequest(BaseModel):
    """Модель запроса для пакетного анализа SQL."""

    queries: List[ReviewRequest]
    environment: str = "test"


class BatchReviewResponse(BaseModel):
    """Модель ответа для пакетного анализа SQL."""

    results: List[Dict[str, Any]]
    overall_score: float
    passed: bool


class IngestRequest(BaseModel):
    """Модель запроса для загрузки правил."""

    rules_dir: str


class ReviewResponse(BaseModel):
    """Модель ответа для SQL анализа."""

    issues: List[Dict[str, Any]]
    overall_score: float
    thread_id: str


class ConfigAnalysisResponse(BaseModel):
    """Модель ответа для анализа конфигурации."""

    issues: List[Dict[str, Any]]
    overall_score: float
