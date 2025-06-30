# Trading Analyzer - Module d'Intégration Web

Ce module permet d'intégrer les fonctionnalités d'analyse de trading dans n'importe quel site web via une API REST.

## Structure des fichiers

```
Integration/
├── api.py              # API REST Flask
├── analyzer.py         # Classe principale d'analyse
├── modules/            # Modules d'analyse
│   ├── forex_analyzer.py
│   └── autres_analyzer.py
├── example.html        # Exemple d'intégration frontend
└── requirements.txt    # Dépendances Python
```

## Installation

1. Copiez le dossier `Integration` sur votre serveur
2. Installez les dépendances :
```bash
pip install -r Integration/requirements.txt
```

## Configuration du serveur

1. Lancez l'API :
```bash
python api.py
```

2. Configurez votre serveur web (nginx, Apache) pour rediriger les requêtes `/api/*` vers l'API Flask.

Exemple de configuration nginx :
```nginx
location /api/ {
    proxy_pass http://localhost:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## Intégration dans votre site web

### 1. Endpoints API

- `POST /api/analyze` : Envoyer des fichiers pour analyse
  - Paramètres : 
    - `files` : Liste des fichiers Excel (multipart/form-data)
    - `analysis_type` : 'forex' ou 'autres'
  - Retourne : `{ task_id: "..." }`

- `GET /api/status/<task_id>` : Vérifier le statut d'une analyse
  - Retourne : `{ status: "...", progress: N, message: "...", results: {...} }`

- `GET /api/report/<task_id>` : Télécharger le rapport Excel
  - Retourne : Le fichier Excel

- `POST /api/cleanup` : Nettoyer les anciens fichiers
  - Retourne : `{ message: "...", cleaned_files: N, cleaned_tasks: N }`

### 2. Exemple d'intégration HTML/JavaScript

Voir le fichier `example.html` pour un exemple complet d'intégration frontend avec :
- Upload de fichiers
- Barre de progression
- Affichage des résultats
- Téléchargement du rapport

Pour utiliser l'exemple :
1. Copiez le contenu de `example.html` dans votre site
2. Modifiez la variable `API_BASE_URL` pour pointer vers votre API
3. Personnalisez le style CSS selon vos besoins

### 3. Exemple d'utilisation avec fetch

```javascript
// Envoyer des fichiers pour analyse
const formData = new FormData();
formData.append('files', fichierExcel);
formData.append('analysis_type', 'forex');

const response = await fetch('/api/analyze', {
    method: 'POST',
    body: formData
});
const { task_id } = await response.json();

// Vérifier le statut
const statusResponse = await fetch(`/api/status/${task_id}`);
const status = await statusResponse.json();

// Télécharger le rapport
if (status.status === 'completed') {
    window.location.href = `/api/report/${task_id}`;
}
```

## Sécurité

L'API inclut :
- Validation des types de fichiers
- Vérification MIME
- Limite de taille de fichier (10MB par défaut)
- Noms de fichiers sécurisés
- Nettoyage automatique des fichiers temporaires

## Notes importantes

1. Les fichiers uploadés sont automatiquement nettoyés après le traitement
2. Les rapports générés sont conservés pendant 24h
3. Utilisez un CRON pour appeler `/api/cleanup` régulièrement
4. L'API supporte les fichiers Excel (.xlsx, .xls)
5. Le traitement est asynchrone avec un système de tâches

## Support

Pour toute question ou problème, veuillez créer une issue sur le dépôt GitHub. 