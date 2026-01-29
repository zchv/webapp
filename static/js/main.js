/**
 * Main API Client and Utilities
 */

class APIClient {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
        this.timeout = 30000; // 30 seconds
    }

    /**
     * Make an API request
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        try {
            // Prepare headers
            const headers = { ...options.headers };

            // Only set Content-Type for JSON requests
            if (options.body && typeof options.body === 'string') {
                headers['Content-Type'] = 'application/json';
            }
            // For FormData, don't set Content-Type (browser will set it with boundary)

            const response = await fetch(url, {
                ...options,
                signal: controller.signal,
                headers: headers,
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                const error = await response.json().catch(() => ({
                    error: `HTTP ${response.status}`,
                }));
                throw new Error(error.error || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error('Request timeout');
            }
            throw error;
        }
    }

    /**
     * Text search
     */
    async searchText(query, options = {}) {
        return this.request('/search/text', {
            method: 'POST',
            body: JSON.stringify({
                query,
                top_k: options.topK || 20,
                enhance: options.enhance !== false,
            }),
        });
    }

    /**
     * Voice search
     */
    async searchVoice(query, options = {}) {
        return this.request('/search/voice', {
            method: 'POST',
            body: JSON.stringify({
                query,
                top_k: options.topK || 20,
                enhance: options.enhance !== false,
            }),
        });
    }

    /**
     * Image search
     */
    async searchImage(file, options = {}) {
        if (!file) {
            throw new Error('No image file provided');
        }

        console.log('searchImage called with:', {
            fileName: file.name,
            fileType: file.type,
            fileSize: file.size,
            options: options
        });

        const formData = new FormData();
        formData.append('image', file);
        formData.append('top_k', options.topK || 20);

        // Debug: log FormData contents
        console.log('FormData entries:');
        for (let pair of formData.entries()) {
            console.log(pair[0], pair[1]);
        }

        return this.request('/search/image', {
            method: 'POST',
            body: formData,
            headers: {}, // Don't set Content-Type, let browser set it with boundary
        });
    }

    /**
     * Multimodal search
     */
    async searchMultimodal(query, file, options = {}) {
        if (!query || !file) {
            throw new Error('Both query and image are required');
        }

        console.log('searchMultimodal called with:', {
            query: query,
            fileName: file.name,
            fileType: file.type,
            fileSize: file.size,
            options: options
        });

        const formData = new FormData();
        formData.append('query', query);
        formData.append('image', file);
        formData.append('alpha', options.alpha || 0.5);
        formData.append('top_k', options.topK || 20);

        // Debug: log FormData contents
        console.log('FormData entries:');
        for (let pair of formData.entries()) {
            console.log(pair[0], pair[1]);
        }

        return this.request('/search/multimodal', {
            method: 'POST',
            body: formData,
            headers: {}, // Don't set Content-Type, let browser set it with boundary
        });
    }

    /**
     * Multi-image search
     */
    async searchMultiImage(files, options = {}) {
        if (!files || files.length === 0) {
            throw new Error('No images provided');
        }

        console.log('searchMultiImage called with:', {
            fileCount: files.length,
            files: files.map(f => ({ name: f.name, type: f.type, size: f.size })),
            options: options
        });

        const formData = new FormData();
        files.forEach((file, index) => {
            formData.append('images', file);
        });
        formData.append('top_k', options.topK || 20);

        // Debug: log FormData contents
        console.log('FormData entries:');
        for (let pair of formData.entries()) {
            console.log(pair[0], pair[1]);
        }

        return this.request('/search/multi-image', {
            method: 'POST',
            body: formData,
            headers: {}, // Don't set Content-Type, let browser set it with boundary
        });
    }

    /**
     * Record feedback
     */
    async recordFeedback(query, imageId, feedbackType) {
        return this.request('/search/feedback/record', {
            method: 'POST',
            body: JSON.stringify({
                query,
                image_id: imageId,
                feedback_type: feedbackType,
            }),
        });
    }

    /**
     * Get feedback stats for an image
     */
    async getFeedbackStats(imageId) {
        return this.request(`/search/feedback/stats/${imageId}`);
    }

    /**
     * Get top rated images
     */
    async getTopRatedImages(limit = 20) {
        return this.request(`/search/feedback/top-rated?limit=${limit}`);
    }

    /**
     * Get search statistics
     */
    async getSearchStats() {
        return this.request('/search/stats');
    }

    /**
     * Health check
     */
    async healthCheck() {
        return this.request('/health');
    }

    /**
     * Get example queries
     */
    async getExamples() {
        return this.request('/examples');
    }
}

// Global API client instance
const api = new APIClient();

/**
 * DOM Utilities
 */
class DOMUtils {
    static getId(id) {
        return document.getElementById(id);
    }

    static getClass(className) {
        return document.querySelectorAll(`.${className}`);
    }

    static querySelector(selector) {
        return document.querySelector(selector);
    }

    static querySelectorAll(selector) {
        return document.querySelectorAll(selector);
    }

    static on(element, event, handler) {
        if (Array.isArray(element)) {
            element.forEach(el => el.addEventListener(event, handler));
        } else {
            element.addEventListener(event, handler);
        }
    }

    static off(element, event, handler) {
        if (Array.isArray(element)) {
            element.forEach(el => el.removeEventListener(event, handler));
        } else {
            element.removeEventListener(event, handler);
        }
    }

    static addClass(element, className) {
        if (Array.isArray(element)) {
            element.forEach(el => el.classList.add(className));
        } else {
            element.classList.add(className);
        }
    }

    static removeClass(element, className) {
        if (Array.isArray(element)) {
            element.forEach(el => el.classList.remove(className));
        } else {
            element.classList.remove(className);
        }
    }

    static toggleClass(element, className) {
        if (Array.isArray(element)) {
            element.forEach(el => el.classList.toggle(className));
        } else {
            element.classList.toggle(className);
        }
    }

    static hasClass(element, className) {
        return element.classList.contains(className);
    }

    static show(element) {
        if (Array.isArray(element)) {
            element.forEach(el => (el.style.display = ''));
        } else {
            element.style.display = '';
        }
    }

    static hide(element) {
        if (Array.isArray(element)) {
            element.forEach(el => (el.style.display = 'none'));
        } else {
            element.style.display = 'none';
        }
    }

    static setText(element, text) {
        element.textContent = text;
    }

    static setHTML(element, html) {
        element.innerHTML = html;
    }

    static getValue(element) {
        return element.value;
    }

    static setValue(element, value) {
        element.value = value;
    }

    static getAttr(element, attr) {
        return element.getAttribute(attr);
    }

    static setAttr(element, attr, value) {
        element.setAttribute(attr, value);
    }

    static removeAttr(element, attr) {
        element.removeAttribute(attr);
    }
}

/**
 * Storage Utilities
 */
class Storage {
    static set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.warn('Storage quota exceeded', e);
        }
    }

    static get(key) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (e) {
            console.warn('Error reading storage', e);
            return null;
        }
    }

    static remove(key) {
        localStorage.removeItem(key);
    }

    static clear() {
        localStorage.clear();
    }
}

/**
 * Search History Management
 */
class SearchHistory {
    constructor(maxItems = 20) {
        this.key = 'search_history';
        this.maxItems = maxItems;
    }

    add(query, type = 'text') {
        const history = this.get();
        const item = { query, type, timestamp: Date.now() };

        // Remove duplicates
        const filtered = history.filter(h => h.query !== query);

        // Add new item at the beginning and limit size
        const updated = [item, ...filtered].slice(0, this.maxItems);

        Storage.set(this.key, updated);
    }

    get() {
        return Storage.get(this.key) || [];
    }

    clear() {
        Storage.remove(this.key);
    }

    getRecent(limit = 5) {
        return this.get().slice(0, limit);
    }
}

// Global search history instance
const searchHistory = new SearchHistory();

/**
 * Initialize mobile menu toggle
 */
document.addEventListener('DOMContentLoaded', () => {
    const navbarToggle = DOMUtils.getId('navbar-toggle');
    const navbarMenu = DOMUtils.getId('navbar-menu');

    if (navbarToggle && navbarMenu) {
        navbarToggle.addEventListener('click', () => {
            DOMUtils.toggleClass(navbarMenu, 'show');
            DOMUtils.toggleClass(navbarToggle, 'active');
        });

        // Close menu when a link is clicked
        DOMUtils.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                DOMUtils.removeClass(navbarMenu, 'show');
                DOMUtils.removeClass(navbarToggle, 'active');
            });
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.navbar')) {
                DOMUtils.removeClass(navbarMenu, 'show');
                DOMUtils.removeClass(navbarToggle, 'active');
            }
        });
    }
});
