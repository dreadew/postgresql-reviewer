from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging
from src.api.schemas import ConnectionCreate, ConnectionResponse, ConnectionUpdate
from src.services.vault_service import VaultService
from src.services.database_service import DatabaseService
from src.models.base import get_db
from src.repositories.connections import ConnectionRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/connections", tags=["connections"])

CONNECTION_NOT_FOUND = "Подключение не найдено"

vault_service = VaultService()


def get_connection_or_404(connection_id: int, db: Session) -> Dict[str, Any]:
    """Получить подключение по ID или вызвать HTTPException."""
    connection_repo = ConnectionRepository(db)
    connection = connection_repo.get_by_id(connection_id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=CONNECTION_NOT_FOUND
        )
    return connection.to_dict()


@router.post("/", response_model=ConnectionResponse)
async def create_connection(
    connection_data: ConnectionCreate, db: Session = Depends(get_db)
):
    """Создать новое подключение к БД."""
    try:
        vault_path = f"secret/database/connections/{connection_data.name.replace(' ', '_').lower()}"

        credentials = {
            "host": connection_data.host,
            "port": connection_data.port,
            "database": connection_data.database,
            "username": connection_data.username,
            "password": connection_data.password,
        }

        success = vault_service.store_credentials(vault_path, credentials)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось сохранить учетные данные в Vault",
            )

        connection_info = {
            "name": connection_data.name,
            "vault_path": vault_path,
            "environment": connection_data.environment,
            "description": connection_data.description,
            "tags": connection_data.tags,
            "is_active": connection_data.is_active,
        }

        database_service = DatabaseService(db)
        result = database_service.create_connection(connection_info)

        logger.info(f"Создано новое подключение: {connection_info['name']}")
        return ConnectionResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка создания подключения: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка создания подключения: {str(e)}",
        )


@router.get("/", response_model=List[ConnectionResponse])
async def get_connections(db: Session = Depends(get_db)):
    """Получить список всех подключений."""
    try:
        database_service = DatabaseService(db)
        connections_data = database_service.get_connections()
        return connections_data
    except Exception as e:
        logger.error(f"Ошибка получения подключений: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения подключений",
        )


@router.get("/{connection_id}", response_model=ConnectionResponse)
async def get_connection(connection_id: int, db: Session = Depends(get_db)):
    """Получить подключение по ID."""
    try:
        connection = get_connection_or_404(connection_id, db)
        return ConnectionResponse(**connection)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения подключения {connection_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения подключения: {str(e)}",
        )


@router.put("/{connection_id}", response_model=ConnectionResponse)
async def update_connection(
    connection_id: int, connection_data: ConnectionUpdate, db: Session = Depends(get_db)
):
    """Обновить подключение."""
    try:
        existing_connection = get_connection_or_404(connection_id, db)

        update_data = connection_data.dict(exclude_unset=True)

        vault_fields = {"host", "port", "database", "username", "password"}
        vault_updates = {k: v for k, v in update_data.items() if k in vault_fields}
        update_data = {k: v for k, v in update_data.items() if k not in vault_fields}

        if vault_updates:
            current_credentials = vault_service.get_credentials(
                existing_connection["vault_path"]
            )

            if current_credentials:
                updated_credentials = current_credentials.copy()
                updated_credentials.update(vault_updates)

                vault_service.store_credentials(
                    existing_connection["vault_path"], updated_credentials
                )

        database_service = DatabaseService(db)
        updated_connection = database_service.update_connection(
            connection_id, update_data
        )
        if not updated_connection:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось обновить подключение",
            )

        logger.info(f"Обновлено подключение: {updated_connection['name']}")
        return ConnectionResponse(**updated_connection)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка обновления подключения {connection_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка обновления подключения: {str(e)}",
        )


@router.delete("/{connection_id}")
async def delete_connection(connection_id: int, db: Session = Depends(get_db)):
    """Удалить подключение."""
    try:
        existing_connection = get_connection_or_404(connection_id, db)

        vault_service.delete_credentials(existing_connection["vault_path"])

        database_service = DatabaseService(db)
        success = database_service.delete_connection(connection_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось удалить подключение из базы данных",
            )

        logger.info(f"Удалено подключение: {existing_connection['name']}")
        return {"message": "Подключение удалено"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка удаления подключения {connection_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка удаления подключения: {str(e)}",
        )
