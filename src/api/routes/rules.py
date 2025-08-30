from fastapi import APIRouter, HTTPException
from src.api.schemas import IngestRequest
from src.kb.ingest import ingest_rules

router = APIRouter(prefix="/rules", tags=["rules"])


@router.post("/ingest")
async def ingest_rules_endpoint(request: IngestRequest):
    """Загрузка правил из директории."""
    try:
        ingest_rules(request.rules_dir)
        return {"message": "Rules ingested successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
