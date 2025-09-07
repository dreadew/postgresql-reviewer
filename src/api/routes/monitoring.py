from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
import logging
from datetime import datetime
import time
import psycopg2
from src.api.schemas import (
    TaskExecution,
    ConnectionStatus,
)
from src.services.database_service import database_service
from src.services.vault_service import VaultService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

vault_service = VaultService()


@router.get("/tasks/executions", response_model=List[TaskExecution])
async def get_task_executions(task_id: Optional[int] = None, limit: int = 50):
    """Получить историю выполнения задач."""
    try:
        executions = database_service.get_task_executions(task_id, limit)
        return executions
    except Exception as e:
        logger.error(f"Error getting task executions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting task executions: {str(e)}",
        )


@router.get("/tasks/{task_id}/executions", response_model=List[TaskExecution])
async def get_task_executions_by_id(task_id: int, limit: int = 20):
    """Получить историю выполнения конкретной задачи."""
    try:
        task = database_service.get_task_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )

        executions = database_service.get_task_executions(task_id, limit)
        return executions
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task executions for task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting task executions: {str(e)}",
        )


@router.post("/tasks/{task_id}/execute")
async def execute_task_manually(task_id: int):
    """Запустить задачу вручную."""
    try:
        task = database_service.get_task_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )

        execution = database_service.create_task_execution(task_id)

        task = database_service.get_task_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена"
            )

        try:
            from src.scheduler.scheduler import SchedulerService
            from src.scheduler.models import TaskQueueItem, TaskType
            import json

            scheduler = SchedulerService()
            await scheduler.initialize()

            queue_item = TaskQueueItem(
                execution_id=execution["id"],
                task_type=TaskType(task["task_type"]),
                connection_id=task["connection_id"],
                scheduled_task_id=task_id,
                parameters=task.get("task_params", {}),
            )

            await scheduler.redis_client.lpush(
                "task_queue", json.dumps(queue_item.model_dump())
            )

            await scheduler.close()

        except Exception as task_error:
            database_service.update_task_execution(
                execution["id"], "failed", error_message=str(task_error)
            )
            raise

        return {
            "message": "Task executed successfully",
            "execution_id": execution["id"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing task: {str(e)}",
        )


@router.get("/connections/status", response_model=List[ConnectionStatus])
async def get_connections_status():
    """Получить статус всех подключений."""
    try:
        statuses = database_service.get_connection_status()
        return statuses
    except Exception as e:
        logger.error(f"Error getting connection statuses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting connection statuses: {str(e)}",
        )


@router.get("/connections/{connection_id}/status", response_model=ConnectionStatus)
async def get_connection_status(connection_id: int):
    """Получить статус конкретного подключения."""
    try:
        connection = database_service.get_connection_by_id(connection_id)
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found"
            )

        statuses = database_service.get_connection_status(connection_id)
        if not statuses:
            await check_connection_health(connection_id)
            statuses = database_service.get_connection_status(connection_id)

        return statuses[0] if statuses else None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting connection status for {connection_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting connection status: {str(e)}",
        )


@router.post("/connections/{connection_id}/check")
async def check_connection_health(connection_id: int):
    """Проверить состояние подключения к БД."""
    try:
        connection = database_service.get_connection_by_id(connection_id)
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found"
            )

        credentials = vault_service.get_credentials(connection["vault_path"])
        if not credentials:
            database_service.update_connection_status(
                connection_id, False, "Failed to get credentials from Vault"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get credentials from Vault",
            )

        start_time = time.time()
        try:
            conn = psycopg2.connect(
                host=credentials.get("host"),
                port=credentials.get("port", 5432),
                database=credentials.get("database"),
                user=credentials.get("username"),
                password=credentials.get("password"),
                connect_timeout=10,
            )

            with conn.cursor() as cursor:
                cursor.execute("SELECT version()")
                version_result = cursor.fetchone()
                server_version = (
                    version_result[0].split()[1] if version_result else None
                )

            conn.close()

            response_time = int((time.time() - start_time) * 1000)

            database_service.update_connection_status(
                connection_id, True, None, response_time, server_version
            )

            return {
                "connection_id": connection_id,
                "is_healthy": True,
                "response_time_ms": response_time,
                "server_version": server_version,
            }

        except psycopg2.Error as db_error:
            response_time = int((time.time() - start_time) * 1000)
            error_message = str(db_error)

            database_service.update_connection_status(
                connection_id, False, error_message, response_time
            )

            return {
                "connection_id": connection_id,
                "is_healthy": False,
                "error_message": error_message,
                "response_time_ms": response_time,
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking connection {connection_id}: {e}")
        database_service.update_connection_status(connection_id, False, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking connection: {str(e)}",
        )


@router.get("/tasks/running")
async def get_running_tasks():
    """Получить список выполняющихся задач."""
    try:
        query = """
            SELECT st.*, te.id as execution_id, te.started_at as execution_started_at
            FROM scheduled_tasks st
            JOIN task_executions te ON st.id = te.scheduled_task_id
            WHERE te.status = 'running'
            ORDER BY te.started_at DESC
        """
        running_tasks = database_service.execute_query(query)
        return running_tasks
    except Exception as e:
        logger.error(f"Error getting running tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting running tasks: {str(e)}",
        )
