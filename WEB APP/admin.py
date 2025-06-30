"""
Blueprint d'administration pour Trading Analyzer
Gestion des utilisateurs, abonnements et statistiques
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from models import User, Analysis, db, UserRole, SubscriptionStatus
from forms import AdminUserForm
from datetime import datetime, timedelta
import logging

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Décorateur pour vérifier les permissions admin"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash('Accès refusé. Permissions administrateur requises.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_required
def dashboard():
    """Tableau de bord administrateur"""
    # Statistiques générales
    total_users = User.query.count()
    premium_users = User.query.filter_by(role=UserRole.PREMIUM).count()
    admin_users = User.query.filter_by(role=UserRole.ADMIN).count()
    active_users = User.query.filter_by(is_active=True).count()
    
    # Analyses
    total_analyses = Analysis.query.count()
    analyses_today = Analysis.query.filter(
        Analysis.created_at >= datetime.utcnow().date()
    ).count()
    
    # Nouveaux utilisateurs cette semaine
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_users_week = User.query.filter(User.created_at >= week_ago).count()
    
    # Utilisateurs par statut d'abonnement
    free_users = User.query.filter_by(subscription_status=SubscriptionStatus.FREE).count()
    active_subs = User.query.filter_by(subscription_status=SubscriptionStatus.ACTIVE).count()
    expired_subs = User.query.filter_by(subscription_status=SubscriptionStatus.EXPIRED).count()
    
    stats = {
        'total_users': total_users,
        'premium_users': premium_users,
        'admin_users': admin_users,
        'active_users': active_users,
        'total_analyses': total_analyses,
        'analyses_today': analyses_today,
        'new_users_week': new_users_week,
        'free_users': free_users,
        'active_subs': active_subs,
        'expired_subs': expired_subs
    }
    
    # Derniers utilisateurs inscrits
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # Dernières analyses
    recent_analyses = Analysis.query.order_by(Analysis.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_users=recent_users,
                         recent_analyses=recent_analyses)

@admin_bp.route('/users')
@admin_required
def users():
    """Liste des utilisateurs avec pagination et filtres"""
    page = request.args.get('page', 1, type=int)
    role_filter = request.args.get('role', '')
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '')
    
    query = User.query
    
    # Filtres
    if role_filter:
        try:
            role_enum = UserRole(role_filter)
            query = query.filter(User.role == role_enum)
        except ValueError:
            pass
    
    if status_filter:
        try:
            status_enum = SubscriptionStatus(status_filter)
            query = query.filter(User.subscription_status == status_enum)
        except ValueError:
            pass
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (User.first_name.ilike(search_pattern)) |
            (User.last_name.ilike(search_pattern)) |
            (User.email.ilike(search_pattern))
        )
    
    # Pagination
    users_paginated = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/users.html', 
                         users=users_paginated,
                         role_filter=role_filter,
                         status_filter=status_filter,
                         search=search)

@admin_bp.route('/user/<int:user_id>')
@admin_required
def user_detail(user_id):
    """Détails d'un utilisateur"""
    user = User.query.get_or_404(user_id)
    
    # Analyses de l'utilisateur
    user_analyses = Analysis.query.filter_by(user_id=user.id).order_by(Analysis.created_at.desc()).limit(10).all()
    
    return render_template('admin/user_detail.html', user=user, analyses=user_analyses)

@admin_bp.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """Modification d'un utilisateur"""
    user = User.query.get_or_404(user_id)
    form = AdminUserForm()
    
    if form.validate_on_submit():
        try:
            # Vérifier l'email unique
            if form.email.data.lower().strip() != user.email:
                existing_user = User.query.filter_by(email=form.email.data.lower().strip()).first()
                if existing_user:
                    flash('Cet email est déjà utilisé par un autre utilisateur.', 'error')
                    return render_template('admin/edit_user.html', form=form, user=user)
            
            # Mise à jour
            user.first_name = form.first_name.data.strip()
            user.last_name = form.last_name.data.strip()
            user.email = form.email.data.lower().strip()
            user.role = UserRole(form.role.data)
            user.subscription_status = SubscriptionStatus(form.subscription_status.data)
            user.is_active = form.is_active.data
            user.email_confirmed = form.email_confirmed.data
            user.monthly_analyses_limit = int(form.monthly_analyses_limit.data)
            
            # Si upgrade vers premium, définir les dates
            if user.role == UserRole.PREMIUM and user.subscription_status == SubscriptionStatus.ACTIVE:
                if not user.subscription_start:
                    user.subscription_start = datetime.utcnow()
                if not user.subscription_end:
                    user.subscription_end = datetime.utcnow() + timedelta(days=30)
            
            db.session.commit()
            flash(f'Utilisateur {user.get_full_name()} mis à jour avec succès !', 'success')
            return redirect(url_for('admin.user_detail', user_id=user.id))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erreur lors de la mise à jour de l'utilisateur: {str(e)}")
            flash('Erreur lors de la mise à jour de l\'utilisateur.', 'error')
    
    elif request.method == 'GET':
        # Pré-remplir le formulaire
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.email.data = user.email
        form.role.data = user.role.value
        form.subscription_status.data = user.subscription_status.value
        form.is_active.data = user.is_active
        form.email_confirmed.data = user.email_confirmed
        form.monthly_analyses_limit.data = str(user.monthly_analyses_limit)
    
    return render_template('admin/edit_user.html', form=form, user=user)

@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Suppression d'un utilisateur"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('Vous ne pouvez pas supprimer votre propre compte !', 'error')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    try:
        user_name = user.get_full_name()
        db.session.delete(user)
        db.session.commit()
        flash(f'Utilisateur {user_name} supprimé avec succès.', 'success')
        return redirect(url_for('admin.users'))
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Erreur lors de la suppression de l'utilisateur: {str(e)}")
        flash('Erreur lors de la suppression de l\'utilisateur.', 'error')
        return redirect(url_for('admin.user_detail', user_id=user_id))

@admin_bp.route('/user/<int:user_id>/toggle_status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """Activer/désactiver un utilisateur"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('Vous ne pouvez pas désactiver votre propre compte !', 'error')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    try:
        user.is_active = not user.is_active
        db.session.commit()
        
        status = "activé" if user.is_active else "désactivé"
        flash(f'Utilisateur {user.get_full_name()} {status} avec succès.', 'success')
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Erreur lors du changement de statut: {str(e)}")
        flash('Erreur lors du changement de statut.', 'error')
    
    return redirect(url_for('admin.user_detail', user_id=user_id))

@admin_bp.route('/analytics')
@admin_required
def analytics():
    """Page d'analytics et statistiques avancées"""
    # Analyses par mois (6 derniers mois)
    monthly_data = []
    for i in range(6):
        start_date = datetime.utcnow().replace(day=1) - timedelta(days=i*30)
        end_date = start_date + timedelta(days=32)  # Approximation
        
        analyses_count = Analysis.query.filter(
            Analysis.created_at >= start_date,
            Analysis.created_at < end_date
        ).count()
        
        monthly_data.append({
            'month': start_date.strftime('%m/%Y'),
            'analyses': analyses_count
        })
    
    monthly_data.reverse()
    
    # Top utilisateurs par nombre d'analyses
    top_users = db.session.query(
        User.first_name, User.last_name, User.email,
        db.func.count(Analysis.id).label('analysis_count')
    ).join(Analysis).group_by(User.id).order_by(
        db.desc('analysis_count')
    ).limit(10).all()
    
    # Répartition par type d'analyse
    forex_count = Analysis.query.filter_by(analysis_type='forex').count()
    autres_count = Analysis.query.filter_by(analysis_type='autres').count()
    
    analysis_types = {
        'forex': forex_count,
        'autres': autres_count
    }
    
    return render_template('admin/analytics.html',
                         monthly_data=monthly_data,
                         top_users=top_users,
                         analysis_types=analysis_types)

@admin_bp.route('/settings')
@admin_required
def settings():
    """Paramètres système"""
    return render_template('admin/settings.html')

# API Routes pour l'admin
@admin_bp.route('/api/stats')
@admin_required
def api_stats():
    """API: Statistiques pour le dashboard"""
    total_users = User.query.count()
    total_analyses = Analysis.query.count()
    premium_users = User.query.filter_by(role=UserRole.PREMIUM).count()
    
    return jsonify({
        'total_users': total_users,
        'total_analyses': total_analyses,
        'premium_users': premium_users,
        'premium_percentage': round((premium_users / total_users * 100) if total_users > 0 else 0, 1)
    })

@admin_bp.route('/api/user/<int:user_id>/reset_usage', methods=['POST'])
@admin_required
def api_reset_user_usage(user_id):
    """API: Réinitialiser l'usage mensuel d'un utilisateur"""
    user = User.query.get_or_404(user_id)
    
    try:
        user.monthly_analyses_used = 0
        user.last_reset_date = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Usage mensuel de {user.get_full_name()} réinitialisé.'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }), 500 