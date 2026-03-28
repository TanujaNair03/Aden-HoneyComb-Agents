"""Runtime configuration for the Analytical Advisor agent."""

import os
from dataclasses import dataclass


@dataclass
class RuntimeConfig:
    """
    Agent-local runtime config.

    We keep this local instead of importing Hive's shared RuntimeConfig so the
    agent can choose an OpenAI default model directly, independent of any global
    ~/.hive/configuration.json setting.
    """

    model: str = os.environ.get("HIVE_AGENT_MODEL", "gemini/gemini-2.5-flash")
    temperature: float = 0.2
    max_tokens: int = 12000
    api_key: str | None = (
        os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
    )
    api_base: str | None = os.environ.get("GEMINI_API_BASE") or os.environ.get("OPENAI_API_BASE")


default_config = RuntimeConfig()


@dataclass
class AgentMetadata:
    name: str = "Analytical Advisor"
    version: str = "1.0.0"
    description: str = (
        "A Principal Data Scientist agent that recommends suitable analytical "
        "techniques, surfaces statistical assumptions, and proposes implementation "
        "workflows for data science problems."
    )
    intro_message: str = (
        "Describe your data problem, dataset, target variable, business goal, and "
        "constraints. I will recommend analytical techniques, state the validity "
        "assumptions, and outline an implementation workflow."
    )


metadata = AgentMetadata()
