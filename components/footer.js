// ================================
// FOOTER COMPONENT JAVASCRIPT
// ================================

class FooterComponent {
    constructor() {
        this.init();
    }

    init() {
        // Attendre que le DOM soit prêt avant d'initialiser les événements
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.setupEventListeners();
            });
        } else {
            this.setupEventListeners();
        }
    }

    // Configurer tous les événements du footer
    setupEventListeners() {
        this.setupNewsletterForm();
        this.setupSocialLinks();
        this.setupLegalLinks();
    }

    // Créer un élément DOM à partir d'une chaîne HTML
    createElementFromHTML(htmlString) {
        const div = document.createElement('div');
        div.innerHTML = htmlString.trim();
        return div.firstChild;
    }

    // Configuration du formulaire de newsletter
    setupNewsletterForm() {
        const newsletterForm = document.querySelector('.newsletter-form');
        if (!newsletterForm) return;

        newsletterForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleNewsletterSubmission(e);
        });

        // Animation sur focus de l'input
        const newsletterInput = document.querySelector('.newsletter-input');
        if (newsletterInput) {
            newsletterInput.addEventListener('focus', () => {
                newsletterInput.parentElement.classList.add('focused');
            });

            newsletterInput.addEventListener('blur', () => {
                newsletterInput.parentElement.classList.remove('focused');
            });
        }
    }

    // Gestion de la soumission de la newsletter
    async handleNewsletterSubmission(event) {
        const form = event.target;
        const emailInput = form.querySelector('.newsletter-input');
        const submitBtn = form.querySelector('.newsletter-btn');
        const email = emailInput.value.trim();

        // Validation de l'email
        if (!this.isValidEmail(email)) {
            this.showNotification('Veuillez entrer une adresse email valide.', 'error');
            emailInput.focus();
            return;
        }

        // Animation de chargement
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Inscription...';
        submitBtn.disabled = true;

        try {
            // Simulation d'une requête API (remplacer par votre endpoint)
            await this.simulateAPICall();
            
            // Succès
            this.showNotification('Merci ! Vous êtes maintenant inscrit à notre newsletter.', 'success');
            emailInput.value = '';
            
        } catch (error) {
            this.showNotification('Une erreur est survenue. Veuillez réessayer.', 'error');
        } finally {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    }

    // Validation d'email
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // Simulation d'appel API
    simulateAPICall() {
        return new Promise((resolve) => {
            setTimeout(resolve, 1500);
        });
    }

    // Configuration des liens sociaux
    setupSocialLinks() {
        const socialLinks = document.querySelectorAll('.social-link');
        
        socialLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                
                const platform = this.getSocialPlatform(link);
                this.trackSocialClick(platform);
                
                // Animation de clic
                link.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    link.style.transform = '';
                }, 150);
                
                // Ouvrir dans un nouvel onglet (remplacer # par les vrais liens)
                if (link.href !== '#') {
                    window.open(link.href, '_blank', 'noopener,noreferrer');
                }
            });
        });
    }

    // Identifier la plateforme sociale
    getSocialPlatform(link) {
        const aria = link.getAttribute('aria-label');
        return aria ? aria.toLowerCase() : 'unknown';
    }

    // Tracking des clics sociaux
    trackSocialClick(platform) {
        // Analytics ou tracking (remplacer par votre solution)
        console.log(`Clic sur réseau social: ${platform}`);
    }

    // Configuration des liens légaux
    setupLegalLinks() {
        const legalLinks = document.querySelectorAll('.legal-link');
        
        legalLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                
                const linkText = link.textContent.trim();
                this.handleLegalLinkClick(linkText);
            });
        });
    }

    // Gestion des clics sur les liens légaux
    handleLegalLinkClick(linkText) {
        // Mapping des liens vers les pages correspondantes
        const legalPages = {
            'Mentions légales': '/legal/mentions-legales.html',
            'Politique de confidentialité': '/legal/confidentialite.html',
            'Conditions d\'utilisation': '/legal/conditions.html',
            'Politique de cookies': '/legal/cookies.html',
            'RGPD': '/legal/rgpd.html'
        };

        const targetPage = legalPages[linkText];
        
        if (targetPage) {
            // Vérifier si la page existe, sinon afficher une modal
            this.checkPageExists(targetPage)
                .then(exists => {
                    if (exists) {
                        window.location.href = targetPage;
                    } else {
                        this.showLegalModal(linkText);
                    }
                });
        } else {
            this.showLegalModal(linkText);
        }
    }

    // Vérifier si une page existe
    async checkPageExists(url) {
        try {
            const response = await fetch(url, { method: 'HEAD' });
            return response.ok;
        } catch {
            return false;
        }
    }

    // Afficher une modal pour les pages légales
    showLegalModal(title) {
        const modal = this.createLegalModal(title);
        document.body.appendChild(modal);
        
        // Animation d'apparition
        setTimeout(() => modal.classList.add('show'), 10);
        
        // Fermeture automatique après 5 secondes
        setTimeout(() => this.closeLegalModal(modal), 5000);
    }

    // Créer la modal légale
    createLegalModal(title) {
        const modal = document.createElement('div');
        modal.className = 'legal-modal';
        modal.innerHTML = `
            <div class="legal-modal-content">
                <div class="legal-modal-header">
                    <h3>${title}</h3>
                    <button class="legal-modal-close">&times;</button>
                </div>
                <div class="legal-modal-body">
                    <p>Cette page est en cours de développement.</p>
                    <p>Pour plus d'informations, contactez-nous à <a href="mailto:contact@wenbot.com">contact@wenbot.com</a></p>
                </div>
            </div>
        `;

        // Événement de fermeture
        modal.addEventListener('click', (e) => {
            if (e.target === modal || e.target.classList.contains('legal-modal-close')) {
                this.closeLegalModal(modal);
            }
        });

        return modal;
    }

    // Fermer la modal légale
    closeLegalModal(modal) {
        modal.classList.add('hide');
        setTimeout(() => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
        }, 300);
    }

    // Système de notifications
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `footer-notification ${type}`;
        notification.textContent = message;
        
        // Styles de base pour la notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '12px 20px',
            borderRadius: '8px',
            color: 'white',
            fontWeight: '500',
            zIndex: '10000',
            transform: 'translateX(100%)',
            transition: 'transform 0.3s ease',
            maxWidth: '300px'
        });

        // Couleurs selon le type
        const colors = {
            success: '#26a69a',
            error: '#ef5350',
            info: '#2962ff'
        };
        notification.style.background = colors[type] || colors.info;

        document.body.appendChild(notification);

        // Animation d'apparition
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 10);

        // Fermeture automatique
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 4000);
    }
}

// Styles CSS pour les modals et notifications (injectés dynamiquement)
const footerStyles = `
    .legal-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .legal-modal.show {
        opacity: 1;
    }

    .legal-modal.hide {
        opacity: 0;
    }

    .legal-modal-content {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: var(--spacing-xl);
        max-width: 500px;
        width: 90%;
        transform: scale(0.9);
        transition: transform 0.3s ease;
    }

    .legal-modal.show .legal-modal-content {
        transform: scale(1);
    }

    .legal-modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--spacing-lg);
        padding-bottom: var(--spacing-md);
        border-bottom: 1px solid var(--border-color);
    }

    .legal-modal-header h3 {
        color: var(--text-primary);
        margin: 0;
    }

    .legal-modal-close {
        background: none;
        border: none;
        color: var(--text-secondary);
        font-size: 24px;
        cursor: pointer;
        padding: 0;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .legal-modal-close:hover {
        color: var(--text-primary);
    }

    .legal-modal-body {
        color: var(--text-secondary);
        line-height: 1.6;
    }

    .legal-modal-body a {
        color: var(--color-blue);
        text-decoration: none;
    }

    .legal-modal-body a:hover {
        text-decoration: underline;
    }
`;

// Injecter les styles
const styleSheet = document.createElement('style');
styleSheet.textContent = footerStyles;
document.head.appendChild(styleSheet);

// Initialiser le composant footer quand le DOM est prêt
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new FooterComponent();
    });
} else {
    new FooterComponent();
} 