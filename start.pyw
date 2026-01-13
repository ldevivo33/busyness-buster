"""
Busyness Buster Launcher
Double-click to start - no command windows shown.
Uses .pyw extension to hide Python console on Windows.
"""

import subprocess
import sys
import time
import os

# Get the directory where this script lives
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Start backend as hidden subprocess
backend = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    creationflags=subprocess.CREATE_NO_WINDOW
)

# Give backend time to start
time.sleep(2)

# Run frontend (this blocks until GUI closes)
try:
    subprocess.run([sys.executable, "app.py"])
finally:
    # Kill backend when frontend closes
    backend.terminate()
    backend.wait()
