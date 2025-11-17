# Aegis: Self-Evolving Agent Fleet  
### Capstone Project — Google x Kaggle AI Agents Intensive  
### Track: Freestyle

---

# 1. Overview  
Aegis is a **Level-4 multi-agent, self-evolving agent system** designed to perform complex multi-step tasks by autonomously:

- Planning a mission  
- Delegating tasks to specialist agents  
- Calling tools via an MCP-compatible tool registry  
- Maintaining session state + long-term memory  
- Evaluating its own performance using LLM-as-Judge  
- Generating new agents/tools when it detects capability gaps  
- Logging and tracing all agent operations  
- Supporting pause/resume long-running missions  
- Running under CI/CD with evaluation gating (AgentOps)

The goal is to demonstrate the **full agentic workflow** taught during the 5-day AI Agents Intensive.

---

# 2. High-Level Architecture

Aegis consists of the following components:

### **2.1 Orchestrator (Root Agent)**  
- Accepts user missions  
- Generates multi-step plans  
- Delegates tasks to specialist agents  
- Stores progress + outputs in the Session Service  
- Calls the LLM-Judge to evaluate runs  
- Triggers AgentCreator for self-evolution  

### **2.2 Planner**
A simple rule-based or LLM-based planner generates steps like:
1. Market research  
2. Copywriting  
3. Deployment  
4. Analytics (auto-created agent)

The planner output is a **sequence of agent calls**.

---

# 3. Multi-Agent System

### **3.1 Specialist Agents**
Aegis includes multiple agents (each exposed as an MCP tool):

| Agent Name                | Purpose                                  |
|--------------------------|------------------------------------------|
| MarketResearchAgent      | Competitor research & insights          |
| CopyAgent                | Marketing copy generation                |
| WebDevAgent              | Creates landing pages & assets          |
| AnalyticsAgent           | (Auto-generated) Campaign analytics       |

### **3.2 AgentCreator (Self-Evolution Module)**
If the judge score < threshold or if a step fails repeatedly:

1. Analyze trace  
2. Identify missing capability  
3. Generate a new agent spec  
4. Register it in the MCP Registry  
5. Re-run mission with new agent  

This demonstrates Level-4 agent behavior.

---

# 4. Tools & MCP Registry

Aegis includes a minimal **MCP-style registry** with:

- Agent schema (name, params, description)  
- Versioning  
- Permissions  
- Registration API  

Each agent is treated as a callable tool.

Example registry entry:
```json
{
  "name": "MarketResearchAgent",
  "description": "Collects competitor insights",
  "parameters": {"query": "string"},
  "version": "1.0"
}
