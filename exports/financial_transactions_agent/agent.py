"""Agent graph construction for Financial Transactions Agent."""

import os
from pathlib import Path

from framework.graph import Constraint, EdgeCondition, EdgeSpec, Goal, SuccessCriterion
from framework.graph.checkpoint_config import CheckpointConfig
from framework.graph.edge import GraphSpec
from framework.graph.executor import ExecutionResult
from framework.llm import LiteLLMProvider
from framework.runner.tool_registry import ToolRegistry
from framework.runtime.agent_runtime import AgentRuntime, create_agent_runtime
from framework.runtime.execution_stream import EntryPointSpec

from .config import default_config, metadata
from .nodes import decision_node, intake_node

goal = Goal(
    id="financial-transactions-goal",
    name="Controlled Financial Transactions",
    description=(
        "Review transaction requests against approvals, controls, and "
        "authorization requirements before classifying them as ready, pending, or blocked."
    ),
    success_criteria=[
        SuccessCriterion(
            id="control-coverage",
            description="The decision covers the key controls and approval requirements.",
            metric="control_coverage",
            target=">=0.9",
            weight=0.4,
        ),
        SuccessCriterion(
            id="decision-discipline",
            description="The transaction is not approved when controls are missing or unclear.",
            metric="governance_discipline",
            target=">=0.95",
            weight=0.35,
        ),
        SuccessCriterion(
            id="auditability",
            description="The output is auditable and operationally actionable.",
            metric="audit_quality",
            target=">=0.9",
            weight=0.25,
        ),
    ],
    constraints=[
        Constraint(
            id="no-governance-bypass",
            description="Never bypass required approvals, controls, or authorization.",
            constraint_type="hard",
            category="compliance",
        ),
        Constraint(
            id="human-accountability",
            description="Escalate missing or unclear approvals rather than assuming consent.",
            constraint_type="hard",
            category="safety",
        ),
        Constraint(
            id="audit-ready-output",
            description="Every decision must contain auditable rationale and next steps.",
            constraint_type="hard",
            category="quality",
        ),
    ],
)

nodes = [intake_node, decision_node]

edges = [
    EdgeSpec(
        id="intake-to-decision",
        source="intake",
        target="decision",
        condition=EdgeCondition.ON_SUCCESS,
        priority=1,
    )
]

entry_node = "intake"
entry_points = {"default": "intake"}
pause_nodes: list[str] = []
terminal_nodes = ["decision"]


class FinancialTransactionsAgent:
    """
    Two-stage controlled transaction agent.

    Flow: intake -> decision

    This is a governance-oriented agent rather than a freeform executor.
    It uses structured validation so Hive only accepts outputs that include:
    summary, disposition, human approval requirement, controls, workflow, and audit notes.
    """

    def __init__(self, config=None):
        self.config = config or default_config
        self.goal = goal
        self.nodes = nodes
        self.edges = edges
        self.entry_node = entry_node
        self.entry_points = entry_points
        self.pause_nodes = pause_nodes
        self.terminal_nodes = terminal_nodes
        self._graph: GraphSpec | None = None
        self._agent_runtime: AgentRuntime | None = None
        self._tool_registry: ToolRegistry | None = None
        self._storage_path: Path | None = None

    def _build_graph(self) -> GraphSpec:
        """Build the graph definition for Hive runtime."""
        return GraphSpec(
            id="financial-transactions-agent-graph",
            goal_id=self.goal.id,
            version="1.0.0",
            entry_node=self.entry_node,
            entry_points=self.entry_points,
            terminal_nodes=self.terminal_nodes,
            pause_nodes=self.pause_nodes,
            nodes=self.nodes,
            edges=self.edges,
            default_model=self.config.model,
            max_tokens=self.config.max_tokens,
            loop_config={
                "max_iterations": 20,
                "max_tool_calls_per_turn": 8,
                "max_history_tokens": 24000,
            },
        )

    def _setup(self, mock_mode: bool = False) -> None:
        """Prepare storage, model provider, tools, and runtime."""
        storage_override = os.environ.get("HIVE_AGENT_STORAGE")
        if storage_override:
            self._storage_path = Path(storage_override).expanduser().resolve()
        else:
            self._storage_path = (
                Path(__file__).resolve().parents[2]
                / ".hive_agents"
                / "financial_transactions_agent"
            )
        self._storage_path.mkdir(parents=True, exist_ok=True)

        self._tool_registry = ToolRegistry()

        llm = None
        if not mock_mode:
            llm = LiteLLMProvider(
                model=self.config.model,
                api_key=self.config.api_key,
                api_base=self.config.api_base,
            )

        self._graph = self._build_graph()

        checkpoint_config = CheckpointConfig(
            enabled=True,
            checkpoint_on_node_start=False,
            checkpoint_on_node_complete=True,
            checkpoint_max_age_days=7,
            async_checkpoint=True,
        )

        entry_point_specs = [
            EntryPointSpec(
                id="default",
                name="Default",
                entry_node=self.entry_node,
                trigger_type="manual",
                isolation_level="shared",
            )
        ]

        self._agent_runtime = create_agent_runtime(
            graph=self._graph,
            goal=self.goal,
            storage_path=self._storage_path,
            entry_points=entry_point_specs,
            llm=llm,
            tools=list(self._tool_registry.get_tools().values()),
            tool_executor=self._tool_registry.get_executor(),
            checkpoint_config=checkpoint_config,
        )

    async def start(self, mock_mode: bool = False) -> None:
        """Set up and start the Hive runtime."""
        if self._agent_runtime is None:
            self._setup(mock_mode=mock_mode)
        if not self._agent_runtime.is_running:
            await self._agent_runtime.start()

    async def stop(self) -> None:
        """Stop the runtime and release references."""
        if self._agent_runtime and self._agent_runtime.is_running:
            await self._agent_runtime.stop()
        self._agent_runtime = None

    async def trigger_and_wait(
        self,
        entry_point: str = "default",
        input_data: dict | None = None,
        session_state: dict | None = None,
    ) -> ExecutionResult | None:
        """Trigger one graph run and wait for completion."""
        if self._agent_runtime is None:
            raise RuntimeError("Agent not started. Call start() first.")

        return await self._agent_runtime.trigger_and_wait(
            entry_point_id=entry_point,
            input_data=input_data or {},
            session_state=session_state,
        )

    async def run(
        self,
        context: dict,
        mock_mode: bool = False,
        session_state: dict | None = None,
    ) -> ExecutionResult:
        """Convenience wrapper for a single execution."""
        await self.start(mock_mode=mock_mode)
        try:
            result = await self.trigger_and_wait(
                "default",
                context,
                session_state=session_state,
            )
            return result or ExecutionResult(success=False, error="Execution timeout")
        finally:
            await self.stop()

    def info(self) -> dict:
        """Human-readable metadata for CLI inspection."""
        return {
            "name": metadata.name,
            "version": metadata.version,
            "description": metadata.description,
            "goal": {
                "name": self.goal.name,
                "description": self.goal.description,
            },
            "nodes": [node.id for node in self.nodes],
            "edges": [edge.id for edge in self.edges],
            "entry_node": self.entry_node,
            "entry_points": self.entry_points,
            "pause_nodes": self.pause_nodes,
            "terminal_nodes": self.terminal_nodes,
            "client_facing_nodes": [node.id for node in self.nodes if node.client_facing],
        }

    def validate(self) -> dict:
        """Basic structural validation."""
        errors: list[str] = []
        warnings: list[str] = []

        node_ids = {node.id for node in self.nodes}
        for edge in self.edges:
            if edge.source not in node_ids:
                errors.append(f"Edge {edge.id}: source '{edge.source}' not found")
            if edge.target not in node_ids:
                errors.append(f"Edge {edge.id}: target '{edge.target}' not found")

        if self.entry_node not in node_ids:
            errors.append(f"Entry node '{self.entry_node}' not found")

        for terminal in self.terminal_nodes:
            if terminal not in node_ids:
                errors.append(f"Terminal node '{terminal}' not found")

        for entry_point_id, node_id in self.entry_points.items():
            if node_id not in node_ids:
                errors.append(
                    f"Entry point '{entry_point_id}' references unknown node '{node_id}'"
                )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }


default_agent = FinancialTransactionsAgent()
