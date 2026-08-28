import streamlit as st
import requests, json

st.set_page_config(
    page_title="DevOpsAgent AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# High-End Gemini-Inspired Dark Theme Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, .stApp {
        background-color: #131314 !important;
        color: #E3E3E3 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Minimal Gemini Top Bar */
    .top-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.5rem 0;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid #282A2C;
    }
    .top-nav .title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #E3E3E3;
    }
    .top-nav .badge {
        background-color: #1E1F20;
        color: #A8C7FA;
        font-size: 0.75rem;
        padding: 4px 10px;
        border-radius: 12px;
        border: 1px solid #282A2C;
    }

    /* Execution Audit Cards */
    .audit-card {
        background-color: #1E1F20;
        border: 1px solid #282A2C;
        border-left: 4px solid #A8C7FA;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
        font-family: monospace;
        font-size: 0.85rem;
    }
    .audit-title {
        color: #A8C7FA;
        font-weight: 600;
        font-size: 0.8rem;
        text-transform: uppercase;
        margin-bottom: 0.25rem;
    }
    .audit-val { color: #E3E3E3; }
    .audit-success { color: #81C995; }

    /* Streamlit Chat Customization */
    .stChatMessage { background-color: transparent !important; }
    div[data-testid="stSidebarNav"] { display: none; }
</style>
""", unsafe_allow_html=True)

# Top Bar
st.markdown("""
<div class="top-nav">
    <div class="title">✨ DevOpsAgent AI</div>
    <div class="badge">Decoupled Taskmaster • Gemini 3.6 Flash</div>
</div>
""", unsafe_allow_html=True)

# Session State for Continuous Chat Memory
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your autonomous SRE DevOps Agent. Upload a log/screenshot or paste an incident trace to trigger self-healing automated workflows."}
    ]

# Render Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# File Upload Attachment (Gemini-style attachment block)
with st.expander("📎 Attach Diagnostic Log or Screenshot", expanded=False):
    uploaded_file = st.file_uploader("Upload File (Max 10MB)", type=["png", "jpg", "txt", "log"])
    
file_payload_text = ""
if uploaded_file:
    if uploaded_file.size > 10 * 1024 * 1024:
        st.error("File exceeds 10MB limit. Please upload a smaller log excerpt.")
    elif uploaded_file.type in ["text/plain", "application/octet-stream"] or uploaded_file.name.endswith(".log"):
        file_payload_text = uploaded_file.getvalue().decode("utf-8", errors="ignore")[:4000]
        st.success(f"Attached log file: `{uploaded_file.name}` ({len(file_payload_text)} chars extracted)")

# Chat Input Box
user_prompt = st.chat_input("Ask DevOpsAgent to diagnose or resolve an infrastructure issue...")

if user_prompt:
    # Combine prompt with uploaded text if present
    full_input = f"{user_prompt}\n\n[Attached File Content]:\n{file_payload_text}" if file_payload_text else user_prompt
    
    # Render User Message
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Trigger Assistant Response via FastAPI
    with st.chat_message("assistant"):
        with st.spinner("Analyzing telemetry & executing remediation loop..."):
            try:
                res = requests.post(
                    "http://127.0.0.1:8000/api/v1/remediate",
                    json={"telemetry_text": full_input},
                    timeout=120
                )
                
                if res.status_code == 200:
                    data = res.json()
                    response_html = ""

                    # Render Tool Call Execution Cards
                    if data.get("tool_calls"):
                        for call in data["tool_calls"]:
                            response_html += f"""
                            <div class="audit-card">
                                <div class="audit-title">⚡ Autonomous Action Executed</div>
                                <div>Tool: <span class="audit-val">{call['name']}</span></div>
                                <div>Parameters: <span class="audit-val">{json.dumps(call['args'])}</span></div>
                                <div class="audit-success">Result: {json.dumps(call['result'])}</div>
                            </div>
                            """

                    diagnosis_text = data.get("diagnosis", "Automated remediation executed successfully.")
                    response_html += f"<div>{diagnosis_text}</div>"

                    st.markdown(response_html, unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": response_html})
                else:
                    err_msg = f"Backend API Error [{res.status_code}]: {res.text}"
                    st.error(err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg})

            except Exception as e:
                err_msg = f"Communication Failure: {str(e)}"
                st.error(err_msg)
                st.session_state.messages.append({"role": "assistant", "content": err_msg})
