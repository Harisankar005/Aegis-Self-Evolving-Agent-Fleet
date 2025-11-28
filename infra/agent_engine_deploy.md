# Deploying Aegis to a Managed Agent Runtime (Agent Engine)  
**File:** `infra/agent_engine_deploy.md`  
**Purpose:** step-by-step, copy-pasteable deployment guide for running the Aegis agent backend on a managed cloud Agent Engine (preferred) or on Cloud Run / GKE as a fallback. Includes Docker, CI/CD, service account, secrets, monitoring and production best practices.

> NOTE — “Agent Engine” is used here as a generic name for a managed agent runtime (for example Google Vertex AI Agent Engine or a comparable managed service). If your cloud provider exposes an explicit `agent`/`ai agent` product, substitute the provider-specific CLI and console steps where marked.

---

## Table of contents
1. Prerequisites
2. Prepare the service (container + config)
3. Push the image (Artifact Registry / Container Registry)
4. Deploy to Agent Engine (managed runtime) — recommended
5. Fallback: Deploy to Cloud Run (simple) or GKE (advanced)
6. Secrets, env vars & credentials
7. CI/CD (GitHub Actions) — build → push → deploy
8. Observability, health checks & monitoring
9. Production best practices & cost controls
10. Troubleshooting checklist

---

## 1) Prerequisites
Before starting, make sure you have:

- A cloud account and a project with billing enabled (e.g., GCP project).  
- `gcloud` CLI (or cloud provider CLI) installed and authenticated.  
- `docker` installed (for building containers).  
- A repository containing your Aegis code (FastAPI / orchestrator / agents).  
- No API keys or secrets committed to GitHub.

Recommended cloud APIs to enable (GCP example):  
- Cloud Run / Vertex AI / Agent Engine API  
- Artifact Registry (or Container Registry)  
- IAM & Service Account APIs  
- Secret Manager  
- Monitoring / Logging (Stackdriver / Cloud Monitoring)

---

## 2) Prepare the service — Dockerfile & config
Create a production-ready Dockerfile at repo root. Example (FastAPI + Uvicorn):

```dockerfile
# infra/Dockerfile
FROM python:3.10-slim

WORKDIR /app
# Install runtime dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY services /app/services
COPY infra/start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Non-root user for security
RUN addgroup --system app && adduser --system --ingroup app app
USER app

EXPOSE 8080
ENV PORT=8080
CMD ["/app/start.sh"]

Config files

- Provide a config.yaml or .env.template (do not include secrets).

- Document required ENV variables in README: PROJECT_ID, ARTIFACT_REGISTRY_REGION, MEMORY_DB_URL, REDIS_URL, SECRET_MANAGER_PREFIX, etc.

## 3) Push the container image

Example using Artifact Registry (GCP):

# Authenticate Docker with Artifact Registry (GCP)
gcloud auth configure-docker LOCATION-docker.pkg.dev

# Build image
docker build -t LOCATION-docker.pkg.dev/PROJECT/REPO/aegis:latest .

# Push
docker push LOCATION-docker.pkg.dev/PROJECT/REPO/aegis:latest

Replace LOCATION, PROJECT, REPO with your values (e.g., us-central1-docker.pkg.dev/my-project/my-repo/aegis:latest).

If using Docker Hub or another registry, replace with that registry’s workflow.

4) Deploy to Agent Engine (managed runtime) — recommended

These are high-level steps because managed runtimes can evolve. You will typically perform these actions in the cloud console or via provider CLI.

A) Create a dedicated service account

Create a service account that the runtime uses. Grant least privilege:

roles/run.invoker (if Cloud Run)

roles/storage.objectViewer (read artifacts/images)

roles/secretmanager.secretAccessor (read secrets)

roles/cloudsql.client (if using Cloud SQL)

roles/monitoring.metricWriter & roles/logging.logWriter

Example (GCP):
gcloud iam service-accounts create aegis-runtime \
  --description="Aegis runtime SA" \
  --display-name="aegis-runtime-sa"

gcloud projects add-iam-policy-binding PROJECT \
  --member="serviceAccount:aegis-runtime@PROJECT.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
# add other roles as needed

B) Register the container as an agent runtime image

(Depending on provider, you may register a "model/agent" resource pointing to your container image.)

C) Create an agent deployment config

Create an agent resource that points to the container image and specifies resources, env vars, secrets, and autoscaling rules. Example YAML (conceptual):

# infra/agent_deploy.yaml (conceptual)
apiVersion: ai.cloud/v1
kind: AgentDeployment
metadata:
  name: aegis-agent
spec:
  container:
    image: LOCATION-docker.pkg.dev/PROJECT/REPO/aegis:latest
    command: ["/app/start.sh"]
    env:
      - name: MEMORY_DB_URL
        valueFrom:
          secretKeyRef:
            name: aegis-secrets
            key: MEMORY_DB_URL
      - name: REDIS_URL
        valueFrom:
          secretKeyRef:
            name: aegis-secrets
            key: REDIS_URL
  resources:
    cpu: 1
    memory: 2Gi
  scaling:
    minReplicas: 1
    maxReplicas: 4
  healthCheck:
    path: /health
    timeoutSeconds: 5

Action: Consult your cloud provider docs for the exact CLI to create an Agent Deployment from YAML. For Vertex AI, look for gcloud ai agents create / gcloud beta ai agents or use the Console UI to create an agent with the container image.

D) Attach IAM / runtime service account & secrets

Configure the runtime to use the SA you created.

Wire secrets from Secret Manager (or equivalent) into environment variables.

E) Verify deployment

Ensure /health returns 200 and readiness.

Check logs in the provider console (Stackdriver / Cloud Logging).

Run a quick end-to-end mission via the demo notebook pointing to the deployed endpoint.

5) Fallback: Cloud Run (simple) or GKE (advanced)

If Agent Engine isn't available, Cloud Run is a solid managed alternative.

Cloud Run (GCP) quick commands:
gcloud run deploy aegis --image LOCATION-docker.pkg.dev/PROJECT/REPO/aegis:latest \
  --region us-central1 \
  --platform managed \
  --service-account aegis-runtime@PROJECT.iam.gserviceaccount.com \
  --set-env-vars MEMORY_DB_URL=projects/PROJECT/secrets/MEMORY_DB_URL:latest

GKE (when you need VPC / private networking / stateful services)

Build Helm chart or Kubernetes manifests (Deployment + Service + HPA).

Use Secret objects referencing Secret Manager (workload identity recommended).

Use LoadBalancer or Ingress for public access; configure HTTPS.

6) Secrets & environment variables

Never store secrets in Git. Use a secret manager.

Secret Manager (GCP) pattern:

Store secrets in Secret Manager.

Grant the runtime service account secretmanager.secretAccessor.

Inject secrets as env vars using provider's native secret mounting or via startup code that reads Secret Manager on boot.

Example runtime envs (non-sensitive):

MEMORY_DB_URL (connection string)

REDIS_URL

AGENT_REGISTRY_URL (if remote)

LOG_LEVEL=INFO

Sensitive items (store in secret manager):

LLM API keys (if needed)

DB passwords

OAuth client secrets

7) CI/CD (GitHub Actions) — build → push → deploy

Example ci/deploy.yml skeleton:

name: Build & Deploy
on:
  push:
    branches: [main]

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
        with:
          project_id: ${{ secrets.GCP_PROJECT }}
          service_account_key: ${{ secrets.GCP_SA_KEY }}
      - name: Build Docker image
        run: |
          docker build -t LOCATION-docker.pkg.dev/$PROJECT/$REPO/aegis:${{ github.sha }} .
          docker push LOCATION-docker.pkg.dev/$PROJECT/$REPO/aegis:${{ github.sha }}
      - name: Deploy to Agent Engine / Cloud Run
        run: |
          # Example Cloud Run deploy (replace with Agent Engine CLI if available)
          gcloud run deploy aegis --image LOCATION-docker.pkg.dev/$PROJECT/$REPO/aegis:${{ github.sha }} --region us-central1 --platform managed


Notes: Store GCP_SA_KEY in GitHub Secrets. Use short-lived credentials or Workload Identity where possible.

8) Observability & health checks

Health endpoint: implement /health returning status of:

app process

connection to Memory DB

connection to Redis (sessions)

Tracing: instrument agents and orchestrator with OpenTelemetry. Export traces to your cloud tracing backend.

Logging: structured JSON logs (include trace_id, span_id, agent, tool).

Metrics: expose Prometheus metrics (or cloud equivalent) for:

requests/sec

P50/P95 latency

tokens-per-run (if you call LLM)

judge-score distribution

tool call success rate

Dashboards & Alerts: create alerts for:

high latency

token / cost spikes

judge score drop below threshold

9) Production best practices & cost controls

Token & model budget: implement per-request token caps and budget guardrails in orchestrator.

Caching: cache RAG results, tool outputs, and expensive computations.

Circuit breakers: for external tools/LLM failures degrade gracefully.

Autoscaling limits: set maxReplicas to control cost.

Audit & governance: log tool calls, agent identities, memory changes for audits.

Reviewer approvals: block high-risk tool calls (payments, DB deletes) behind an approval flow.

10) Troubleshooting checklist

Deployment not starting:

Check container logs for errors.

Validate health probe path matches your app.

Secrets not available:

Confirm service account has secretmanager.secretAccessor.

Check secret names / versions.

DB connection failing:

Confirm VPC / network access (if Cloud SQL/GKE).

Check credentials in Secret Manager.

Reasoning/memory behavior differs from local:

Compare environment variables and model versions.

Ensure same config for RAG vector DB.

Appendix: Helpful commands (summary)
# Build & push (example)
docker build -t LOCATION-docker.pkg.dev/PROJECT/REPO/aegis:latest .
gcloud auth configure-docker LOCATION-docker.pkg.dev
docker push LOCATION-docker.pkg.dev/PROJECT/REPO/aegis:latest

# Create service account
gcloud iam service-accounts create aegis-runtime --display-name "Aegis runtime"

# Grant roles
gcloud projects add-iam-policy-binding PROJECT \
  --member="serviceAccount:aegis-runtime@PROJECT.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Cloud Run deploy (fallback)
gcloud run deploy aegis \
  --image LOCATION-docker.pkg.dev/PROJECT/REPO/aegis:latest \
  --region us-central1 \
  --platform managed \
  --service-account aegis-runtime@PROJECT.iam.gserviceaccount.com
