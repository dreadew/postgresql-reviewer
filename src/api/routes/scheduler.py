"""
API роуты для управления планировщиком задач.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
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
from src.services.database_service import DatabaseService
from src.models.base import get_db

router = APIRouter(prefix="/scheduler", tags=["scheduler"])

TASK_NOT_FOUND = "Задача не найдена"


async def get_scheduler_service():
    """Получить сервис планировщика."""
    scheduler = SchedulerService()
    await scheduler.initialize()
    return scheduler


@router.post(
    "/tasks", response_model=ScheduledTaskResponse, status_code=status.HTTP_201_CREATED
)
@router.post(
    "/tasks/", response_model=ScheduledTaskResponse, status_code=status.HTTP_201_CREATED
)
async def create_scheduled_task(
    task_data: ScheduledTaskCreate,
    db: Session = Depends(get_db),
):
    """Создать новую запланированную задачу."""
    try:
        database_service = DatabaseService(db)
        task_dict = task_data.dict()
        result = database_service.create_task(task_dict)

        return ScheduledTaskResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/tasks", response_model=List[ScheduledTaskResponse])
@router.get("/tasks/", response_model=List[ScheduledTaskResponse])
async def get_scheduled_tasks(
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """Получить список запланированных задач."""
    try:
        database_service = DatabaseService(db)
        tasks = database_service.get_tasks()

        # Фильтруем по активности если необходимо
        if is_active is not None:
            tasks = [task for task in tasks if task.get("is_active") == is_active]

        return [ScheduledTaskResponse(**task) for task in tasks]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/tasks/{task_id}", response_model=ScheduledTaskResponse)
async def get_scheduled_task(task_id: int, db: Session = Depends(get_db)):
    """Получить запланированную задачу по ID."""
    try:
        database_service = DatabaseService(db)
        task = database_service.get_task_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=TASK_NOT_FOUND
            )
        return ScheduledTaskResponse(**task)
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
    db: Session = Depends(get_db),
):
    """Обновить запланированную задачу."""
    try:
        database_service = DatabaseService(db)

        # Проверяем существование задачи
        existing_task = database_service.get_task_by_id(task_id)
        if not existing_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=TASK_NOT_FOUND
            )

        # Обновляем задачу
        update_data = task_data.dict(exclude_unset=True)
        updated_task = database_service.update_task(task_id, update_data)

        if not updated_task:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось обновить задачу",
            )

        return ScheduledTaskResponse(**updated_task)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/tasks/{task_id}")
async def delete_scheduled_task(
    task_id: int,
    db: Session = Depends(get_db),
    scheduler: SchedulerService = Depends(get_scheduler_service),
):
    """Удалить запланированную задачу."""
    try:
        database_service = DatabaseService(db)

        # Проверяем существование задачи
        existing_task = database_service.get_task_by_id(task_id)
        if not existing_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=TASK_NOT_FOUND
            )

        # Удаляем задачу из планировщика
        await scheduler.remove_task_from_schedule(task_id)

        # Удаляем задачу из базы данных
        success = database_service.delete_task(task_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось удалить задачу",
            )

        return {"message": "Задача удалена"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/tasks/{task_id}/execute")
async def execute_task_manually(
    task_id: int,
    db: Session = Depends(get_db),
    scheduler: SchedulerService = Depends(get_scheduler_service),
):
    """Запустить задачу вручную."""
    try:
        database_service = DatabaseService(db)

        # Проверяем существование задачи
        task = database_service.get_task_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=TASK_NOT_FOUND
            )

        # Запускаем задачу
        execution = await scheduler.execute_task_manually(task_id)

        return {"message": "Задача запущена", "execution_id": execution.get("id")}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/executions", response_model=List[TaskExecutionResponse])
async def get_task_executions(
    task_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Получить историю выполнения задач."""
    try:
        database_service = DatabaseService(db)
        executions = database_service.get_task_executions(task_id=task_id, limit=limit)
        return [TaskExecutionResponse(**execution) for execution in executions]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/executions/{execution_id}", response_model=TaskExecutionResponse)
async def get_task_execution(execution_id: int, db: Session = Depends(get_db)):
    """Получить информацию о выполнении задачи."""
    try:
        database_service = DatabaseService(db)
        executions = database_service.get_task_executions(limit=1)

        # Ищем нужное выполнение
        execution = next((e for e in executions if e.get("id") == execution_id), None)

        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Выполнение задачи не найдено",
            )

        return TaskExecutionResponse(**execution)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/status")
async def get_scheduler_status(
    scheduler: SchedulerService = Depends(get_scheduler_service),
):
    """Получить статус планировщика."""
    try:
        status_info = await scheduler.get_status()
        return status_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/start")
async def start_scheduler(scheduler: SchedulerService = Depends(get_scheduler_service)):
    """Запустить планировщик."""
    try:
        await scheduler.start()
        return {"message": "Планировщик запущен"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/stop")
async def stop_scheduler(scheduler: SchedulerService = Depends(get_scheduler_service)):
    """Остановить планировщик."""
    try:
        await scheduler.stop()
        return {"message": "Планировщик остановлен"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
