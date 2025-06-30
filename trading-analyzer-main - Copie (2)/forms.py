"""
Formulaires pour l'authentification et la gestion des utilisateurs
Utilise Flask-WTF pour la validation et la sécurité CSRF
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    """Formulaire de connexion"""
    email = StringField('Email', validators=[
        DataRequired(message='L\'email est requis'),
        Email(message='Veuillez entrer un email valide')
    ], render_kw={'placeholder': 'votre@email.com'})
    
    password = PasswordField('Mot de passe', validators=[
        DataRequired(message='Le mot de passe est requis')
    ], render_kw={'placeholder': 'Votre mot de passe'})
    
    remember_me = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')

class RegisterForm(FlaskForm):
    """Formulaire d'inscription"""
    first_name = StringField('Prénom', validators=[
        DataRequired(message='Le prénom est requis'),
        Length(min=2, max=50, message='Le prénom doit contenir entre 2 et 50 caractères')
    ], render_kw={'placeholder': 'Jean'})
    
    last_name = StringField('Nom', validators=[
        DataRequired(message='Le nom est requis'),
        Length(min=2, max=50, message='Le nom doit contenir entre 2 et 50 caractères')
    ], render_kw={'placeholder': 'Dupont'})
    
    email = StringField('Email', validators=[
        DataRequired(message='L\'email est requis'),
        Email(message='Veuillez entrer un email valide')
    ], render_kw={'placeholder': 'jean.dupont@email.com'})
    
    password = PasswordField('Mot de passe', validators=[
        DataRequired(message='Le mot de passe est requis'),
        Length(min=6, message='Le mot de passe doit contenir au moins 6 caractères')
    ], render_kw={'placeholder': 'Minimum 6 caractères'})
    
    password2 = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(message='La confirmation est requise'),
        EqualTo('password', message='Les mots de passe doivent correspondre')
    ], render_kw={'placeholder': 'Confirmez votre mot de passe'})
    
    accept_terms = BooleanField('J\'accepte les conditions d\'utilisation', validators=[
        DataRequired(message='Vous devez accepter les conditions d\'utilisation')
    ])
    
    submit = SubmitField('Créer mon compte')
    
    def validate_email(self, email):
        """Vérifier que l'email n'est pas déjà utilisé"""
        user = User.query.filter_by(email=email.data.lower().strip()).first()
        if user:
            raise ValidationError('Cet email est déjà utilisé. Utilisez un autre email ou connectez-vous.')

class ProfileForm(FlaskForm):
    """Formulaire de modification du profil"""
    first_name = StringField('Prénom', validators=[
        DataRequired(message='Le prénom est requis'),
        Length(min=2, max=50, message='Le prénom doit contenir entre 2 et 50 caractères')
    ])
    
    last_name = StringField('Nom', validators=[
        DataRequired(message='Le nom est requis'),
        Length(min=2, max=50, message='Le nom doit contenir entre 2 et 50 caractères')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='L\'email est requis'),
        Email(message='Veuillez entrer un email valide')
    ])
    
    submit = SubmitField('Mettre à jour le profil')
    
    def __init__(self, original_email, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.original_email = original_email
    
    def validate_email(self, email):
        """Vérifier que l'email n'est pas déjà utilisé par un autre utilisateur"""
        if email.data.lower().strip() != self.original_email:
            user = User.query.filter_by(email=email.data.lower().strip()).first()
            if user:
                raise ValidationError('Cet email est déjà utilisé par un autre utilisateur.')

class ChangePasswordForm(FlaskForm):
    """Formulaire de changement de mot de passe"""
    current_password = PasswordField('Mot de passe actuel', validators=[
        DataRequired(message='Le mot de passe actuel est requis')
    ])
    
    new_password = PasswordField('Nouveau mot de passe', validators=[
        DataRequired(message='Le nouveau mot de passe est requis'),
        Length(min=6, message='Le mot de passe doit contenir au moins 6 caractères')
    ])
    
    new_password2 = PasswordField('Confirmer le nouveau mot de passe', validators=[
        DataRequired(message='La confirmation est requise'),
        EqualTo('new_password', message='Les mots de passe doivent correspondre')
    ])
    
    submit = SubmitField('Changer le mot de passe')

class AdminUserForm(FlaskForm):
    """Formulaire d'administration des utilisateurs"""
    first_name = StringField('Prénom', validators=[
        DataRequired(message='Le prénom est requis'),
        Length(min=2, max=50)
    ])
    
    last_name = StringField('Nom', validators=[
        DataRequired(message='Le nom est requis'),
        Length(min=2, max=50)
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='L\'email est requis'),
        Email(message='Email invalide')
    ])
    
    role = SelectField('Rôle', choices=[
        ('user', '👤 Utilisateur'),
        ('premium', '⭐ Premium'),
        ('admin', '👑 Administrateur')
    ], validators=[DataRequired()])
    
    subscription_status = SelectField('Statut d\'abonnement', choices=[
        ('free', '🆓 Gratuit'),
        ('active', '✅ Actif'),
        ('expired', '⌛ Expiré'),
        ('cancelled', '❌ Annulé')
    ], validators=[DataRequired()])
    
    is_active = BooleanField('Compte actif')
    email_confirmed = BooleanField('Email confirmé')
    
    monthly_analyses_limit = StringField('Limite mensuelle d\'analyses', validators=[
        DataRequired(message='La limite est requise')
    ], render_kw={'type': 'number', 'min': '0'})
    
    submit = SubmitField('Mettre à jour l\'utilisateur')

class ResetPasswordRequestForm(FlaskForm):
    """Formulaire de demande de réinitialisation du mot de passe"""
    email = StringField('Email', validators=[
        DataRequired(message='L\'email est requis'),
        Email(message='Veuillez entrer un email valide')
    ], render_kw={'placeholder': 'votre@email.com'})
    
    submit = SubmitField('Envoyer le lien de réinitialisation')

class ResetPasswordForm(FlaskForm):
    """Formulaire de réinitialisation du mot de passe"""
    password = PasswordField('Nouveau mot de passe', validators=[
        DataRequired(message='Le mot de passe est requis'),
        Length(min=6, message='Le mot de passe doit contenir au moins 6 caractères')
    ])
    
    password2 = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(message='La confirmation est requise'),
        EqualTo('password', message='Les mots de passe doivent correspondre')
    ])
    
    submit = SubmitField('Réinitialiser le mot de passe')

class ContactForm(FlaskForm):
    """Formulaire de contact amélioré"""
    first_name = StringField('Prénom', validators=[
        DataRequired(message='Le prénom est requis'),
        Length(min=2, max=50)
    ], render_kw={'placeholder': 'Jean'})
    
    last_name = StringField('Nom', validators=[
        DataRequired(message='Le nom est requis'),
        Length(min=2, max=50)
    ], render_kw={'placeholder': 'Dupont'})
    
    email = StringField('Email', validators=[
        DataRequired(message='L\'email est requis'),
        Email(message='Email invalide')
    ], render_kw={'placeholder': 'jean.dupont@email.com'})
    
    subject = StringField('Sujet', validators=[
        DataRequired(message='Le sujet est requis'),
        Length(min=5, max=100)
    ], render_kw={'placeholder': 'Sujet de votre message'})
    
    message = TextAreaField('Message', validators=[
        DataRequired(message='Le message est requis'),
        Length(min=10, max=1000, message='Le message doit contenir entre 10 et 1000 caractères')
    ], render_kw={
        'placeholder': 'Votre message...',
        'rows': 5
    })
    
    submit = SubmitField('Envoyer le message') 