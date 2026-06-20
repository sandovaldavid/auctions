/**
 * Error Pages JavaScript
 * Handles animations and interactive elements for error pages
 */

class ErrorPageManager {
	constructor() {
		this.init();
	}

	init() {
		this.setupFloatingElements();
		this.setupParticleEffect();
		this.setupButtonAnimations();
		this.setupThemeSupport();
	}

	/**
	 * Setup floating elements animation
	 */
	setupFloatingElements() {
		const floatingElements = document.querySelectorAll('.floating-element');
		if (floatingElements.length === 0) return;

		floatingElements.forEach((element, index) => {
			// Set random animation delay for more natural movement
			const delay = Math.random() * 2;
			element.style.animationDelay = `${delay}s`;

			// Add random rotation to floating elements
			const rotation = Math.random() * 360;
			element.style.transform = `rotate(${rotation}deg)`;
		});
	}

	/**
	 * Create particle effect in the background
	 */
	setupParticleEffect() {
		const errorContainer = document.querySelector('.error-container');
		if (!errorContainer) return;

		// Create particles every 2 seconds
		setInterval(() => {
			this.createParticle(errorContainer);
		}, 2000);

		// Create initial particles
		for (let i = 0; i < 3; i++) {
			setTimeout(() => {
				this.createParticle(errorContainer);
			}, i * 500);
		}
	}

	/**
	 * Create a single particle
	 */
	createParticle(container) {
		const particle = document.createElement('div');
		particle.className = 'particle';

		// Random properties
		const size = Math.random() * 4 + 2; // 2-6px
		const startX = Math.random() * 100;
		const duration = Math.random() * 4 + 6; // 6-10 seconds
		const color = this.getRandomParticleColor();

		// Apply styles
		particle.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            background: ${color};
            border-radius: 50%;
            left: ${startX}%;
            top: 100%;
            opacity: 0.3;
            animation: particleFloat ${duration}s linear infinite;
            pointer-events: none;
        `;

		container.appendChild(particle);

		// Remove particle after animation
		setTimeout(() => {
			if (particle.parentNode) {
				particle.parentNode.removeChild(particle);
			}
		}, duration * 1000);
	}

	/**
	 * Get random particle color based on error type
	 */
	getRandomParticleColor() {
		const colors = [
			'#667eea',
			'#764ba2',
			'#f093fb',
			'#f5576c',
			'#9b59b6',
			'#8e44ad',
			'#7d3c98',
			'#6c3483',
			'#f39c12',
			'#e67e22',
			'#d35400',
			'#c0392b',
			'#e74c3c',
			'#c0392b',
			'#f39c12',
			'#e67e22',
		];
		return colors[Math.floor(Math.random() * colors.length)];
	}

	/**
	 * Setup button hover animations
	 */
	setupButtonAnimations() {
		const buttons = document.querySelectorAll(
			'.btn-custom, .btn-outline-custom'
		);

		buttons.forEach((button) => {
			button.addEventListener('mouseenter', () => {
				button.style.transform = 'translateY(-2px) scale(1.05)';
			});

			button.addEventListener('mouseleave', () => {
				button.style.transform = 'translateY(0) scale(1)';
			});

			button.addEventListener('click', (e) => {
				// Add ripple effect
				this.createRippleEffect(e, button);
			});
		});
	}

	/**
	 * Create ripple effect on button click
	 */
	createRippleEffect(event, button) {
		const ripple = document.createElement('span');
		const rect = button.getBoundingClientRect();
		const size = Math.max(rect.width, rect.height);
		const x = event.clientX - rect.left - size / 2;
		const y = event.clientY - rect.top - size / 2;

		ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
        `;

		button.style.position = 'relative';
		button.style.overflow = 'hidden';
		button.appendChild(ripple);

		setTimeout(() => {
			if (ripple.parentNode) {
				ripple.parentNode.removeChild(ripple);
			}
		}, 600);
	}

	/**
	 * Setup theme support for error pages
	 */
	setupThemeSupport() {
		// Apply theme class to body if dark theme is active
		const savedTheme = localStorage.getItem('theme');
		if (savedTheme === 'dark') {
			document.body.setAttribute('data-theme', 'dark');
		}
	}

	/**
	 * Add error-specific animations based on error type
	 */
	addErrorSpecificAnimations() {
		const errorCode = document.querySelector('.error-code');
		if (!errorCode) return;

		const code = errorCode.textContent.trim();

		switch (code) {
			case '404':
				this.add404Animations();
				break;
			case '400':
				this.add400Animations();
				break;
			case '403':
				this.add403Animations();
				break;
			case '500':
				this.add500Animations();
				break;
		}
	}

	/**
	 * 404 specific animations
	 */
	add404Animations() {
		const icon = document.querySelector('.error-icon i');
		if (icon) {
			icon.classList.add('bounce');
		}
	}

	/**
	 * 400 specific animations
	 */
	add400Animations() {
		const icon = document.querySelector('.error-icon i');
		if (icon) {
			icon.classList.add('rotate');
		}
	}

	/**
	 * 403 specific animations
	 */
	add403Animations() {
		const icon = document.querySelector('.error-icon i');
		if (icon) {
			icon.classList.add('pulse');
		}
	}

	/**
	 * 500 specific animations
	 */
	add500Animations() {
		const icon = document.querySelector('.error-icon i');
		if (icon) {
			icon.classList.add('shake');
		}
	}
}

/**
 * Utility functions
 */
const ErrorPageUtils = {
	/**
	 * Add CSS animation keyframes dynamically
	 */
	addAnimationKeyframes() {
		const style = document.createElement('style');
		style.textContent = `
            @keyframes particleFloat {
                0% {
                    transform: translateY(0) rotate(0deg);
                    opacity: 0.3;
                }
                50% {
                    opacity: 0.6;
                }
                100% {
                    transform: translateY(-100vh) rotate(360deg);
                    opacity: 0;
                }
            }
            
            @keyframes ripple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
        `;
		document.head.appendChild(style);
	},

	/**
	 * Smooth scroll to top
	 */
	scrollToTop() {
		window.scrollTo({
			top: 0,
			behavior: 'smooth',
		});
	},

	/**
	 * Go back in history
	 */
	goBack() {
		if (window.history.length > 1) {
			window.history.back();
		} else {
			window.location.href = '/';
		}
	},
};

/**
 * Initialize when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', () => {
	// Add animation keyframes
	ErrorPageUtils.addAnimationKeyframes();

	// Initialize error page manager
	const errorManager = new ErrorPageManager();

	// Add error-specific animations
	errorManager.addErrorSpecificAnimations();

	// Setup utility functions
	window.ErrorPageUtils = ErrorPageUtils;
});

/**
 * Export for module systems
 */
if (typeof module !== 'undefined' && module.exports) {
	module.exports = { ErrorPageManager, ErrorPageUtils };
}
