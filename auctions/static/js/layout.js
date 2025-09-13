/**
 * Layout JavaScript - Main functionality for the site layout
 * Handles theme switching, back to top button, and other layout features
 */

(function () {
	'use strict';

	// Configuration
	const CONFIG = {
		backToTopThreshold: 300,
		themeStorageKey: 'theme',
		animationDuration: 300,
	};

	// DOM Elements
	let themeToggle, themeIcon, backToTopButton, body;

	// Initialize immediately for onclick handlers, then when DOM is loaded
	initializeElements();
	initializeTheme();

	document.addEventListener('DOMContentLoaded', function () {
		initializeBackToTop();
		initializeAccessibility();
	});

	/**
	 * Initialize DOM elements
	 */
	function initializeElements() {
		themeToggle = document.querySelector('.theme-toggle');
		themeIcon = document.getElementById('themeIcon');
		backToTopButton = document.getElementById('back-to-top');
		body = document.body;
	}

	/**
	 * Initialize theme functionality
	 */
	function initializeTheme() {
		if (!themeToggle || !themeIcon) return;

		// Apply saved theme
		const savedTheme = localStorage.getItem(CONFIG.themeStorageKey);
		if (savedTheme === 'dark') {
			applyDarkTheme();
		} else {
			applyLightTheme();
		}

		// Add click event listener
		themeToggle.addEventListener('click', toggleTheme);
	}

	/**
	 * Toggle between light and dark theme
	 */
	function toggleTheme() {
		if (body.getAttribute('data-theme') === 'dark') {
			applyLightTheme();
		} else {
			applyDarkTheme();
		}
	}

	/**
	 * Apply light theme
	 */
	function applyLightTheme() {
		body.removeAttribute('data-theme');
		if (themeIcon) {
			themeIcon.classList.replace('fa-moon', 'fa-sun');
		}
		localStorage.setItem(CONFIG.themeStorageKey, 'light');

		// Dispatch custom event
		document.dispatchEvent(
			new CustomEvent('themeChanged', {
				detail: { theme: 'light' },
			})
		);
	}

	/**
	 * Apply dark theme
	 */
	function applyDarkTheme() {
		body.setAttribute('data-theme', 'dark');
		if (themeIcon) {
			themeIcon.classList.replace('fa-sun', 'fa-moon');
		}
		localStorage.setItem(CONFIG.themeStorageKey, 'dark');

		// Dispatch custom event
		document.dispatchEvent(
			new CustomEvent('themeChanged', {
				detail: { theme: 'dark' },
			})
		);
	}

	// Expose functions globally for HTML onclick handlers
	window.toggleTheme = toggleTheme;

	// Debug logging
	console.log('toggleTheme function defined:', typeof window.toggleTheme);

	/**
	 * Initialize back to top button functionality
	 */
	function initializeBackToTop() {
		if (!backToTopButton) return;

		// Initially hide the button
		backToTopButton.style.display = 'none';

		// Show/hide based on scroll position
		window.addEventListener('scroll', throttle(handleScroll, 100));

		// Scroll to top when clicked
		backToTopButton.addEventListener('click', scrollToTop);
	}

	/**
	 * Handle scroll event for back to top button
	 */
	function handleScroll() {
		if (window.pageYOffset > CONFIG.backToTopThreshold) {
			backToTopButton.style.display = 'flex';
			backToTopButton.style.opacity = '0';
			backToTopButton.style.transform = 'translateY(20px)';

			// Animate in
			requestAnimationFrame(() => {
				backToTopButton.style.transition = 'all 0.3s ease';
				backToTopButton.style.opacity = '1';
				backToTopButton.style.transform = 'translateY(0)';
			});
		} else {
			backToTopButton.style.opacity = '0';
			backToTopButton.style.transform = 'translateY(20px)';

			setTimeout(() => {
				if (window.pageYOffset <= CONFIG.backToTopThreshold) {
					backToTopButton.style.display = 'none';
				}
			}, CONFIG.animationDuration);
		}
	}

	/**
	 * Scroll to top smoothly
	 */
	function scrollToTop() {
		window.scrollTo({
			top: 0,
			behavior: 'smooth',
		});
	}

	/**
	 * Initialize accessibility features
	 */
	function initializeAccessibility() {
		// Skip link functionality
		const skipLink = document.querySelector('.skip-link');
		if (skipLink) {
			skipLink.addEventListener('click', function (e) {
				e.preventDefault();
				const target = document.querySelector(this.getAttribute('href'));
				if (target) {
					target.focus();
					target.scrollIntoView({ behavior: 'smooth' });
				}
			});
		}

		// Keyboard navigation for theme toggle
		if (themeToggle) {
			themeToggle.addEventListener('keydown', function (e) {
				if (e.key === 'Enter' || e.key === ' ') {
					e.preventDefault();
					toggleTheme();
				}
			});
		}

		// Keyboard navigation for back to top button
		if (backToTopButton) {
			backToTopButton.addEventListener('keydown', function (e) {
				if (e.key === 'Enter' || e.key === ' ') {
					e.preventDefault();
					scrollToTop();
				}
			});
		}
	}

	/**
	 * Throttle function to limit function calls
	 */
	function throttle(func, limit) {
		let inThrottle;
		return function () {
			const args = arguments;
			const context = this;
			if (!inThrottle) {
				func.apply(context, args);
				inThrottle = true;
				setTimeout(() => (inThrottle = false), limit);
			}
		};
	}

	/**
	 * Debounce function to delay function calls
	 */
	function debounce(func, wait, immediate) {
		let timeout;
		return function () {
			const context = this;
			const args = arguments;
			const later = function () {
				timeout = null;
				if (!immediate) func.apply(context, args);
			};
			const callNow = immediate && !timeout;
			clearTimeout(timeout);
			timeout = setTimeout(later, wait);
			if (callNow) func.apply(context, args);
		};
	}

	/**
	 * Show loading state
	 */
	function showLoading(element) {
		if (element) {
			element.classList.add('loading');
			element.style.display = 'block';
		}
	}

	/**
	 * Hide loading state
	 */
	function hideLoading(element) {
		if (element) {
			element.classList.remove('loading');
			element.style.display = 'none';
		}
	}

	/**
	 * Utility function to add smooth transitions
	 */
	function addSmoothTransition(element, duration = CONFIG.animationDuration) {
		if (element) {
			element.style.transition = `all ${duration}ms ease`;
		}
	}

	// Public API
	window.LayoutUtils = {
		toggleTheme: toggleTheme,
		applyLightTheme: applyLightTheme,
		applyDarkTheme: applyDarkTheme,
		scrollToTop: scrollToTop,
		showLoading: showLoading,
		hideLoading: hideLoading,
		addSmoothTransition: addSmoothTransition,
		throttle: throttle,
		debounce: debounce,
	};

	// Console log for debugging
	console.log('Layout JavaScript initialized successfully');
})();
