"""
Busyness Buster Launcher
Double-click to start - no command windows shown.
"""

import subprocess
import sys
import os
import urllib.request

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Start backend as hidden subprocess
backend = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    creationflags=subprocess.CREATE_NO_WINDOW
)

# Poll until backend is ready (faster than fixed sleep)
for _ in range(20):  # Max ~2 seconds
    try:
        urllib.request.urlopen("http://localhost:8000/docs", timeout=0.1)
        break
    except:
        pass

# Run frontend (blocks until GUI closes)
try:
    subprocess.run([sys.executable, "app.py"])
finally:
    backend.terminate()
    backend.wait()
