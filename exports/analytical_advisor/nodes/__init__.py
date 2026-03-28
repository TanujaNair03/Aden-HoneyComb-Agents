"""Node definitions and structured output models for Analytical Advisor."""

from pydantic import BaseModel, Field

from framework.graph import NodeSpec


class TechniqueRecommendation(BaseModel):
    """One candidate method with rationale."""

    technique: str = Field(description="Name of the analytical technique.")
    why: str = Field(
        min_length=20,
        description="Why this technique fits the described data problem.",
    )


class AssumptionItem(BaseModel):
    """One assumption that should be checked before trusting results."""

    assumption: str = Field(description="The assumption or validity condition.")
    relevance: str = Field(
        min_length=20,
        description="Why the assumption matters in this scenario.",
    )


class WorkflowStep(BaseModel):
    """One implementation step in the recommended workflow."""

    step: str = Field(description="Short step title.")
    details: str = Field(
        min_length=20,
        description="Concrete implementation guidance for this step.",
    )


class AnalyticalAdvisorOutput(BaseModel):
    """Structured response enforced by Hive's output_model validation."""

    recommended_analytical_techniques: list[TechniqueRecommendation] = Field(
        min_length=1,
        max_length=5,
        description="Recommended analytical techniques with a brief why for each.",
    )
    key_assumptions: list[AssumptionItem] = Field(
        min_length=2,
        max_length=10,
        description="Statistical or causal assumptions that must hold.",
    )
    workflow_choices: list[WorkflowStep] = Field(
        min_length=4,
        max_length=10,
        description="A practical step-by-step implementation workflow.",
    )


# Intake keeps the user request as a clean, analysis-ready problem statement.
intake_node = NodeSpec(
    id="intake",
    name="Problem Intake",
    description="Clarify the analytics problem and translate it into an analysis brief.",
    node_type="event_loop",
    client_facing=True,
    max_node_visits=0,
    input_keys=["user_query"],
    output_keys=["analysis_brief"],
    success_criteria=(
        "The analysis brief clearly states the business question, target outcome, "
        "data context, decision horizon, and any major constraints or unknowns."
    ),
    system_prompt="""\
You are the intake specialist for a Principal Data Scientist.

Your job is to turn the user's natural-language query into a concise analysis brief.

Rules:
- Do not recommend methods yet.
- Ask at most 2 clarifying questions if the request is materially ambiguous.
- If the problem is already clear enough, confirm your understanding briefly.
- After clarification, call:
  set_output("analysis_brief", "<clear paragraph describing the problem, data context, target, constraints, and success criteria>")
""",
    tools=[],
)


# The advisor node is where outcome-driven execution matters most.
# Hive will only move past this node once the required output keys exist AND the
# response validates against the Pydantic model below. If the LLM omits a section
# or returns the wrong structure, Hive retries the same node with validation feedback.
advisor_node = NodeSpec(
    id="advisor",
    name="Analytical Advisor",
    description=(
        "Recommend statistically valid analytical techniques, assumptions, and "
        "workflow choices for the provided analysis brief."
    ),
    node_type="event_loop",
    client_facing=False,
    max_node_visits=0,
    input_keys=["analysis_brief"],
    output_keys=[
        "recommended_analytical_techniques",
        "key_assumptions",
        "workflow_choices",
    ],
    output_model=AnalyticalAdvisorOutput,
    output_schema={
        "recommended_analytical_techniques": {
            "type": "array",
            "required": True,
            "description": "List of recommended techniques and why they fit.",
        },
        "key_assumptions": {
            "type": "array",
            "required": True,
            "description": "List of assumptions or validity conditions.",
        },
        "workflow_choices": {
            "type": "array",
            "required": True,
            "description": "Ordered implementation workflow steps.",
        },
    },
    success_criteria=(
        "The response contains a statistically defensible recommendation, clearly "
        "states assumptions, and provides an implementation workflow that a data "
        "scientist could follow."
    ),
    system_prompt="""\
You are a Principal Data Scientist acting as an Analytical Advisor.

Your standards:
- Expert-level statistical reasoning
- Strong concern for identification strategy, bias, leakage, and uncertainty
- Preference for the simplest method that is valid for the decision at hand
- Honest discussion of tradeoffs, assumptions, and failure modes

How to reason:
1. Infer the problem type from the analysis_brief:
   classification, regression, clustering, causal inference, experimentation,
   forecasting, anomaly detection, survival analysis, dimensionality reduction,
   or exploratory analytics.
2. Recommend 1-3 techniques that are appropriate for the data-generating process
   and business decision. Include at least one interpretable option when feasible.
3. State the assumptions that most affect validity. Focus on assumptions that
   would change the decision if violated.
4. Provide an implementation workflow that covers:
   data audit, preprocessing, feature strategy, validation design, modeling or
   estimation, diagnostics, and communication.

Output rules:
- Return valid JSON only.
- Do not include markdown, code fences, or extra narration.
- Use these exact top-level keys:
  recommended_analytical_techniques
  key_assumptions
  workflow_choices
- recommended_analytical_techniques: 1-3 items, each with technique and why
- key_assumptions: 2-8 items, each with assumption and relevance
- workflow_choices: 4-8 ordered steps, each with step and details

Quality bar:
- Prefer methods that align with sample size, class imbalance, temporal ordering,
  observational vs experimental data, and explainability needs.
- Flag common threats such as non-independence, confounding, non-stationarity,
  selection bias, missing-not-at-random data, distribution shift, and metric mismatch.
- Do NOT call save_data, append_data, or any file-writing tool for the final answer.
- Do NOT replace any field with placeholders like "Saved to ..." or "Use load_data(...)"
- Keep the response compact enough to fit inline as a single valid JSON object.
""",
    tools=[],
)

__all__ = [
    "AnalyticalAdvisorOutput",
    "AssumptionItem",
    "TechniqueRecommendation",
    "WorkflowStep",
    "intake_node",
    "advisor_node",
]
