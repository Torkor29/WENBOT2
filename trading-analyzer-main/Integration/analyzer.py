from flask import Flask, request, jsonify, send_file
import os
import json
from datetime import datetime
import uuid
from werkzeug.utils import secure_filename
import threading
import time
import logging
import mimetypes

# Import des modules d'analyse
from modules.forex_analyzer import ForexAnalyzer
from modules.autres_analyzer import AutresAnalyzer

class TradingAnalyzer:
    def __init__(self, upload_folder, reports_folder):
        """Initialisation de l'analyseur de trading"""
        self.UPLOAD_FOLDER = upload_folder
        self.REPORTS_FOLDER = reports_folder
        self.ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
        self.task_status = {}
        
        # Créer les dossiers nécessaires
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(self.REPORTS_FOLDER, exist_ok=True)
    
    def allowed_file(self, filename):
        """Vérifie si le fichier est autorisé"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
    
    def secure_upload_validation(self, file):
        """Validation sécurisée des fichiers uploadés"""
        # Vérification de l'extension
        if not self.allowed_file(file.filename):
            return False, "Extension de fichier non autorisée"
        
        # Vérification du type MIME
        mime_type, _ = mimetypes.guess_type(file.filename)
        allowed_mimes = [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # .xlsx
            'application/vnd.ms-excel'  # .xls
        ]
        
        if mime_type not in allowed_mimes:
            return False, "Type MIME non autorisé"
        
        # Vérification de la taille (max 10MB)
        file.seek(0, 2)
        size = file.tell()
        file.seek(0)
        
        if size > 10 * 1024 * 1024:  # 10MB
            return False, "Fichier trop volumineux"
        
        return True, "OK"
    
    def process_files(self, files, analysis_type='forex'):
        """Traite les fichiers et lance l'analyse"""
        saved_files = []
        
        try:
            # Validation et sauvegarde des fichiers
            for file in files:
                if file and file.filename:
                    # Validation sécurisée
                    is_valid, message = self.secure_upload_validation(file)
                    if not is_valid:
                        return {'error': f'Erreur avec {file.filename}: {message}'}, 400
                    
                    # Sauvegarde sécurisée
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    unique_filename = f"{timestamp}_{filename}"
                    file_path = os.path.join(self.UPLOAD_FOLDER, unique_filename)
                    
                    file.save(file_path)
                    saved_files.append(file_path)
            
            if saved_files:
                # Créer un ID unique pour cette tâche
                task_id = str(uuid.uuid4())
                
                # Lancer le traitement en arrière-plan
                thread = threading.Thread(
                    target=self._process_files_background,
                    args=(task_id, saved_files, analysis_type)
                )
                thread.daemon = True
                thread.start()
                
                return {'task_id': task_id}, 200
            
            return {'error': 'Aucun fichier valide'}, 400
            
        except Exception as e:
            # Nettoyer les fichiers en cas d'erreur
            for file_path in saved_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
            return {'error': str(e)}, 500
    
    def _process_files_background(self, task_id, file_paths, analysis_type):
        """Traite les fichiers en arrière-plan"""
        try:
            self.task_status[task_id] = {
                'status': 'processing',
                'progress': 0,
                'message': 'Initialisation...',
                'results': None,
                'error': None,
                'timestamp': time.time()
            }
            
            # Choisir l'analyseur
            if analysis_type == 'forex':
                analyzer = ForexAnalyzer()
            else:
                analyzer = AutresAnalyzer()
            
            # Traitement des fichiers
            results = analyzer.process_files(file_paths, task_id, self.task_status)
            
            if results is not None and len(results) > 0:
                # Générer le rapport Excel
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_filename = analyzer.create_excel_report(results, self.REPORTS_FOLDER, timestamp)
                
                self.task_status[task_id].update({
                    'status': 'completed',
                    'progress': 100,
                    'message': 'Analyse terminée avec succès!',
                    'results': {
                        'data': results,
                        'report_file': report_filename,
                        'timestamp': timestamp,
                        'analysis_type': analysis_type
                    }
                })
            else:
                self.task_status[task_id].update({
                    'status': 'error',
                    'error': 'Aucune donnée trouvée dans les fichiers'
                })
                
        except Exception as e:
            self.task_status[task_id].update({
                'status': 'error',
                'error': str(e)
            })
        
        finally:
            # Nettoyer les fichiers uploadés
            for file_path in file_paths:
                if os.path.exists(file_path):
                    os.remove(file_path)
    
    def get_task_status(self, task_id):
        """Récupère le statut d'une tâche"""
        try:
            print(f"[DEBUG] Getting status for task {task_id}")
            print(f"[DEBUG] Available tasks: {list(self.task_status.keys())}")
            
            if task_id not in self.task_status:
                print(f"[DEBUG] Task {task_id} not found")
                return {'error': 'Tâche introuvable'}, 404
            
            status = self.task_status[task_id].copy()
            print(f"[DEBUG] Raw status: {status}")
            
            # Nettoyer les données non-sérialisables
            if 'results' in status and status['results']:
                results = status['results'].copy()
                if 'data' in results:
                    try:
                        df = results['data']
                        stats = {
                            'total_trades': len(df),
                            'trades_gagnants': len(df[df["Profit"] > 0]),
                            'trades_perdants': len(df[df["Profit"] < 0]),
                            'profit_total': float(df['Profit'].sum()),
                            'solde_final': float(df['Solde_cumule'].iloc[-1]) if len(df) > 0 else 10000,
                            'drawdown_max': float(df['Drawdown_pct'].max()) if 'Drawdown_pct' in df.columns else 0,
                            'taux_reussite': float(len(df[df["Profit"] > 0]) / len(df) * 100) if len(df) > 0 else 0,
                            'rendement': float((float(df['Solde_cumule'].iloc[-1]) - 10000) / 10000 * 100) if len(df) > 0 else 0
                        }
                        results['data'] = stats
                        print(f"[DEBUG] Processed stats: {stats}")
                    except Exception as e:
                        print(f"[ERROR] Error processing DataFrame: {str(e)}")
                        results['data'] = {'error': f'Erreur lors du traitement des données: {str(e)}'}
                status['results'] = results
            
            return status, 200
            
        except Exception as e:
            print(f"[ERROR] Error in get_task_status: {str(e)}")
            return {'error': f'Erreur lors de la récupération du statut: {str(e)}'}, 500
    
    def get_report_file(self, task_id):
        """Récupère le fichier de rapport"""
        if task_id not in self.task_status:
            return {'error': 'Tâche introuvable'}, 404
        
        task = self.task_status[task_id]
        
        if task['status'] != 'completed':
            return {'error': 'Le rapport n\'est pas encore prêt'}, 400
        
        report_file = task['results']['report_file']
        
        if os.path.exists(report_file):
            return send_file(
                report_file,
                as_attachment=True,
                download_name=os.path.basename(report_file)
            )
        
        return {'error': 'Fichier de rapport introuvable'}, 404
    
    def cleanup_old_tasks(self, hours=24):
        """Nettoie les anciennes tâches et fichiers"""
        try:
            current_time = time.time()
            
            # Nettoyer les fichiers uploadés
            cleaned_files = 0
            if os.path.exists(self.UPLOAD_FOLDER):
                for filename in os.listdir(self.UPLOAD_FOLDER):
                    file_path = os.path.join(self.UPLOAD_FOLDER, filename)
                    if os.path.isfile(file_path):
                        file_age = current_time - os.path.getctime(file_path)
                        if file_age > hours * 3600:
                            os.remove(file_path)
                            cleaned_files += 1
            
            # Nettoyer les anciens statuts de tâches
            old_tasks = []
            for task_id, task in self.task_status.items():
                if 'timestamp' in task and (current_time - task['timestamp']) > hours * 3600:
                    old_tasks.append(task_id)
            
            for task_id in old_tasks:
                del self.task_status[task_id]
            
            return {
                'message': 'Nettoyage effectué',
                'cleaned_files': cleaned_files,
                'cleaned_tasks': len(old_tasks)
            }, 200
            
        except Exception as e:
            return {'error': str(e)}, 500 