import uuid
from fastapi import APIRouter, HTTPException, Depends
from src.api.schemas import (
    ReviewRequest,
    BatchReviewRequest,
    BatchReviewResponse,
)
from src.services.review_service import ReviewService
from src.api.dependencies import get_review_service

router = APIRouter(prefix="/review", tags=["review"])


@router.post("/")
async def review_sql(
    request: ReviewRequest, service: ReviewService = Depends(get_review_service)
):
    """Проверка одиночного SQL-запроса."""
    try:
        thread_id = request.thread_id or str(uuid.uuid4())
        environment = request.environment or "test"

        result = service.review(
            {
                "sql": request.sql,
                "query_plan": request.query_plan,
                "tables": request.tables,
                "server_info": request.server_info,
                "thread_id": thread_id,
                "environment": environment,
            }
        )

        result["thread_id"] = thread_id
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=BatchReviewResponse)
async def review_batch(
    request: BatchReviewRequest, service: ReviewService = Depends(get_review_service)
):
    """Проверка нескольких SQL-запросов в пакетном режиме."""
    try:
        results = []
        total_score = 0

        for query in request.queries:
            thread_id = query.thread_id or str(uuid.uuid4())
            result = service.review(
                {
                    "sql": query.sql,
                    "query_plan": query.query_plan,
                    "tables": query.tables,
                    "server_info": query.server_info,
                    "thread_id": thread_id,
                    "environment": request.environment,
                }
            )
            result["thread_id"] = thread_id
            results.append(result)
            total_score += result.get("overall_score", 0)

        overall_score = total_score / len(results) if results else 0
        passed = overall_score >= 70

        return BatchReviewResponse(
            results=results, overall_score=overall_score, passed=passed
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
