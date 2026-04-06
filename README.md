# Aegis — Self-Evolving Agent Fleet

> **Aegis composes specialist agents to carry out open missions, detects capability gaps, synthesises new agents on the fly, and self-improves via LLM-judges, memory consolidation, and AgentOps.**

Aegis is a **Level-4 autonomous multi-agent system** built as a Google × Kaggle AI Agents Intensive Capstone Project. It automates complex multi-step workflows — research, content generation, deployment, and analytics — through planning, tools, memory, evaluation, and self-evolution.

---

## What Aegis does

Given a user mission, Aegis:

1. **Plans** the task into agent-level subtasks
2. **Dispatches** subtasks to specialist agents (research → copy → analytics → deploy)
3. **Uses tools** (search, HTTP) via an MCP-style registry
4. **Persists memory** across sessions (session state + long-term MemoryBank)
5. **Judges** its own outputs with an LLM-as-Judge evaluation loop
6. **Adapts** by generating new agents when a capability gap is detected
7. **Observes** execution through structured trace spans on every session

---

## Architecture

```
User Mission
    ↓
Planner  ──────────────────────────────────────────────────────────┐
    ↓                                                              │
Orchestrator                                                       │
    ├── MarketResearchAgent   (research step)                      │
    ├── CopyAgent             (copywriting step)                   │
    ├── AnalyticsAgent        (analytics step)                     │
    ├── WebDevAgent           (deployment step)                    │
    ├── [keyword-triggered]   (monitor / sentiment / SEO / email)  │
    │                                                              │
    ├── MCPRegistry           (tool + agent dispatch)             │
    ├── SessionService        (per-mission trace + state)         │
    ├── MemoryBank            (long-term cross-session memory)    │
    │                                                              │
    ├── Judge                 (trajectory evaluation + gap detect)│
    └── AgentCreator ←────────────────────────────────────────────┘
         (synthesises + registers new agents when score < threshold)
```

### Key components

| Component | File | Role |
|---|---|---|
| **Orchestrator** | `services/orchestrator/orchestrator.py` | Mission controller |
| **Planner** | `services/orchestrator/planner.py` | Task decomposition |
| **Router** | `services/orchestrator/router.py` | Agent-to-step resolution |
| **Evaluator** | `services/orchestrator/evaluator.py` | Batch + golden eval |
| **Judge** | `evaluation/judge.py` | Trajectory scoring + gap detection |
| **AgentCreator** | `services/agents/agent_creator.py` | Meta-agent synthesis |
| **MCPRegistry** | `services/tools/mcp_gateway.py` | Tool + agent registry |
| **SessionService** | `services/memory/session_service.py` | Short-term state + trace |
| **MemoryBank** | `services/memory/memory_bank.py` | Long-term persistence |
| **MemoryConsolidation** | `services/memory/memory_consolidation.py` | Summarisation + dedup |

---

## Repository structure

```
aegis/
├── services/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── market_research_agent.py
│   │   ├── copy_agent.py
│   │   ├── analytics_agent.py
│   │   ├── webdev_agent.py
│   │   └── agent_creator.py
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   ├── orchestrator.py
│   │   ├── planner.py
│   │   ├── router.py
│   │   └── evaluator.py
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── session_service.py
│   │   ├── memory_bank.py
│   │   └── memory_consolidation.py
│   └── tools/
│       ├── __init__.py
│       ├── mcp_gateway.py
│       ├── search_tool.py
│       └── http_tool.py
├── evaluation/
│   ├── judge.py
│   ├── metrics.py
│   ├── run_eval.py
│   └── golden_dataset.json
├── tests/
│   ├── test_agents.py
│   ├── test_memory.py
│   ├── test_planner.py
│   └── test_tools.py
├── ci/
│   ├── premerge-eval.yml
│   ├── run_golden_eval.py
│   └── README-ci.md
├── docs/
│   ├── design.md
│   ├── agent_specs/
│   ├── architecture_diagram.png
│   └── system_flow.png
├── infra/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── agent_engine_deploy.md
│   └── cloudrun.md
├── notebooks/
│   ├── demo-end-to-end-ipynb.ipynb
│   └── eval-harness-ipynb.ipynb
├── requirements.txt
└── README.md
```

---

## Local setup

```bash
git clone https://github.com/Harisankar005/Aegis-Self-Evolving-Agent-Fleet
cd Aegis-Self-Evolving-Agent-Fleet
pip install -r requirements.txt
```

### Run a mission

```python
from services.orchestrator.orchestrator import Orchestrator

o      = Orchestrator()
result = o.run_mission("Launch a marketing campaign for Product X targeting students")

print(f"Score : {result['score']}")
print(f"Steps : {[s['step'] for s in result['plan']]}")
print(f"Traces: {len(result['trace'])} spans")
```

### Run the evaluation suite

```bash
python evaluation/run_eval.py --gold evaluation/golden_dataset.json --threshold 0.75
```

### Run unit tests

```bash
pytest tests/ -v
```

### CI golden eval (mirrors GitHub Actions)

```bash
python ci/run_golden_eval.py --threshold 0.75 --golden evaluation/golden_dataset.json
```

---

## Self-evolution loop

When the Judge scores a mission below `EVOLUTION_THRESHOLD` (default 0.85):

1. **Judge** calls `suggest_missing_capability(mission, trace)` → returns a capability label (e.g. `"analytics"`)
2. **AgentCreator** calls `generate_new_agent(capability)`:
   - Generates a JSON spec (name, description, input/output schemas)
   - Builds a Python callable implementing the agent
   - Registers it in the live MCPRegistry
3. Next mission run: the new agent is available for routing
4. Judge bonus scoring: every auto-generated agent that runs earns `+0.02` on top of the base score, so evolution genuinely improves the metric

---

## Evaluation system

The Judge scores trajectories dynamically:

| Agent present in trace | Score contribution |
|---|---|
| MarketResearchAgent | +0.35 |
| CopyAgent | +0.30 |
| WebDevAgent | +0.25 |
| Each auto-generated agent | +0.02 (max +0.10 bonus) |

`Judge.suggest_missing_capability()` inspects both the mission text and the trace to infer what is missing, enabling targeted agent synthesis.

---

## Deployment

```bash
# Docker
docker build -t aegis-agent .
docker run -p 8080:8080 aegis-agent

# Cloud Run
gcloud builds submit --tag gcr.io/<project>/aegis
gcloud run deploy aegis --image gcr.io/<project>/aegis --platform managed
```

---

## Tech stack

Python 3.10+ · Google Gemini (optional, stubbed) · Rich · Pytest · Docker · Cloud Run

---

## License

MIT
