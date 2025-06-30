@echo off
cd /d "%~dp0"
echo.
echo ==========================================
echo   Trading Analyzer - Lancement Local
echo ==========================================
echo.
echo Lancement de l'application...
echo Accessible sur: http://localhost:5000
echo.
echo Pour arreter: Ctrl+C
echo.
set FLASK_ENV=development
set FLASK_DEBUG=1
python app.py
pause 