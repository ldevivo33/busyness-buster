@echo off
REM === Busyness Buster Startup ===

REM Get script directory (allows running from anywhere)
set "PROJECT_DIR=%~dp0"
set "CONDA_ROOT=%USERPROFILE%\miniconda3"
set "ENV_NAME=bb_env"

REM Add conda to PATH
set "PATH=%CONDA_ROOT%;%CONDA_ROOT%\Scripts;%CONDA_ROOT%\Library\bin;%PATH%"

echo Starting Busyness Buster...

REM Start backend (minimized)
start /min "BB-Backend" cmd /k "cd /d %PROJECT_DIR% && conda run -n %ENV_NAME% uvicorn main:app --reload"

REM Wait for backend to initialize
timeout /t 3 >nul

REM Start frontend
start "BB-Frontend" cmd /k "cd /d %PROJECT_DIR% && conda run -n %ENV_NAME% python app.py"

echo Backend and Frontend started.
