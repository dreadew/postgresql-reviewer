"""
Определения типов для системы агентов.
"""

from typing import List, Dict, Any, TypedDict, Optional


class AgentState(TypedDict):
    """Базовое состояние агента."""

    sql: str
    query_plan: str
    tables: List[Dict[str, str]]
    server_info: Dict[str, str]
    retrieved_rules: List[Dict[str, Any]]
    prompt: str
    response: str
    result: Dict[str, Any]
    chat_history: List[Dict[str, str]]
    environment: str


class ConfigAgentState(TypedDict):
    """Состояние для анализа конфигурации."""

    config: Dict[str, Any]
    server_info: Dict[str, str]
    retrieved_rules: List[Dict[str, Any]]
    prompt: str
    response: str
    result: Dict[str, Any]
    environment: str


class LogsAgentState(TypedDict):
    """Состояние для анализа логов"""

    logs: str
    server_info: Dict[str, str]
    retrieved_rules: List[Dict[str, Any]]
    prompt: str
    response: str
    result: Dict[str, Any]
    environment: str


class WorkflowResult(TypedDict):
    """Результат выполнения рабочего процесса."""

    issues: List[Dict[str, Any]]
    overall_score: float
    thread_id: Optional[str]


class RuleMetadata(TypedDict):
    """Метаданные для правила."""

    title: str
    source: str
    type: str
    severity_default: str


class RetrievedRule(TypedDict):
    """Извлеченное правило с его содержимым."""

    page_content: str
    metadata: RuleMetadata
