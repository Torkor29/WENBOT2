# Script PowerShell pour lancer Trading Analyzer
Set-Location $PSScriptRoot

Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "   Trading Analyzer - Lancement Local" -ForegroundColor Cyan  
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Lancement de l'application..." -ForegroundColor Green
Write-Host "🌐 Accessible sur: http://localhost:5000" -ForegroundColor Yellow
Write-Host ""
Write-Host "⏹️  Pour arrêter: Ctrl+C" -ForegroundColor Red
Write-Host ""

# Définir les variables d'environnement
$env:FLASK_ENV = "development"
$env:FLASK_DEBUG = "1"

# Lancer l'application
python app.py

# Pause à la fin
Write-Host ""
Write-Host "Appuyez sur une touche pour fermer..." -ForegroundColor Gray
Read-Host 