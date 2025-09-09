from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from pathlib import Path
import logging
from src.api.schemas import IngestRequest
from src.kb.ingest import ingest_rules
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rules", tags=["rules"])

from src.core.config import settings

RULES_DIR = Path(settings.kb_rules_dir)


class RuleInfo(BaseModel):
    filename: str
    title: str
    category: str
    content: Optional[str] = None


class RuleCreate(BaseModel):
    filename: str
    title: str
    category: str
    content: str


class RuleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


@router.post("/ingest")
async def ingest_rules_endpoint(request: IngestRequest):
    """Загрузка правил из директории."""
    try:
        ingest_rules(request.rules_dir)
        return {"message": "Rules ingested successfully"}
    except Exception as e:
        logger.error(f"Error ingesting rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[RuleInfo])
async def get_rules(category: Optional[str] = None):
    """Получить список всех правил."""
    try:
        print(f"DEBUG: Getting rules with category: {category}")
        print(f"DEBUG: RULES_DIR: {RULES_DIR}")
        print(f"DEBUG: RULES_DIR exists: {RULES_DIR.exists()}")

        rules = []

        search_dirs = []
        if category:
            logger.info(f"Category specified: {category}")
            if category in ["config", "sql", "logs"]:
                search_dirs.append(RULES_DIR / category)
                logger.info(f"Added search dir: {RULES_DIR / category}")
            else:
                logger.error(f"Invalid category: {category}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category must be 'config', 'sql' or 'logs',",
                )
        else:
            logger.info("No category specified, searching all")
            search_dirs = [RULES_DIR / "config", RULES_DIR / "sql", RULES_DIR / "logs"]
            logger.info(f"Search dirs: {search_dirs}")

        for search_dir in search_dirs:
            logger.info(f"Checking search dir: {search_dir}")
            logger.info(f"Search dir exists: {search_dir.exists()}")
            if not search_dir.exists():
                logger.warning(f"Search dir does not exist: {search_dir}")
                continue

            md_files = list(search_dir.glob("*.md"))
            logger.info(f"Found {len(md_files)} .md files in {search_dir}")
            for file_path in md_files:
                logger.info(f"Processing file: {file_path}")
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    lines = content.split("\n")
                    title = (
                        lines[0].replace("#", "").strip() if lines else file_path.stem
                    )

                    rules.append(
                        RuleInfo(
                            filename=file_path.name,
                            title=title,
                            category=search_dir.name,
                            content=None,
                        )
                    )
                except Exception as e:
                    logger.warning(f"Error reading rule {file_path}: {e}")

        return rules

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting rules: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting rules: {str(e)}",
        )


@router.get("/{category}/{filename}")
async def get_rule(category: str, filename: str):
    """Получить правило по категории и имени файла."""
    try:
        if category not in ["config", "sql", "logs"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category must be 'config', 'sql' or 'logs',",
            )

        file_path = RULES_DIR / category / filename
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found"
            )

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")
        title = lines[0].replace("#", "").strip() if lines else filename

        return RuleInfo(
            filename=filename, title=title, category=category, content=content
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting rule {category}/{filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting rule: {str(e)}",
        )


@router.post("/")
async def create_rule(rule: RuleCreate):
    """Создать новое правило."""
    try:
        if rule.category not in ["config", "sql", "logs"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category must be 'config', 'sql' or 'logs',",
            )

        category_dir = RULES_DIR / rule.category
        category_dir.mkdir(exist_ok=True)

        file_path = category_dir / rule.filename

        if file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Rule already exists"
            )

        formatted_content = f"# {rule.title}\n\n{rule.content}"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(formatted_content)

        logger.info(f"Created rule: {rule.category}/{rule.filename}")
        return {"message": "Rule created successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating rule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating rule: {str(e)}",
        )


@router.put("/{category}/{filename}")
async def update_rule(category: str, filename: str, rule_update: RuleUpdate):
    """Обновить правило."""
    try:
        if category not in ["config", "sql", "logs"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category must be 'config', 'sql' or 'logs',",
            )

        file_path = RULES_DIR / category / filename
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found"
            )

        with open(file_path, "r", encoding="utf-8") as f:
            current_content = f.read()

        new_content = current_content
        if rule_update.title:
            lines = current_content.split("\n")
            if lines:
                lines[0] = f"# {rule_update.title}"
                new_content = "\n".join(lines)

        if rule_update.content is not None:
            if "\n\n" in new_content:
                header, _ = new_content.split("\n\n", 1)
                new_content = f"{header}\n\n{rule_update.content}"
            else:
                new_content = rule_update.content

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        logger.info(f"Updated rule: {category}/{filename}")
        return {"message": "Rule updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating rule {category}/{filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating rule: {str(e)}",
        )


@router.delete("/{category}/{filename}")
async def delete_rule(category: str, filename: str):
    """Удалить правило."""
    try:
        if category not in ["config", "sql", "logs"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category must be 'config', 'sql' or 'logs',",
            )

        file_path = RULES_DIR / category / filename
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found"
            )

        file_path.unlink()

        logger.info(f"Deleted rule: {category}/{filename}")
        return {"message": "Rule deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting rule {category}/{filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting rule: {str(e)}",
        )
