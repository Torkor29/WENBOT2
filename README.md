# WenBot Trading Platform

Une plateforme de trading avancée combinant une interface web moderne et des analyseurs de trading professionnels.

## 🚀 Architecture du Projet

Le projet est divisé en deux parties principales :
1. Interface Web (HTML/CSS/JS)
2. Backend Trading Analyzer (Python)

## 📦 Structure des Dossiers

```
WENBOT/
├── Interface Web
│   ├── css/
│   ├── js/
│   ├── images/
│   ├── components/
│   └── templates/
├── Trading Analyzer
│   ├── Integration/
│   │   ├── analyzer.py
│   │   ├── api.py
│   │   └── modules/
│   └── reports/
```

## 🔧 Configuration WordPress

### Prérequis
- WordPress 6.0+
- PHP 8.0+
- MySQL 5.7+
- Extension Python pour PHP
- Modules Python requis (voir requirements.txt)

### Installation sur WordPress

1. **Préparation du Serveur**
   ```bash
   # Installer les dépendances Python
   pip install -r requirements.txt
   
   # Configurer les permissions
   chmod +x Integration/analyzer.py
   chmod +x Integration/api.py
   ```

2. **Configuration WordPress**
   - Installer et activer le thème personnalisé WenBot
   - Configurer les permaliens (Settings > Permalinks) sur "Post name"
   - Activer le plugin "WP REST API" si non inclus

3. **Intégration des Fichiers**
   - Copier le contenu du dossier `WENBOT` dans le répertoire de votre thème :
     ```bash
     cp -r WENBOT/* /var/www/html/wp-content/themes/wenbot/
     ```
   - Adapter les chemins dans `wp-config.php` :
     ```php
     define('WENBOT_PATH', dirname(__FILE__) . '/wp-content/themes/wenbot');
     define('PYTHON_PATH', '/usr/bin/python3');
     ```

4. **Configuration de l'API**
   - Créer un fichier `.env` dans le dossier racine :
     ```
     DB_HOST=localhost
     DB_USER=your_db_user
     DB_PASS=your_db_password
     DB_NAME=your_db_name
     API_KEY=your_trading_api_key
     ```

5. **Sécurité**
   - Configurer le pare-feu pour les ports nécessaires
   - Mettre en place HTTPS
   - Sécuriser les fichiers sensibles :
     ```bash
     chmod 600 .env
     chmod 644 *.html
     chmod 755 Integration/*.py
     ```

### Configuration Apache

Ajouter dans le fichier `.htaccess` :
```apache
# Redirection HTTPS
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Protection des fichiers sensibles
<FilesMatch "^\.env">
    Order allow,deny
    Deny from all
</FilesMatch>

# Configuration Python
AddHandler cgi-script .py
Options +ExecCGI

# Cache et Compression
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType image/jpg "access plus 1 year"
    ExpiresByType image/jpeg "access plus 1 year"
    ExpiresByType image/webp "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"
</IfModule>
```

### Intégration des Pages

1. **Pages Principales**
   - Créer les pages dans WordPress
   - Utiliser les modèles de page personnalisés :
     - `template-analyzer.php` pour Analyzer
     - `template-pricing.php` pour Pricing
     - etc.

2. **Menu et Navigation**
   - Configurer le menu principal dans WordPress
   - Adapter les liens dans la navbar

3. **Widgets et Sidebars**
   - Configurer les widgets nécessaires
   - Intégrer les formulaires de contact

## 📈 Trading Analyzer

### Configuration de l'Analyseur
1. Configurer les paramètres dans `config.py`
2. Tester l'API avec `test_api.py`
3. Vérifier les logs dans `logs/analyzer.log`

### Cron Jobs
Ajouter au crontab :
```bash
# Mise à jour des analyses toutes les heures
0 * * * * /usr/bin/python3 /var/www/html/wp-content/themes/wenbot/Integration/analyzer.py

# Nettoyage des rapports anciens
0 0 * * * find /var/www/html/wp-content/themes/wenbot/reports/* -mtime +30 -exec rm {} \;
```

## 🔒 Sécurité et Performance

1. **Sécurité**
   - Installer et configurer WordFence
   - Activer la double authentification
   - Limiter les tentatives de connexion

2. **Performance**
   - Installer WP Super Cache
   - Configurer un CDN
   - Optimiser les images avec WebP

3. **Maintenance**
   - Sauvegardes automatiques
   - Mises à jour régulières
   - Monitoring des performances

## 🛠️ Dépannage

1. **Problèmes Courants**
   - Vérifier les logs PHP et Python
   - Tester les permissions des fichiers
   - Vérifier la configuration de l'API

2. **Support**
   - Documentation technique : `/docs`
   - Logs : `/logs`
   - Contact support : support@wenbot.com

## 📝 License

MIT License - voir LICENSE.md pour plus de détails 