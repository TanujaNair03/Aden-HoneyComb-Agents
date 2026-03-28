# HoneyComb Agents

Collection of small, focused AI agents for HoneyComb-style bounties and role-specific workflows.

## What This Repo Is

This repo is meant to hold many narrow agents rather than one large general assistant.
Each agent should have:

- A clearly defined job to do
- A stable prompt/persona
- A structured output contract
- Lightweight packaging for upload
- Notes on category, token use, and marketplace positioning

## Wrapper vs Agent

These projects are best thought of as **task-specific agents built with an agent wrapper/runtime**.

That means:

- The intelligence mostly comes from the underlying model and prompt
- The "agent" behavior comes from the wrapper around it:
  graph stages, routing, validation, runtime config, packaging, and export
- As the agents become more capable, they can add tools, memory, external context,
  retries, and multi-step workflows

So this is still an AI agent, but a **narrow agent product** rather than a fully autonomous long-horizon system.

## Repo Layout

```text
agents/
  analytical_advisor/
shared/
  prompts/
  schemas/
  templates/
exports/
  analytical_advisor/
```

## Conventions

- `agents/<agent_name>/` holds agent-specific docs, notes, and product metadata
- `exports/<agent_name>/` holds the runnable/exportable Hive package
- `shared/` holds reusable prompt, schema, and packaging patterns

The Hive framework checkout is best kept as a local dependency or git submodule,
not committed directly into this repo by default.

## Current Agent

- `analytical_advisor`: Principal Data Scientist advisor for method selection,
  assumptions, and workflow guidance
