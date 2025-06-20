// Authentication Management System
class AuthManager {
    constructor() {
        this.currentUser = null;
        this.init();
    }

    init() {
        // Check if user is already logged in
        this.checkAuthState();
        this.setupEventListeners();
        this.setupJoinButtonRedirects();
    }

    setupEventListeners() {
        // Login form
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        // Register form
        const registerForm = document.getElementById('registerForm');
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => this.handleRegister(e));
        }

        // Trading application form
        const tradingForm = document.getElementById('tradingApplicationForm');
        if (tradingForm) {
            tradingForm.addEventListener('submit', (e) => this.handleTradingApplication(e));
        }
    }

    setupJoinButtonRedirects() {
        // Find all Join buttons and add click handlers
        const joinButtons = document.querySelectorAll('.btn-join');
        joinButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleJoinClick();
            });
        });
    }

    handleJoinClick() {
        if (this.isLoggedIn()) {
            // User is logged in, show trading application modal
            this.showTradingApplicationModal();
        } else {
            // User is not logged in, redirect to auth page
            window.location.href = 'auth.html';
        }
    }

    async handleLogin(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const email = formData.get('email');
        const password = formData.get('password');
        const remember = formData.get('remember');

        try {
            // Simulate API call - replace with actual authentication
            const success = await this.simulateLogin(email, password);
            
            if (success) {
                const userData = {
                    id: Date.now(),
                    email: email,
                    firstname: email.split('@')[0],
                    lastname: 'User',
                    loginTime: new Date().toISOString()
                };

                // Store user data
                if (remember) {
                    localStorage.setItem('wenbot_user', JSON.stringify(userData));
                } else {
                    sessionStorage.setItem('wenbot_user', JSON.stringify(userData));
                }

                this.currentUser = userData;
                this.showSuccessMessage('Login successful! Redirecting...');
                
                // Redirect to home page after 1 second
                setTimeout(() => {
                    window.location.href = 'index.html';
                }, 1000);
            } else {
                this.showErrorMessage('Invalid email or password. Please try again.');
            }
        } catch (error) {
            this.showErrorMessage('Login failed. Please try again.');
            console.error('Login error:', error);
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const firstname = formData.get('firstname');
        const lastname = formData.get('lastname');
        const email = formData.get('email');
        const password = formData.get('password');
        const confirmPassword = formData.get('confirmPassword');
        const terms = formData.get('terms');

        // Validation
        if (password !== confirmPassword) {
            this.showErrorMessage('Passwords do not match.');
            return;
        }

        if (!terms) {
            this.showErrorMessage('You must agree to the Terms of Service.');
            return;
        }

        if (password.length < 6) {
            this.showErrorMessage('Password must be at least 6 characters long.');
            return;
        }

        try {
            // Simulate API call - replace with actual registration
            const success = await this.simulateRegister(email, password, firstname, lastname);
            
            if (success) {
                const userData = {
                    id: Date.now(),
                    email: email,
                    firstname: firstname,
                    lastname: lastname,
                    loginTime: new Date().toISOString()
                };

                // Store user data
                localStorage.setItem('wenbot_user', JSON.stringify(userData));
                this.currentUser = userData;
                
                this.showSuccessMessage('Registration successful! Welcome to WenBot!');
                
                // Redirect to home page after 1 second
                setTimeout(() => {
                    window.location.href = 'index.html';
                }, 1000);
            } else {
                this.showErrorMessage('Registration failed. Email may already exist.');
            }
        } catch (error) {
            this.showErrorMessage('Registration failed. Please try again.');
            console.error('Registration error:', error);
        }
    }

    async handleTradingApplication(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const applicationData = {
            firstName: formData.get('firstName'),
            lastName: formData.get('lastName'),
            email: formData.get('email'),
            experience: formData.get('experience'),
            initialDeposit: formData.get('initialDeposit'),
            riskAcknowledgment: formData.get('riskAcknowledgment'),
            submissionTime: new Date().toISOString()
        };

        try {
            // Simulate API call - replace with actual submission
            const success = await this.submitTradingApplication(applicationData);
            
            if (success) {
                // Store application data
                const existingApplications = JSON.parse(localStorage.getItem('wenbot_applications') || '[]');
                existingApplications.push(applicationData);
                localStorage.setItem('wenbot_applications', JSON.stringify(existingApplications));

                this.showSuccessMessage('Application submitted successfully! We will contact you soon.');
                this.closeTradingApplicationModal();
                
                // Optional: Redirect to a thank you page
                setTimeout(() => {
                    this.showApplicationSuccessModal();
                }, 1000);
            } else {
                this.showErrorMessage('Failed to submit application. Please try again.');
            }
        } catch (error) {
            this.showErrorMessage('Submission failed. Please try again.');
            console.error('Application submission error:', error);
        }
    }

    showTradingApplicationModal() {
        // Create modal if it doesn't exist
        if (!document.getElementById('tradingApplicationModal')) {
            this.createTradingApplicationModal();
        }
        
        const modal = document.getElementById('tradingApplicationModal');
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    createTradingApplicationModal() {
        const modalHTML = `
            <div id="tradingApplicationModal" class="trading-modal">
                <div class="trading-modal-content">
                    <div class="trading-modal-header">
                        <h2>Trading Application</h2>
                        <span class="close-modal" onclick="authManager.closeTradingApplicationModal()">&times;</span>
                    </div>
                    
                    <form id="tradingApplicationForm" class="trading-form">
                        <div class="form-row">
                            <div class="form-group">
                                <label for="firstName">First Name *</label>
                                <input type="text" id="firstName" name="firstName" required>
                            </div>
                            <div class="form-group">
                                <label for="lastName">Last Name *</label>
                                <input type="text" id="lastName" name="lastName" required>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label for="email">Email Address *</label>
                            <input type="email" id="email" name="email" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="experience">Online Investment Experience *</label>
                            <select id="experience" name="experience" required>
                                <option value="">Select your experience level</option>
                                <option value="beginner">Beginner (0-1 years)</option>
                                <option value="intermediate">Intermediate (1-3 years)</option>
                                <option value="advanced">Advanced (3-5 years)</option>
                                <option value="expert">Expert (5+ years)</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="initialDeposit">Intended Initial Deposit Amount (USD) *</label>
                            <select id="initialDeposit" name="initialDeposit" required>
                                <option value="">Select deposit range</option>
                                <option value="250-500">$250 - $500</option>
                                <option value="500-1000">$500 - $1,000</option>
                                <option value="1000-5000">$1,000 - $5,000</option>
                                <option value="5000-10000">$5,000 - $10,000</option>
                                <option value="10000+">$10,000+</option>
                            </select>
                        </div>
                        
                        <div class="risk-warning">
                            <h3>⚠️ Risk Warning</h3>
                            <p><strong>Trading involves substantial risk and may result in the loss of your entire investment.</strong></p>
                            <ul>
                                <li>Past performance does not guarantee future results</li>
                                <li>No trading system or algorithm can predict market movements with certainty</li>
                                <li>You should never invest more than you can afford to lose</li>
                                <li>Please ensure you fully understand the risks involved before proceeding</li>
                            </ul>
                        </div>
                        
                        <div class="form-group">
                            <label class="checkbox-container">
                                <input type="checkbox" name="riskAcknowledgment" required>
                                <span class="checkmark"></span>
                                I acknowledge and understand the risks associated with trading and confirm that I am investing at my own discretion *
                            </label>
                        </div>
                        
                        <button type="submit" class="btn-submit">Submit Application</button>
                    </form>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Setup event listeners for the new modal
        const form = document.getElementById('tradingApplicationForm');
        if (form) {
            form.addEventListener('submit', (e) => this.handleTradingApplication(e));
        }
        
        // Pre-fill user data if available
        if (this.currentUser) {
            document.getElementById('firstName').value = this.currentUser.firstname || '';
            document.getElementById('lastName').value = this.currentUser.lastname || '';
            document.getElementById('email').value = this.currentUser.email || '';
        }
    }

    closeTradingApplicationModal() {
        const modal = document.getElementById('tradingApplicationModal');
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    }

    showApplicationSuccessModal() {
        const successHTML = `
            <div id="successModal" class="trading-modal">
                <div class="trading-modal-content success-content">
                    <div class="success-icon">✓</div>
                    <h2>Application Submitted Successfully!</h2>
                    <p>Thank you for your interest in WenBot. Our team will review your application and contact you within 24-48 hours.</p>
                    <p>You will receive a confirmation email shortly with next steps.</p>
                    <button class="btn-submit" onclick="authManager.closeSuccessModal()">Continue</button>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', successHTML);
        const modal = document.getElementById('successModal');
        modal.style.display = 'flex';
    }

    closeSuccessModal() {
        const modal = document.getElementById('successModal');
        if (modal) {
            modal.remove();
        }
    }

    checkAuthState() {
        // Check localStorage first, then sessionStorage
        const userData = localStorage.getItem('wenbot_user') || sessionStorage.getItem('wenbot_user');
        
        if (userData) {
            this.currentUser = JSON.parse(userData);
            this.updateNavigation();
        }
    }

    updateNavigation() {
        const authButtons = document.getElementById('auth-buttons');
        const userDashboard = document.querySelector('.user-dashboard');
        
        if (this.isLoggedIn() && authButtons) {
            // Hide auth buttons, show user info
            authButtons.style.display = 'none';
            
            // Create or show user dashboard
            if (!userDashboard) {
                this.createUserDashboard(authButtons.parentNode);
            } else {
                userDashboard.style.display = 'flex';
            }
        }
    }

    createUserDashboard(parent) {
        const userInitials = this.getUserInitials();
        const userName = `${this.currentUser.firstname} ${this.currentUser.lastname}`;
        
        const dashboardHTML = `
            <div class="user-dashboard">
                <div class="user-info-nav">
                    <div class="user-avatar-nav">${userInitials}</div>
                    <span class="user-name-nav">${userName}</span>
                </div>
                <button class="btn-logout" onclick="authManager.logout()">Logout</button>
            </div>
        `;
        
        parent.insertAdjacentHTML('beforeend', dashboardHTML);
    }

    getUserInitials() {
        if (!this.currentUser) return '?';
        const first = this.currentUser.firstname?.charAt(0)?.toUpperCase() || '';
        const last = this.currentUser.lastname?.charAt(0)?.toUpperCase() || '';
        return first + last;
    }

    logout() {
        // Clear all stored data
        localStorage.removeItem('wenbot_user');
        sessionStorage.removeItem('wenbot_user');
        this.currentUser = null;
        
        // Redirect to home page
        window.location.href = 'index.html';
    }

    isLoggedIn() {
        return this.currentUser !== null;
    }

    // Simulation methods - replace with actual API calls
    async simulateLogin(email, password) {
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Simple validation - in real app, this would be server-side
        return email.includes('@') && password.length >= 6;
    }

    async simulateRegister(email, password, firstname, lastname) {
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Check if email already exists (simulate)
        const existingUser = localStorage.getItem(`user_${email}`);
        if (existingUser) {
            return false;
        }
        
        // Store user (simulate database)
        localStorage.setItem(`user_${email}`, JSON.stringify({
            email, password, firstname, lastname, created: Date.now()
        }));
        
        return true;
    }

    async submitTradingApplication(data) {
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Simulate successful submission
        return true;
    }

    showSuccessMessage(message) {
        this.showMessage(message, 'success');
    }

    showErrorMessage(message) {
        this.showMessage(message, 'error');
    }

    showMessage(message, type) {
        // Remove existing messages
        const existingMessages = document.querySelectorAll('.auth-message');
        existingMessages.forEach(msg => msg.remove());
        
        const messageHTML = `
            <div class="auth-message ${type}">
                ${message}
            </div>
        `;
        
        const form = document.querySelector('.auth-form');
        if (form) {
            form.insertAdjacentHTML('afterbegin', messageHTML);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                const message = document.querySelector('.auth-message');
                if (message) message.remove();
            }, 5000);
        }
    }
}

// Authentication form switching functions
function showLogin() {
    document.getElementById('login-form').classList.remove('hidden');
    document.getElementById('register-form').classList.add('hidden');
}

function showRegister() {
    document.getElementById('login-form').classList.add('hidden');
    document.getElementById('register-form').classList.remove('hidden');
}

// Initialize authentication manager when DOM is loaded
let authManager;
document.addEventListener('DOMContentLoaded', () => {
    authManager = new AuthManager();
});

// Export for global access
window.authManager = authManager; 