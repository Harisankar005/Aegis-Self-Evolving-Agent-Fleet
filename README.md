# Aegis — Self-Evolving Agent Fleet

> **Aegis composes specialist agents to carry out open missions, detects capability gaps, synthesizes new agent/tools on the fly, and self-improves via LLM-judges, memory consolidation, and AgentOps.**

Aegis is a **Level-4 autonomous multi-agent system** built as a **Google x Kaggle AI Agents Intensive Capstone Project**. It is designed to automate complex multi-step workflows such as **research, content generation, deployment, and analytics** through planning, tools, memory, evaluation, and self-evolution.

[Repository](https://github.com/Harisankar005/Aegis-Self-Evolving-Agent-Fleet)

---

## Why this project matters

Most agent demos stop at “chat with tools.” Aegis goes further:

- plans a mission into executable steps
- delegates work to specialist agents
- stores context across sessions
- evaluates itself with an LLM judge
- creates new agents when capabilities are missing
- provides observability through traces, logs, and metrics
- ships with Docker and Cloud Run deployment scaffolding

This is not a wrapper. It is an **agentic system architecture**.

---

## What Aegis does

Given a user mission, Aegis can:

1. **Plan** the task into subtasks
2. **Dispatch** subtasks to specialist agents
3. **Use tools** to gather data or generate outputs
4. **Persist memory** across conversations and long-running work
5. **Judge** its own outputs with Gemini-powered evaluation
6. **Adapt** by generating new agents when a capability gap appears
7. **Observe** execution with structured traces and logs
8. **Deploy** using Docker and Cloud Run templates

---

## Core capabilities

- **Multi-agent collaboration**
- **MCP-style tool use**
- **Sessions + long-term memory**
- **Observability**: tracing, logs, metrics
- **LLM-as-Judge evaluation**
- **Automatic agent generation** via `AgentCreator`
- **Gemini integration**
- **Deployment scaffolding** with Docker + Cloud Run

---

## Architecture at a glance

```text
User Mission
    ↓
Planner Agent
    ↓
Orchestrator
    ├── MarketResearchAgent
    ├── CopyAgent
    ├── WebDevAgent
    ├── AnalyticsAgent (auto-generated)
    ├── Judge Agent
    └── AgentCreator (meta-agent)

Supporting services:
- MCP Registry
- SessionService
- MemoryBank
- Evaluation harness
- Trace/log pipeline
```

### Key components

- **Orchestrator** — manages execution and session control
- **Planner** — breaks a mission into actionable steps
- **Specialist agents** — research, copywriting, web/dev, analytics
- **MCP Registry** — routes calls to tools and agents
- **SessionService** — stores conversation and execution state
- **MemoryBank** — stores embeddings and long-term summaries
- **Judge Agent** — evaluates outputs and triggers improvement
- **AgentCreator** — generates new agents automatically when needed

---

## Repository structure

```text
aegis-agent-fleet/
├── services/
├── orchestrator/
├── agents/
├── tools/
├── memory/
├── evaluation/
├── notebooks/
├── tests/
├── docs/
├── infra/
├── ci/
└── README.md
```

---

## Evaluation and testing

Aegis includes:

- a **demo notebook** for end-to-end run-throughs
- an **evaluation notebook** with golden dataset + judge scoring
- tests under `/tests/` to verify:
  - agents run end to end
  - the planner produces valid plans
  - the registry behaves correctly

---

## Local setup

```bash
git clone https://github.com/Harisankar005/Aegis-Self-Evolving-Agent-Fleet
cd Aegis-Self-Evolving-Agent-Fleet
pip install -r requirements.txt
```

### Run a demo

The repository includes orchestrator and agent modules under `services/`. Start from the demo notebook or wire up the agents through the orchestrator as shown in the project documentation.

---

## Deployment

Aegis includes Docker and Cloud Run instructions.

```bash
docker build -t aegis-agent .
docker run -p 8080:8080 aegis-agent

gcloud builds submit --tag gcr.io/<project>/aegis
gcloud run deploy aegis --image gcr.io/<project>/aegis --platform managed
```

---

## What recruiters should notice first

- **System design**, not isolated scripts
- **Agent orchestration**, not just prompt chaining
- **Evaluation**, not just generation
- **Observability**, not just execution
- **Extensibility**, through automatic agent creation

---

## Tech stack

The repository is primarily Python-based and includes Jupyter notebooks and Docker support.

---

## License

MIT License
