"""
Базовые классы и интерфейсы агентов
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from langchain_gigachat import GigaChat
from langsmith import Client
from langfuse import get_client


class BaseAgent(ABC):
    """Базовый класс для агентов."""

    def __init__(self, api_key: str, model_name: str = "GigaChat"):
        if not api_key:
            raise ValueError("API key is required")
        self.model = GigaChat(
            model=model_name,
            credentials=api_key,
            verify_ssl_certs=False,
            profanity_check=False,
            streaming=False,
            max_tokens=500,
            timeout=60,
        )
        self.langsmith_client = Client()
        self.langfuse_client = get_client()

    @abstractmethod
    def review(
        self,
        sql: str,
        query_plan: str,
        tables: List[Dict[str, str]],
        server_info: Dict[str, str],
        thread_id: str = None,
        environment: str = "test",
    ) -> Dict[str, Any]:
        """Проверить SQL запрос с использованием рабочего процесса SQL."""
        pass

    @abstractmethod
    def analyze_config(
        self, config: Dict[str, Any], environment: str = "test"
    ) -> Dict[str, Any]:
        """Анализ конфигурации PostgreSQL с использованием рабочего процесса конфигурации."""
        pass


class LLMService:
    """Сервис для операций с LLM."""

    def __init__(self, model: GigaChat):
        self.model = model

    def invoke_with_messages(self, messages: List) -> str:
        """Invoke LLM with messages."""
        response = self.model.invoke(messages)
        return response.content

    def invoke_with_prompt(self, prompt: str, system_message: str = None) -> str:
        """Invoke LLM with a single prompt."""
        from langchain.schema import HumanMessage, SystemMessage

        messages = []
        if system_message:
            messages.append(SystemMessage(content=system_message))
        messages.append(HumanMessage(content=prompt))

        return self.invoke_with_messages(messages)
