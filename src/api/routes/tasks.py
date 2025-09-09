from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
import logging
from src.api.schemas import TaskCreate, TaskResponse, TaskUpdate
from src.services.scheduler_service import SchedulerService
from src.services.database_service import DatabaseService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])

TASK_NOT_FOUND = "Задача не найдена"

database_service = DatabaseService()
scheduler_service = SchedulerService()


def get_task_or_404(task_id: int) -> Dict[str, Any]:
    """Получить задачу по ID или вызвать HTTPException."""
    task = database_service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=TASK_NOT_FOUND
        )
    return task


@router.post("/", response_model=TaskResponse)
async def create_task(task_data: TaskCreate):
    """Создать новую задачу планировщика."""
    try:
        task_dict = {
            "name": task_data.name,
            "connection_id": task_data.connection_id,
            "schedule": task_data.schedule,
            "task_type": task_data.task_type,
            "parameters": task_data.parameters or {},
            "is_active": task_data.is_active,
        }

        task = database_service.create_task(task_dict)

        queue_task = {
            "task_id": task["id"],
            "task_type": task_data.task_type,
            "connection_id": task_data.connection_id,
            "parameters": task_data.parameters,
        }
        scheduler_service.add_task_to_queue(queue_task)

        logger.info(f"Создана новая задача: {task['name']}")
        return TaskResponse(**task)

    except Exception as e:
        logger.error(f"Ошибка создания задачи: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка создания задачи: {str(e)}",
        )


@router.get("/", response_model=List[TaskResponse])
async def get_tasks():
    """Получить список всех задач."""
    try:
        tasks = database_service.get_tasks()
        return [TaskResponse(**task) for task in tasks]
    except Exception as e:
        logger.error(f"Ошибка получения задач: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения задач: {str(e)}",
        )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int):
    """Получить задачу по ID."""
    try:
        task = get_task_or_404(task_id)
        return TaskResponse(**task)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения задачи {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения задачи: {str(e)}",
        )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_data: TaskUpdate):
    """Обновить задачу."""
    try:
        get_task_or_404(task_id)

        update_data = task_data.dict(exclude_unset=True)
        updated_task = database_service.update_task(task_id, update_data)

        logger.info(f"Обновлена задача: {updated_task['name']}")
        return TaskResponse(**updated_task)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка обновления задачи {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка обновления задачи: {str(e)}",
        )


@router.delete("/{task_id}")
async def delete_task(task_id: int):
    """Удалить задачу."""
    try:
        existing_task = get_task_or_404(task_id)

        task_name = existing_task["name"]

        success = database_service.delete_task(task_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось удалить задачу",
            )

        logger.info(f"Удалена задача: {task_name}")
        return {"message": "Задача удалена"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка удаления задачи {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка удаления задачи: {str(e)}",
        )


@router.post("/{task_id}/run")
async def run_task_now(task_id: int):
    """Запустить задачу немедленно."""
    try:
        task = get_task_or_404(task_id)

        queue_task = {
            "task_id": task_id,
            "task_type": task["task_type"],
            "connection_id": task["connection_id"],
            "parameters": task["parameters"],
        }
        scheduler_service.add_task_to_queue(queue_task)

        database_service.update_task_last_run(task_id)

        logger.info(f"Задача {task_id} добавлена в очередь для немедленного выполнения")
        return {"message": "Задача добавлена в очередь"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка запуска задачи {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка запуска задачи: {str(e)}",
        )
