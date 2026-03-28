# Analytical Advisor

Hive agent for the HoneyComb Data Scientist bounty:

> Provide guidance on suitable analytical techniques, assumptions, and workflow choices for specific problems.

## What this agent does

- Accepts a natural-language data science problem description
- Clarifies the problem into an analysis brief
- Returns a structured advisory response with:
  - Recommended Analytical Techniques
  - Key Assumptions
  - Workflow Choices

## Why the structure is reliable

The `advisor` node uses Hive's `output_model` support with a Pydantic schema. That means Hive validates the LLM response before marking the node complete. If the response is missing a section or uses the wrong shape, Hive retries the node with validation feedback.

## Run

From a Hive repository root:

```bash
PYTHONPATH=core:. python -m exports.analytical_advisor validate
PYTHONPATH=core:. python -m exports.analytical_advisor demo
PYTHONPATH=core:. python -m exports.analytical_advisor run --query "I need to estimate uplift from a retention campaign on observational CRM data."
```

## Package for upload

```bash
PYTHONPATH=core:. python -m exports.analytical_advisor archive
```

That command writes a `.zip` containing the standard Hive export package.
