#!/usr/bin/env python3
"""
Script de lancement pour Trading Analyzer
Ce script configure l'environnement et démarre l'application Flask
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Configure l'environnement avant de lancer l'application"""
    # S'assurer qu'on est dans le bon répertoire
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Ajouter le répertoire au Python path
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))
    
    # Variables d'environnement par défaut
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('FLASK_DEBUG', '1')
    
    print("🚀 Lancement de l'application Trading Analyzer...")
    print(f"📂 Répertoire de travail: {script_dir}")
    print("🌐 L'application sera accessible sur: http://localhost:5000")
    print("⏹️  Pour arrêter l'application, appuyez sur Ctrl+C")
    print("-" * 60)

def main():
    """Point d'entrée principal"""
    setup_environment()
    
    try:
        # Importer et lancer l'application
        from app import app
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False  # Éviter les problèmes de redémarrage
        )
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("Vérifiez que tous les modules sont installés:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 