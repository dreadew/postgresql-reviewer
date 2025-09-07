"""
Модели для планировщика задач.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from enum import Enum


class TaskType(str, Enum):
    LOG_ANALYSIS = "log_analysis"
    CONFIG_CHECK = "config_check"
    QUERY_ANALYSIS = "query_analysis"
    CUSTOM_SQL = "custom_sql"
    TABLE_ANALYSIS = "table_analysis"


class AnalysisTarget(str, Enum):
    LOGS = "logs"
    CONFIG = "config"
    PERFORMANCE = "performance"
    SECURITY = "security"
    TABLES = "tables"
    QUERIES = "queries"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskParameters(BaseModel):
    """Параметры выполнения задач."""

    analysis_target: Optional[AnalysisTarget] = None
    environment: Optional[str] = "production"

    log_level: Optional[str] = None
    log_source: Optional[str] = None
    time_range_hours: Optional[int] = 24

    config_sections: Optional[list] = None
    check_performance: Optional[bool] = True
    check_security: Optional[bool] = True

    custom_sql: Optional[str] = None
    target_tables: Optional[list] = None
    query_timeout: Optional[int] = 300

    output_format: Optional[str] = "json"
    detailed_analysis: Optional[bool] = False


class ScheduledTaskCreate(BaseModel):
    name: str
    task_type: TaskType
    connection_id: int
    cron_schedule: str
    description: Optional[str] = None
    task_params: Optional[TaskParameters] = None
    is_active: bool = True


class ScheduledTaskUpdate(BaseModel):
    name: Optional[str] = None
    cron_schedule: Optional[str] = None
    description: Optional[str] = None
    task_params: Optional[TaskParameters] = None
    is_active: Optional[bool] = None


class ScheduledTaskResponse(BaseModel):
    id: int
    name: str
    task_type: TaskType
    connection_id: int
    cron_schedule: str
    is_active: bool
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    task_params: Optional[TaskParameters] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class TaskExecutionCreate(BaseModel):
    task_type: TaskType
    connection_id: int
    scheduled_task_id: Optional[int] = None
    parameters: Optional[Dict[str, Any]] = {}


class TaskExecutionResponse(BaseModel):
    id: int
    task_type: TaskType
    connection_id: int
    scheduled_task_id: Optional[int] = None
    status: TaskStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    parameters: Dict[str, Any]

    class Config:
        from_attributes = True


class TaskQueueItem(BaseModel):
    """Элемент очереди задач для Redis."""

    execution_id: int
    task_type: TaskType
    connection_id: int
    scheduled_task_id: Optional[int] = None
    parameters: Dict[str, Any] = {}
    priority: int = 0
    retry_count: int = 0
    max_retries: int = 3
