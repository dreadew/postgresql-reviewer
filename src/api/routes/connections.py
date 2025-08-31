from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
import logging
from src.api.schemas import ConnectionCreate, ConnectionResponse, ConnectionUpdate
from src.services.vault_service import VaultService
from src.services.database_service import database_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/connections", tags=["connections"])

CONNECTION_NOT_FOUND = "Подключение не найдено"

vault_service = VaultService()


def get_connection_or_404(connection_id: int) -> Dict[str, Any]:
    """Получить подключение по ID или вызвать HTTPException."""
    connection = database_service.get_connection_by_id(connection_id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=CONNECTION_NOT_FOUND
        )
    return connection


@router.post("/", response_model=ConnectionResponse)
async def create_connection(connection_data: ConnectionCreate):
    """Создать новое подключение к БД."""
    try:
        vault_path = f"database/creds/connection_{connection_data.name.replace(' ', '_').lower()}"

        credentials = {
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
            "host": connection_data.host,
            "port": connection_data.port,
            "database": connection_data.database,
            "username": connection_data.username,
            "vault_path": vault_path,
            "is_active": connection_data.is_active,
        }

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
async def get_connections():
    """Получить список всех подключений."""
    try:
        connections_data = database_service.get_connections()
        connections = []
        for conn in connections_data:
            connections.append(ConnectionResponse(**conn))
        return connections
    except Exception as e:
        logger.error(f"Ошибка получения подключений: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения подключений: {str(e)}",
        )


@router.get("/{connection_id}", response_model=ConnectionResponse)
async def get_connection(connection_id: int):
    """Получить подключение по ID."""
    try:
        connection = get_connection_or_404(connection_id)
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
async def update_connection(connection_id: int, connection_data: ConnectionUpdate):
    """Обновить подключение."""
    try:
        existing_connection = get_connection_or_404(connection_id)

        update_data = connection_data.dict(exclude_unset=True)

        # Обновить учетные данные в Vault если указан новый пароль или имя пользователя
        if (hasattr(connection_data, "password") and connection_data.password) or (
            hasattr(connection_data, "username") and connection_data.username
        ):
            new_username = connection_data.username or existing_connection["username"]
            new_password = connection_data.password or None

            if new_password:  # Обновляем пароль только если он указан
                credentials = {
                    "username": new_username,
                    "password": new_password,
                }
                vault_service.store_credentials(
                    existing_connection["vault_path"], credentials
                )

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
async def delete_connection(connection_id: int):
    """Удалить подключение."""
    try:
        existing_connection = get_connection_or_404(connection_id)

        vault_service.delete_credentials(existing_connection["vault_path"])

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
