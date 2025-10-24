@echo off
REM === Define where Miniconda lives ===
set "CONDA_ROOT=C:\Users\luked\miniconda3"

REM === Add conda to PATH for new windows ===
set "PATH=%CONDA_ROOT%;%CONDA_ROOT%\Scripts;%CONDA_ROOT%\Library\bin;%PATH%"

REM === Start backend ===
start "Backend" cmd /k "cd /d C:\Users\luked\Documents\Projects\busyness-buster && conda run -n bb_env uvicorn main:app --reload"

REM === short pause to avoid temp-file collision ===
timeout /t 3 >nul

REM === Start frontend (Tkinter GUI) ===
start "Frontend" cmd /k "cd /d C:\Users\luked\Documents\Projects\busyness-buster && conda run -n bb_env python app.py"

