"""
Модуль для запуска воркера.
"""

import asyncio
import logging
import sys
import os

sys.path.insert(0, "/app")

from src.scheduler.worker import TaskWorker


async def main():
    """Запуск воркера."""

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("/app/logs/worker.log"),
        ],
    )

    logger = logging.getLogger(__name__)
    logger.info("Запуск воркера планировщика")

    worker = TaskWorker("worker-1")

    try:
        await worker.initialize()
        await worker.start_worker()
    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания")
    except Exception as e:
        logger.error(f"Критическая ошибка воркера: {e}")
        sys.exit(1)
    finally:
        await worker.close()
        logger.info("Воркер завершен")


if __name__ == "__main__":
    asyncio.run(main())
