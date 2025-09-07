"""
API роуты для управления планировщиком задач.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime
from src.scheduler.scheduler import SchedulerService
from src.scheduler.models import (
    ScheduledTaskCreate,
    ScheduledTaskUpdate,
    ScheduledTaskResponse,
    TaskExecutionResponse,
    TaskType,
    TaskStatus,
)
from src.api.dependencies import get_database_service
from src.services.database_service import DatabaseService

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


async def get_scheduler_service():
    """Получить сервис планировщика."""
    scheduler = SchedulerService()
    await scheduler.initialize()
    return scheduler


@router.post(
    "/tasks", response_model=ScheduledTaskResponse, status_code=status.HTTP_201_CREATED
)
async def create_scheduled_task(
    task_data: ScheduledTaskCreate,
    scheduler: SchedulerService = Depends(get_scheduler_service),
):
    """Создать новую запланированную задачу."""
    try:
        return scheduler.create_scheduled_task(task_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/tasks", response_model=List[ScheduledTaskResponse])
async def get_scheduled_tasks(
    is_active: Optional[bool] = None,
    db_service: DatabaseService = Depends(get_database_service),
):
    """Получить список запланированных задач."""
    try:
        tasks = db_service.get_tasks()
        if is_active is not None:
            tasks = [task for task in tasks if task.get("is_active") == is_active]
        return tasks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/tasks/{task_id}", response_model=ScheduledTaskResponse)
async def get_scheduled_task(
    task_id: int, scheduler: SchedulerService = Depends(get_scheduler_service)
):
    """Получить запланированную задачу по ID."""
    try:
        task = scheduler.get_scheduled_task(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена"
            )
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/tasks/{task_id}", response_model=ScheduledTaskResponse)
async def update_scheduled_task(
    task_id: int,
    task_data: ScheduledTaskUpdate,
    scheduler: SchedulerService = Depends(get_scheduler_service),
):
    """Обновить запланированную задачу."""
    try:
        task = await scheduler.update_scheduled_task(task_id, task_data)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена"
            )
        return task
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scheduled_task(
    task_id: int, scheduler: SchedulerService = Depends(get_scheduler_service)
):
    """Удалить запланированную задачу."""
    try:
        success = await scheduler.delete_scheduled_task(task_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/tasks/{task_id}/run", response_model=dict)
async def run_task_now(
    task_id: int, scheduler: SchedulerService = Depends(get_scheduler_service)
):
    """Запустить задачу немедленно."""
    try:
        task = scheduler.get_scheduled_task(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена"
            )

        if not task.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Задача неактивна"
            )

        await scheduler.queue_task(task_id)
        return {"message": "Задача добавлена в очередь выполнения", "task_id": task_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/executions", response_model=List[TaskExecutionResponse])
async def get_task_executions(
    task_id: Optional[int] = None,
    limit: int = 100,
    db_service: DatabaseService = Depends(get_database_service),
):
    """Получить историю выполнения задач."""
    try:
        executions = db_service.get_task_executions(
            task_id=task_id,
            limit=limit,
        )
        return executions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/executions/{execution_id}", response_model=TaskExecutionResponse)
async def get_task_execution(
    execution_id: int, db_service: DatabaseService = Depends(get_database_service)
):
    """Получить информацию о выполнении задачи."""
    try:
        execution = await db_service.get_task_execution(execution_id)
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Выполнение задачи не найдено",
            )
        return execution
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/queue/status")
async def get_queue_status(
    scheduler: SchedulerService = Depends(get_scheduler_service),
):
    """Получить статус очереди задач."""
    try:
        if not scheduler.redis_client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Redis недоступен",
            )

        queue_length = await scheduler.redis_client.llen("task_queue")

        return {"queue_length": queue_length, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/stats")
async def get_scheduler_stats(
    db_service: DatabaseService = Depends(get_database_service),
):
    """Получить статистику планировщика."""
    try:
        stats_query = """
            SELECT 
                COUNT(*) as total_tasks,
                COUNT(*) FILTER (WHERE is_active = true) as active_tasks,
                COUNT(*) FILTER (WHERE is_active = false) as inactive_tasks
            FROM scheduled_tasks
        """

        task_stats = db_service.fetch_one(stats_query)

        execution_stats_query = """
            SELECT 
                COUNT(*) as total_executions,
                COUNT(*) FILTER (WHERE status = 'completed') as completed,
                COUNT(*) FILTER (WHERE status = 'failed') as failed,
                COUNT(*) FILTER (WHERE status = 'running') as running
            FROM task_executions
            WHERE started_at >= NOW() - INTERVAL '24 hours'
        """

        execution_stats = db_service.fetch_one(execution_stats_query)

        return {
            "tasks": dict(task_stats) if task_stats else {},
            "executions_24h": dict(execution_stats) if execution_stats else {},
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/tasks/{task_id}/queue")
async def queue_task_for_execution(
    task_id: int, scheduler: SchedulerService = Depends(get_scheduler_service)
):
    """Поставить задачу в очередь для немедленного выполнения."""
    try:
        task = scheduler.get_scheduled_task(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена"
            )

        await scheduler.queue_task(task_id)

        return {"message": f"Задача {task_id} добавлена в очередь", "task_id": task_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
