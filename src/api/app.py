from fastapi import FastAPI
from src.api.routes.review import router as review_router
from src.api.routes.config import router as config_router
from src.api.routes.rules import router as rules_router
from src.core.config import settings


def create_application() -> FastAPI:
    """Создание и настройка FastAPI приложения."""

    app = FastAPI(
        title=settings.app_name,
        description="ИИ-агент для ревью SQL-запросов PostgreSQL",
        version=settings.app_version,
        debug=settings.debug,
    )

    app.include_router(review_router)
    app.include_router(config_router)
    app.include_router(rules_router)

    @app.get("/health")
    async def health_check():
        """Health check эндпоинт."""
        return {
            "status": "healthy",
            "version": settings.app_version,
            "debug": settings.debug,
        }

    return app


app = create_application()
