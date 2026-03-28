# Financial Transactions Agent

Hive agent for controlled financial transaction execution readiness.

## What this agent does

- Accepts a natural-language transaction request
- Clarifies the transaction details and approval state
- Determines whether the transaction is:
  - `ready_to_execute`
  - `pending_approval`
  - `blocked`
- Returns auditable controls, workflow steps, and rationale

## Why this agent is structured this way

This is a higher-risk workflow than a normal advisory agent, so the design is intentionally conservative:

- missing approvals lead to escalation rather than silent approval
- structured outputs force explicit control coverage
- the agent focuses on execution readiness, not governance bypass

## Run

From a Hive repository root:

```bash
PYTHONPATH=core:. python -m exports.financial_transactions_agent validate
PYTHONPATH=core:. python -m exports.financial_transactions_agent demo
PYTHONPATH=core:. python -m exports.financial_transactions_agent run --query "Process a vendor payment of USD 48,000 with procurement approval but pending finance sign-off."
```

## Package for upload

```bash
PYTHONPATH=core:. python -m exports.financial_transactions_agent archive
```
