<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:FEF3C7,50:FDE68A,100:FACC15&height=130&section=header&text=HoneyComb%20Agents&fontSize=40&fontColor=3b2f1b&fontAlignY=60&animation=fadeIn" width="100%"/>

### Small, focused AI agents for HoneyComb-style bounties and role-specific workflows

<p>
  <img src="https://img.shields.io/badge/Agents-2-FACC15?style=for-the-badge&logoColor=3b2f1b" alt="Agents" />
  <img src="https://img.shields.io/badge/Framework-Hive-FDE68A?style=for-the-badge&logoColor=3b2f1b" alt="Hive" />
  <img src="https://img.shields.io/badge/Focus-Structured%20Outputs-FBBF24?style=for-the-badge&logoColor=3b2f1b" alt="Structured Outputs" />
  <img src="https://img.shields.io/badge/Theme-HoneyComb-EAB308?style=for-the-badge&logoColor=3b2f1b" alt="HoneyComb" />
</p>

</div>

---

## What This Repo Is

This repository is a collection of **narrow, purpose-built AI agents** designed for HoneyComb-style tasks.

Instead of building one general assistant, this repo focuses on agents that each do one job well:

- a clear role
- a constrained task surface
- a stable prompt/persona
- a structured output contract
- lightweight packaging for marketplace upload

This makes the agents easier to test, improve, reuse, and position as portfolio-ready products.

---

## Agent Or Wrapper?

These projects are best understood as **real AI agents with a strong wrapper layer**.

The model handles the reasoning, while the agent framework adds the operational behavior:

- graph stages
- routing between steps
- validation of outputs
- runtime configuration
- packaging and export
- guardrails around higher-risk workflows

So these are not “just prompts,” and they are not giant autonomous systems either. They sit in the practical middle: **small agent products with explicit contracts and behavior**.

---

## Current Agents

### 1. Analytical Advisor

**Role:** Data Scientist  
**Purpose:** Recommends suitable analytical techniques, surfaces key assumptions, and proposes implementation workflows for data science problems.

Highlights:
- Principal Data Scientist persona
- structured output with enforced sections
- focused on statistical validity and workflow quality

Paths:
- [Agent Notes](/Users/tanujanair/Desktop/HoneyComb/Data%20Science%20AI%20Agent/agents/analytical_advisor/README.md)
- [Marketplace Notes](/Users/tanujanair/Desktop/HoneyComb/Data%20Science%20AI%20Agent/agents/analytical_advisor/marketplace.md)
- [Runnable Export](/Users/tanujanair/Desktop/HoneyComb/Data%20Science%20AI%20Agent/exports/analytical_advisor/README.md)

### 2. Financial Transactions Agent

**Role:** Supply Chain Analyst  
**Purpose:** Reviews transaction requests against controls, approvals, and authorization requirements before deciding whether they are ready, pending, or blocked.

Highlights:
- compliance-first design
- explicit `human_approval_required` field
- audit-oriented workflow and dispositioning

Paths:
- [Agent Notes](/Users/tanujanair/Desktop/HoneyComb/Data%20Science%20AI%20Agent/agents/financial_transactions_agent/README.md)
- [Marketplace Notes](/Users/tanujanair/Desktop/HoneyComb/Data%20Science%20AI%20Agent/agents/financial_transactions_agent/marketplace.md)
- [Runnable Export](/Users/tanujanair/Desktop/HoneyComb/Data%20Science%20AI%20Agent/exports/financial_transactions_agent/README.md)

---

## Repo Structure

```text
agents/
  analytical_advisor/
  financial_transactions_agent/
shared/
  prompts/
  schemas/
  templates/
exports/
  analytical_advisor/
  financial_transactions_agent/
```

---

## Design Principles

- **Narrow scope beats vague capability.** Each agent should solve one concrete workflow.
- **Structured outputs over pretty prose.** A reliable schema is more valuable than a long answer.
- **Compliance matters where risk is high.** Agents handling sensitive workflows should escalate instead of guessing.
- **Packaging matters.** A good agent is not just a prompt; it should be runnable, explainable, and uploadable.

---

## How I’m Using This Repo

This repo is both:

- a working collection of HoneyComb-ready mini agents
- a portfolio of applied agent design patterns

As more agents are added, shared prompts, templates, schemas, and packaging conventions can be reused across roles and tasks.

---

## Local Workflow

Typical flow for a new agent:

1. Define the task, role, and output contract
2. Build the Hive export under `exports/<agent_name>/`
3. Add agent-facing docs under `agents/<agent_name>/`
4. Validate locally
5. Package into a `.zip` for upload

---

## Notes

The Hive framework checkout is best kept as a **local dependency or submodule**, not committed directly into this repo by default.

<div align="center">
  <sub>Built as a growing portfolio of practical AI agents, not just one-off prompt demos.</sub>
</div>

<br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:FACC15,50:FDE68A,100:FEF3C7&height=90&section=footer" width="100%"/>
