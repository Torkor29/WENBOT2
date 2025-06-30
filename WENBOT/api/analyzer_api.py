from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import sys
import json
from datetime import datetime
import uuid
from werkzeug.utils import secure_filename

# Ajouter le chemin du trading-analyzer-main au PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), '../../trading-analyzer-main'))

# Import des modules d'analyse
from Integration.analyzer import TradingAnalyzer
from modules.forex_analyzer import ForexAnalyzer
from modules.autres_analyzer import AutresAnalyzer

app = Flask(__name__, static_folder='../')
CORS(app)  # Activer CORS pour permettre les requêtes depuis le frontend

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
REPORTS_FOLDER = os.path.join(os.path.dirname(__file__), 'reports')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)

# Initialiser l'analyseur
analyzer = TradingAnalyzer(UPLOAD_FOLDER, REPORTS_FOLDER)

# Routes pour servir les fichiers statiques
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/analyze', methods=['POST'])
def analyze_files():
    """Point d'entrée pour l'analyse des fichiers"""
    try:
        if 'files[]' not in request.files:
            return jsonify({'error': 'Aucun fichier trouvé'}), 400
        
        files = request.files.getlist('files[]')
        analysis_type = request.form.get('type', 'forex')  # 'forex' par défaut
        
        result, status_code = analyzer.process_files(files, analysis_type)
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<task_id>', methods=['GET'])
def get_status(task_id):
    """Récupère le statut d'une tâche d'analyse"""
    try:
        status, status_code = analyzer.get_task_status(task_id)
        return jsonify(status), status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/report/<task_id>', methods=['GET'])
def get_report(task_id):
    """Télécharge le rapport d'analyse"""
    try:
        return analyzer.get_report_file(task_id)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=== TRADING ANALYZER API ===")
    print("Serveur démarré sur http://localhost:5000")
    print("Pour accéder à l'interface, ouvrez http://localhost:5000/Analyzer_1.html")
    print("===============================")
    app.run(port=5000, debug=True) 