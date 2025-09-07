"""
Скрипт для запуска планировщика и воркера в одном процессе.
"""

import asyncio
import gc
import logging
import signal
import sys
from typing import List
from src.scheduler.scheduler import SchedulerService
from src.scheduler.worker import TaskWorker
from src.core.config import settings

logger = logging.getLogger(__name__)


class SchedulerManager:
    """Менеджер для управления планировщиком и воркерами."""

    def __init__(self):
        self.scheduler = SchedulerService()
        self.workers: List[TaskWorker] = []
        self.tasks: List[asyncio.Task] = []
        self.is_running = False

    async def initialize(self):
        """Инициализация компонентов."""
        try:
            await self.scheduler.initialize()

            for i in range(settings.scheduler_workers_count):
                worker = TaskWorker(f"worker-{i+1}")
                await worker.initialize()
                self.workers.append(worker)

            logger.info(f"Планировщик и {len(self.workers)} воркеров инициализированы")

        except Exception as e:
            logger.error(f"Ошибка инициализации: {e}")
            raise

    async def start(self):
        """Запустить планировщик и воркеры."""
        self.is_running = True

        try:
            scheduler_task = asyncio.create_task(
                self.scheduler.start_scheduler_loop(), name="scheduler_loop"
            )
            self.tasks.append(scheduler_task)

            for i, worker in enumerate(self.workers):
                worker_task = asyncio.create_task(
                    worker.start_worker(), name=f"worker_{i+1}"
                )
                self.tasks.append(worker_task)

            logger.info(f"Запущены планировщик и {len(self.workers)} воркер(ов)")

            await asyncio.gather(*self.tasks, return_exceptions=True)

        except Exception as e:
            logger.error(f"Ошибка в работе планировщика: {e}")
        finally:
            await self.cleanup()

    async def stop(self):
        """Остановить планировщик и воркеры."""
        logger.info("Остановка планировщика и воркеров...")

        self.is_running = False

        self.scheduler.stop_scheduler()

        for worker in self.workers:
            worker.stop_worker()

        for task in self.tasks:
            if not task.done():
                task.cancel()

        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)

    async def cleanup(self):
        """Очистка ресурсов."""
        try:
            await self.scheduler.close()
            for worker in self.workers:
                await worker.close()

            self.tasks.clear()
            self.workers.clear()
            gc.collect()

            logger.info("Ресурсы очищены")
            logger.info("Ресурсы освобождены")
        except Exception as e:
            logger.error(f"Ошибка при очистке ресурсов: {e}")


async def main():
    """Главная функция."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("/app/logs/scheduler.log"),
        ],
    )

    manager = SchedulerManager()

    def signal_handler(signum, frame):
        logger.info(f"Получен сигнал {signum}")
        stop_task = asyncio.create_task(manager.stop())
        return stop_task

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        await manager.initialize()
        await manager.start()
    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)
    finally:
        logger.info("Планировщик завершен")


if __name__ == "__main__":
    asyncio.run(main())
