# DevOpsAgent AI // Autonomous SRE & Infrastructure Engine (v28)

> **Decoupled SRE taskmaster powered by FastAPI, Streamlit, Google Gemini API, and Google Cloud Infrastructure.**

DevOpsAgent AI is an autonomous site reliability engineering tool built for the **All Things Agentic Hackathon**. It converts raw infrastructure errors, telemetry logs, and stack traces into immediate operational remediation.

---

### **System Architecture**

```text
┌────────────────────────────────┐         HTTP / JSON         ┌────────────────────────────────┐
│  Streamlit Frontend            ├────────────────────────────►│  FastAPI Backend Orchestrator  │
│  (Gemini Dark UI on :8080)     │◄────────────────────────────┤  (Agent Engine on :8000)       │
└────────────────────────────────┘      Audit Card Payload     └───────────────┬────────────────┘
                                                                               │
                                                                 Tool Invocation / Call Map
                                                                               ▼
                                                               ┌────────────────────────────────┐
                                                               │  Dual-Mode Tool Execution Map  │
                                                               ├────────────────────────────────┤
                                                               │ • query_cloud_logging          │
                                                               │ • restart_cloud_run_service    │
                                                               │ • grant_temporary_iam_role     │
                                                               │ • update_model_config          │
                                                               └────────────────────────────────┘
Key Features
Dual Execution Architecture: Connects to live Google Cloud APIs (Cloud Run v2, Stackdriver Logging, gcloud IAM) when GCP billing credits are active, while maintaining seamless fallback to simulated execution if APIs are restricted.

Autonomous Telemetry Triage: Queries real-time Cloud Run error stack traces directly via the google-cloud-logging API.

Codebase Self-Repair: Automatically updates deprecated LLM model strings across backend and frontend files upon detecting 404 API errors.

Decoupled Microservice: Built with FastAPI and Streamlit running as a single containerized process on Google Cloud Run with warm minimum instances (--min-instances 1).

Repository Structure
Plaintext
devops-agent/
├── backend/
│   ├── __init__.py
│   ├── main.py        # FastAPI orchestrator & Gemini API agent
│   └── tools.py       # Dual-Mode execution engine (Cloud Run, Logging, IAM, Code Patch)
├── frontend/
│   └── app.py         # Streamlit chat interface
├── Dockerfile         # Container image definition
├── main_runner.py     # Process manager (FastAPI + Streamlit)
└── requirements.txt   # Dependencies
Local Setup & Execution
Bash
# 1. Clone repository
git clone [https://github.com/creationsofh/devops-agent.git](https://github.com/creationsofh/devops-agent.git)
cd devops-agent

# 2. Setup environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Export variables and run
export GEMINI_API_KEY="your_gemini_api_key"
export GCP_PROJECT="project-d1771649-7eea-41e2-939"
python3 main_runner.py
Access local UI at http://localhost:8080.

Cloud Run Deployment
Bash
gcloud builds submit --tag gcr.io/project-d1771649-7eea-41e2-939/devops-agent:v28

gcloud run deploy devops-agent-service \
    --image gcr.io/project-d1771649-7eea-41e2-939/devops-agent:v28 \
    --set-env-vars GEMINI_API_KEY="$GEMINI_API_KEY",GCP_PROJECT="project-d1771649-7eea-41e2-939" \
    --min-instances 1 \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
