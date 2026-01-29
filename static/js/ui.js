/**
 * UI Utilities - Toast notifications, loading states, etc.
 */

class UI {
    /**
     * Show a toast notification
     */
    static showToast(message, type = 'info', duration = 3000) {
        const container = DOMUtils.getId('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;

        container.appendChild(toast);

        // Auto-hide
        setTimeout(() => {
            toast.classList.add('hide');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    /**
     * Show success toast
     */
    static showSuccess(message, duration = 3000) {
        UI.showToast(message, 'success', duration);
    }

    /**
     * Show error toast
     */
    static showError(message, duration = 5000) {
        UI.showToast(message, 'error', duration);
    }

    /**
     * Show warning toast
     */
    static showWarning(message, duration = 4000) {
        UI.showToast(message, 'warning', duration);
    }

    /**
     * Show info toast
     */
    static showInfo(message, duration = 3000) {
        UI.showToast(message, 'info', duration);
    }

    /**
     * Show loading overlay
     */
    static showLoading(text = 'Loading...') {
        const overlay = DOMUtils.getId('loading-overlay');
        const loadingText = DOMUtils.getId('loading-text');

        if (overlay) {
            DOMUtils.removeClass(overlay, 'hidden');
            if (loadingText) {
                DOMUtils.setText(loadingText, text);
            }
        }
    }

    /**
     * Hide loading overlay
     */
    static hideLoading() {
        const overlay = DOMUtils.getId('loading-overlay');
        if (overlay) {
            DOMUtils.addClass(overlay, 'hidden');
        }
    }

    /**
     * Show element
     */
    static show(element) {
        DOMUtils.show(element);
    }

    /**
     * Hide element
     */
    static hide(element) {
        DOMUtils.hide(element);
    }

    /**
     * Toggle element visibility
     */
    static toggle(element) {
        if (element.style.display === 'none') {
            UI.show(element);
        } else {
            UI.hide(element);
        }
    }

    /**
     * Scroll to element
     */
    static scrollTo(element, options = {}) {
        element.scrollIntoView({
            behavior: options.smooth !== false ? 'smooth' : 'auto',
            block: options.block || 'start',
        });
    }

    /**
     * Confirm dialog
     */
    static confirm(message, callback) {
        if (window.confirm(message)) {
            callback();
        }
    }

    /**
     * Format file size
     */
    static formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';

        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));

        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    /**
     * Format date
     */
    static formatDate(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }

    /**
     * Format relative time
     */
    static formatRelativeTime(timestamp) {
        const now = Date.now();
        const diff = now - timestamp;

        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
        if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        return 'Just now';
    }

    /**
     * Debounce function
     */
    static debounce(func, delay = 300) {
        let timeout;
        return function (...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), delay);
        };
    }

    /**
     * Throttle function
     */
    static throttle(func, limit = 300) {
        let inThrottle;
        return function (...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => (inThrottle = false), limit);
            }
        };
    }

    /**
     * Copy to clipboard
     */
    static async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            UI.showSuccess('Copied to clipboard!');
        } catch (error) {
            UI.showError('Failed to copy to clipboard');
            console.error('Copy failed:', error);
        }
    }

    /**
     * Check if element is in viewport
     */
    static isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }

    /**
     * Lazy load image
     */
    static lazyLoadImage(img, src) {
        // Set a placeholder or loading state
        img.style.backgroundColor = '#f0f0f0';
        img.style.minHeight = '200px';

        // Add error handler
        img.onerror = function() {
            console.error('Failed to load image:', src);
            img.alt = 'Image failed to load: ' + src;
            img.style.backgroundColor = '#ffebee';
        };

        // Add load handler for debugging
        img.onload = function() {
            console.log('Image loaded successfully:', src);
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    console.log('Loading image:', src);
                    img.src = src;
                    observer.disconnect();
                }
            });
        });

        observer.observe(img);
    }

    /**
     * Get color for similarity score
     */
    static getScoreColor(score) {
        if (score >= 30) return 'high';
        if (score >= 20) return 'medium';
        return 'low';
    }

    /**
     * Create element with properties
     */
    static createElement(tag, props = {}, children = []) {
        const element = document.createElement(tag);

        // Set properties
        Object.keys(props).forEach(key => {
            if (key === 'className') {
                element.className = props[key];
            } else if (key === 'style') {
                Object.assign(element.style, props[key]);
            } else if (key === 'dataset') {
                Object.assign(element.dataset, props[key]);
            } else if (key.startsWith('on')) {
                const event = key.substring(2).toLowerCase();
                element.addEventListener(event, props[key]);
            } else {
                element.setAttribute(key, props[key]);
            }
        });

        // Append children
        children.forEach(child => {
            if (typeof child === 'string') {
                element.appendChild(document.createTextNode(child));
            } else if (child instanceof Node) {
                element.appendChild(child);
            }
        });

        return element;
    }

    /**
     * Show empty state
     */
    static showEmptyState(container, message, icon = '🔍') {
        const emptyDiv = UI.createElement('div', { className: 'empty-state' }, [
            UI.createElement('div', { className: 'empty-icon' }, [icon]),
            UI.createElement('p', { className: 'empty-text' }, [message]),
        ]);

        container.innerHTML = '';
        container.appendChild(emptyDiv);
    }

    /**
     * Show error state
     */
    static showErrorState(container, message, icon = '⚠️') {
        const errorDiv = UI.createElement('div', { className: 'error-state' }, [
            UI.createElement('div', { className: 'error-icon' }, [icon]),
            UI.createElement('p', { className: 'error-message' }, [message]),
        ]);

        container.innerHTML = '';
        container.appendChild(errorDiv);
    }

    /**
     * Disable button
     */
    static disableButton(button, text = null) {
        button.disabled = true;
        if (text) {
            button.dataset.originalText = button.textContent;
            button.textContent = text;
        }
    }

    /**
     * Enable button
     */
    static enableButton(button) {
        button.disabled = false;
        if (button.dataset.originalText) {
            button.textContent = button.dataset.originalText;
            delete button.dataset.originalText;
        }
    }

    /**
     * Update slider value display
     */
    static updateSliderValue(slider, display) {
        display.textContent = slider.value;
        slider.addEventListener('input', () => {
            display.textContent = slider.value;
        });
    }

    /**
     * Initialize all slider value displays
     */
    static initSliders() {
        const sliders = [
            { slider: 'text-top-k', display: 'text-top-k-value' },
            { slider: 'voice-top-k', display: 'voice-top-k-value' },
            { slider: 'image-top-k', display: 'image-top-k-value' },
            { slider: 'multimodal-top-k', display: 'multimodal-top-k-value' },
            { slider: 'multimodal-alpha', display: 'multimodal-alpha-value' },
            { slider: 'multi-image-top-k', display: 'multi-image-top-k-value' },
        ];

        sliders.forEach(({ slider, display }) => {
            const sliderEl = DOMUtils.getId(slider);
            const displayEl = DOMUtils.getId(display);
            if (sliderEl && displayEl) {
                UI.updateSliderValue(sliderEl, displayEl);
            }
        });
    }
}

// Initialize UI on DOM load
document.addEventListener('DOMContentLoaded', () => {
    UI.initSliders();
});
