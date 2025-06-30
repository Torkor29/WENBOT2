from flask import Flask, request, jsonify, render_template_string
from analyzer import TradingAnalyzer
import os

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
REPORTS_FOLDER = os.path.join(os.path.dirname(__file__), 'reports')

# Initialisation de l'analyseur
analyzer = TradingAnalyzer(UPLOAD_FOLDER, REPORTS_FOLDER)

# Template HTML minimal
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Analyse Trading</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .progress { margin: 20px 0; }
        #status { margin: 10px 0; }
        #result { margin-top: 20px; }
    </style>
</head>
<body>
    <h1>Analyse Trading</h1>
    
    <form id="uploadForm" enctype="multipart/form-data">
        <input type="file" name="files" multiple accept=".xlsx,.xls" required>
        <select name="analysis_type">
            <option value="forex">Forex</option>
            <option value="autres">Autres</option>
        </select>
        <button type="submit">Analyser</button>
    </form>

    <div class="progress" style="display: none;">
        <p>Progression : <span id="progress">0</span>%</p>
        <p id="status">En attente...</p>
    </div>

    <div id="result"></div>

    <script>
        const uploadForm = document.getElementById('uploadForm');
        const progressDiv = document.querySelector('.progress');
        const progressSpan = document.getElementById('progress');
        const statusP = document.getElementById('status');
        const resultDiv = document.getElementById('result');

        uploadForm.onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData(uploadForm);
            
            try {
                // Envoyer les fichiers
                const response = await fetch('/analyze', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                
                if (data.task_id) {
                    progressDiv.style.display = 'block';
                    pollStatus(data.task_id);
                } else {
                    alert('Erreur: ' + data.error);
                }
            } catch (error) {
                alert('Erreur lors de l\'envoi: ' + error);
            }
        };

        async function pollStatus(taskId) {
            try {
                const response = await fetch(`/status/${taskId}`);
                const data = await response.json();
                
                progressSpan.textContent = data.progress || 0;
                statusP.textContent = data.message || 'En cours...';
                
                if (data.status === 'completed') {
                    resultDiv.innerHTML = `
                        <h3>Analyse terminée !</h3>
                        <p>Télécharger le rapport : 
                            <a href="/download/${taskId}" target="_blank">Rapport Excel</a>
                        </p>
                        <pre>${JSON.stringify(data.results?.data || {}, null, 2)}</pre>
                    `;
                } else if (data.status === 'error') {
                    resultDiv.innerHTML = `<p style="color: red;">Erreur: ${data.error}</p>`;
                } else {
                    setTimeout(() => pollStatus(taskId), 1000);
                }
            } catch (error) {
                statusP.textContent = 'Erreur lors de la vérification du statut';
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze_files():
    if 'files' not in request.files:
        return jsonify({'error': 'Aucun fichier envoyé'}), 400
    
    files = request.files.getlist('files')
    analysis_type = request.form.get('analysis_type', 'forex')
    
    return analyzer.process_files(files, analysis_type)

@app.route('/status/<task_id>')
def get_status(task_id):
    return analyzer.get_task_status(task_id)

@app.route('/download/<task_id>')
def download_report(task_id):
    return analyzer.get_report_file(task_id)

if __name__ == '__main__':
    # Créer les dossiers nécessaires
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(REPORTS_FOLDER, exist_ok=True)
    
    # Lancer l'application
    app.run(debug=True, port=5000) 