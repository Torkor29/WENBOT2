@echo off
echo ====================================
echo    DEMARRAGE DU TRADING ANALYZER
echo ====================================

REM Création des dossiers nécessaires
mkdir api 2>nul
mkdir api\uploads 2>nul
mkdir api\reports 2>nul

REM Vérification de Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installe.
    echo Veuillez installer Python depuis https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Installation des dépendances si nécessaire
echo Installation des dependances...
pip install -r api\requirements.txt

REM Lancement de l'API en arrière-plan
start /B python api\analyzer_api.py

REM Attendre que l'API démarre
timeout /t 3 /nobreak

REM Ouvrir la page web dans le navigateur par défaut
echo Ouverture de l'interface...
start http://localhost:5000/Analyzer_1.html

echo ====================================
echo    SYSTEME DEMARRE AVEC SUCCES
echo ====================================
echo.
echo Pour arreter le systeme, fermez cette fenetre.
echo.
pause 