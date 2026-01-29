/**
 * Global Settings Loader
 * Loads settings from localStorage and applies them to all search tabs
 */

class GlobalSettingsLoader {
    constructor() {
        this.init();
    }

    init() {
        console.log('🔧 Initializing GlobalSettingsLoader...');

        // Load settings when page becomes visible
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                console.log('👁️ Page visible, reloading settings...');
                this.loadAndApplySettings();
            }
        });

        // Load settings on page load
        this.loadAndApplySettings();
    }

    /**
     * Load settings from localStorage and apply to all sliders
     */
    loadAndApplySettings() {
        const defaultTopK = Storage.get('default_top_k');

        if (defaultTopK) {
            console.log('📊 Loading default_top_k from localStorage:', defaultTopK);
            this.applyTopKToAllSliders(parseInt(defaultTopK));
        }
    }

    /**
     * Apply top_k value to all search tab sliders
     */
    applyTopKToAllSliders(topKValue) {
        const sliders = [
            { id: 'text-top-k', display: 'text-top-k-value' },
            { id: 'voice-top-k', display: 'voice-top-k-value' },
            { id: 'image-top-k', display: 'image-top-k-value' },
            { id: 'multimodal-top-k', display: 'multimodal-top-k-value' },
            { id: 'multi-image-top-k', display: 'multi-image-top-k-value' },
        ];

        sliders.forEach(({ id, display }) => {
            const slider = DOMUtils.getId(id);
            const displayEl = DOMUtils.getId(display);

            if (slider && slider.value != topKValue) {
                slider.value = topKValue;
                console.log(`  ✅ Updated ${id} to ${topKValue}`);
            }

            if (displayEl && displayEl.textContent != topKValue) {
                displayEl.textContent = topKValue;
            }
        });
    }
}

// Initialize on DOM load
let globalSettingsLoader;
document.addEventListener('DOMContentLoaded', () => {
    globalSettingsLoader = new GlobalSettingsLoader();
    window.globalSettingsLoader = globalSettingsLoader;
});
