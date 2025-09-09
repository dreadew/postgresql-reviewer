"""
API роуты для анализа логов PostgreSQL.
"""

import ssl
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from pydantic import BaseModel
from src.services.review_service import ReviewService
from src.api.dependencies import get_review_service

router = APIRouter(prefix="/logs", tags=["logs"])


class LogAnalysisRequest(BaseModel):
    logs: str
    server_info: Dict[str, Any]
    environment: str = "production"


class LogAnalysisResponse(BaseModel):
    errors: list
    overall_score: int
    notes: str
    analysis_summary: Dict[str, Any]


@router.post("/analyze", response_model=LogAnalysisResponse)
async def analyze_logs(
    request: LogAnalysisRequest, service: ReviewService = Depends(get_review_service)
):
    """Анализ логов PostgreSQL."""
    try:
        result = service.analyze_logs(
            {
                "logs": request.logs,
                "server_info": request.server_info,
                "environment": request.environment,
            }
        )

        return LogAnalysisResponse(
            errors=result.get("errors", []),
            overall_score=result.get("overall_score", 100),
            notes=result.get("notes", "Анализ логов завершен"),
            analysis_summary=result.get("analysis_summary", {}),
        )

    except ssl.SSLError as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Ошибка SSL соединения с AI сервисом: {str(e)}. Попробуйте позже."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка анализа логов: {str(e)}")
