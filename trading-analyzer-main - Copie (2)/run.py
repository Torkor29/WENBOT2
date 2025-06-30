#!/usr/bin/env python3
"""
Script de lancement simple pour l'application Trading Analyzer
Usage: python run.py
"""

import os
from app import app

if __name__ == '__main__':
    print("🚀 Lancement de l'application Trading Analyzer...")
    print("📂 Répertoire de travail:", os.getcwd())
    print("🌐 L'application sera accessible sur: http://localhost:5000")
    print("⏹️  Pour arrêter l'application, appuyez sur Ctrl+C")
    print("-" * 60)
    
    # Configuration pour le développement local
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,  # En mode debug pour les tests locaux
        use_reloader=False  # Désactiver le rechargement automatique pour éviter les problèmes
    ) 