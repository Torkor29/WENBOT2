@echo off
echo ====================================
echo    REDEMARRAGE DU TRADING ANALYZER
echo ====================================

REM Arrêter tous les processus Python en cours
echo Arret des processus Python en cours...
taskkill /F /IM python.exe /T 2>nul
timeout /t 2 /nobreak >nul

REM Nettoyer les fichiers temporaires
echo Nettoyage des fichiers temporaires...
if exist "api\uploads\*" del /Q "api\uploads\*"
if exist "api\reports\*" del /Q "api\reports\*"

REM Recréer les dossiers nécessaires
echo Creation des dossiers necessaires...
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

REM Installation/Mise à jour des dépendances
echo Installation/Mise a jour des dependances...
pip install -r api\requirements.txt

REM Lancement de l'API en arrière-plan
echo Demarrage du serveur...
start /B python api\analyzer_api.py

REM Attendre que l'API démarre
timeout /t 3 /nobreak >nul

REM Ouvrir la page web dans le navigateur par défaut
echo Ouverture de l'interface...
start http://localhost:5000/index.html

echo ====================================
echo    SERVEUR REDEMARRE AVEC SUCCES
echo ====================================
echo.
echo Pour arreter le serveur, fermez cette fenetre.
echo.
pause 