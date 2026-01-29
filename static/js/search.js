/**
 * Search Form Management and Tab Switching
 */

class SearchManager {
    constructor() {
        this.currentTab = 'text-tab';
        this.currentQuery = '';
        this.currentResults = [];

        this.init();
    }

    init() {
        this.initTabs();
        this.initTextSearch();
        this.initExamples();
    }

    /**
     * Initialize tab switching
     */
    initTabs() {
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabContents = document.querySelectorAll('.tab-content');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const tabId = button.dataset.tab;

                // Update active states
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));

                button.classList.add('active');
                const tabContent = DOMUtils.getId(tabId);
                if (tabContent) {
                    tabContent.classList.add('active');
                    this.currentTab = tabId;

                    // Clear previous search results when switching tabs
                    this.clearResults();
                }
            });
        });
    }

    /**
     * Clear search results
     */
    clearResults() {
        const resultsSection = DOMUtils.getId('results-section');
        const resultsGrid = DOMUtils.getId('results-grid');

        if (resultsSection) {
            UI.hide(resultsSection);
        }

        if (resultsGrid) {
            resultsGrid.innerHTML = '';
        }

        this.currentResults = [];
    }

    /**
     * Initialize text search form
     */
    initTextSearch() {
        const form = DOMUtils.getId('text-search-form');
        const input = DOMUtils.getId('text-query');
        const enhanceCheckbox = DOMUtils.getId('text-enhance');
        const topKSlider = DOMUtils.getId('text-top-k');

        // Load settings
        const defaultTopK = Storage.get('default_top_k') || 20;
        const queryEnhancement = Storage.get('query_enhancement') !== false;

        if (topKSlider) topKSlider.value = defaultTopK;
        if (enhanceCheckbox) enhanceCheckbox.checked = queryEnhancement;

        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();

                const query = input.value.trim();
                if (!query) {
                    UI.showWarning('Please enter a search query');
                    return;
                }

                try {
                    UI.showLoading('Searching...');

                    const results = await api.searchText(query, {
                        enhance: enhanceCheckbox.checked,
                        topK: parseInt(topKSlider.value)
                    });

                    // Show enhanced query if different
                    if (results.enhanced_query && results.enhanced_query !== query) {
                        const enhancedDiv = DOMUtils.getId('text-enhanced-query');
                        const enhancedText = DOMUtils.getId('text-enhanced-text');
                        enhancedText.textContent = results.enhanced_query;
                        UI.show(enhancedDiv);
                    } else {
                        UI.hide(DOMUtils.getId('text-enhanced-query'));
                    }

                    // Store query for feedback
                    this.currentQuery = query;

                    // Add to search history
                    searchHistory.add(query, 'text');

                    // Display results
                    window.resultsManager.displayResults(results.results, query);

                    UI.hideLoading();
                    UI.showSuccess(`Found ${results.total_results} results`);

                } catch (error) {
                    UI.hideLoading();
                    UI.showError(`Search failed: ${error.message}`);
                    console.error('Search error:', error);
                }
            });
        }
    }

    /**
     * Initialize example queries
     */
    initExamples() {
        const exampleButtons = document.querySelectorAll('.example-button');
        const textInput = DOMUtils.getId('text-query');

        exampleButtons.forEach(button => {
            button.addEventListener('click', () => {
                const query = button.dataset.query;
                if (textInput) {
                    textInput.value = query;
                    // Trigger search
                    const form = DOMUtils.getId('text-search-form');
                    if (form) {
                        form.dispatchEvent(new Event('submit'));
                    }
                }
            });
        });
    }

    /**
     * Get current query
     */
    getCurrentQuery() {
        return this.currentQuery;
    }

    /**
     * Set current query
     */
    setCurrentQuery(query) {
        this.currentQuery = query;
    }
}

// Initialize search manager on DOM load
let searchManager;
document.addEventListener('DOMContentLoaded', () => {
    searchManager = new SearchManager();
});
