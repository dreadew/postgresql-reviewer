"""
Определения workflow для различных типов анализа.
"""

import json
import logging
from typing import Dict, Any, List
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from src.core.types import AgentState, ConfigAgentState
from src.core.utils.json_helper import safe_extract_json
from src.core.agents.prompt_templates import (
    BASE_PROMPT_TEMPLATE,
    SYSTEM_REVIEWER_PROMPT,
    CONFIG_ANALYZE_TEMPLATE,
)

logger = logging.getLogger(__name__)
from src.core.config import settings
from langchain.schema import HumanMessage, SystemMessage


class SQLReviewWorkflow:
    """Workflow для анализа SQL запросов."""

    def __init__(self, llm_service, store):
        self.llm_service = llm_service
        self.store = store
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(AgentState)
        graph.add_node("retrieve_rules", self._retrieve_rules_node)
        graph.add_node("compose_prompt", self._compose_prompt_node)
        graph.add_node("call_llm", self._call_llm_node)
        graph.add_node("parse_response", self._parse_response_node)

        graph.add_edge(START, "retrieve_rules")
        graph.add_edge("retrieve_rules", "compose_prompt")
        graph.add_edge("compose_prompt", "call_llm")
        graph.add_edge("call_llm", "parse_response")
        graph.add_edge("parse_response", END)

        return graph.compile(checkpointer=MemorySaver())

    def _retrieve_rules_node(self, state: AgentState) -> AgentState:
        retrieved_rules = self._retrieve_rules(state["sql"])
        state["retrieved_rules"] = retrieved_rules
        return state

    def _compose_prompt_node(self, state: AgentState) -> AgentState:
        prompt = self._compose_sql_prompt(
            state["sql"],
            state["query_plan"],
            state["server_info"],
            state["tables"],
            state["retrieved_rules"],
            state["environment"],
        )
        state["prompt"] = prompt
        return state

    def _call_llm_node(self, state: AgentState) -> AgentState:
        messages = [SystemMessage(content=SYSTEM_REVIEWER_PROMPT)]
        if state.get("chat_history"):
            for msg in state["chat_history"]:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    from langchain.schema import AIMessage

                    messages.append(AIMessage(content=msg["content"]))

        messages.append(HumanMessage(content=state["prompt"]))

        response = self.llm_service.invoke_with_messages(messages)
        state["response"] = response

        if "chat_history" not in state:
            state["chat_history"] = []
        state["chat_history"].append({"role": "user", "content": state["prompt"]})
        state["chat_history"].append(
            {"role": "assistant", "content": state["response"]}
        )

        return state

    def _parse_response_node(self, state: AgentState) -> AgentState:
        json_response = safe_extract_json(state["response"])
        state["result"] = json.loads(json_response)
        return state

    def _retrieve_rules(
        self, sql: str, top_k: int = settings.max_rules_to_retrieve
    ) -> List[Dict[str, Any]]:
        if not self.store:
            return []
        return self.store.similarity_search(sql, k=top_k)

    def _compose_sql_prompt(
        self,
        sql: str,
        query_plan: str,
        server_info: Dict[str, str],
        tables: List[Dict[str, str]],
        retrieved_rules: List[Dict[str, Any]],
        environment: str,
    ) -> str:
        tables_summary = [
            {
                "schema": t.get("schema", ""),
                "name": t.get("name", ""),
                "row_estimate": t.get("row_estimate", 0),
                "columns": [
                    {
                        "name": c.get("name"),
                        "type": c.get("type"),
                        "indexed": c.get("indexed"),
                    }
                    for c in t.get("columns", [])
                ],
            }
            for t in tables
        ]

        rules_text = ""
        for r in retrieved_rules:
            rules_text += f"- {r.get('title', '')}: {r.get('text', '')[:800]} (severity={r.get('severity_default', 'medium')})\n"

        return BASE_PROMPT_TEMPLATE.format(
            retrieved_rules=rules_text,
            sql=sql,
            query_plan=query_plan or "None",
            server_info=json.dumps(server_info),
            tables_summary=json.dumps(tables_summary),
            environment=environment,
        )

    def execute(
        self, initial_state: Dict[str, Any], thread_id: str = None
    ) -> Dict[str, Any]:
        config = {"configurable": {"thread_id": thread_id or "default"}}
        final_state = self.graph.invoke(initial_state, config=config)
        return final_state["result"]


class ConfigAnalysisWorkflow:
    """Workflow для анализа конфигурации."""

    def __init__(self, llm_service, store):
        self.llm_service = llm_service
        self.store = store
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(ConfigAgentState)
        graph.add_node("retrieve_config_rules", self._retrieve_config_rules_node)
        graph.add_node("compose_config_prompt", self._compose_config_prompt_node)
        graph.add_node("call_config_llm", self._call_config_llm_node)
        graph.add_node("parse_config_response", self._parse_config_response_node)

        graph.add_edge(START, "retrieve_config_rules")
        graph.add_edge("retrieve_config_rules", "compose_config_prompt")
        graph.add_edge("compose_config_prompt", "call_config_llm")
        graph.add_edge("call_config_llm", "parse_config_response")
        graph.add_edge("parse_config_response", END)

        return graph.compile(checkpointer=MemorySaver())

    def _retrieve_config_rules_node(self, state: ConfigAgentState) -> ConfigAgentState:
        retrieved_rules = self._retrieve_config_rules(state["config"])
        state["retrieved_rules"] = retrieved_rules
        return state

    def _compose_config_prompt_node(self, state: ConfigAgentState) -> ConfigAgentState:
        prompt = self._compose_config_prompt(
            state["config"],
            state["server_info"],
            state["retrieved_rules"],
            state["environment"],
        )
        state["prompt"] = prompt
        return state

    def _call_config_llm_node(self, state: ConfigAgentState) -> ConfigAgentState:
        messages = [
            SystemMessage(content="Ты — эксперт по конфигурации PostgreSQL."),
            HumanMessage(content=state["prompt"]),
        ]
        response = self.llm_service.invoke_with_messages(messages)
        state["response"] = response
        return state

    def _parse_config_response_node(self, state: ConfigAgentState) -> ConfigAgentState:
        json_response = safe_extract_json(state["response"])
        state["result"] = json.loads(json_response)
        return state

    def _retrieve_config_rules(
        self, config: Dict[str, Any], top_k: int = settings.max_rules_to_retrieve
    ) -> List[Dict[str, Any]]:
        if not self.store:
            return []
        search_query = " ".join(config.keys())
        return self.store.similarity_search(search_query, k=top_k)

    def _compose_config_prompt(
        self,
        config: Dict[str, Any],
        server_info: Dict[str, str],
        retrieved_rules: List[Dict[str, Any]],
        environment: str,
    ) -> str:
        rules_text = ""
        for r in retrieved_rules:
            rules_text += f"- {r.get('title', '')}: {r.get('text', '')[:800]}\n"

        return CONFIG_ANALYZE_TEMPLATE.format(
            retrieved_rules=rules_text,
            config=json.dumps(config, indent=2),
            server_info=json.dumps(server_info, indent=2),
            environment=environment,
        )

    def execute(
        self, initial_state: Dict[str, Any], thread_id: str = None
    ) -> Dict[str, Any]:
        config = {"configurable": {"thread_id": thread_id or "config_analysis"}}
        final_state = self.graph.invoke(initial_state, config=config)
        return final_state["result"]
