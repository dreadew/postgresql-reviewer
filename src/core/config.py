import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения."""

    app_name: str = "PostgreSQL Reviewer"
    app_version: str = "1.0.0"
    debug: bool = False

    gigachat_api_key: Optional[str] = None
    model_name: Optional[str] = None
    langsmith_tracing: bool = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
    langsmith_api_key: Optional[str] = None
    langsmith_endpoint: str = os.getenv(
        "LANGSMITH_ENDPOINT", "https://api.smith.langchain.com"
    )
    langsmith_project: str = os.getenv("LANGSMITH_PROJECT", "postgresql-reviewer")

    vector_store: str = os.getenv("VECTOR_STORE", "faiss")
    faiss_persist_dir: str = os.getenv("FAISS_PERSIST_DIR", "./data/faiss")
    kb_rules_dir: str = os.getenv("KB_RULES_DIR", "./src/kb/rules")
    embeddings_model: str = os.getenv("EMBEDDINGS_MODEL", "all-MiniLM-L6-v2")
    tokenizers_parallelism: bool = (
        os.getenv("TOKENIZERS_PARALLELISM", "false").lower() == "true"
    )

    chunk_size: int = os.getenv("CHUNK_SIZE", 1500)
    chunk_overlap: int = os.getenv("CHUNK_OVERLAP", 200)
    max_rules_to_retrieve: int = os.getenv("MAX_RULES_TO_RETRIEVE", 6)

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings(
    gigachat_api_key=os.getenv("GIGACHAT_API_KEY"),
    model_name=os.getenv("GIGACHAT_MODEL_NAME"),
    langsmith_api_key=os.getenv("LANGSMITH_API_KEY"),
)
