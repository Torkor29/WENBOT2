/* ==============================================
   ANALYSEUR TRADING PRO - SCRIPTS PRINCIPAUX
   ============================================== */

// Configuration globale
const APP_CONFIG = {
    apiBaseUrl: window.location.origin,
    maxFileSize: 16 * 1024 * 1024, // 16MB
    allowedExtensions: ['.xlsx', '.xls'],
    polling: {
        interval: 1000, // 1 second
        maxRetries: 300 // 5 minutes max
    },
    animations: {
        duration: 300,
        easing: 'ease-in-out'
    }
};

// Utilitaires généraux
const Utils = {
    /**
     * Formate un nombre en euros
     */
    formatEuro(value) {
        return new Intl.NumberFormat('fr-FR', {
            style: 'currency',
            currency: 'EUR',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(value);
    },

    /**
     * Formate la taille d'un fichier
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    /**
     * Valide l'extension d'un fichier
     */
    isValidFileExtension(filename) {
        const extension = '.' + filename.split('.').pop().toLowerCase();
        return APP_CONFIG.allowedExtensions.includes(extension);
    },

    /**
     * Valide la taille d'un fichier
     */
    isValidFileSize(size) {
        return size <= APP_CONFIG.maxFileSize;
    },

    /**
     * Débounce une fonction
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Affiche une notification toast
     */
    showToast(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${this.getToastIcon(type)} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        // Ajouter le toast au container
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '1055';
            document.body.appendChild(toastContainer);
        }

        toastContainer.appendChild(toast);

        // Initialiser le toast Bootstrap
        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: duration
        });
        bsToast.show();

        // Supprimer le toast après fermeture
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },

    /**
     * Retourne l'icône appropriée pour le type de toast
     */
    getToastIcon(type) {
        const icons = {
            'success': 'check-circle',
            'danger': 'exclamation-triangle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle',
            'primary': 'info-circle'
        };
        return icons[type] || 'info-circle';
    },

    /**
     * Copie du texte dans le presse-papiers
     */
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showToast('Copié dans le presse-papiers', 'success', 2000);
        } catch (err) {
            console.error('Erreur lors de la copie:', err);
            this.showToast('Erreur lors de la copie', 'danger', 3000);
        }
    },

    /**
     * Anime un élément au scroll
     */
    animateOnScroll(elements, animation = 'fadeInUp') {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add(`animate-${animation}`);
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        elements.forEach(element => {
            element.style.opacity = '0';
            observer.observe(element);
        });
    },

    /**
     * Charge un script dynamiquement
     */
    loadScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    },

    /**
     * Effectue une requête API
     */
    async apiRequest(endpoint, options = {}) {
        const url = `${APP_CONFIG.apiBaseUrl}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }
};

// Gestionnaire de fichiers
const FileManager = {
    selectedFiles: [],

    /**
     * Initialise le gestionnaire de fichiers
     */
    init(dropzoneId, fileInputId, fileListId) {
        this.dropzone = document.getElementById(dropzoneId);
        this.fileInput = document.getElementById(fileInputId);
        this.fileList = document.getElementById(fileListId);

        if (this.dropzone && this.fileInput) {
            this.setupDropzone();
            this.setupFileInput();
        }
    },

    /**
     * Configure la zone de glisser-déposer
     */
    setupDropzone() {
        // Événements de drag & drop
        this.dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.dropzone.classList.add('dragover');
        });

        this.dropzone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            this.dropzone.classList.remove('dragover');
        });

        this.dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            this.dropzone.classList.remove('dragover');
            
            const files = Array.from(e.dataTransfer.files);
            this.handleFiles(files);
        });

        // Clic sur la zone
        this.dropzone.addEventListener('click', () => {
            this.fileInput.click();
        });
    },

    /**
     * Configure l'input de fichier
     */
    setupFileInput() {
        this.fileInput.addEventListener('change', (e) => {
            const files = Array.from(e.target.files);
            this.handleFiles(files);
        });
    },

    /**
     * Traite les fichiers sélectionnés
     */
    handleFiles(files) {
        // Filtrer les fichiers valides
        const validFiles = files.filter(file => {
            if (!Utils.isValidFileExtension(file.name)) {
                Utils.showToast(`Fichier non supporté: ${file.name}`, 'warning');
                return false;
            }
            
            if (!Utils.isValidFileSize(file.size)) {
                Utils.showToast(`Fichier trop volumineux: ${file.name}`, 'warning');
                return false;
            }
            
            return true;
        });

        if (validFiles.length === 0) {
            Utils.showToast('Aucun fichier valide sélectionné', 'danger');
            return;
        }

        this.selectedFiles = validFiles;
        this.updateFileInput();
        this.displayFiles();
        this.notifyFileChange();
    },

    /**
     * Met à jour l'input de fichier
     */
    updateFileInput() {
        const dt = new DataTransfer();
        this.selectedFiles.forEach(file => dt.items.add(file));
        this.fileInput.files = dt.files;
    },

    /**
     * Affiche la liste des fichiers
     */
    displayFiles() {
        if (!this.fileList) return;

        if (this.selectedFiles.length === 0) {
            this.fileList.style.display = 'none';
            return;
        }

        this.fileList.style.display = 'block';
        const fileItemsContainer = this.fileList.querySelector('#fileItems') || this.fileList;
        fileItemsContainer.innerHTML = '';

        this.selectedFiles.forEach((file, index) => {
            const fileItem = this.createFileItem(file, index);
            fileItemsContainer.appendChild(fileItem);
        });
    },

    /**
     * Crée un élément de fichier
     */
    createFileItem(file, index) {
        const fileSize = Utils.formatFileSize(file.size);
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item p-3 mb-2 d-flex justify-content-between align-items-center hover-lift';
        
        fileItem.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-file-excel text-success me-3 fa-lg"></i>
                <div>
                    <div class="fw-bold">${file.name}</div>
                    <div class="file-size text-muted">${fileSize}</div>
                </div>
            </div>
            <button type="button" class="btn btn-sm btn-outline-danger" onclick="FileManager.removeFile(${index})">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        return fileItem;
    },

    /**
     * Supprime un fichier
     */
    removeFile(index) {
        this.selectedFiles.splice(index, 1);
        this.updateFileInput();
        this.displayFiles();
        this.notifyFileChange();
        
        if (this.selectedFiles.length === 0) {
            Utils.showToast('Tous les fichiers ont été supprimés', 'info');
        }
    },

    /**
     * Notifie le changement de fichiers
     */
    notifyFileChange() {
        // Déclencher un événement personnalisé
        const event = new CustomEvent('filesChanged', {
            detail: { files: this.selectedFiles }
        });
        document.dispatchEvent(event);
    },

    /**
     * Réinitialise le gestionnaire
     */
    reset() {
        this.selectedFiles = [];
        if (this.fileInput) {
            this.fileInput.value = '';
        }
        this.displayFiles();
    }
};

// Gestionnaire de progression
const ProgressManager = {
    taskId: null,
    isPolling: false,
    pollCount: 0,

    /**
     * Démarre le suivi de progression
     */
    start(taskId) {
        this.taskId = taskId;
        this.isPolling = true;
        this.pollCount = 0;
        this.poll();
    },

    /**
     * Arrête le suivi de progression
     */
    stop() {
        this.isPolling = false;
        this.taskId = null;
        this.pollCount = 0;
    },

    /**
     * Effectue le polling de progression
     */
    async poll() {
        if (!this.isPolling || !this.taskId) return;

        if (this.pollCount >= APP_CONFIG.polling.maxRetries) {
            this.handleTimeout();
            return;
        }

        try {
            const data = await Utils.apiRequest(`/api/progress/${this.taskId}`);
            this.handleProgressUpdate(data);
            
            if (data.status === 'processing') {
                this.pollCount++;
                setTimeout(() => this.poll(), APP_CONFIG.polling.interval);
            } else {
                this.stop();
            }
        } catch (error) {
            console.error('Erreur lors du polling:', error);
            this.pollCount++;
            setTimeout(() => this.poll(), APP_CONFIG.polling.interval * 2); // Retry avec délai plus long
        }
    },

    /**
     * Gère la mise à jour de progression
     */
    handleProgressUpdate(data) {
        // Déclencher un événement personnalisé
        const event = new CustomEvent('progressUpdate', { detail: data });
        document.dispatchEvent(event);
    },

    /**
     * Gère le timeout
     */
    handleTimeout() {
        Utils.showToast('Le traitement prend plus de temps que prévu. Veuillez réessayer.', 'warning');
        this.stop();
    }
};

// Initialisation globale
document.addEventListener('DOMContentLoaded', function() {
    // Animer les éléments au scroll si ils existent
    const animateElements = document.querySelectorAll('.feature-card, .stat-card, .step-item');
    if (animateElements.length > 0) {
        Utils.animateOnScroll(animateElements);
    }

    // Activer les tooltips Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Activer les popovers Bootstrap
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Gérer les clics sur les liens externes
    document.addEventListener('click', function(e) {
        if (e.target.matches('a[href^="http"]')) {
            e.target.setAttribute('target', '_blank');
            e.target.setAttribute('rel', 'noopener noreferrer');
        }
    });

    // Smooth scroll pour les ancres
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Préloader pour les images
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));

    // Message de bienvenue en console
    console.log('%c🚀 Wenbot trading analyzer v2.0', 'color: #0d6efd; font-size: 16px; font-weight: bold;');
    console.log('%cApplication web développée pour l\'analyse de performances de trading.', 'color: #6c757d;');
});

// Exposer les utilitaires globalement
window.Utils = Utils;
window.FileManager = FileManager;
window.ProgressManager = ProgressManager; 