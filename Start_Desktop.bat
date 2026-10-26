@echo off
rem Porneste varianta desktop (matplotlib) a simulatorului PID.
cd /d "%~dp0"
python -c "import matplotlib" >nul 2>nul
if errorlevel 1 python -m pip install matplotlib
python PIDClass.py
if errorlevel 1 pause
