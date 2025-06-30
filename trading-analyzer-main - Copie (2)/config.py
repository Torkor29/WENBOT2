import os

class Config:
    """Configuration de base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Dossiers de l'application
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'static/uploads'
    REPORTS_FOLDER = os.environ.get('REPORTS_FOLDER') or 'reports'
    
    # Taille max des fichiers (16MB)
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    
    # Extensions autorisées
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

class DevelopmentConfig(Config):
    """Configuration pour le développement"""
    DEBUG = True
    SECRET_KEY = 'dev-secret-key-not-for-production'

class ProductionConfig(Config):
    """Configuration pour la production"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-this-secret-key-in-production'
    
    # Logs pour la production
    LOG_LEVEL = 'INFO'

class TestingConfig(Config):
    """Configuration pour les tests"""
    TESTING = True
    DEBUG = True
    SECRET_KEY = 'test-secret-key'

# Dictionnaire des configurations
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 