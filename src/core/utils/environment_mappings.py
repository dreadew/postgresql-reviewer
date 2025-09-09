from src.core.constants import ENVIRONMENT_MAPPING


def normalize_environment(env: str) -> str:
    """Преобразовать короткое название окружения в полное."""
    if env is None:
        return "test"
    return ENVIRONMENT_MAPPING.get(env.lower(), env)
