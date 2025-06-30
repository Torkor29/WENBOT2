# 📧 Configuration Email pour Production

## ❌ Problème actuel
L'application ne peut pas envoyer d'emails en production car :
1. **Variables d'environnement SMTP manquantes** (MAIL_USERNAME, MAIL_PASSWORD)
2. **Pas de serveur SMTP configuré** pour envoyer les emails
3. L'adresse de destination `contact@wenbot.club` est correcte mais l'envoi échoue

**➡️ Les emails doivent être envoyés VERS `contact@wenbot.club` mais il faut configurer un compte Gmail pour les ENVOYER**

---

## ✅ Solutions possibles

### Option 1 : Gmail SMTP (Recommandé)

#### 1. Créer un mot de passe d'application Gmail
1. Connectez-vous à votre compte Gmail
2. Allez dans les paramètres Google Account
3. Sécurité → Authentification à 2 facteurs (activez si pas fait)
4. Sécurité → Mots de passe des applications
5. Créez un nouveau mot de passe d'application pour "Mail"
6. Notez ce mot de passe (16 caractères)

#### 2. Configurer les variables d'environnement en production
Sur **Render.com** (ou votre hébergeur), ajoutez :
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=votre-email@gmail.com
MAIL_PASSWORD=mot-de-passe-application-16-chars
MAIL_DEFAULT_SENDER=votre-email@gmail.com
```

### Option 2 : Utiliser un service email professionnel

#### SendGrid (gratuit jusqu'à 100 emails/jour)
```
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=votre-api-key-sendgrid
MAIL_DEFAULT_SENDER=votre-email-verifie@domain.com
```

#### Mailgun
```
MAIL_SERVER=smtp.mailgun.org
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=postmaster@mg.yourdomain.com
MAIL_PASSWORD=votre-password-mailgun
MAIL_DEFAULT_SENDER=noreply@yourdomain.com
```

---

## 🎯 Configuration immédiate avec Gmail

### 1. L'adresse de destination est déjà correcte
✅ Les emails sont envoyés vers `contact@wenbot.club` comme voulu.

**Il faut juste configurer le compte Gmail qui va ENVOYER les emails.**

### 2. Variables d'environnement sur Render
1. Allez dans votre app Render
2. Settings → Environment
3. Ajoutez ces variables :
```
MAIL_USERNAME=votre-email@gmail.com
MAIL_PASSWORD=votre-mot-de-passe-app-gmail
```

### 3. Redéployez
L'application va automatiquement redéployer avec la nouvelle config.

---

## 🔍 Test de vérification

### 1. Test en local avec vraie config
Créez un fichier `.env` :
```bash
MAIL_USERNAME=votre-email@gmail.com
MAIL_PASSWORD=votre-mot-de-passe-app
FLASK_ENV=production
```

### 2. Lancez en mode production local
```bash
python app.py
```

### 3. Testez le formulaire de contact
L'email devrait maintenant être envoyé à votre Gmail.

---

## 🛡️ Sécurité

⚠️ **Important** :
- N'utilisez jamais votre mot de passe Gmail principal
- Utilisez uniquement des mots de passe d'application
- Gardez ces credentials secrets
- En production, utilisez les variables d'environnement uniquement

---

## 📋 Checklist finale

- [ ] Créer mot de passe d'application Gmail
- [ ] Modifier les adresses email dans le code
- [ ] Configurer variables d'environnement en production
- [ ] Tester l'envoi d'email
- [ ] Vérifier la réception

**Une fois configuré, vous recevrez tous les messages du formulaire de contact !** 