#!/usr/bin/env python3
"""
Script de test pour vérifier la configuration email
"""

from flask_mail import Mail, Message
from app import app

def test_email_config():
    """Test de la configuration email"""
    print("🔧 Configuration Email:")
    print(f"📧 MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
    print(f"🔌 MAIL_PORT: {app.config.get('MAIL_PORT')}")
    print(f"🔐 MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
    print(f"👤 MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
    print(f"🔑 MAIL_PASSWORD: {'*' * len(app.config.get('MAIL_PASSWORD', ''))}")
    print(f"📮 MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER')}")
    print()

def test_email_sending():
    """Test d'envoi d'email de test"""
    try:
        print("📧 Test d'envoi d'email...")
        
        with app.app_context():
            mail = Mail(app)
            
            msg = Message(
                subject="Test Trading Analyzer - Configuration Email",
                recipients=["contact@wenbot.club"],
                body="""
Test de configuration email pour Trading Analyzer

Si vous recevez ce message, la configuration email fonctionne correctement !

Configuration testée :
- Serveur SMTP : Gmail
- Authentification : Réussie
- Envoi : Réussi

Date du test : {date}
                """.format(date=__import__('datetime').datetime.now().strftime('%d/%m/%Y à %H:%M:%S')),
                reply_to="contact@wenbot.club"
            )
            
            mail.send(msg)
            print("✅ Email de test envoyé avec succès !")
            print("📬 Vérifiez votre boîte mail contact@wenbot.club")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi : {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Test de Configuration Email Trading Analyzer")
    print("=" * 50)
    
    test_email_config()
    
    # Test d'envoi
    success = test_email_sending()
    
    print("=" * 50)
    if success:
        print("🎉 Configuration email opérationnelle !")
    else:
        print("⚠️  Problème de configuration détecté")
    print("=" * 50) 