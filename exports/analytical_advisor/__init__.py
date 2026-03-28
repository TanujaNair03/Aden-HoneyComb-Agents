"""Analytical Advisor Hive agent package."""

from .config import AgentMetadata, RuntimeConfig, default_config, metadata

__version__ = "1.0.0"

__all__ = [
    "AnalyticalAdvisorAgent",
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
    """Lazily load Hive runtime objects so archive-only commands stay lightweight."""
    if name in {"AnalyticalAdvisorAgent", "default_agent", "goal", "nodes", "edges"}:
        from .agent import AnalyticalAdvisorAgent, default_agent, edges, goal, nodes

        exports = {
            "AnalyticalAdvisorAgent": AnalyticalAdvisorAgent,
            "default_agent": default_agent,
            "goal": goal,
            "nodes": nodes,
            "edges": edges,
        }
        return exports[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
