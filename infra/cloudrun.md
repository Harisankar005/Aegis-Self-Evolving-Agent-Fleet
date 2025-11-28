# Deploying Aegis to Google Cloud Run

This document explains how to deploy the Aegis multi-agent system to **Google Cloud Run**.

---

## ✅ Prerequisites

- Google Cloud account
- gcloud CLI installed locally
- Billing enabled
- Artifact Registry enabled
- Cloud Run API enabled

Run:

```bash
gcloud auth login
gcloud config set project Aegis: Self-Evolving Agent Fleet

📦 Step 1 — Build & Push Docker Image
gcloud builds submit --tag \
  us-central1-docker.pkg.dev/Aegis: Self-Evolving Agent Fleet/aegis/aegis-image

This will:

- Build Docker image

- Push it to Artifact Registry

🚀 Step 2 — Deploy to Cloud Run
gcloud run deploy aegis-service \
  --image us-central1-docker.pkg.dev/Aegis: Self-Evolving Agent Fleet/aegis/aegis-image \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1

🌐 Step 3 — Access Your Service
After deployment, Cloud Run returns a public HTTPS endpoint:
https://aegis-service-xxxxx-uc.a.run.app
This endpoint becomes the orchestrator API endpoint for your agents or UI.

🔒 Security Notes

- DO NOT hardcode keys in Docker or environment variables.

- Use Google Secret Manager for model keys if needed.

- Disable unauthenticated access for private agent usage.

You have now deployed Aegis to Cloud Run successfully!

---

# 🟦 **4. agent_engine_deploy.md**
Deploy Aegis using **Agent Engine** (agent runtime provided by Google).

```markdown
# Deploying Aegis using Google Agent Engine

This document explains how to deploy the Aegis multi-agent system using **Agent Engine**, enabling:
- Automatic session management
- Model integration
- Scaling
- Logging & Tracing
- Runtime safety

---

## 1. Create an Agent Engine Application

In the Google Cloud Console:

1. Navigate to **AI Agent Builder → Agent Engine**
2. Click **Create Application**
3. Choose **Custom Agent**
4. Provide:
   - Name: `aegis-orchestrator`
   - Runtime: Python
   - Cloud Run region: `us-central1`

---

## 2. Add Your Agent Orchestration Code

Upload these files:

services/orchestrator/orchestrator.py
services/agents/*
services/tools/*
services/memory/*
evaluation/judge.py


Ensure `orchestrator.py` exposes a FastAPI or function entrypoint named `app`.

Example:

```python
from fastapi import FastAPI
app = FastAPI()

@app.post("/mission")
def run_mission(mission: str):
    # call planner + agents
    ...
3. Configure Runtime Environment

In the Agent Engine setup:

- Add requirements.txt

- Set environment variables:

MEMORY_DB_HOST=redis
VECTOR_DB_HOST=milvus

4. Add Tools
In the "Tools" section, register:

- Search tool

- HTTP tool

- Code execution tool

- Custom agent tools

You can create an AgentTool wrapper for sub-agents.

5. Deploy

Click Deploy.

Agent Engine will:

- Build your container

- Deploy via Cloud Run

- Attach monitoring and tracing

- Provide you with a private endpoint for calling your agent

6. Test via CURL

curl -X POST https://<AGENT_ENGINE_URL>/mission \
  -H "Content-Type: application/json" \
  -d '{"mission": "Launch a micro campaign for Product X"}'

You're Done! 🎉

Aegis is now deployed using Google Agent Engine with:

- Built-in scaling

- Observability

- Safe execution

- Session management




