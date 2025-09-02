"""
Входная точка для приложения FastAPI.
"""

import os
import logging
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv

from src.api.app import app
from src.core.config import settings
from src.kb.ingest import ingest_rules

from src.core.constants import LOG_MAX_BYTES, LOG_BACKUP_COUNT

load_dotenv()

logger = logging.getLogger(__name__)

log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
logging.basicConfig(
    level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)

file_handler = RotatingFileHandler(
    settings.log_file, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT
)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
file_handler.setLevel(log_level)

root_logger = logging.getLogger()
root_logger.addHandler(file_handler)

# Автоматическая загрузка правил для всех типов
rules_base_dir = settings.kb_rules_dir
if os.path.exists(rules_base_dir):
    for item in os.listdir(rules_base_dir):
        rule_dir = os.path.join(rules_base_dir, item)
        if os.path.isdir(rule_dir):
            index_path = os.path.join(settings.faiss_persist_dir, item, "index.faiss")
            if not os.path.exists(index_path):
                logger.info(f"Загрузка правил типа '{item}' из {rule_dir}")
                ingest_rules(rule_dir, item)
else:
    logger.warning(f"Базовая директория правил {rules_base_dir} не найдена")
