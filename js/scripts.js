/* ================================
   GLOBAL VARIABLES & UTILITY FUNCTIONS
   ================================ */

// Debounce function for performance optimization
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Smooth scrolling utility
function smoothScrollTo(target) {
    const element = document.querySelector(target);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

/* ================================
   HERO CHART MODULE
   ================================ */

const HeroChartModule = {
    init() {
        this.canvas = document.getElementById('heroChart');
        if (!this.canvas) return;

        this.ctx = this.canvas.getContext('2d');
        this.setupCanvas();
        this.generateChartData();
        this.startAnimation();
    },

    setupCanvas() {
        this.canvas.width = 700;  // Réduction de la largeur
        this.canvas.height = 260; // Réduction de la hauteur
        
        // Ajustement des marges pour un meilleur affichage
        this.padding = {
            left: 70,    // Réduction de la marge gauche
            right: 30,   // Réduction de la marge droite
            top: 20,     
            bottom: 50   // Réduction de la marge basse
        };
        
        this.chartWidth = this.canvas.width - (this.padding.left + this.padding.right);
        this.chartHeight = this.canvas.height - (this.padding.top + this.padding.bottom);
    },

    generateChartData() {
        // Points de données pour une courbe croissante progressive jusqu'à 170%
        this.dataPoints = [0, 25, 45, 75, 95, 125, 150, 162, 170];
        this.labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'];
        
        this.maxValue = 175; // Échelle max ajustée
        this.minValue = 0;
        this.range = this.maxValue - this.minValue;
    },

    startAnimation() {
        this.animationProgress = 0;
        this.startTime = Date.now();
        this.animationDuration = 6000; // 6 secondes pour une animation plus lente
        this.animate();
    },

    animate() {
        const currentTime = Date.now();
        const elapsed = currentTime - this.startTime;
        
        // Fonction d'easing personnalisée pour une fin plus douce
        const easeOutQuart = (x) => {
            const t = x - 1;
            return 1 - (t * t * t * t);
        };
        
        this.animationProgress = Math.min(1, elapsed / this.animationDuration);
        // Application de l'easing seulement sur la dernière partie de l'animation
        if (this.animationProgress > 0.8) {
            const finalProgress = (this.animationProgress - 0.8) / 0.2;
            this.animationProgress = 0.8 + (0.2 * easeOutQuart(finalProgress));
        }

        this.clear();
        this.drawGrid();
        this.drawAxis();
        this.drawChart();

        if (elapsed < this.animationDuration) {
            requestAnimationFrame(() => this.animate());
        }
    },

    drawGrid() {
        const ctx = this.ctx;
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
        ctx.lineWidth = 1;

        // Lignes horizontales principales
        const ySteps = [0, 45, 90, 135, 170];
        ySteps.forEach(value => {
            const y = this.padding.top + (1 - (value / this.maxValue)) * this.chartHeight;
            ctx.beginPath();
            ctx.moveTo(this.padding.left, y);
            ctx.lineTo(this.padding.left + this.chartWidth, y);
            ctx.stroke();
        });
    },

    drawAxis() {
        const ctx = this.ctx;
        
        // Style des labels optimisé
        ctx.font = '10px Inter';
        ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';

        // Y-axis labels avec valeurs spécifiques
        const ySteps = [0, 45, 90, 135, 170];
        ySteps.forEach(value => {
            const y = this.padding.top + (1 - (value / this.maxValue)) * this.chartHeight;
            ctx.textAlign = 'right';
            ctx.textBaseline = 'middle';
            ctx.fillText(value + '%', this.padding.left - 8, y);
        });

        // X-axis labels avec rotation pour économiser l'espace
        ctx.textAlign = 'right';
        ctx.textBaseline = 'middle';
        this.labels.forEach((label, index) => {
            const x = this.padding.left + (index * (this.chartWidth / (this.labels.length - 1)));
            ctx.save();
            ctx.translate(x, this.canvas.height - this.padding.bottom + 12);
            ctx.rotate(-Math.PI / 6); // Rotation de 30 degrés
            ctx.fillText(label, 0, 0);
            ctx.restore();
        });
    },

    drawChart() {
        const ctx = this.ctx;
        ctx.save();
        
        // Clip the chart area
        ctx.beginPath();
        ctx.rect(this.padding.left, this.padding.top, this.chartWidth, this.chartHeight);
        ctx.clip();

        // Draw the line
        ctx.beginPath();
        ctx.lineWidth = 2;
        ctx.strokeStyle = '#2962ff';

        // Create gradient fill
        const gradient = ctx.createLinearGradient(0, this.padding.top, 0, this.padding.top + this.chartHeight);
        gradient.addColorStop(0, 'rgba(41, 98, 255, 0.2)');
        gradient.addColorStop(1, 'rgba(41, 98, 255, 0)');

        // Calculate points with smooth progression
        const currentPoints = this.dataPoints.map((value, index) => {
            const x = this.padding.left + (index * (this.chartWidth / (this.labels.length - 1)));
            let progress = this.animationProgress;
            
            // Ralentissement spécial pour les deux derniers points
            if (index >= this.dataPoints.length - 2) {
                const finalPart = Math.max(0, (progress - 0.8) / 0.2);
                progress = Math.min(progress, 0.8 + (0.2 * Math.pow(finalPart, 1.5)));
            }
            
            const animatedValue = value * progress;
            const y = this.padding.top + (1 - (animatedValue / this.maxValue)) * this.chartHeight;
            return { x, y };
        });

        // Draw the curve with tension control
        ctx.beginPath();
        ctx.moveTo(currentPoints[0].x, currentPoints[0].y);
        
        for (let i = 1; i < currentPoints.length; i++) {
            const prev = currentPoints[i - 1];
            const current = currentPoints[i];
            
            // Amélioration des points de contrôle pour une courbe plus fluide
            const tension = 0.3;
            const cp1x = prev.x + (current.x - prev.x) * tension;
            const cp1y = prev.y;
            const cp2x = prev.x + (current.x - prev.x) * (1 - tension);
            const cp2y = current.y;
            
            ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, current.x, current.y);
        }

        // Stroke the line
        ctx.stroke();

        // Fill the area under the curve
        ctx.lineTo(currentPoints[currentPoints.length - 1].x, this.padding.top + this.chartHeight);
        ctx.lineTo(currentPoints[0].x, this.padding.top + this.chartHeight);
        ctx.fillStyle = gradient;
        ctx.fill();

        ctx.restore();
    },

    clear() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
};

/* ================================
   TRADING PAIRS CAROUSEL MODULE
   ================================ */

const TradingPairsModule = {
    init() {
        this.track = document.getElementById('pairs-track');
        if (!this.track) return;

        this.setupCarousel();
        this.startPriceUpdates();
    },

    setupCarousel() {
        // Clone cards for infinite scroll effect
        const cards = this.track.children;
        const cardArray = Array.from(cards);
        
        // Clone all cards and append them
        cardArray.forEach(card => {
            const clone = card.cloneNode(true);
            this.track.appendChild(clone);
        });
    },

    startPriceUpdates() {
        // Update prices every 3 seconds to simulate real-time data
        setInterval(() => {
            this.updatePrices();
        }, 3000);
    },

    updatePrices() {
        const priceElements = document.querySelectorAll('.pair-price');
        const changeElements = document.querySelectorAll('.pair-change');

        priceElements.forEach((priceEl, index) => {
            const changeEl = changeElements[index];
            if (!changeEl) return;

            // Generate realistic price movement
            const changePercent = (Math.random() - 0.5) * 0.5; // -0.25% to +0.25%
            const currentPrice = parseFloat(priceEl.textContent.replace(/,/g, ''));
            const newPrice = currentPrice * (1 + (changePercent / 100));

            // Format price based on magnitude
            let formattedPrice;
            if (newPrice > 1000) {
                formattedPrice = Math.round(newPrice).toLocaleString();
            } else if (newPrice > 10) {
                formattedPrice = newPrice.toFixed(2);
            } else {
                formattedPrice = newPrice.toFixed(4);
            }

            // Update price with animation
            priceEl.style.transform = 'scale(1.05)';
            priceEl.style.color = changePercent > 0 ? '#26a69a' : '#ef5350';
            
            setTimeout(() => {
                priceEl.textContent = formattedPrice;
                priceEl.style.transform = 'scale(1)';
                priceEl.style.color = '';
            }, 150);

            // Update change percentage
            const totalChange = parseFloat(changeEl.textContent.replace(/[+%]/g, '')) + changePercent;
            const formattedChange = (totalChange >= 0 ? '+' : '') + totalChange.toFixed(2) + '%';
            
            changeEl.textContent = formattedChange;
            changeEl.className = 'pair-change ' + (totalChange > 0 ? 'positive' : totalChange < 0 ? 'negative' : 'neutral');
        });
    }
};

/* ================================
   AUTHENTICATION INTEGRATION
   ================================ */

// Initialize authentication system for Join buttons
function initializeAuthSystem() {
    // This will be handled by auth.js when loaded
    // Adding this placeholder to ensure compatibility
    console.log('Authentication system initialization placeholder');
}

/* ================================
   MAIN INITIALIZATION
   ================================ */

/* ================================
   SMOOTH SCROLL NAVIGATION
   ================================ */

const SmoothScrollModule = {
    init() {
        // Smooth scroll pour les liens de navigation
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }
};

document.addEventListener('DOMContentLoaded', function() {
    // Initialize existing modules
    HeroChartModule.init();
    TradingPairsModule.init();
    SmoothScrollModule.init();
    
    // Initialize authentication system
    initializeAuthSystem();
    
    // Additional initialization can be added here
    console.log('WenBot application initialized successfully');
});

// Handle window resize
window.addEventListener('resize', debounce(() => {
    // Reinitialize chart with new dimensions
    if (HeroChartModule.canvas) {
        HeroChartModule.setupCanvas();
        HeroChartModule.animate();
    }
}, 250)); 