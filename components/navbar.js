/* ================================
   NAVIGATION COMPONENT SCRIPT
   ================================ */

class NavbarComponent {
    constructor() {
        this.navbar = null;
        this.navLinks = null;
        this.navToggle = null;
        this.navMenu = null;
        this.isInitialized = false;
    }

    // Initialisation du composant
    init() {
        if (this.isInitialized) return;
        
        this.navbar = document.getElementById('navbar');
        this.navLinks = document.querySelectorAll('.nav-link');
        this.navToggle = document.getElementById('nav-toggle');
        this.navMenu = document.getElementById('nav-menu');
        
        if (!this.navbar) {
            console.warn('Navbar element not found');
            return;
        }

        this.bindEvents();
        this.handleScroll();
        this.isInitialized = true;
        
        console.log('Navbar component initialized');
    }

    // Liaison des événements
    bindEvents() {
        // Gestion du scroll avec débouncing
        window.addEventListener('scroll', this.debounce(() => {
            this.handleScroll();
        }, 16));

        // Gestion des clics sur les liens de navigation
        this.navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                const target = link.getAttribute('href');
                
                // Si c'est un lien vers une page externe (.html), laisser la navigation normale
                if (target && target.includes('.html')) {
                    this.setActiveLink(link);
                    this.closeMobileMenu();
                    // Ne pas empêcher la navigation par défaut pour les liens .html
                    return;
                }
                
                // Pour les ancres internes, utiliser le smooth scroll
                if (target && target.startsWith('#')) {
                    e.preventDefault();
                    this.setActiveLink(link);
                    this.smoothScrollTo(target);
                    this.closeMobileMenu();
                }
            });
        });

        // Gestion du menu mobile
        if (this.navToggle) {
            this.navToggle.addEventListener('click', () => {
                this.toggleMobileMenu();
            });
        }

        // Fermeture du menu mobile en cliquant à l'extérieur
        document.addEventListener('click', (e) => {
            if (this.navbar && !this.navbar.contains(e.target)) {
                this.closeMobileMenu();
            }
        });

        // Gestion du redimensionnement de la fenêtre
        window.addEventListener('resize', this.debounce(() => {
            this.handleResize();
        }, 250));
    }

    // Gestion du scroll
    handleScroll() {
        const scrollY = window.scrollY;
        const sections = document.querySelectorAll('section');
        
        // Ajout de la classe scrolled
        if (scrollY > 50) {
            this.navbar.classList.add('scrolled');
        } else {
            this.navbar.classList.remove('scrolled');
        }

        // Adaptation de l'apparence selon la section
        this.updateNavbarAppearance(sections, scrollY);
        
        // Mise à jour du lien actif
        this.updateActiveLink(sections, scrollY);
    }

    // Mise à jour de l'apparence de la navbar selon la section
    updateNavbarAppearance(sections, scrollY) {
        let isOnWhiteSection = false;
        let currentSection = null;
        
        // Trouver la section actuelle
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 100;
            const sectionHeight = section.offsetHeight;
            
            if (scrollY >= sectionTop && scrollY < sectionTop + sectionHeight) {
                currentSection = section;
            }
        });

        if (currentSection) {
            console.log('📍 Section actuelle:', currentSection.id, currentSection.className);
            
            // Vérifier l'attribut data-navbar-style en priorité
            const navbarStyle = currentSection.getAttribute('data-navbar-style');
            console.log('🏷️ Attribut data-navbar-style:', navbarStyle);
            
            if (navbarStyle === 'light') {
                // Section blanche = navbar doit être sombre pour contraste
                isOnWhiteSection = true;
                console.log('✨ Mode forcé: navbar sombre (pour section blanche)');
            } else if (navbarStyle === 'dark') {
                // Section sombre = navbar doit être claire
                isOnWhiteSection = false;
                console.log('🌙 Mode forcé: navbar claire (pour section sombre)');
            } else {
                // Détection automatique uniquement pour les sections sans attribut
                const computedStyle = window.getComputedStyle(currentSection);
                const backgroundColor = computedStyle.backgroundColor;
                console.log('🎨 Couleur de fond détectée:', backgroundColor);
                
                // Détection des sections avec fond clair
                if (currentSection.classList.contains('trading-pairs-section') || 
                    currentSection.classList.contains('faq-section') ||
                    currentSection.classList.contains('white-section') ||
                    backgroundColor === 'rgb(255, 255, 255)' ||
                    backgroundColor === 'white') {
                    isOnWhiteSection = true;
                    console.log('⚪ Section blanche détectée automatiquement');
                } else {
                    console.log('⚫ Section sombre détectée');
                }
            }
        }

        // Application des styles
        if (isOnWhiteSection) {
            this.navbar.classList.add('white-section');
            console.log('🔄 Navbar adaptée pour section blanche');
        } else {
            this.navbar.classList.remove('white-section');
            console.log('🔄 Navbar normale (mode sombre)');
        }
    }

    // Mise à jour du lien actif
    updateActiveLink(sections, scrollY) {
        let currentSection = '';
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 150;
            const sectionHeight = section.offsetHeight;
            
            if (scrollY >= sectionTop && scrollY < sectionTop + sectionHeight) {
                currentSection = section.id;
            }
        });

        this.navLinks.forEach(link => {
            const href = link.getAttribute('href').substring(1);
            if (href === currentSection) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }

    // Définition manuelle du lien actif
    setActiveLink(activeLink) {
        this.navLinks.forEach(link => link.classList.remove('active'));
        activeLink.classList.add('active');
    }

    // Gestion du menu mobile
    toggleMobileMenu() {
        if (this.navMenu && this.navToggle) {
            const isActive = this.navMenu.classList.toggle('active');
            this.navToggle.classList.toggle('active');
            
            // Empêcher le scroll du body quand le menu est ouvert
            if (isActive) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
            
            // Gérer l'accessibilité
            this.navToggle.setAttribute('aria-expanded', isActive);
            this.navMenu.setAttribute('aria-hidden', !isActive);
        }
    }

    closeMobileMenu() {
        if (this.navMenu && this.navToggle) {
            this.navMenu.classList.remove('active');
            this.navToggle.classList.remove('active');
            document.body.style.overflow = ''; // Restaurer le scroll
        }
    }

    // Gestion du redimensionnement
    handleResize() {
        // Fermer le menu mobile si la fenêtre devient assez large
        if (window.innerWidth > 767 && this.navMenu) {
            this.closeMobileMenu();
        }
        
        // Réinitialiser le scroll du body
        document.body.style.overflow = '';
    }

    // Scroll fluide vers une section
    smoothScrollTo(target) {
        const element = document.querySelector(target);
        if (element) {
            const offsetTop = element.offsetTop - 80; // Compensation pour la navbar fixe
            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });
        }
    }

    // Fonction de débouncing pour optimiser les performances
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func.apply(this, args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Méthode pour charger le composant depuis un fichier externe
    static async loadComponent(targetElement) {
        try {
            const response = await fetch('components/navbar.html');
            const html = await response.text();
            
            if (targetElement) {
                targetElement.innerHTML = html;
            } else {
                // Insérer au début du body si aucun élément cible spécifié
                document.body.insertAdjacentHTML('afterbegin', html);
            }
            
            // Initialiser le composant après chargement
            const navbar = new NavbarComponent();
            navbar.init();
            
            return navbar;
        } catch (error) {
            console.error('Erreur lors du chargement de la navbar:', error);
        }
    }

    // Méthode pour détruire le composant
    destroy() {
        // Retirer tous les event listeners
        // (implémentation basique, à améliorer selon les besoins)
        this.isInitialized = false;
        console.log('Navbar component destroyed');
    }
}

// Export pour utilisation modulaire
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NavbarComponent;
}

// Initialisation forcée avec plusieurs méthodes de détection
function initNavbar() {
    console.log('🚀 Tentative d\'initialisation de la navbar...');
    
    // Vérifier si la navbar existe dans le DOM
    if (document.getElementById('navbar')) {
        console.log('✅ Navbar trouvée, initialisation...');
        const navbar = new NavbarComponent();
        navbar.init();
        
        // Rendre accessible globalement
        window.NavbarComponent = navbar;
        console.log('✅ NavbarComponent initialisé et disponible globalement');
    } else {
        console.warn('❌ Navbar non trouvée dans le DOM');
    }
}

// Méthodes multiples d'initialisation pour s'assurer que ça marche
if (document.readyState === 'loading') {
    console.log('📋 DOM en cours de chargement, attente...');
    document.addEventListener('DOMContentLoaded', initNavbar);
} else {
    console.log('📋 DOM déjà chargé, initialisation immédiate');
    initNavbar();
}

// Backup d'initialisation après un délai
setTimeout(() => {
    if (!window.NavbarComponent) {
        console.log('🔄 Backup d\'initialisation après délai...');
        initNavbar();
    }
}, 500); 