# Guide de Déploiement - Trading Analyzer

Ce guide explique comment déployer le Trading Analyzer en ligne, soit sur Render.com (pour une solution complète), soit sur WordPress (pour l'interface uniquement).

## Table des matières
1. [Déploiement sur Render](#déploiement-sur-render)
2. [Intégration avec WordPress](#intégration-avec-wordpress)
3. [Configuration des variables d'environnement](#configuration-des-variables-denvironnement)
4. [Sécurité et bonnes pratiques](#sécurité-et-bonnes-pratiques)

## Déploiement sur Render

### Prérequis
- Un compte [Render.com](https://render.com)
- Un compte GitHub
- Python 3.8+ installé localement

### Étapes de déploiement

1. **Préparation du code**
   ```bash
   # Créer un nouveau repository Git
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <votre-repo-url>
   git push -u origin main
   ```

2. **Configuration sur Render**
   - Connectez-vous à [Render.com](https://render.com)
   - Cliquez sur "New Web Service"
   - Sélectionnez votre repository GitHub
   - Configurez le service :
     ```
     Name: trading-analyzer
     Environment: Python 3
     Build Command: pip install -r api/requirements.txt
     Start Command: python api/analyzer_api.py
     ```

3. **Configuration des variables d'environnement sur Render**
   ```
   PYTHON_VERSION=3.8.12
   FLASK_ENV=production
   PORT=10000
   ```

4. **Modification du code pour la production**
   
   Dans `analyzer_api.py`, ajoutez :
   ```python
   import os
   
   port = int(os.environ.get('PORT', 5000))
   
   if __name__ == '__main__':
       app.run(host='0.0.0.0', port=port)
   ```

## Intégration avec WordPress

### Méthode 1 : Plugin personnalisé

1. **Créer la structure du plugin**
   ```
   trading-analyzer/
   ├── trading-analyzer.php
   ├── includes/
   ├── assets/
   │   ├── css/
   │   └── js/
   └── templates/
   ```

2. **Fichier principal du plugin (trading-analyzer.php)**
   ```php
   <?php
   /*
   Plugin Name: Trading Analyzer
   Description: Système d'analyse de trading
   Version: 1.0
   Author: Votre Nom
   */
   
   // Empêcher l'accès direct
   if (!defined('ABSPATH')) exit;
   
   // Enregistrer les styles et scripts
   function ta_enqueue_scripts() {
       wp_enqueue_style('ta-styles', plugins_url('assets/css/styles.css', __FILE__));
       wp_enqueue_script('ta-scripts', plugins_url('assets/js/main.js', __FILE__));
   }
   add_action('wp_enqueue_scripts', 'ta_enqueue_scripts');
   
   // Ajouter le shortcode
   function ta_analyzer_shortcode() {
       ob_start();
       include(plugin_dir_path(__FILE__) . 'templates/analyzer.php');
       return ob_get_clean();
   }
   add_shortcode('trading_analyzer', 'ta_analyzer_shortcode');
   ```

3. **Template principal (templates/analyzer.php)**
   ```php
   <div class="trading-analyzer-container">
       <!-- Copier le contenu de Analyzer_1.html ici -->
   </div>
   ```

### Méthode 2 : Pages personnalisées

1. **Créer trois nouvelles pages dans WordPress**
   - Analyzer 1 : Upload et résultats
   - Analyzer 2 : Analyse par paire
   - Analyzer 3 : Analyse avancée

2. **Utiliser un page builder (Elementor, Divi, etc.)**
   - Créer une section personnalisée
   - Ajouter un bloc HTML personnalisé
   - Copier le code HTML/CSS/JS de chaque page

3. **Configuration CORS**
   
   Dans `wp-config.php` :
   ```php
   define('ALLOW_CORS', true);
   ```

## Configuration des variables d'environnement

### Production (Render)
```env
FLASK_ENV=production
DEBUG=False
UPLOAD_FOLDER=/tmp/uploads
REPORTS_FOLDER=/tmp/reports
MAX_CONTENT_LENGTH=16777216
```

### Développement (Local)
```env
FLASK_ENV=development
DEBUG=True
UPLOAD_FOLDER=./uploads
REPORTS_FOLDER=./reports
MAX_CONTENT_LENGTH=16777216
```

## Sécurité et bonnes pratiques

1. **Protection des fichiers**
   ```apache
   # .htaccess
   <FilesMatch "\.(py|json|md)$">
       Order allow,deny
       Deny from all
   </FilesMatch>
   ```

2. **Limitation des uploads**
   ```python
   # analyzer_api.py
   app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
   ```

3. **Validation des fichiers**
   ```python
   ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
   
   def allowed_file(filename):
       return '.' in filename and \
              filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
   ```

4. **Nettoyage automatique**
   ```python
   # Supprimer les fichiers après 24h
   @app.after_request
   def cleanup_old_files(response):
       cleanup_files(hours=24)
       return response
   ```

## Notes importantes

1. **Performance**
   - Utilisez un CDN pour les assets statiques
   - Activez la compression gzip
   - Mettez en cache les résultats d'analyse

2. **Maintenance**
   - Surveillez l'utilisation du disque
   - Mettez en place des sauvegardes
   - Configurez des alertes

3. **Mise à l'échelle**
   - Utilisez Redis pour le cache
   - Configurez un load balancer
   - Utilisez des workers pour l'analyse

## Support

Pour toute question ou assistance :
1. Ouvrez une issue sur GitHub
2. Contactez le support technique
3. Consultez la documentation complète

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails. 