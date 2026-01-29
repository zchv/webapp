/**
 * Settings Page Management
 */

class SettingsManager {
    constructor() {
        this.settings = this.loadSettings();
        this.init();
    }

    /**
     * Load settings from localStorage
     */
    loadSettings() {
        return {
            defaultTopK: Storage.get('default_top_k') || 20,
            queryEnhancement: Storage.get('query_enhancement') !== false,
            enableReranking: Storage.get('enable_reranking') !== false,
            loadingMode: Storage.get('loading_mode') || 'pagination',
            resultsPerPage: Storage.get('results_per_page') || 20,
        };
    }

    /**
     * Initialize settings page
     */
    init() {
        this.loadCurrentSettings();
        this.initControls();
        this.initSliders();
    }

    /**
     * Load current settings into UI
     */
    loadCurrentSettings() {
        const defaultTopK = DOMUtils.getId('default-top-k');
        const queryEnhancement = DOMUtils.getId('query-enhancement');
        const enableReranking = DOMUtils.getId('enable-reranking');
        const loadingMode = DOMUtils.getId('loading-mode');
        const resultsPerPage = DOMUtils.getId('results-per-page');

        if (defaultTopK) defaultTopK.value = this.settings.defaultTopK;
        if (queryEnhancement) queryEnhancement.checked = this.settings.queryEnhancement;
        if (enableReranking) enableReranking.checked = this.settings.enableReranking;
        if (loadingMode) loadingMode.value = this.settings.loadingMode;
        if (resultsPerPage) resultsPerPage.value = this.settings.resultsPerPage;
    }

    /**
     * Initialize control handlers
     */
    initControls() {
        // Save button
        const saveBtn = DOMUtils.getId('save-settings-btn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveSettings());
        }

        // Reset button
        const resetBtn = DOMUtils.getId('reset-settings-btn');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetSettings());
        }

        // Clear history button
        const clearHistoryBtn = DOMUtils.getId('clear-history-btn');
        if (clearHistoryBtn) {
            clearHistoryBtn.addEventListener('click', () => this.clearHistory());
        }

        // Clear cache button
        const clearCacheBtn = DOMUtils.getId('clear-cache-btn');
        if (clearCacheBtn) {
            clearCacheBtn.addEventListener('click', () => this.clearCache());
        }
    }

    /**
     * Initialize sliders
     */
    initSliders() {
        const sliders = [
            { slider: 'default-top-k', display: 'default-top-k-value' },
            { slider: 'results-per-page', display: 'results-per-page-value' },
        ];

        sliders.forEach(({ slider, display }) => {
            const sliderEl = DOMUtils.getId(slider);
            const displayEl = DOMUtils.getId(display);
            if (sliderEl && displayEl) {
                UI.updateSliderValue(sliderEl, displayEl);
            }
        });
    }

    /**
     * Save settings
     */
    saveSettings() {
        const defaultTopK = DOMUtils.getId('default-top-k');
        const queryEnhancement = DOMUtils.getId('query-enhancement');
        const enableReranking = DOMUtils.getId('enable-reranking');
        const loadingMode = DOMUtils.getId('loading-mode');
        const resultsPerPage = DOMUtils.getId('results-per-page');

        // Save to localStorage
        if (defaultTopK) Storage.set('default_top_k', parseInt(defaultTopK.value));
        if (queryEnhancement) Storage.set('query_enhancement', queryEnhancement.checked);
        if (enableReranking) Storage.set('enable_reranking', enableReranking.checked);
        if (loadingMode) Storage.set('loading_mode', loadingMode.value);
        if (resultsPerPage) Storage.set('results_per_page', parseInt(resultsPerPage.value));

        // Update results manager if exists
        if (window.resultsManager && loadingMode) {
            window.resultsManager.setLoadingMode(loadingMode.value);
            window.resultsManager.resultsPerPage = parseInt(resultsPerPage.value);
        }

        console.log('✅ Settings saved to localStorage');
        UI.showSuccess('设置已保存，将在下次搜索时生效');
    }

    /**
     * Reset settings to defaults
     */
    resetSettings() {
        UI.confirm('Reset all settings to defaults?', () => {
            // Clear storage
            Storage.remove('default_top_k');
            Storage.remove('query_enhancement');
            Storage.remove('enable_reranking');
            Storage.remove('loading_mode');
            Storage.remove('results_per_page');

            // Reload defaults
            this.settings = this.loadSettings();
            this.loadCurrentSettings();

            UI.showSuccess('Settings reset to defaults');
        });
    }

    /**
     * Clear search history
     */
    clearHistory() {
        UI.confirm('Clear all search history?', () => {
            if (window.searchHistory) {
                window.searchHistory.clear();
            }
            UI.showSuccess('Search history cleared');
        });
    }

    /**
     * Clear feedback cache
     */
    clearCache() {
        UI.confirm('Clear feedback cache?', () => {
            if (window.feedbackManager) {
                window.feedbackManager.clearCache();
            }
            UI.showSuccess('Feedback cache cleared');
        });
    }
}

// Initialize settings manager on DOM load
let settingsManager;
document.addEventListener('DOMContentLoaded', () => {
    settingsManager = new SettingsManager();
});
