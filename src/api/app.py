from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from src.api.routes.review import router as review_router
from src.api.routes.config import router as config_router
from src.api.routes.rules import router as rules_router
from src.api.routes.connections import router as connections_router
from src.api.routes.monitoring import router as monitoring_router
from src.api.routes.scheduler import router as scheduler_router
from src.api.routes.logs import router as logs_router
from src.core.config import settings

API_V1_PREFIX = "/api/v1"
API_V1_DOCS = f"{API_V1_PREFIX}/docs"
API_V1_REDOC = f"{API_V1_PREFIX}/redoc"
API_V1_OPENAPI = f"{API_V1_PREFIX}/openapi.json"


def check_faiss_index() -> bool:
    """Проверить существование FAISS индекса."""
    import os

    faiss_path = os.path.join(settings.faiss_persist_dir, "index.faiss")
    return os.path.exists(faiss_path)


def create_application() -> FastAPI:
    """Создание и настройка FastAPI приложения."""

    app = FastAPI(
        title=settings.app_name,
        description="ИИ-агент для ревью SQL-запросов PostgreSQL",
        version=settings.app_version,
        debug=settings.debug,
        openapi_url=API_V1_OPENAPI,
        docs_url=API_V1_DOCS,
        redoc_url=API_V1_REDOC,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    app.include_router(review_router, prefix=API_V1_PREFIX)
    app.include_router(config_router, prefix=API_V1_PREFIX)
    app.include_router(rules_router, prefix=API_V1_PREFIX)
    app.include_router(connections_router, prefix=API_V1_PREFIX)
    app.include_router(monitoring_router, prefix=API_V1_PREFIX)
    app.include_router(scheduler_router, prefix=API_V1_PREFIX)
    app.include_router(logs_router, prefix=API_V1_PREFIX)

    app.include_router(review_router, prefix="/api")
    app.include_router(config_router, prefix="/api")
    app.include_router(rules_router, prefix="/api")
    app.include_router(connections_router, prefix="/api")
    app.include_router(monitoring_router, prefix="/api")
    app.include_router(scheduler_router, prefix="/api")
    app.include_router(logs_router, prefix="/api")

    @app.get("/")
    async def root():
        """Корневая страница с веб-интерфейсом."""
        return {
            "message": "PostgreSQL Reviewer API",
            "version": settings.app_version,
            "api_docs": API_V1_DOCS,
            "api_redoc": API_V1_REDOC,
            "api_openapi": API_V1_OPENAPI,
            "web_ui": "/static/index.html",
            "health": "/health",
        }

    @app.get("/health")
    async def health_check():
        """Health check эндпоинт."""
        import os
        from pathlib import Path
        from datetime import datetime

        static_exists = Path(settings.static_dir).exists()

        return {
            "status": "healthy",
            "version": settings.app_version,
            "debug": settings.debug,
            "faiss_index_loaded": check_faiss_index(),
            "static_files_available": static_exists,
            "environment": os.getenv("ENVIRONMENT", "development"),
            "timestamp": datetime.now(),
        }

    @app.get("/api/versions")
    async def api_versions():
        """Получить информацию о доступных версиях API."""
        return {
            "current_version": "v1",
            "supported_versions": ["v1"],
            "deprecated_versions": [],
            "endpoints": {
                "v1": {
                    "docs": API_V1_DOCS,
                    "redoc": API_V1_REDOC,
                    "openapi": API_V1_OPENAPI,
                }
            },
        }

    return app


app = create_application()
