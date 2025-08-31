from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from src.api.routes.review import router as review_router
from src.api.routes.config import router as config_router
from src.api.routes.rules import router as rules_router
from src.api.routes.tasks import router as tasks_router
from src.api.routes.connections import router as connections_router
from src.core.config import settings


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
    )

    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")

    app.include_router(review_router)
    app.include_router(config_router)
    app.include_router(rules_router)
    app.include_router(tasks_router)
    app.include_router(connections_router)

    @app.get("/")
    async def root():
        """Корневая страница с веб-интерфейсом."""
        return {
            "message": "PostgreSQL Reviewer API",
            "docs": "/docs",
            "web_ui": "/static/index.html",
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

    return app


app = create_application()
