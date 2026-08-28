import subprocess
import time
import sys
import os

env = os.environ.copy()

# Start FastAPI backend on port 8000
backend = subprocess.Popen([sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"], env=env)

time.sleep(2)

# Start Streamlit frontend on port 8080
frontend = subprocess.Popen([
    sys.executable, "-m", "streamlit", "run", "frontend/app.py",
    "--server.port=8080",
    "--server.address=0.0.0.0",
    "--server.enableCORS=false",
    "--server.enableXsrfProtection=false"
], env=env)

backend.wait()
frontend.wait()
