"""
Базовые классы и интерфейсы агентов
"""

import ssl
import requests
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

        # Сначала пробуем с включенной проверкой SSL
        try:
            self.model = GigaChat(
                model=model_name,
                credentials=api_key,
                verify_ssl_certs=True,
                profanity_check=False,
                streaming=False,
                max_tokens=2048,
                timeout=300,
            )
            # Проверяем соединение простым запросом
            test_messages = [{"role": "user", "content": "test"}]
            self.model.invoke(test_messages)
            print("GigaChat initialized with SSL verification enabled")
        except (ssl.SSLError, requests.exceptions.SSLError) as e:
            print(f"SSL verification failed: {e}")
            print("Initializing GigaChat with SSL verification disabled...")
            self.model = GigaChat(
                model=model_name,
                credentials=api_key,
                verify_ssl_certs=False,
                profanity_check=False,
                streaming=False,
                max_tokens=2048,
                timeout=300,
            )
            print("GigaChat initialized with SSL verification disabled")
        except Exception as e:
            print(f"Failed to initialize GigaChat: {e}")
            # Последняя попытка с отключенной проверкой SSL
            self.model = GigaChat(
                model=model_name,
                credentials=api_key,
                verify_ssl_certs=False,
                profanity_check=False,
                streaming=False,
                max_tokens=2048,
                timeout=300,
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
        try:
            response = self.model.invoke(messages)
            return response.content
        except (ssl.SSLError, requests.exceptions.SSLError) as e:
            print(f"SSL Error during invocation: {e}")
            print("Recreating model with SSL verification disabled...")

            # Пересоздаем модель без проверки SSL
            try:
                old_model_name = getattr(self.model, "model_name", "GigaChat")
                old_credentials = getattr(self.model, "credentials", None)

                self.model = GigaChat(
                    model=old_model_name,
                    credentials=old_credentials,
                    verify_ssl_certs=False,
                    profanity_check=False,
                    streaming=False,
                    max_tokens=2048,
                    timeout=300,
                )
                response = self.model.invoke(messages)
                return response.content
            except Exception as retry_error:
                print(f"Retry with disabled SSL also failed: {retry_error}")
                raise ssl.SSLError(
                    f"SSL connection failed even with disabled verification: {e}"
                ) from e
        except Exception as e:
            print(f"Unexpected error in LLM service: {e}")
            raise

    def invoke_with_prompt(self, prompt: str, system_message: str = None) -> str:
        """Invoke LLM with a single prompt."""
        from langchain.schema import HumanMessage, SystemMessage

        messages = []
        if system_message:
            messages.append(SystemMessage(content=system_message))
        messages.append(HumanMessage(content=prompt))

        return self.invoke_with_messages(messages)
