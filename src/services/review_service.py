from typing import Dict, Any
import logging
from src.core.agents.gigachat_agent import GigaChatAgent

logger = logging.getLogger(__name__)


class ReviewService:
    def __init__(self, api_key: str):
        self.agent = GigaChatAgent(api_key=api_key)

    def review(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        thread_id = payload.get("thread_id")
        environment = payload.get("environment", "test")
        logger.info(f"Starting review with payload: {payload}")

        result = self.agent.review(
            sql=payload["sql"],
            query_plan=payload["query_plan"],
            tables=payload["tables"],
            server_info=payload["server_info"],
            thread_id=thread_id,
            environment=environment,
        )

        logger.info(f"Review result type: {type(result)}, result: {result}")
        return result

    def analyze_config(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        environment = payload.get("environment", "test")
        server_info = payload.get("server_info", {})
        return self.agent.analyze_config(
            config=payload["config"],
            server_info=server_info,
            environment=environment,
        )

    def analyze_logs(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ логов PostgreSQL."""
        environment = payload.get("environment", "production")
        server_info = payload.get("server_info", {})
        return self.agent.analyze_logs(
            logs=payload["logs"],
            server_info=server_info,
            environment=environment,
        )
