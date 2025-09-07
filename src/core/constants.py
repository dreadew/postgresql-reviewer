"""
Константы приложения
"""

CRITICALITY_MULTIPLIERS = {
    "development": 1.0,
    "test": 1.25,
    "staging": 1.35,
    "production": 1.5,
}

SCORE_THRESHOLD_PASS = 70.0
SCORE_THRESHOLD_WARNING = 50.0

TASK_TYPES = ("config_check", "query_analysis", "log_analysis")

FILE_ENCODING = "utf-8"

DEFAULT_CHUNK_SIZE = 1500
DEFAULT_CHUNK_OVERLAP = 200

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

DEFAULT_RATE_LIMIT_REQUESTS = 100
DEFAULT_RATE_LIMIT_WINDOW = 60

DEFAULT_MAX_RULES_TO_RETRIEVE = 6

ERROR_TASK_CREATION_FAILED = "Не удалось создать задачу"
