#!/usr/bin/env python3
"""
Script de préparation pour le déploiement
Analyseur Trading Pro
"""

import os
import sys
import subprocess
import secrets

def generate_secret_key():
    """Génère une clé secrète sécurisée"""
    return secrets.token_urlsafe(32)

def check_files():
    """Vérifie que tous les fichiers nécessaires sont présents"""
    required_files = [
        'app.py',
        'config.py',
        'requirements.txt',
        'Procfile',
        'runtime.txt',
        '.gitignore'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Fichiers manquants: {', '.join(missing_files)}")
        return False
    
    print("✅ Tous les fichiers requis sont présents")
    return True

def check_directories():
    """Vérifie et crée les dossiers nécessaires"""
    required_dirs = [
        'static/uploads',
        'reports',
        'modules',
        'templates',
        'static/css',
        'static/js'
    ]
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            print(f"📁 Dossier créé: {dir_path}")
        else:
            print(f"✅ Dossier existant: {dir_path}")

def create_env_example():
    """Crée un fichier .env.example avec les variables nécessaires"""
    env_content = f"""# Variables d'environnement pour l'Analyseur Trading Pro
# Copiez ce fichier en .env et remplissez les valeurs

# Environnement (development, production, testing)
FLASK_ENV=production

# Clé secrète (générez une nouvelle clé pour la production)
SECRET_KEY={generate_secret_key()}

# Port de l'application (automatique sur la plupart des hébergeurs)
PORT=5000

# Dossiers de l'application
UPLOAD_FOLDER=static/uploads
REPORTS_FOLDER=reports

# Taille maximale des fichiers (en bytes)
MAX_CONTENT_LENGTH=16777216

# Logs (pour la production)
LOG_LEVEL=INFO
"""
    
    with open('.env.example', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Fichier .env.example créé")
    print("🔑 Nouvelle clé secrète générée")

def test_import():
    """Teste si toutes les dépendances peuvent être importées"""
    try:
        import flask
        import pandas
        import openpyxl
        print("✅ Toutes les dépendances sont installées")
        return True
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("💡 Exécutez: pip install -r requirements.txt")
        return False

def run_tests():
    """Exécute des tests basiques de l'application"""
    try:
        from app import create_app
        
        # Test de création de l'app
        app = create_app('testing')
        
        with app.test_client() as client:
            # Test de la page d'accueil
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Page d'accueil accessible")
            else:
                print(f"❌ Erreur page d'accueil: {response.status_code}")
                return False
            
            # Test du health check
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ Health check fonctionnel")
            else:
                print(f"❌ Erreur health check: {response.status_code}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        return False

def show_deployment_instructions():
    """Affiche les instructions de déploiement"""
    print("\n" + "="*60)
    print("🚀 INSTRUCTIONS DE DÉPLOIEMENT")
    print("="*60)
    
    print("\n📋 ÉTAPES SUIVANTES:")
    print("1. Créez un repository Git:")
    print("   git init")
    print("   git add .")
    print("   git commit -m 'Initial commit - Trading Analyzer'")
    
    print("\n2. Poussez sur GitHub:")
    print("   - Créez un nouveau repository sur GitHub")
    print("   - Suivez les instructions pour pousser votre code")
    
    print("\n3. Déployez sur Render.com (RECOMMANDÉ):")
    print("   - Allez sur https://render.com")
    print("   - Connectez votre GitHub")
    print("   - Créez un nouveau Web Service")
    print("   - Build Command: pip install -r requirements.txt")
    print("   - Start Command: gunicorn app:app")
    
    print("\n4. Configurez les variables d'environnement:")
    print("   FLASK_ENV=production")
    print(f"   SECRET_KEY={generate_secret_key()}")
    
    print("\n💡 ALTERNATIVES:")
    print("   - Railway.app: npm install -g @railway/cli && railway deploy")
    print("   - PythonAnywhere: Upload files + configure WSGI")
    print("   - DigitalOcean App Platform: Connect Git repository")
    
    print("\n🔗 LIENS UTILES:")
    print("   - Guide complet: deployment_guide.md")
    print("   - Support Render: https://render.com/docs")
    print("   - Support Railway: https://docs.railway.app")

def main():
    """Fonction principale"""
    print("🔧 PRÉPARATION AU DÉPLOIEMENT - Analyseur Trading Pro")
    print("="*60)
    
    # Vérifications
    if not check_files():
        sys.exit(1)
    
    check_directories()
    create_env_example()
    
    if not test_import():
        print("\n❌ Installez d'abord les dépendances:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    if not run_tests():
        print("\n❌ Les tests ont échoué. Vérifiez votre code.")
        sys.exit(1)
    
    print("\n✅ PRÉPARATION TERMINÉE AVEC SUCCÈS!")
    show_deployment_instructions()

if __name__ == "__main__":
    main() 