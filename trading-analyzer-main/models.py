"""
Modèles de base de données pour Trading Analyzer
Gestion des utilisateurs, rôles et abonnements
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import enum

db = SQLAlchemy()

class UserRole(enum.Enum):
    """Énumération des rôles utilisateur"""
    USER = "user"           # Utilisateur gratuit
    PREMIUM = "premium"     # Utilisateur premium
    ADMIN = "admin"         # Administrateur

class SubscriptionStatus(enum.Enum):
    """Statuts d'abonnement"""
    FREE = "free"           # Gratuit (limité)
    ACTIVE = "active"       # Abonnement actif
    EXPIRED = "expired"     # Abonnement expiré
    CANCELLED = "cancelled" # Abonnement annulé

class User(UserMixin, db.Model):
    """Modèle utilisateur avec authentification et abonnement"""
    
    __tablename__ = 'users'
    
    # Informations de base
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # Informations personnelles
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    
    # Métadonnées
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    email_confirmed = db.Column(db.Boolean, default=False)
    
    # Rôle et permissions
    role = db.Column(db.Enum(UserRole), default=UserRole.USER, nullable=False)
    
    # Abonnement
    subscription_status = db.Column(db.Enum(SubscriptionStatus), default=SubscriptionStatus.FREE)
    subscription_start = db.Column(db.DateTime)
    subscription_end = db.Column(db.DateTime)
    
    # Limitations d'usage
    monthly_analyses_used = db.Column(db.Integer, default=0)
    monthly_analyses_limit = db.Column(db.Integer, default=5)  # Limite gratuite
    last_reset_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    analyses = db.relationship('Analysis', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, email, password, first_name, last_name):
        self.email = email.lower().strip()
        self.set_password(password)
        self.first_name = first_name.strip()
        self.last_name = last_name.strip()
    
    def set_password(self, password):
        """Hash et stocke le mot de passe"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Vérifie le mot de passe"""
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        """Retourne le nom complet"""
        return f"{self.first_name} {self.last_name}"
    
    def is_admin(self):
        """Vérifie si l'utilisateur est admin"""
        return self.role == UserRole.ADMIN
    
    def is_premium(self):
        """Vérifie si l'utilisateur est premium ou admin"""
        return self.role in [UserRole.PREMIUM, UserRole.ADMIN]
    
    def has_active_subscription(self):
        """Vérifie si l'abonnement est actif"""
        if self.subscription_status == SubscriptionStatus.ACTIVE:
            return self.subscription_end and self.subscription_end > datetime.utcnow()
        return False
    
    def can_perform_analysis(self):
        """Vérifie si l'utilisateur peut effectuer une analyse"""
        # Admin et premium illimité
        if self.is_premium():
            return True
        
        # Vérifier et réinitialiser le compteur mensuel
        self.check_and_reset_monthly_limit()
        
        # Utilisateur gratuit avec limite
        return self.monthly_analyses_used < self.monthly_analyses_limit
    
    def check_and_reset_monthly_limit(self):
        """Réinitialise le compteur mensuel si nécessaire"""
        now = datetime.utcnow()
        if self.last_reset_date is None:
            self.last_reset_date = now
        
        # Si on est dans un nouveau mois, réinitialiser
        if (now.year != self.last_reset_date.year or 
            now.month != self.last_reset_date.month):
            self.monthly_analyses_used = 0
            self.last_reset_date = now
            db.session.commit()
    
    def increment_usage(self):
        """Incrémente l'usage mensuel"""
        if not self.is_premium():
            self.monthly_analyses_used += 1
            db.session.commit()
    
    def get_remaining_analyses(self):
        """Retourne le nombre d'analyses restantes ce mois"""
        if self.is_premium():
            return float('inf')  # Illimité
        
        self.check_and_reset_monthly_limit()
        return max(0, self.monthly_analyses_limit - self.monthly_analyses_used)
    
    def update_last_login(self):
        """Met à jour la date de dernière connexion"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convertit l'utilisateur en dictionnaire pour l'API"""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'role': self.role.value,
            'subscription_status': self.subscription_status.value,
            'is_premium': self.is_premium(),
            'is_admin': self.is_admin(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'remaining_analyses': self.get_remaining_analyses(),
            'email_confirmed': self.email_confirmed
        }
    
    def __repr__(self):
        return f'<User {self.email}>'

class Analysis(db.Model):
    """Modèle pour stocker l'historique des analyses"""
    
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Métadonnées de l'analyse
    analysis_type = db.Column(db.String(20), nullable=False)  # 'forex' ou 'autres'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Fichiers et résultats
    original_filename = db.Column(db.String(255))
    report_filename = db.Column(db.String(255))
    
    # Statistiques de l'analyse
    total_trades = db.Column(db.Integer)
    profit_total = db.Column(db.Float)
    drawdown_max = db.Column(db.Float)
    success_rate = db.Column(db.Float)
    
    # Status
    status = db.Column(db.String(20), default='completed')  # 'processing', 'completed', 'failed'
    
    def to_dict(self):
        """Convertit l'analyse en dictionnaire"""
        return {
            'id': self.id,
            'analysis_type': self.analysis_type,
            'created_at': self.created_at.isoformat(),
            'original_filename': self.original_filename,
            'total_trades': self.total_trades,
            'profit_total': self.profit_total,
            'drawdown_max': self.drawdown_max,
            'success_rate': self.success_rate,
            'status': self.status
        }
    
    def __repr__(self):
        return f'<Analysis {self.id} - {self.analysis_type}>'

def init_db(app):
    """Initialise la base de données"""
    db.init_app(app)
    
    with app.app_context():
        # Créer toutes les tables
        db.create_all()
        
        # Créer un utilisateur admin par défaut si il n'existe pas
        admin = User.query.filter_by(email='admin@wenbot.club').first()
        if not admin:
            admin = User(
                email='admin@wenbot.club',
                password='admin123',  # À changer en production !
                first_name='Admin',
                last_name='Wenbot'
            )
            admin.role = UserRole.ADMIN
            admin.email_confirmed = True
            admin.subscription_status = SubscriptionStatus.ACTIVE
            
            db.session.add(admin)
            db.session.commit()
            print("✅ Utilisateur admin créé: admin@wenbot.club / admin123") 