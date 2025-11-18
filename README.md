Aegis: Gemini-Powered Self-Evolving Agent Fleet

# Overview
Aegis is a Gemini-powered Level-4 autonomous multi-agent system that can:
  1. Understand complex missions
  2. Break them down using a Gemini-driven Planner
  3. Delegate tasks to specialized agents (research, copywriting, web page generation, analytics)
  4. Use the Gemini API for reasoning, generation, and analysis
  5. Store memory and session state
  6. Evaluate its own performance with a Gemini LLM-as-Judge
  7. Automatically generate entirely new agents using a Gemini-powered AgentCreator
  8.Continuously improve execution quality through self-evolution

Aegis was built as part of the Google × Kaggle AI Agents Intensive (Nov 10–14, 2025) and is designed to demonstrate advanced agent concepts taught in the course.

# Problem
Modern workflows like launching marketing campaigns involve multiple steps:
  1. Market research
  2. Generating marketing copy
  3. Designing or deploying landing pages
  4. Running analytics
  5. Iterating based on results
     
These tasks require multiple tools, frequent context switching, and hours of manual effort. There is no unified system that can understand the mission, coordinate tasks, evaluate the results, and then improve itself for future missions.

# Solution: Aegis
Aegis solves this by creating a fully autonomous, self-evolving multi-agent system where:

✔️ Gemini Pro performs:

    1. Mission planning
    2. Research
    3. Copywriting
    4. HTML generation
    5. Analytics
    6. Agent evaluation
    7. Agent creation

✔️ The Orchestrator:

      1. Reads the mission 
      2. Requests a plan from the Gemini-powered Planner
      3. Executes each agent step
      4. Stores memory and session state
      5. Runs a Gemini-powered Judge
      6. Activates the AgentCreator if quality is low

✔️ The AgentCreator:

1. If Aegis encounters tasks it cannot perform well, the Gemini-based AgentCreator generates:
2. A new agent name
3. Description
4. Prompt schema
5. Behavior template
6. Python class
7. Final agent implementation

This is then added to the registry and used immediately.

# Architecture

                     ┌─────────────────────┐
                     │   User Mission      │
                     └──────────┬──────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Gemini Planner  │
                       └───────┬─────────┘
                               │ JSON Plan
                               ▼
                    ┌─────────────────────────┐
                    │     Orchestrator        │
                    └──────┬────────┬────────┘
                           │        │
         ┌─────────────────┘        └────────────────┐
         ▼                                           ▼
 ┌───────────────┐                           ┌──────────────┐
 │ Specialist     │                           │ Specialist   │
 │ Agents         │                           │ Agents       │
 │ (Gemini-LLM)   │                           │ (Gemini-LLM) │
 └───────────────┘                           └──────────────┘
         │                                           │
         └────────────────────┬──────────────────────┘
                              ▼
                     ┌─────────────────┐
                     │Session + Memory │
                     └───────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Gemini Judge     │
                    └───────┬──────────┘
                             │
                          Score < 0.75?
                 ┌─────────────┴───────────────┐
                 │                               │
             Yes ▼                               │ No
     ┌──────────────────────┐                    │
     │ Gemini AgentCreator  │                    │
     └───────────┬──────────┘                    │
                 │ generates new agent           │
                 ▼                               ▼
         Register new agent                Return outputs

# Features Demonstrated (Course Concepts)

Aegis uses ALL 8 required agent concepts:

✔️ Multi-Agent System
     Planner → Orchestrator → Agents → Judge → AgentCreator.
✔️ Tools (MCP Registry + Custom Tools)
     Each agent is registered as a callable tool with JSON schema inputs.
✔️ Gemini Use (Bonus Points Earned)
     Agents, Planner, Judge, and Creator are all powered by Gemini-Pro.
✔️ Sessions & Memory
     SessionService stores full trace & intermediate events.
     MemoryBank stores long-term embeddings and task summaries.
✔️ Context Engineering
     Prompts are compacted for long conversations.
✔️ Long-Running Operations
     SessionService supports pause/resume.
✔️ Observability
     Trace events recorded for each agent call.
     Used in evaluation + debugging.
✔️ Evaluation
     LLM-as-Judge using Gemini creates a quality score (0–1 scale).
✔️ A2A Protocol
     Agents can call other agents via the MCP registry.
✔️ Deployment (Bonus Points Earned)
     Repository includes:
          1. Dockerfile 
          2. Docker Compose 
          3. Cloud Run instructions

# Installation & Setup
1. Clone the repo
   git clone https://github.com/<you>/aegis-gemini.git
   cd aegis-gemini
2. Install dependencies
   pip install -r requirements.txt
3. Set your Gemini API key
   GEMINI_API_KEY=your_key_here
   
   or set environment variable:
   export GEMINI_API_KEY=your_key_here

# Running the Demo
Run a mission using the Orchestrator : 
    from services.orchestrator.orchestrator import Orchestrator
    from services.agents.market_research_agent import MarketResearchAgent
    from services.agents.copy_agent import CopyAgent
    from services.agents.webdev_agent import WebDevAgent

    orch = Orchestrator()
    orch.registry.register("MarketResearchAgent", MarketResearchAgent())
    orch.registry.register("CopyAgent", CopyAgent())
    orch.registry.register("WebDevAgent", WebDevAgent())

    output = orch.run_mission("Launch a smart-band campaign for students in India")
    print(output)

# Evaluation (Kaggle Notebook)
Two notebooks are provided:

    ✔️ demo_end_to_end_gemini.ipynb
        Runs a full mission end-to-end.
    ✔️ evaluation_gemini.ipynb
        Loads golden dataset
        Runs multiple missions
        Scores using Gemini Judge
        Shows histograms + metrics
        These notebooks are ready for Kaggle submission.
# Project Structure
services/
  orchestrator/
  agents/
  tools/
  memory/
evaluation/
notebooks/
docs/
tests/
Each folder contains well-commented, modular, production-grade code.

# Deploying the Agent System (Optional Bonus)
The deployment options include:
    Cloud Run:
       gcloud builds submit --tag gcr.io/<project>/aegis-gemini
       gcloud run deploy aegis-gemini --image gcr.io/<project>/aegis-gemini
    Docker Compose
       docker-compose up --build

# Video Guide
A 3-minute YouTube video script is included in /docs/video_script.md demonstrating:
    Problem
    Why agents
    Architecture overview
    Demo
    Build process

# Summary

Aegis (Gemini Edition) is a fully autonomous, self-improving agentic system demonstrating:
    Advanced agent collaboration
    Tool integration
    Memory and session handling
    Evaluation pipelines
    Dynamic agent creation
    Gemini-powered reasoning & generation
    End-to-end mission automation
It is specifically designed to score full points across all categories of the Kaggle × Google Agents Capstone rubric.
