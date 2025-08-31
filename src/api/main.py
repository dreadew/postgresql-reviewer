"""
Входная точка для приложения FastAPI.
"""

import os
import logging
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv

from src.core.config import settings
from src.kb.ingest import ingest_rules

from src.core.constants import LOG_MAX_BYTES, LOG_BACKUP_COUNT

load_dotenv()

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

if not os.path.exists(os.path.join(settings.faiss_persist_dir, "index.faiss")):
    rules_dir = settings.kb_rules_dir
    ingest_rules(rules_dir)
