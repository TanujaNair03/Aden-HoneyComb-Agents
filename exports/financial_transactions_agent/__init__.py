"""Financial Transactions Agent Hive package."""

from .config import AgentMetadata, RuntimeConfig, default_config, metadata

__version__ = "1.0.0"

__all__ = [
    "FinancialTransactionsAgent",
    "default_agent",
    "goal",
    "nodes",
    "edges",
    "RuntimeConfig",
    "AgentMetadata",
    "default_config",
    "metadata",
]


def __getattr__(name):
    """Lazily load runtime-heavy exports."""
    if name in {"FinancialTransactionsAgent", "default_agent", "goal", "nodes", "edges"}:
        from .agent import FinancialTransactionsAgent, default_agent, edges, goal, nodes

        exports = {
            "FinancialTransactionsAgent": FinancialTransactionsAgent,
            "default_agent": default_agent,
            "goal": goal,
            "nodes": nodes,
            "edges": edges,
        }
        return exports[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
