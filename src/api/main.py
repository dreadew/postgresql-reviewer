"""
Входная точка для приложения FastAPI.
"""

import os
import logging
from dotenv import load_dotenv
from src.kb.ingest import ingest_rules
from src.core.config import settings
from src.api.app import app

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

load_dotenv()

if not os.path.exists(os.path.join(settings.faiss_persist_dir, "index.faiss")):
    rules_dir = settings.kb_rules_dir
    ingest_rules(rules_dir)
