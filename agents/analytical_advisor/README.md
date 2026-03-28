# Analytical Advisor

Principal Data Scientist mini agent for HoneyComb.

## Purpose

Help a user decide:

- which analytical techniques are suitable
- which assumptions matter for validity
- which workflow steps to follow to implement the analysis

## Why This Agent Is Useful

This agent is strong for early-stage analysis planning because it narrows an ambiguous
data problem into a concrete, statistically grounded plan.

## Implementation

The runnable Hive export for this agent lives in:

- `exports/analytical_advisor/`

The package currently uses:

- a 2-node graph (`intake -> advisor`)
- structured Pydantic output validation
- a marketplace-oriented CLI for validate/demo/archive
