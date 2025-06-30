# 🚀 GUIDE DE LANCEMENT SIMPLE

## ✅ MÉTHODES DE LANCEMENT

### Option 1: Fichier batch (le plus simple sur Windows)
```
Double-clic sur START.bat
```

### Option 2: Script Python
```bash
python run.py
```

### Option 3: Application directe
```bash
python app.py
```

### Option 4: PowerShell (étape par étape)
```powershell
# 1. Ouvrir PowerShell dans le dossier WEB APP
cd "C:\OUTIL\FICHIERS\WEB APP"

# 2. Lancer l'application
python run.py
```

## 🌐 ACCÈS À L'APPLICATION

Une fois lancée, l'application est accessible sur:
- **Local**: http://localhost:5000
- **Réseau local**: http://192.168.x.x:5000

## 🔧 DÉPANNAGE

### Problème: Python non trouvé
```bash
# Vérifier que Python est installé
python --version
```

### Problème: Module non trouvé
```bash
# Installer les dépendances
pip install -r requirements.txt
```

### Problème: Port déjà utilisé
- Fermer l'ancienne instance avec Ctrl+C
- Ou utiliser taskkill /f /im python.exe

## 📧 TEST DU FORMULAIRE DE CONTACT

Le formulaire de contact fonctionne en mode debug local:
- Remplir tous les champs obligatoires
- En mode debug, l'email est simulé (pas vraiment envoyé)
- Les logs apparaissent dans la console

## 🎯 POUR LA PRODUCTION

Pour déployer en production, voir le fichier DEPLOY_NOW.md 