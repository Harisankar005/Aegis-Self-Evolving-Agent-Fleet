# Aegis: Self-Evolving Agent Fleet (Freestyle Track)

This project is my Capstone submission for the Google x Kaggle 5-Day AI Agents Intensive (Nov 2025).

Aegis is a Level-4 multi-agent system capable of:
- Planning missions
- Delegating to specialist agents
- Using tools (MCP-compatible)
- Maintaining sessions + long-term memory
- Running long tasks (pause/resume)
- Self-evolving: generating new agents/tools via AgentCreator
- Running LLM-as-Judge evaluation
- Logging, tracing, and metrics
- CI/CD + evaluation gating (AgentOps)

---

## 🚀 Demo Notebook

Run **demo_end_to_end.ipynb** (mocked → no API keys needed):
- Mission → plan → multi-agent execution  
- Judge score  
- AgentCreator generating a new agent  
- Re-run with improved results  
- Traces, logs, metrics

---

## 📈 Evaluation Notebook

Run **eval_harness.ipynb**:
- Golden dataset
- LLM-as-Judge scoring
- Regression testing
- Safety checks

---

## 🧠 Architecture

See `/docs/design.md` for complete:
- Architecture diagram
- Agents, tools, memory design
- Sessions + long-term memory
- MCP tool registry
- AgentOps, safety, logging, tracing

---

## 🛠 Tools & Frameworks

- Python  
- Function-calling agents  
- MCP-style tool registry  
- Sessions & MemoryBank  
- OpenTelemetry traces  
- GitHub Actions CI/CD

---

## 📝 License  
MIT License


