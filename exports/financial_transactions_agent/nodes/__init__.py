"""Node definitions and structured output models for Financial Transactions Agent."""

from pydantic import BaseModel, Field

from framework.graph import NodeSpec


class ControlCheck(BaseModel):
    """One control or compliance requirement."""

    control: str = Field(description="Name of the control or approval requirement.")
    status: str = Field(
        description="Status of the control. Use one of: satisfied, missing, unclear."
    )
    notes: str = Field(
        min_length=10,
        description="Why the control is satisfied, missing, or unclear.",
    )


class WorkflowStep(BaseModel):
    """One operational step in the transaction process."""

    step: str = Field(description="Short workflow step title.")
    details: str = Field(
        min_length=15,
        description="Concrete execution or remediation instruction.",
    )


class TransactionDecision(BaseModel):
    """Structured decision output for a proposed transaction."""

    transaction_summary: str = Field(
        min_length=20,
        description="Short summary of the requested transaction and business purpose.",
    )
    approval_status: str = Field(
        description=(
            "Overall disposition. Use one of: ready_to_execute, pending_approval, blocked."
        )
    )
    human_approval_required: bool = Field(
        description="Whether a human approver must explicitly review or sign off before execution."
    )
    required_controls_and_authorizations: list[ControlCheck] = Field(
        min_length=3,
        max_length=10,
        description="List of controls, approvals, and compliance checks.",
    )
    execution_workflow: list[WorkflowStep] = Field(
        min_length=4,
        max_length=8,
        description="Step-by-step execution or remediation workflow.",
    )
    audit_notes: str = Field(
        min_length=20,
        description="Audit trail notes documenting rationale, exceptions, and next action.",
    )


intake_node = NodeSpec(
    id="intake",
    name="Transaction Intake",
    description="Clarify the requested financial transaction and required approvals.",
    node_type="event_loop",
    client_facing=True,
    max_node_visits=0,
    input_keys=["user_query"],
    output_keys=["transaction_brief"],
    success_criteria=(
        "The transaction brief clearly identifies the transaction type, amount, "
        "counterparties, purpose, known approvals, and missing information."
    ),
    system_prompt="""\
You are the intake specialist for a controlled financial transactions agent.

Your job is to convert the user's request into a concise transaction brief.

Rules:
- Do not approve or reject the transaction yet.
- Ask at most 2 clarifying questions if a key detail is missing.
- Focus on transaction type, amount, currency, counterparty, purpose, requester,
  known approvals, compliance constraints, and execution deadline.
- After clarification, call:
  set_output("transaction_brief", "<clear paragraph summarizing the transaction request, approval state, controls, and missing items>")
""",
    tools=[],
)


decision_node = NodeSpec(
    id="decision",
    name="Controls and Authorization Review",
    description=(
        "Evaluate whether a financial transaction is ready, pending approval, "
        "or blocked based on controls and authorization requirements."
    ),
    node_type="event_loop",
    client_facing=False,
    max_node_visits=0,
    input_keys=["transaction_brief"],
    output_keys=[
        "transaction_summary",
        "approval_status",
        "human_approval_required",
        "required_controls_and_authorizations",
        "execution_workflow",
        "audit_notes",
    ],
    output_model=TransactionDecision,
    success_criteria=(
        "The response clearly states whether the transaction can proceed, names "
        "the required controls, and provides an auditable workflow."
    ),
    system_prompt="""\
You are a financial transactions control specialist.

Your role:
- Evaluate transaction requests against process discipline, approval requirements,
  segregation of duties, compliance checks, and auditability.
- Be conservative. If approvals, controls, or authorization are missing or unclear,
  do NOT mark the transaction ready to execute.
- This agent supports execution readiness, but it must not bypass governance.

Decision rules:
1. Use "ready_to_execute" only when the transaction brief clearly indicates that
   required approvals and controls are satisfied.
2. Use "pending_approval" when the transaction appears legitimate but approvals,
   documents, or control checks are still incomplete.
3. Use "blocked" when the request has control failures, missing authorization,
   policy conflicts, or insufficient auditability.

Output rules:
- Return valid JSON only.
- Do not include markdown or extra commentary.
- Use these exact top-level keys:
  transaction_summary
  approval_status
  human_approval_required
  required_controls_and_authorizations
  execution_workflow
  audit_notes
- required_controls_and_authorizations must be a list of objects with:
  control, status, notes
- execution_workflow must be a list of objects with:
  step, details
- Do NOT save fields to files or return placeholders like "Saved to ..."

What to emphasize:
- authorization level
- segregation of duties
- documentation completeness
- counterparty verification
- amount / threshold approval
- policy compliance
- audit trail quality
- exception handling
- Set human_approval_required to true whenever approvals are missing, unclear,
  threshold-sensitive, exception-based, or when the transaction should not be
  auto-executed without accountable human sign-off.
""",
    tools=[],
)

__all__ = [
    "ControlCheck",
    "TransactionDecision",
    "WorkflowStep",
    "intake_node",
    "decision_node",
]
