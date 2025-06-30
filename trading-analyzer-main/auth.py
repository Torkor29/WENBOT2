"""
Blueprint d'authentification pour Trading Analyzer
Gestion de la connexion, inscription, profil utilisateur
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from models import User, db, UserRole, SubscriptionStatus
from forms import LoginForm, RegisterForm, ProfileForm, ChangePasswordForm
from datetime import datetime
import logging

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Votre compte a été désactivé. Contactez l\'administrateur.', 'error')
                return render_template('auth/login.html', form=form)
            
            # Connexion réussie
            login_user(user, remember=form.remember_me.data)
            user.update_last_login()
            
            # Message de bienvenue personnalisé
            if user.is_admin():
                flash(f'Bienvenue Admin {user.get_full_name()} ! 👑', 'success')
            elif user.is_premium():
                flash(f'Bienvenue {user.get_full_name()} ! ⭐ Compte Premium', 'success')
            else:
                remaining = user.get_remaining_analyses()
                if remaining == float('inf'):
                    flash(f'Bienvenue {user.get_full_name()} ! 🚀', 'success')
                else:
                    flash(f'Bienvenue {user.get_full_name()} ! Il vous reste {remaining} analyses ce mois.', 'success')
            
            # Redirection après connexion
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Email ou mot de passe incorrect.', 'error')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Page d'inscription"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        try:
            # Créer le nouvel utilisateur
            user = User(
                email=form.email.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data
            )
            
            db.session.add(user)
            db.session.commit()
            
            flash(f'Félicitations {user.get_full_name()} ! Votre compte a été créé avec succès. 🎉', 'success')
            flash('Vous pouvez maintenant vous connecter et commencer à analyser vos trades !', 'info')
            
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erreur lors de l'inscription: {str(e)}")
            flash('Une erreur est survenue lors de la création du compte. Veuillez réessayer.', 'error')
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Déconnexion"""
    user_name = current_user.get_full_name()
    logout_user()
    session.clear()
    flash(f'Au revoir {user_name} ! À bientôt sur Trading Analyzer. 👋', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """Page de profil utilisateur"""
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Modification du profil"""
    form = ProfileForm(current_user.email)
    
    if form.validate_on_submit():
        try:
            current_user.first_name = form.first_name.data.strip()
            current_user.last_name = form.last_name.data.strip()
            current_user.email = form.email.data.lower().strip()
            
            db.session.commit()
            flash('Votre profil a été mis à jour avec succès ! ✅', 'success')
            return redirect(url_for('auth.profile'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erreur lors de la mise à jour du profil: {str(e)}")
            flash('Une erreur est survenue lors de la mise à jour.', 'error')
    
    elif request.method == 'GET':
        # Pré-remplir le formulaire
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
    
    return render_template('auth/edit_profile.html', form=form)

@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Changement de mot de passe"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            try:
                current_user.set_password(form.new_password.data)
                db.session.commit()
                flash('Votre mot de passe a été modifié avec succès ! 🔒', 'success')
                return redirect(url_for('auth.profile'))
                
            except Exception as e:
                db.session.rollback()
                logging.error(f"Erreur lors du changement de mot de passe: {str(e)}")
                flash('Une erreur est survenue lors du changement de mot de passe.', 'error')
        else:
            flash('Le mot de passe actuel est incorrect.', 'error')
    
    return render_template('auth/change_password.html', form=form)

@auth_bp.route('/subscription')
@login_required
def subscription():
    """Page d'informations sur l'abonnement"""
    return render_template('auth/subscription.html', user=current_user)

@auth_bp.route('/upgrade')
@login_required
def upgrade():
    """Page de mise à niveau vers Premium"""
    if current_user.is_premium():
        flash('Vous avez déjà un compte Premium ! ⭐', 'info')
        return redirect(url_for('auth.subscription'))
    
    # Pour l'instant, simple simulation
    # Plus tard: intégration Stripe/PayPal
    return render_template('auth/upgrade.html', user=current_user)

@auth_bp.route('/upgrade_demo')
@login_required
def upgrade_demo():
    """Simulation de mise à niveau (pour les tests)"""
    if not current_user.is_premium():
        try:
            current_user.role = UserRole.PREMIUM
            current_user.subscription_status = SubscriptionStatus.ACTIVE
            current_user.subscription_start = datetime.utcnow()
            # 30 jours d'essai
            from datetime import timedelta
            current_user.subscription_end = datetime.utcnow() + timedelta(days=30)
            
            db.session.commit()
            flash('🎉 Félicitations ! Vous avez été mis à niveau vers Premium pour 30 jours !', 'success')
            flash('Vous avez maintenant accès à des analyses illimitées ! ⭐', 'info')
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erreur lors de la mise à niveau: {str(e)}")
            flash('Erreur lors de la mise à niveau.', 'error')
    else:
        flash('Vous avez déjà un compte Premium !', 'info')
    
    return redirect(url_for('auth.subscription'))

# Route historique supprimée sur demande de l'utilisateur

# Routes pour l'API (JSON)
@auth_bp.route('/api/user')
@login_required
def api_user():
    """API: Informations utilisateur"""
    return current_user.to_dict()

@auth_bp.route('/api/check_usage')
@login_required
def api_check_usage():
    """API: Vérifier l'usage restant"""
    return {
        'can_analyze': current_user.can_perform_analysis(),
        'remaining_analyses': current_user.get_remaining_analyses(),
        'is_premium': current_user.is_premium(),
        'monthly_limit': current_user.monthly_analyses_limit,
        'monthly_used': current_user.monthly_analyses_used
    } 