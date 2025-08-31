"""
Агент GigaChat для анализа SQL и конфигурации.
"""

from typing import List, Dict, Any
from src.core.agents.base import BaseAgent, LLMService
from src.core.workflows import SQLReviewWorkflow, ConfigAnalysisWorkflow
from src.store.factory import VectorStoreFactory
from src.core.config import settings


class GigaChatAgent(BaseAgent):
    """Агент для анализа SQL и конфигурации."""

    def __init__(self, api_key: str, model_name: str = settings.gigachat_model_name):
        super().__init__(api_key, model_name)

        self.llm_service = LLMService(self.model)

        self.sql_store = VectorStoreFactory.create("sql")
        self.config_store = VectorStoreFactory.create("config")

        self.sql_workflow = SQLReviewWorkflow(self.llm_service, self.sql_store)
        self.config_workflow = ConfigAnalysisWorkflow(
            self.llm_service, self.config_store
        )

    def review(
        self,
        sql: str,
        query_plan: str,
        tables: List[Dict[str, str]],
        server_info: Dict[str, str],
        thread_id: str = None,
        environment: str = "test",
    ) -> Dict[str, Any]:
        initial_state = {
            "sql": sql,
            "query_plan": query_plan,
            "tables": tables,
            "server_info": server_info,
            "retrieved_rules": [],
            "prompt": "",
            "response": "",
            "result": {},
            "chat_history": [],
            "environment": environment,
        }

        return self.sql_workflow.execute(initial_state, thread_id)

    def analyze_config(
        self,
        config: Dict[str, Any],
        server_info: Dict[str, str],
        environment: str = "test",
    ) -> Dict[str, Any]:
        initial_state = {
            "config": config,
            "server_info": server_info,
            "retrieved_rules": [],
            "prompt": "",
            "response": "",
            "result": {},
            "environment": environment,
        }

        return self.config_workflow.execute(initial_state)
