from flask import Flask, request, jsonify, send_file, render_template
from analyzer import TradingAnalyzer
import os

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
REPORTS_FOLDER = os.path.join(os.path.dirname(__file__), 'reports')

# Initialisation de l'analyseur
analyzer = TradingAnalyzer(UPLOAD_FOLDER, REPORTS_FOLDER)

@app.route('/')
def index():
    """Sert la page d'exemple directement"""
    return app.send_static_file('example.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Endpoint pour analyser les fichiers"""
    if 'files' not in request.files:
        return jsonify({'error': 'Aucun fichier envoyé'}), 400
    
    files = request.files.getlist('files')
    analysis_type = request.form.get('analysis_type', 'forex')
    
    return analyzer.process_files(files, analysis_type)

@app.route('/api/status/<task_id>')
def get_status(task_id):
    """Endpoint pour vérifier le statut d'une analyse"""
    return analyzer.get_task_status(task_id)

@app.route('/api/report/<task_id>')
def get_report(task_id):
    """Endpoint pour télécharger le rapport"""
    return analyzer.get_report_file(task_id)

@app.route('/api/cleanup', methods=['POST'])
def cleanup():
    """Endpoint pour nettoyer les anciens fichiers"""
    return analyzer.cleanup_old_tasks(hours=24)

if __name__ == '__main__':
    # Créer les dossiers nécessaires
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(REPORTS_FOLDER, exist_ok=True)
    
    # Lancer l'API en mode développement
    app.run(host='0.0.0.0', port=5000, debug=True) 