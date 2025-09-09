import os
from typing import Optional
from pydantic_settings import BaseSettings

from src.core.constants import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_MAX_RULES_TO_RETRIEVE,
    DEFAULT_RATE_LIMIT_REQUESTS,
    DEFAULT_RATE_LIMIT_WINDOW,
)


class Settings(BaseSettings):
    """Настройки приложения."""

    app_name: str = "PostgreSQL Reviewer"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = os.getenv("ENVIRONMENT", "dev")

    postgres_db: str = os.getenv("POSTGRES_DB", "analyzer_db")
    postgres_user: str = os.getenv("POSTGRES_USER", "analyzer")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "analyzer_password")

    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/postgres",
    )

    vault_addr: str = os.getenv("VAULT_ADDR", "http://localhost:8200")
    vault_token: Optional[str] = os.getenv("VAULT_TOKEN")

    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    gigachat_api_key: Optional[str] = os.getenv("GIGACHAT_API_KEY")
    gigachat_model_name: str = os.getenv("GIGACHAT_MODEL_NAME", "GigaChat")

    langsmith_tracing: bool = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
    langsmith_api_key: Optional[str] = os.getenv("LANGSMITH_API_KEY")
    langsmith_endpoint: str = os.getenv(
        "LANGSMITH_ENDPOINT", "https://api.smith.langchain.com"
    )
    langsmith_project: str = os.getenv("LANGSMITH_PROJECT", "postgresql-reviewer")

    langfuse_tracing: bool = os.getenv("LANGFUSE_TRACING", "false").lower() == "true"
    langfuse_secret_key: Optional[str] = os.getenv("LANGFUSE_SECRET_KEY")
    langfuse_public_key: Optional[str] = os.getenv("LANGFUSE_PUBLIC_KEY")
    langfuse_host: str = os.getenv("LANGFUSE_HOST", "http://localhost:3000")

    log_level: str = "INFO"
    log_file: str = "./logs/postgresql-reviewer.log"

    vector_store: str = "faiss"
    faiss_persist_dir: str = "./data/faiss"
    kb_rules_dir: str = "./src/kb/rules"
    embeddings_model: str = "all-MiniLM-L6-v2"
    tokenizers_parallelism: bool = False
    chunk_size: int = DEFAULT_CHUNK_SIZE
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
    max_rules_to_retrieve: int = DEFAULT_MAX_RULES_TO_RETRIEVE

    rate_limit_requests: int = DEFAULT_RATE_LIMIT_REQUESTS
    rate_limit_window: int = DEFAULT_RATE_LIMIT_WINDOW

    static_dir: str = "./src/api/static"
    logs_dir: str = "./logs"

    scheduler_workers_count: int = int(os.getenv("SCHEDULER_WORKERS_COUNT", "1"))
    scheduler_check_interval: int = int(os.getenv("SCHEDULER_CHECK_INTERVAL", "30"))
    scheduler_api_url: str = os.getenv(
        "SCHEDULER_API_URL", "http://postgresql-reviewer:8000"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
