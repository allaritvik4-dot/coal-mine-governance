@echo off
title Coal Mine Smart Governance System
setlocal enabledelayedexpansion

set "PYTHONW=C:\Users\EDIFY\AppData\Local\Programs\Python\Python313\pythonw.exe"
set "PYTHON=C:\Users\EDIFY\AppData\Local\Programs\Python\Python313\python.exe"
set "PROJECT_DIR=%~dp0"

cd /d "%PROJECT_DIR%\backend"

:: Start backend silently with pythonw if not already running
netstat -ano | findstr :5000 | findstr LISTENING >nul
if errorlevel 1 (
    start "" "%PYTHONW%" app.py
    ping 127.0.0.1 -n 3 >nul
)

:: Try Chrome first (app mode)
set "CHROME=C:\Program Files\Google\Chrome\Application\chrome.exe"
if exist "%CHROME%" (
    start "" "%CHROME%" --app=http://127.0.0.1:5000 --window-size=1440,900
    exit /b 0
)

:: Try Edge next (app mode)
set "EDGE_1=C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
set "EDGE_2=C:\Program Files\Microsoft\Edge\Application\msedge.exe"

if exist "%EDGE_1%" (
    start "" "%EDGE_1%" --app=http://127.0.0.1:5000 --window-size=1440,900
    exit /b 0
)

if exist "%EDGE_2%" (
    start "" "%EDGE_2%" --app=http://127.0.0.1:5000 --window-size=1440,900
    exit /b 0
)

:: Universal fallback - open default system browser
start http://127.0.0.1:5000
exit /b 0
