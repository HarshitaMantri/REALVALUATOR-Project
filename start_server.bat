@echo off
echo Starting RealValuator Server...
echo.
cd /d "%~dp0"
cd server
python server.py
pause

