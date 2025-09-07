from fastapi import APIRouter, HTTPException, Depends
from src.api.schemas import ConfigRequest
from src.services.review_service import ReviewService
from src.api.dependencies import get_review_service

router = APIRouter(prefix="/config", tags=["config"])


@router.post("/analyze")
async def analyze_config(
    request: ConfigRequest, service: ReviewService = Depends(get_review_service)
):
    """Эндпоинт для анализа конфигурации PostgreSQL."""
    try:
        result = service.analyze_config(
            {
                "config": request.config,
                "server_info": request.server_info,
                "environment": request.environment,
            }
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
