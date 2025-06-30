from flask import Flask, render_template, request, jsonify, send_file, session, flash, redirect, url_for
from flask_mail import Mail, Message
from flask_login import LoginManager, login_required, current_user
import os
import json
from datetime import datetime
import uuid
from werkzeug.utils import secure_filename
import threading
import time
import logging
import mimetypes
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import config

# Import des modules d'analyse
from modules.forex_analyzer import ForexAnalyzer
from modules.autres_analyzer import AutresAnalyzer

# Import des modules d'authentification
from models import init_db, User, Analysis, db
from auth import auth_bp
from admin import admin_bp
from forms import ContactForm

def create_app(config_name=None):
    """Factory pour créer l'application Flask"""
    app = Flask(__name__)
    
    # Configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Configuration de la base de données
    if not hasattr(app.config, 'SQLALCHEMY_DATABASE_URI'):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trading_analyzer.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configuration WTF pour la sécurité des formulaires
    app.config['WTF_CSRF_ENABLED'] = True
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Configuration des logs pour la production
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
        app.logger.info('Trading Analyzer started')
    
    return app

app = create_app()

# Configuration de l'email (utilisation de Gmail SMTP)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'contact@wenbot.club'
app.config['MAIL_PASSWORD'] = 'agyw bdmb ccyb ovch'
app.config['MAIL_DEFAULT_SENDER'] = 'contact@wenbot.club'

# Initialiser les extensions
mail = Mail(app)

# Initialiser la base de données
init_db(app)

# Configuration de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    """Charge un utilisateur pour Flask-Login"""
    return User.query.get(int(user_id))

# Enregistrer les blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)

# Configuration des dossiers
UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
REPORTS_FOLDER = app.config['REPORTS_FOLDER']
ALLOWED_EXTENSIONS = app.config['ALLOWED_EXTENSIONS']

# Dictionnaire pour stocker l'état des tâches en cours
task_status = {}

# Système de traduction simple
translations = {}

def load_translations():
    """Charge les fichiers de traduction JSON"""
    global translations
    translations_dir = os.path.join(os.path.dirname(__file__), 'translations')
    
    for lang in ['en', 'fr']:
        try:
            with open(os.path.join(translations_dir, f'{lang}.json'), 'r', encoding='utf-8') as f:
                translations[lang] = json.load(f)
        except Exception as e:
            app.logger.error(f"Erreur lors du chargement des traductions {lang}: {e}")
            translations[lang] = {}

def get_current_language():
    """Obtient la langue courante depuis la session ou cookie"""
    return session.get('language', request.cookies.get('language', 'en'))

def t(key, **kwargs):
    """Fonction de traduction simple"""
    lang = get_current_language()
    
    # Naviguer dans le dictionnaire des traductions
    keys = key.split('.')
    translation = translations.get(lang, {})
    
    for k in keys:
        if isinstance(translation, dict) and k in translation:
            translation = translation[k]
        else:
            # Fallback vers l'anglais si la traduction n'existe pas
            translation = translations.get('en', {})
            for fallback_k in keys:
                if isinstance(translation, dict) and fallback_k in translation:
                    translation = translation[fallback_k]
                else:
                    return key  # Retourner la clé si aucune traduction n'est trouvée
            break
    
    # Si on a des arguments pour le formatage
    if kwargs and isinstance(translation, str):
        try:
            translation = translation.format(**kwargs)
        except:
            pass
    
    return translation

# Charger les traductions au démarrage
load_translations()

# Rendre la fonction t disponible dans tous les templates
@app.context_processor
def inject_translation():
    return dict(t=t, current_lang=get_current_language())

def allowed_file(filename):
    """Vérifie si le fichier est autorisé"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_upload_validation(file):
    """Validation sécurisée des fichiers uploadés"""
    # Vérification de l'extension
    if not allowed_file(file.filename):
        return False, "Extension de fichier non autorisée"
    
    # Vérification du type MIME
    mime_type, _ = mimetypes.guess_type(file.filename)
    allowed_mimes = [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # .xlsx
        'application/vnd.ms-excel'  # .xls
    ]
    
    if mime_type not in allowed_mimes:
        return False, "Type MIME non autorisé"
    
    # Vérification de la taille
    file.seek(0, 2)  # Aller à la fin du fichier
    size = file.tell()
    file.seek(0)  # Retourner au début
    
    if size > app.config['MAX_CONTENT_LENGTH']:
        return False, "Fichier trop volumineux"
    
    return True, "OK"

def process_files_background(task_id, file_paths, analysis_type, user_id=None, original_filenames=None):
    """Traite les fichiers en arrière-plan"""
    try:
        # Récupérer l'utilisateur si fourni
        user = None
        if user_id:
            with app.app_context():
                user = User.query.get(user_id)
                if user:
                    # Incrémenter l'usage dès le début
                    user.increment_usage()
        task_status[task_id] = {
            'status': 'processing',
            'progress': 0,
            'message': 'Initialisation...',
            'results': None,
            'error': None,
            'timestamp': time.time()
        }
        
        app.logger.info(f'Starting task {task_id} with {len(file_paths)} files, type: {analysis_type}')
        
        # Choisir l'analyseur
        task_status[task_id]['message'] = 'Chargement de l\'analyseur...'
        task_status[task_id]['progress'] = 5
        
        try:
            if analysis_type == 'forex':
                app.logger.info(f'Loading ForexAnalyzer for task {task_id}')
                analyzer = ForexAnalyzer()
            else:
                app.logger.info(f'Loading AutresAnalyzer for task {task_id}')
                analyzer = AutresAnalyzer()
            
            app.logger.info(f'Analyzer loaded successfully for task {task_id}')
            task_status[task_id]['message'] = 'Analyseur chargé, début du traitement...'
            task_status[task_id]['progress'] = 10
            
        except Exception as e:
            app.logger.error(f'Error loading analyzer for task {task_id}: {str(e)}')
            raise Exception(f"Erreur lors du chargement de l'analyseur: {str(e)}")
        
        # Traitement des fichiers
        task_status[task_id]['message'] = 'Traitement des fichiers Excel...'
        task_status[task_id]['progress'] = 20
        
        app.logger.info(f'Starting file processing for task {task_id}')
        results = analyzer.process_files(file_paths, task_id, task_status)
        app.logger.info(f'File processing completed for task {task_id}')
        
        if results is not None and len(results) > 0:
            task_status[task_id]['progress'] = 80
            task_status[task_id]['message'] = 'Génération du rapport Excel...'
            
            app.logger.info(f'Generating Excel report for task {task_id}')
            # Générer le rapport Excel
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = analyzer.create_excel_report(results, REPORTS_FOLDER, timestamp)
            
            task_status[task_id]['status'] = 'completed'
            task_status[task_id]['progress'] = 100
            task_status[task_id]['message'] = 'Analyse terminée avec succès!'
            task_status[task_id]['results'] = {
                'data': results,
                'report_file': report_filename,
                'timestamp': timestamp,
                'analysis_type': analysis_type
            }
            
            # Enregistrer l'analyse en base de données
            if user:
                try:
                    with app.app_context():
                        # Calculer les statistiques de l'analyse
                        total_trades = len(results) if hasattr(results, '__len__') else 0
                        profit_total = results['Profit'].sum() if 'Profit' in results.columns else 0
                        drawdown_max = results['Drawdown_pct'].max() if 'Drawdown_pct' in results.columns else 0
                        
                        # Calculer le taux de réussite
                        if total_trades > 0:
                            trades_gagnants = len(results[results["Profit"] > 0]) if 'Profit' in results.columns else 0
                            success_rate = (trades_gagnants / total_trades) * 100
                        else:
                            success_rate = 0
                        
                        # Créer l'enregistrement d'analyse
                        analysis = Analysis(
                            user_id=user.id,
                            analysis_type=analysis_type,
                            original_filename=', '.join(original_filenames) if original_filenames else 'Unknown',
                            report_filename=os.path.basename(report_filename),
                            total_trades=total_trades,
                            profit_total=float(profit_total),
                            drawdown_max=float(drawdown_max),
                            success_rate=float(success_rate),
                            status='completed'
                        )
                        
                        db.session.add(analysis)
                        db.session.commit()
                        
                        app.logger.info(f'Analysis saved to database for user {user.email}')
                        
                except Exception as e:
                    app.logger.error(f'Error saving analysis to database: {str(e)}')
                    # Ne pas faire échouer l'analyse si la BDD échoue
            
            app.logger.info(f'Analysis completed for task {task_id}')
        else:
            app.logger.warning(f'No data found for task {task_id}')
            task_status[task_id]['status'] = 'error'
            task_status[task_id]['error'] = 'Aucune donnée trouvée dans les fichiers'
            
    except Exception as e:
        app.logger.error(f'Error in task {task_id}: {str(e)}')
        task_status[task_id]['status'] = 'error'
        task_status[task_id]['error'] = str(e)
    
    finally:
        # Nettoyer les fichiers uploadés après traitement
        try:
            for file_path in file_paths:
                if os.path.exists(file_path):
                    os.remove(file_path)
        except Exception as e:
            app.logger.warning(f'Could not clean up files: {str(e)}')

@app.route('/set_language/<language>')
def set_language(language):
    """Change la langue de l'interface"""
    if language in ['en', 'fr']:
        session['language'] = language
        # Définir aussi un cookie pour la persistance
        resp = redirect(request.referrer or url_for('index'))
        resp.set_cookie('language', language, max_age=60*60*24*30)  # 30 jours
        return resp
    return redirect(url_for('index'))

@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_files():
    """Page d'upload et de traitement des fichiers - SANS login_required"""
    # DEBUG: Log pour vérifier l'accès à la route
    print(f"[DEBUG] Route /upload appelée - Méthode: {request.method}, Utilisateur connecté: {current_user.is_authenticated}")
    print(f"[DEBUG] User agent: {request.headers.get('User-Agent', 'Unknown')}")
    print(f"[DEBUG] Referer: {request.headers.get('Referer', 'None')}")
    
    if request.method == 'POST':
        # Vérifier que l'utilisateur est connecté pour POST
        if not current_user.is_authenticated:
            flash('Vous devez créer un compte pour utiliser l\'analyse !', 'warning')
            return redirect(url_for('auth.register'))
        # Vérifier les limites d'usage de l'utilisateur
        if not current_user.can_perform_analysis():
            remaining = current_user.get_remaining_analyses()
            if remaining == 0:
                flash('Vous avez atteint votre limite mensuelle d\'analyses. Passez au Premium pour un accès illimité !', 'warning')
            else:
                flash(f'Vous avez dépassé votre limite. Il vous reste {remaining} analyses ce mois.', 'warning')
            return redirect(url_for('auth.upgrade'))
        
        # Vérifier si des fichiers ont été envoyés
        if 'files' not in request.files:
            flash('Aucun fichier sélectionné', 'error')
            return redirect(request.url)
        
        files = request.files.getlist('files')
        analysis_type = request.form.get('analysis_type', 'forex')
        
        if not files or files[0].filename == '':
            flash('Aucun fichier sélectionné', 'error')
            return redirect(request.url)
        
        # Validation et sauvegarde des fichiers
        saved_files = []
        for file in files:
            if file and file.filename:
                # Validation sécurisée
                is_valid, message = secure_upload_validation(file)
                if not is_valid:
                    flash(f'Erreur avec {file.filename}: {message}', 'error')
                    return redirect(request.url)
                
                # Sauvegarde sécurisée
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_filename = f"{timestamp}_{filename}"
                file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                
                file.save(file_path)
                saved_files.append(file_path)
        
        if saved_files:
            # Créer un ID unique pour cette tâche
            task_id = str(uuid.uuid4())
            
            # Enregistrer les noms de fichiers originaux
            original_filenames = [file.filename for file in files if file.filename]
            
            # Lancer le traitement en arrière-plan
            thread = threading.Thread(
                target=process_files_background, 
                args=(task_id, saved_files, analysis_type, current_user.id, original_filenames)
            )
            thread.daemon = True  # Thread daemon pour éviter les blocages
            thread.start()
            
            return redirect(url_for('progress', task_id=task_id))
    
    # DEBUG: Log pour la réponse GET
    print(f"[DEBUG] Retour du template upload.html pour utilisateur connecté: {current_user.is_authenticated}")
    return render_template('upload.html')

@app.route('/progress/<task_id>')
@login_required
def progress(task_id):
    """Page de progression du traitement"""
    if task_id not in task_status:
        flash('Tâche introuvable', 'error')
        return redirect(url_for('index'))
    
    return render_template('progress.html', task_id=task_id)

@app.route('/api/progress/<task_id>')
@login_required
def api_progress(task_id):
    """API pour récupérer l'état de progression"""
    if task_id in task_status:
        # Créer une copie sans les DataFrames pour éviter les erreurs JSON
        status_copy = task_status[task_id].copy()
        
        # Si on a des résultats, on retire le DataFrame qui n'est pas JSON serializable
        if 'results' in status_copy and status_copy['results'] is not None:
            results = status_copy['results'].copy()
            if 'data' in results:
                # Remplacer le DataFrame par des stats de base
                try:
                    df = results['data']
                    results['data'] = {
                        'total_rows': len(df),
                        'columns': list(df.columns) if hasattr(df, 'columns') else [],
                        'sample_data': 'DataFrame processed successfully'
                    }
                except Exception as e:
                    results['data'] = f'DataFrame processing error: {str(e)}'
            
            status_copy['results'] = results
        
        return jsonify(status_copy)
    else:
        return jsonify({'status': 'not_found', 'error': 'Tâche introuvable'}), 404

@app.route('/results/<task_id>')
@login_required
def results(task_id):
    """Page des résultats"""
    if task_id not in task_status:
        flash('Tâche introuvable', 'error')
        return redirect(url_for('index'))
    
    task = task_status[task_id]
    
    if task['status'] != 'completed':
        flash('Le traitement n\'est pas terminé', 'error')
        return redirect(url_for('progress', task_id=task_id))
    
    return render_template('results.html', task_id=task_id, results=task['results'])

@app.route('/api/results/<task_id>')
@login_required
def api_results(task_id):
    """API pour récupérer les résultats JSON"""
    if task_id not in task_status:
        return jsonify({'error': 'Tâche introuvable'}), 404
    
    task = task_status[task_id]
    
    if task['status'] != 'completed':
        return jsonify({'error': 'Traitement non terminé'}), 400
    
    # Préparer les données pour JSON (retirer les DataFrames)
    results = task['results']
    
    try:
        # Extraire les statistiques du DataFrame au lieu de l'envoyer
        df = results['data']
        stats = extract_stats_from_dataframe(df)
        
        json_results = {
            'analysis_type': results['analysis_type'],
            'timestamp': results['timestamp'],
            'stats': stats,
            'report_available': True,
            'total_trades': len(df) if hasattr(df, '__len__') else 0
        }
        
        return jsonify(json_results)
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la préparation des résultats: {str(e)}'}), 500

@app.route('/download/<task_id>')
@login_required
def download_report(task_id):
    """Télécharger le rapport Excel"""
    if task_id not in task_status:
        flash('Tâche introuvable', 'error')
        return redirect(url_for('index'))
    
    task = task_status[task_id]
    
    if task['status'] != 'completed':
        flash('Le rapport n\'est pas encore prêt', 'error')
        return redirect(url_for('progress', task_id=task_id))
    
    report_file = task['results']['report_file']
    
    if os.path.exists(report_file):
        return send_file(
            report_file,
            as_attachment=True,
            download_name=os.path.basename(report_file)
        )
    else:
        flash('Fichier de rapport introuvable', 'error')
        return redirect(url_for('results', task_id=task_id))

def extract_stats_from_dataframe(df):
    """Extrait les statistiques principales du DataFrame pour l'API JSON"""
    try:
        total_trades = len(df)
        trades_gagnants = len(df[df["Profit"] > 0])
        trades_perdants = len(df[df["Profit"] < 0])
        profit_total = df['Profit'].sum()
        solde_final = df['Solde_cumule'].iloc[-1] if len(df) > 0 else 10000
        drawdown_max = df['Drawdown_pct'].max() if 'Drawdown_pct' in df.columns else 0
        
        # NOUVEAU : Extraire les données réelles pour les graphiques
        balance_evolution = []
        if 'Solde_cumule' in df.columns and len(df) > 0:
            # Utiliser directement les valeurs de Solde_cumule (qui contiennent déjà l'évolution complète)
            # CORRECTION : Ne pas ajouter 10000 au début car Solde_cumule commence déjà près de 10000
            solde_values = df['Solde_cumule'].tolist()
            
            # Ajouter le solde initial SEULEMENT au début pour avoir le point de départ avant le premier trade
            balance_evolution = [10000] + solde_values
            
            # DEBUG FORCÉ : Affichage obligatoire
            print("=" * 50)
            print("DEBUG FORCÉ - ANALYSE DES DONNÉES")
            print("=" * 50)
            print(f"DataFrame Solde_cumule - First 10 values: {solde_values[:10]}")
            print(f"DataFrame Solde_cumule - Last 10 values: {solde_values[-10:]}")
            print(f"Balance evolution FINALE - First 10 values: {balance_evolution[:10]}")
            print(f"Balance evolution FINALE - Last 10 values: {balance_evolution[-10:]}")
            print(f"Balance evolution length: {len(balance_evolution)}")
            print(f"Min balance: {min(balance_evolution)}, Max balance: {max(balance_evolution)}")
            
            # Vérifier les différences entre valeurs consécutives
            differences = []
            for i in range(1, len(balance_evolution)):
                diff = balance_evolution[i] - balance_evolution[i-1]
                differences.append(diff)
            
            print(f"Différences entre valeurs consécutives: {differences[:10]}")
            print(f"Max différence absolue: {max([abs(d) for d in differences]) if differences else 0}")
            
            # Compter les trades avec profit non nul
            non_zero_changes = [d for d in differences if abs(d) > 0.01]
            print(f"Nombre de changements significatifs (>0.01€): {len(non_zero_changes)}")
            print(f"Pourcentage de trades actifs: {len(non_zero_changes)/len(differences)*100:.1f}%")
            
            # Vérifier s'il y a vraiment des variations
            unique_values = list(set(balance_evolution))
            if len(unique_values) == 1:
                print(f"❌ PROBLÈME: Toutes les valeurs sont identiques ! Valeur: {unique_values[0]}")
            elif len(unique_values) <= 5:
                print(f"⚠️  ATTENTION: Seulement {len(unique_values)} valeurs uniques: {unique_values}")
            else:
                print(f"✅ OK: {len(unique_values)} valeurs uniques dans balance_evolution")
                print(f"✅ Écart min-max: {max(balance_evolution) - min(balance_evolution):.2f} €")
            print("=" * 50)
        else:
            balance_evolution = [10000]
            print("❌ ERREUR: Aucune colonne Solde_cumule trouvée ou DataFrame vide")
        
        # Extraire aussi les profits individuels pour analyser les variations
        profit_evolution = []
        if 'Profit' in df.columns and len(df) > 0:
            profit_evolution = df['Profit'].tolist()
            print(f"[DEBUG] Profit evolution - First 10 values: {profit_evolution[:10]}")
            print(f"[DEBUG] Profits positifs: {len([p for p in profit_evolution if p > 0])}")
            print(f"[DEBUG] Profits négatifs: {len([p for p in profit_evolution if p < 0])}")
        
        return {
            'total_trades': total_trades,
            'trades_gagnants': trades_gagnants,
            'trades_perdants': trades_perdants,
            'taux_reussite': (trades_gagnants / (trades_gagnants + trades_perdants) * 100) if (trades_gagnants + trades_perdants) > 0 else 0,
            'profit_total': round(profit_total, 2),
            'solde_final': round(solde_final, 2),
            'rendement': round(((solde_final - 10000) / 10000 * 100), 2),
            'drawdown_max': round(drawdown_max, 2),
            'balance_evolution': [round(b, 2) for b in balance_evolution],  # DONNÉES RÉELLES
            'profit_evolution': [round(p, 2) for p in profit_evolution]     # PROFITS RÉELS
        }
    except Exception as e:
        print(f"[ERROR] Erreur dans extract_stats_from_dataframe: {str(e)}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return {'error': f'Erreur lors de l\'extraction des statistiques: {str(e)}'}

@app.route('/cleanup')
def cleanup():
    """Nettoie les anciens fichiers temporaires"""
    try:
        # Nettoyer les fichiers uploadés de plus de 24h
        upload_dir = UPLOAD_FOLDER
        current_time = time.time()
        cleaned_files = 0
        
        if os.path.exists(upload_dir):
            for filename in os.listdir(upload_dir):
                file_path = os.path.join(upload_dir, filename)
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getctime(file_path)
                    if file_age > 24 * 3600:  # 24 heures
                        os.remove(file_path)
                        cleaned_files += 1
        
        # Nettoyer les anciens statuts de tâches
        old_tasks = []
        for task_id, task in task_status.items():
            if 'timestamp' in task and (current_time - task.get('timestamp', 0)) > 24 * 3600:
                old_tasks.append(task_id)
        
        for task_id in old_tasks:
            del task_status[task_id]
        
        return jsonify({
            'message': 'Nettoyage effectué', 
            'cleaned_files': cleaned_files,
            'cleaned_tasks': len(old_tasks)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Endpoint de vérification de santé pour les hébergeurs"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0'
    })

@app.route('/debug')
def debug_route():
    """Route de debug pour tester les imports et modules"""
    debug_info = {
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'python_path': os.getcwd(),
        'upload_folder_exists': os.path.exists(UPLOAD_FOLDER),
        'reports_folder_exists': os.path.exists(REPORTS_FOLDER)
    }
    
    # Test des imports
    try:
        from modules.forex_analyzer import ForexAnalyzer
        debug_info['forex_analyzer_import'] = 'success'
        try:
            analyzer = ForexAnalyzer()
            debug_info['forex_analyzer_init'] = 'success'
        except Exception as e:
            debug_info['forex_analyzer_init'] = f'error: {str(e)}'
    except Exception as e:
        debug_info['forex_analyzer_import'] = f'error: {str(e)}'
    
    try:
        from modules.autres_analyzer import AutresAnalyzer
        debug_info['autres_analyzer_import'] = 'success'
        try:
            analyzer = AutresAnalyzer()
            debug_info['autres_analyzer_init'] = 'success'
        except Exception as e:
            debug_info['autres_analyzer_init'] = f'error: {str(e)}'
    except Exception as e:
        debug_info['autres_analyzer_import'] = f'error: {str(e)}'
    
    # Test des dépendances
    try:
        import pandas as pd
        debug_info['pandas_version'] = pd.__version__
    except Exception as e:
        debug_info['pandas_error'] = str(e)
    
    try:
        import numpy as np
        debug_info['numpy_version'] = np.__version__
    except Exception as e:
        debug_info['numpy_error'] = str(e)
    
    return jsonify(debug_info)

@app.route('/contact', methods=['POST'])
def contact():
    """Route pour traiter les demandes de contact"""
    try:
        # Récupérer les données du formulaire
        prenom = request.form.get('prenom', '').strip()
        nom = request.form.get('nom', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        
        # Validation des champs obligatoires
        if not prenom or not nom or not email or not message:
            return jsonify({
                'success': False,
                'message': 'Veuillez remplir tous les champs obligatoires.'
            }), 400
        
        # Validation basique de l'email
        if '@' not in email or '.' not in email:
            return jsonify({
                'success': False,
                'message': 'Adresse email invalide.'
            }), 400
        
        # Préparer le sujet du message
        email_subject = f"Contact Wenbot Trading Analyzer - {subject if subject else 'Message général'}"
        
        # Préparer le contenu du message
        email_body = f"""
Nouveau message depuis le formulaire de contact Wenbot Trading Analyzer

Informations du contact:
- Prénom: {prenom}
- Nom: {nom}
- Email: {email}
- Sujet: {subject if subject else 'Non spécifié'}

Message:
{message}

---
Message envoyé automatiquement depuis wenbot-analyzer.com
Date: {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}
        """
        
        # Vérifier si on est en mode développement local
        is_debug_mode = (
            app.config.get('DEBUG', False) or 
            os.environ.get('FLASK_ENV') == 'development' or
            os.environ.get('FLASK_DEBUG') == '1'
        )
        
        if is_debug_mode:
            app.logger.info('=' * 60)
            app.logger.info('📧 DEBUG MODE: Simulation d\'envoi d\'email')
            app.logger.info(f'📫 Destinataire: contact@wenbot.club')
            app.logger.info(f'👤 De: {prenom} {nom} ({email})')
            app.logger.info(f'📋 Sujet: {subject or "Message général"}')
            app.logger.info(f'💬 Message: {message}')
            app.logger.info('✅ Email simulé avec succès en mode développement')
            app.logger.info('=' * 60)
        else:
            # Tentative d'envoi réel seulement en production
            try:
                if app.config.get('MAIL_USERNAME') and app.config.get('MAIL_PASSWORD'):
                    msg = Message(
                        subject=email_subject,
                        recipients=['contact@wenbot.club'],
                        body=email_body,
                        reply_to=email
                    )
                    mail.send(msg)
                    app.logger.info(f'Email sent successfully via Flask-Mail from {email}')
                else:
                    # Fallback: envoi direct via SMTP
                    app.logger.warning('Flask-Mail not configured, trying direct SMTP')
                    send_email_direct(email_subject, email_body, email)
                    
            except Exception as email_error:
                app.logger.error(f'Email sending failed: {str(email_error)}')
                return jsonify({
                    'success': False,
                    'message': 'Erreur lors de l\'envoi de l\'email. Veuillez réessayer plus tard.'
                }), 500
        
        return jsonify({
            'success': True,
            'message': 'Message envoyé avec succès ! Nous vous répondrons dans les plus brefs délais.'
        })
        
    except Exception as e:
        app.logger.error(f'Error in contact route: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'Une erreur est survenue. Veuillez réessayer.'
        }), 500

def send_email_direct(subject, body, reply_to):
    """Fonction de fallback pour l'envoi direct d'email"""
    try:
        # Configuration SMTP pour Gmail (à adapter selon vos besoins)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_username = app.config.get('MAIL_USERNAME')
        smtp_password = app.config.get('MAIL_PASSWORD')
        
        if not smtp_username or not smtp_password:
            raise Exception("Configuration email manquante")
        
        # Créer le message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = 'contact@wenbot.club'
        msg['Subject'] = subject
        msg['Reply-To'] = reply_to
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Envoyer le message
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_username, 'contact@wenbot.club', text)
        server.quit()
        
        app.logger.info(f'Email sent successfully via direct SMTP from {reply_to}')
        
    except Exception as e:
        app.logger.error(f'Direct SMTP failed: {str(e)}')
        raise e

if __name__ == '__main__':
    # Créer les dossiers s'ils n'existent pas
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(REPORTS_FOLDER, exist_ok=True)
    
    # Configuration pour la production/développement
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = app.config['DEBUG']
    
    app.run(host=host, port=port, debug=debug) 