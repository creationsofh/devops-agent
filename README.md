# DevOpsAgent AI // Autonomous SRE & Infrastructure Engine

> *Decoupled SRE taskmaster powered by FastAPI, Streamlit, and Google Gemini API.*

DevOpsAgent AI is an autonomous site reliability engineering tool designed to diagnose system telemetry, patch local codebase errors, manage Google Cloud Run microservices, and provision IAM permissions automatically.

---

### *Architecture Overview*

```text
┌─────────────────────────┐        HTTP / JSON         ┌──────────────────────────────┐
│  Streamlit Frontend     ├───────────────────────────►│  FastAPI Orchestrator        │
│  (Gemini-Themed Chat)   │◄───────────────────────────┤  (Backend Engine)            │
└─────────────────────────┘      Remediation Payload   └──────────────┬───────────────┘
                                                                      │
                                                        Tool Invocation / Tool Calls
                                                                      ▼
                                                       ┌──────────────────────────────┐
                                                       │ Autonomous Tool Registry     │
                                                       ├──────────────────────────────┤
                                                       │ • update_model_config        │
                                                       │ • restart_cloud_run_service  │
                                                       │ • grant_temporary_iam_role   │
                                                       └──────────────────────────────┘

```

---

### *Key Features*

* *Gemini-Inspired Chat UI:* Built with Streamlit, featuring multi-turn conversation memory, execution audit cards, and diagnostic file attachment support.
* *Autonomous Tool Execution:* Directly executes infrastructure actions instead of returning plain text advice when actionable telemetry is provided.
* *Resilient Model Fallbacks:* Built-in rate-limit handling (429 exponential backoffs) and dynamic fallback routing across active Gemini 3.x Flash endpoints.
* *Decoupled Microservice Architecture:* Clean separation of concerns with FastAPI managing backend agent logic and Streamlit handling UI rendering.

---

### *Repository Structure*

```text
devops-agent/
├── backend/
│   ├── __init__.py
│   ├── main.py        # FastAPI orchestrator & Gemini API agent
│   └── tools.py       # Autonomous execution tools (Code patch, Cloud Run, IAM)
├── frontend/
│   └── app.py         # Streamlit chat interface
├── Dockerfile         # Multi-process Cloud Run container definition
├── main_runner.py     # Process manager starting FastAPI (8000) & Streamlit (8080)
└── requirements.txt   # Dependencies

```

---

### *Local Setup & Execution*

*1. Clone the repository:*

```bash
git clone https://github.com/creationsofh/devops-agent.git
cd devops-agent

```

*2. Set up virtual environment & install dependencies:*

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```

*3. Configure environment variables:*

```bash
export GEMINI_API_KEY="AQ.Ab8RN6KHV3wQdOPxcnRihApLRq4khzLmOjXFxdNGbxjos4--Aw"

```

*4. Run locally:*

```bash
python3 main_runner.py

```

Access the application at `http://localhost:8080`.

---

### *Deployment to Google Cloud Run*

Deploy to Cloud Run using Google Cloud Build:

```bash
gcloud config set project project-d1771649-7eea-41e2-939
export GEMINI_API_KEY="AQ.Ab8RN6KHV3wQdOPxcnRihApLRq4khzLmOjXFxdNGbxjos4--Aw"

# Build container image
gcloud builds submit --tag gcr.io/project-d1771649-7eea-41e2-939/devops-agent:v27

# Deploy to Cloud Run
gcloud run deploy devops-agent-service \
    --image gcr.io/project-d1771649-7eea-41e2-939/devops-agent:v27 \
    --set-env-vars GEMINI_API_KEY="$GEMINI_API_KEY" \
    --platform managed \
    --region us-central1 \
    --project project-d1771649-7eea-41e2-939 \
    --allow-unauthenticated

```
