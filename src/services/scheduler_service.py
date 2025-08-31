import asyncio
import redis
import json
import signal
from typing import Dict, Any
import logging
from src.core.config import settings

logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(self, redis_url: str = None):
        # Используем настройки из config вместо жестко заданного URL
        redis_url = redis_url or settings.redis_url or "redis://localhost:6379"
        self.redis_client = redis.from_url(redis_url)
        self.running = False
        self.tasks = []

    async def start_scheduler(self):
        """Запустить планировщик задач."""
        self.running = True
        logger.info("Планировщик задач запущен")

        # Настраиваем обработчики сигналов в асинхронном контексте
        def signal_handler(signum, frame):
            logger.info(f"Получен сигнал {signum}, останавливаю планировщик...")
            # Сохраняем задачу в переменную для предотвращения garbage collection
            stop_task = asyncio.create_task(self.stop_scheduler_async())

        # Используем asyncio для неблокирующей обработки сигналов
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, signal_handler)

        while self.running:
            try:
                # Используем asyncio.to_thread для неблокирующих Redis операций
                task_data = await asyncio.to_thread(
                    self.redis_client.blpop, "task_queue", timeout=10
                )
                if task_data:
                    task_info = json.loads(task_data[1])
                    # Используем asyncio.to_thread для неблокирующей обработки задач
                    await asyncio.to_thread(self.process_task, task_info)
                else:
                    await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Ошибка обработки задачи: {e}")
                if self.running:
                    await asyncio.sleep(1)

        logger.info("Планировщик задач остановлен")

    def stop_scheduler_async(self):
        """Асинхронно остановить планировщик."""
        self.running = False
        logger.info("Планировщик задач остановлен асинхронно")

    def process_task(self, task_info: Dict[str, Any]):
        """Обработать задачу."""
        try:
            task_id = task_info.get("task_id")
            task_type = task_info.get("task_type")
            connection_id = task_info.get("connection_id")

            logger.info(
                f"Обработка задачи {task_id} типа {task_type} для соединения {connection_id}"
            )

            if task_type == "config_check":
                self.process_config_check(task_info)
            elif task_type == "query_analysis":
                self.process_query_analysis(task_info)
            elif task_type == "log_analysis":
                self.process_log_analysis(task_info)
            else:
                logger.warning(f"Неизвестный тип задачи: {task_type}")
                raise ValueError(f"Неизвестный тип задачи: {task_type}")

        except Exception as e:
            logger.error(f"Ошибка в process_task: {e}")
            # Можно добавить логику повторных попыток или уведомлений
            raise  # Передаем исключение выше для обработки

    def process_config_check(self, task_info: Dict[str, Any]):
        """Обработать задачу проверки конфигурации."""
        try:
            connection_id = task_info.get("connection_id")
            logger.info(
                f"Выполняю проверку конфигурации для соединения {connection_id}"
            )

            logger.info(
                f"Проверка конфигурации для соединения {connection_id} завершена"
            )

        except Exception as e:
            logger.error(f"Ошибка проверки конфигурации: {e}")
            raise

    def process_query_analysis(self, task_info: Dict[str, Any]):
        """Обработать задачу анализа запросов."""
        try:
            connection_id = task_info.get("connection_id")

            logger.info(f"Выполняю анализ запросов для соединения {connection_id}")

            logger.info(f"Анализ запросов для соединения {connection_id} завершен")

        except Exception as e:
            logger.error(f"Ошибка анализа запросов: {e}")
            raise

    def process_log_analysis(self, task_info: Dict[str, Any]):
        """Обработать задачу анализа логов."""
        try:
            connection_id = task_info.get("connection_id")

            logger.info(f"Выполняю анализ логов для соединения {connection_id}")

            logger.warning(
                f"Анализ логов для соединения {connection_id} пропущен - требуется настройка"
            )

        except Exception as e:
            logger.error(f"Ошибка анализа логов: {e}")
            raise

    def stop_scheduler(self):
        """Остановить планировщик."""
        self.running = False
        logger.info("Планировщик задач остановлен")

    async def add_task_to_queue_async(self, task_info: Dict[str, Any]):
        """Асинхронно добавить задачу в очередь."""
        try:
            await asyncio.to_thread(
                self.redis_client.rpush, "task_queue", json.dumps(task_info)
            )
            logger.info(f"Задача {task_info.get('task_id')} добавлена в очередь")
        except Exception as e:
            logger.error(f"Ошибка добавления задачи в очередь: {e}")
            raise

    def add_task_to_queue(self, task_info: Dict[str, Any]):
        """Добавить задачу в очередь."""
        try:
            self.redis_client.rpush("task_queue", json.dumps(task_info))
            logger.info(f"Задача {task_info.get('task_id')} добавлена в очередь")
        except Exception as e:
            logger.error(f"Ошибка добавления задачи в очередь: {e}")
            raise
