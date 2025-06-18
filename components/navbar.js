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
                e.preventDefault();
                const target = link.getAttribute('href');
                this.setActiveLink(link);
                this.smoothScrollTo(target);
                this.closeMobileMenu();
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
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 100;
            const sectionHeight = section.offsetHeight;
            
            if (scrollY >= sectionTop && scrollY < sectionTop + sectionHeight) {
                // Vérifier si la section a un fond blanc/clair
                const computedStyle = window.getComputedStyle(section);
                const backgroundColor = computedStyle.backgroundColor;
                
                // Détection des sections avec fond clair
                if (section.classList.contains('trading-pairs-section') || 
                    section.classList.contains('faq-section') ||
                    section.classList.contains('white-section') ||
                    backgroundColor === 'rgb(255, 255, 255)' ||
                    backgroundColor === 'white') {
                    isOnWhiteSection = true;
                }
            }
        });

        // Application des styles selon le type de section
        if (isOnWhiteSection) {
            this.navbar.classList.add('white-section');
        } else {
            this.navbar.classList.remove('white-section');
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
            this.navMenu.classList.toggle('active');
            this.navToggle.classList.toggle('active');
        }
    }

    closeMobileMenu() {
        if (this.navMenu && this.navToggle) {
            this.navMenu.classList.remove('active');
            this.navToggle.classList.remove('active');
        }
    }

    // Gestion du redimensionnement
    handleResize() {
        // Fermer le menu mobile si on passe en desktop
        if (window.innerWidth > 768) {
            this.closeMobileMenu();
        }
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

// Initialisation automatique si le DOM est prêt
document.addEventListener('DOMContentLoaded', () => {
    // Vérifier si la navbar existe déjà dans le DOM
    if (document.getElementById('navbar')) {
        const navbar = new NavbarComponent();
        navbar.init();
        
        // Rendre accessible globalement
        window.NavbarComponent = navbar;
    }
}); 