@echo off
setlocal
set "PYTHON_EXE=python"
if not "%RESEARCHKB_ROOT%"=="" (
    if exist "%RESEARCHKB_ROOT%\.venv\Scripts\python.exe" (
        set "PYTHON_EXE=%RESEARCHKB_ROOT%\.venv\Scripts\python.exe"
    )
)
"%PYTHON_EXE%" "%~dp0rk_health.py" %*
