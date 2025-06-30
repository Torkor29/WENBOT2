# Composant Navbar WenBot

## 📋 Description

Composant de barre de navigation réutilisable avec toutes les fonctionnalités modernes :
- **Fond transparent** qui s'adapte automatiquement aux sections
- **Logo WenBot en blanc** par défaut avec adaptation contextuelle
- **Barre de recherche** améliorée (plus grande, rectangulaire, sans icône)
- **Adaptation automatique** selon la couleur de fond des sections
- **Responsive design** avec menu mobile

## 🚀 Installation

### Méthode 1 : Inclusion directe dans une page existante

```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="css/styles.css">
    <link rel="stylesheet" href="components/navbar.css">
</head>
<body>
    <!-- Inclure le HTML de la navbar -->
    <nav class="navbar" id="navbar">
        <div class="nav-container">
            <div class="nav-brand">
                <span class="nav-brand-text">WenBot</span>
            </div>
            
            <div class="nav-menu" id="nav-menu">
                <a href="#home" class="nav-link active">Home</a>
                <a href="#features" class="nav-link">Features</a>
                <a href="#advantages" class="nav-link">Advantages</a>
                <a href="#pricing" class="nav-link">Pricing</a>
                <a href="#faq" class="nav-link">FAQ</a>
            </div>
            
            <div class="nav-actions">
                <div class="search-container">
                    <input type="text" placeholder="Search..." class="search-input">
                </div>
                <button class="btn-join">Join</button>
            </div>
            
            <div class="nav-toggle" id="nav-toggle">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    </nav>

    <script src="components/navbar.js"></script>
</body>
</html>
```

### Méthode 2 : Chargement dynamique du composant

```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="css/styles.css">
    <link rel="stylesheet" href="components/navbar.css">
</head>
<body>
    <script src="components/navbar.js"></script>
    <script>
        // Charger le composant dynamiquement
        NavbarComponent.loadComponent().then(navbar => {
            console.log('Navbar chargée avec succès !');
        });
    </script>
</body>
</html>
```

## 🎨 Fonctionnalités

### 1. Adaptation automatique aux sections
La navbar détecte automatiquement la couleur de fond des sections et adapte son apparence :

```css
/* Section avec fond blanc - la navbar s'adapte automatiquement */
.my-white-section {
    background: white;
    color: #333;
}

/* Ou ajoutez la classe 'white-section' pour forcer l'adaptation */
.my-section.white-section {
    background: #f5f5f5;
}
```

### 2. Logo WenBot
- **Couleur par défaut** : Blanc
- **Adaptation automatique** : Devient sombre sur les sections claires
- **Transition fluide** : Animation douce lors des changements

### 3. Barre de recherche améliorée
- **Fond transparent** avec bordure subtile
- **Taille augmentée** : 240px de largeur, padding généreux
- **Forme rectangulaire** : border-radius réduit (4px)
- **Sans icône de loupe** : Design épuré
- **Focus interactif** : Effets visuels au focus

### 4. Responsive Design
- **Desktop** : Menu horizontal complet
- **Tablet/Mobile** : Menu hamburger avec overlay plein écran

## 🔧 Personnalisation

### Variables CSS disponibles
Le composant utilise les variables CSS définies dans votre fichier principal :

```css
:root {
    --bg-primary: #0d1421;
    --text-primary: #d1d4dc;
    --text-secondary: #8a8e9b;
    --color-blue: #2962ff;
    --color-gradient: linear-gradient(135deg, #2962ff 0%, #9c27b0 100%);
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 2rem;
}
```

### Personnaliser les liens de navigation
Modifiez directement dans le HTML ou via JavaScript :

```javascript
// Ajouter un nouveau lien de navigation
const navMenu = document.getElementById('nav-menu');
const newLink = document.createElement('a');
newLink.href = '#contact';
newLink.textContent = 'Contact';
newLink.className = 'nav-link';
navMenu.appendChild(newLink);

// Réinitialiser les event listeners
window.NavbarComponent.bindEvents();
```

## 📱 Support Mobile

Le composant inclut une gestion complète du responsive design :
- **Menu hamburger** automatique sous 768px
- **Barre de recherche masquée** sous 480px pour optimiser l'espace
- **Touch-friendly** : zones de clic optimisées pour mobile

## 🔄 API JavaScript

### Méthodes disponibles

```javascript
const navbar = window.NavbarComponent;

// Ouvrir/fermer le menu mobile
navbar.toggleMobileMenu();
navbar.closeMobileMenu();

// Scroll vers une section
navbar.smoothScrollTo('#features');

// Définir le lien actif manuellement
const homeLink = document.querySelector('a[href="#home"]');
navbar.setActiveLink(homeLink);

// Détruire le composant
navbar.destroy();
```

### Événements personnalisés

Le composant peut être étendu pour émettre des événements personnalisés :

```javascript
// Exemple d'extension pour écouter les changements de section
navbar.onSectionChange = (sectionId) => {
    console.log(`Section active : ${sectionId}`);
    // Logique personnalisée ici
};
```

## 🎯 Exemples d'utilisation

### Nouvelle page avec la navbar
```html
<!DOCTYPE html>
<html>
<head>
    <title>Ma nouvelle page - WenBot</title>
    <link rel="stylesheet" href="../css/styles.css">
    <link rel="stylesheet" href="../components/navbar.css">
</head>
<body>
    <!-- Contenu spécifique à votre page -->
    <section id="home" class="hero-section">
        <h1>Ma nouvelle page</h1>
    </section>
    
    <section id="content" class="white-section">
        <h2>Contenu avec fond blanc</h2>
        <p>La navbar s'adaptera automatiquement !</p>
    </section>

    <script src="../components/navbar.js"></script>
    <script>
        // Chargement automatique via le composant
        NavbarComponent.loadComponent();
    </script>
</body>
</html>
```

## 🛠️ Dépannage

### La navbar ne s'affiche pas
Vérifiez que tous les fichiers sont correctement liés :
- `components/navbar.css`
- `components/navbar.js`
- Variables CSS dans le fichier principal

### L'adaptation aux sections ne fonctionne pas
Ajoutez la classe `white-section` à vos sections avec fond clair :
```html
<section class="my-section white-section">
    <!-- Contenu -->
</section>
```

### Menu mobile ne fonctionne pas
Vérifiez que l'ID `nav-toggle` et `nav-menu` sont présents dans le HTML.

---

**Version :** 1.0  
**Compatibilité :** Tous navigateurs modernes (ES6+)  
**Auteur :** WenBot Team 