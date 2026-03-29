"""Runtime configuration for the Financial Transactions Agent."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class RuntimeConfig:
    """Agent-local runtime config."""

    model: str = os.environ.get("HIVE_AGENT_MODEL", "gemini/gemini-2.5-flash")
    temperature: float = 0.1
    max_tokens: int = 12000
    api_key: Optional[str] = (
        os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
    )
    api_base: Optional[str] = os.environ.get("GEMINI_API_BASE") or os.environ.get(
        "OPENAI_API_BASE"
    )


default_config = RuntimeConfig()


@dataclass
class AgentMetadata:
    name: str = "Financial Transactions Agent"
    version: str = "1.0.0"
    description: str = (
        "A compliance-first transaction execution agent that checks approvals, "
        "controls, and authorization requirements before marking a financial "
        "transaction ready to execute."
    )
    intro_message: str = (
        "Describe the transaction request, amount, counterparties, purpose, "
        "approval status, and required controls. I will determine whether the "
        "transaction is approved, blocked, or conditionally ready."
    )


metadata = AgentMetadata()
