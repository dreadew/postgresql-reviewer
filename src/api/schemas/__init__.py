"""
Схемы Pydantic для запросов и ответов сервера.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, validator
from datetime import datetime
from enum import Enum
import croniter


class TaskStatus(str, Enum):
    """Статусы выполнения задач."""

    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ConnectionStatus(BaseModel):
    """Статус подключения к БД."""

    connection_id: int
    is_healthy: bool
    last_check: datetime
    error_message: Optional[str] = None
    response_time_ms: Optional[int] = None
    server_version: Optional[str] = None


class TaskExecution(BaseModel):
    """Запуск задачи."""

    id: int
    task_id: int
    status: TaskStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class TaskExecutionCreate(BaseModel):
    """Создание запуска задачи."""

    task_id: int
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class ReviewRequest(BaseModel):
    """Модель запроса для SQL анализа."""

    sql: str
    query_plan: str = ""
    tables: List[Dict[str, Any]]
    server_info: Dict[str, str]
    thread_id: Optional[str] = None
    environment: Optional[str] = None

    @validator("environment")
    def validate_environment(cls, v):
        if v is not None:
            valid_environments = ["dev", "test", "stage", "prod"]
            if v not in valid_environments:
                raise ValueError(f"Environment must be one of: {valid_environments}")
        return v


class ConfigRequest(BaseModel):
    """Модель запроса для анализа конфигурации."""

    config: Dict[str, Any]
    server_info: Dict[str, str]
    environment: str = "test"


class BatchReviewRequest(BaseModel):
    """Модель запроса для пакетного анализа SQL."""

    queries: List[ReviewRequest]
    environment: str = "test"

    @validator("environment")
    def validate_environment(cls, v):
        valid_environments = ["dev", "test", "stage", "prod"]
        if v not in valid_environments:
            raise ValueError(f"Environment must be one of: {valid_environments}")
        return v


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


class TaskBase(BaseModel):
    name: str
    connection_id: int
    schedule: str
    task_type: str
    parameters: Optional[Dict[str, Any]] = None
    is_active: bool = True


class TaskCreate(TaskBase):
    @validator("schedule")
    def validate_cron(cls, v):
        try:
            croniter.croniter(v)
            return v
        except Exception:
            raise ValueError("Invalid cron expression")


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    connection_id: Optional[int] = None
    schedule: Optional[str] = None
    task_type: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

    @validator("schedule")
    def validate_cron(cls, v):
        if v is not None:
            try:
                croniter.croniter(v)
                return v
            except Exception:
                raise ValueError("Invalid cron expression")
        return v


class TaskResponse(TaskBase):
    id: int
    last_run: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ConnectionBase(BaseModel):
    name: str
    vault_path: str
    is_active: bool = True
    environment: str = "development"
    description: Optional[str] = None
    tags: List[str] = []


class ConnectionCreate(ConnectionBase):
    host: str
    port: int = 5432
    database: str
    username: str
    password: str


class ConnectionUpdate(BaseModel):
    name: Optional[str] = None
    vault_path: Optional[str] = None
    is_active: Optional[bool] = None
    environment: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class ConnectionResponse(ConnectionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
