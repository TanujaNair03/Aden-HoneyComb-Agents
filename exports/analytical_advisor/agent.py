"""Agent graph construction for the Analytical Advisor Hive agent."""

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
from .nodes import advisor_node, intake_node

goal = Goal(
    id="analytical-advisor-goal",
    name="Analytical Advisor",
    description=(
        "Advise data scientists on suitable analytical techniques, critical "
        "assumptions, and implementation workflow choices for real-world problems."
    ),
    success_criteria=[
        SuccessCriterion(
            id="method-fit",
            description="Recommended techniques fit the problem type and decision need.",
            metric="recommendation_relevance",
            target=">=0.9",
            weight=0.35,
        ),
        SuccessCriterion(
            id="assumption-rigor",
            description="Key assumptions and validity conditions are clearly identified.",
            metric="assumption_coverage",
            target=">=0.9",
            weight=0.35,
        ),
        SuccessCriterion(
            id="workflow-actionability",
            description="The workflow is concrete enough for implementation.",
            metric="workflow_actionability",
            target=">=0.85",
            weight=0.30,
        ),
    ],
    constraints=[
        Constraint(
            id="statistical-validity",
            description="Recommendations must emphasize statistical validity and defensible inference.",
            constraint_type="hard",
            category="quality",
        ),
        Constraint(
            id="no-overclaiming",
            description="Do not claim causality, generalization, or certainty unless warranted by the problem setup.",
            constraint_type="hard",
            category="safety",
        ),
        Constraint(
            id="structured-response",
            description="Always return the three required response sections in structured form.",
            constraint_type="hard",
            category="format",
        ),
    ],
)

nodes = [intake_node, advisor_node]

edges = [
    EdgeSpec(
        id="intake-to-advisor",
        source="intake",
        target="advisor",
        condition=EdgeCondition.ON_SUCCESS,
        priority=1,
    )
]

entry_node = "intake"
entry_points = {"default": "intake"}
pause_nodes: list[str] = []
terminal_nodes = ["advisor"]


class AnalyticalAdvisorAgent:
    """
    Two-stage advisory agent.

    Flow: intake -> advisor

    Outcome-driven routing in this agent:
    - Hive enters `intake` first and waits until a clean `analysis_brief` exists.
    - On success, Hive routes to `advisor`.
    - The `advisor` node is guarded by a Pydantic output model; Hive does not
      consider the node complete unless all three required sections validate.
    - If validation fails, Hive retries the same node with feedback instead of
      advancing with a malformed answer.
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
        """Build the GraphSpec consumed by Hive runtime."""
        return GraphSpec(
            id="analytical-advisor-graph",
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
        """Prepare storage, tools, model provider, and runtime."""
        storage_override = os.environ.get("HIVE_AGENT_STORAGE")
        if storage_override:
            self._storage_path = Path(storage_override).expanduser().resolve()
        else:
            # Default to project-local storage so the agent runs cleanly in sandboxes
            # and developer workspaces without needing write access to ~/.hive.
            self._storage_path = Path(__file__).resolve().parents[2] / ".hive_agents" / "analytical_advisor"
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
        """Trigger one graph run and wait for the terminal node."""
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
        """Basic structural validation before runtime execution."""
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


default_agent = AnalyticalAdvisorAgent()
