from typing import Dict, Any
from src.core.agents.gigachat_agent import GigaChatAgent


class ReviewService:
    def __init__(self, api_key: str):
        self.agent = GigaChatAgent(api_key=api_key)

    def review(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        thread_id = payload.get("thread_id")
        environment = payload.get("environment", "test")
        return self.agent.review(
            sql=payload["sql"],
            query_plan=payload["query_plan"],
            tables=payload["tables"],
            server_info=payload["server_info"],
            thread_id=thread_id,
            environment=environment,
        )

    def analyze_config(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        environment = payload.get("environment", "test")
        return self.agent.analyze_config(
            config=payload["config"],
            environment=environment,
        )
