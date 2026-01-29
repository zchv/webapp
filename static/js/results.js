/**
 * Results Display and Grid Management
 */

class ResultsManager {
    constructor() {
        this.results = [];
        this.currentPage = 1;
        this.resultsPerPage = 20;
        this.loadingMode = 'pagination'; // 'pagination' or 'infinite'
        this.allResultsLoaded = false;

        this.init();
    }

    init() {
        this.loadSettings();
        this.initPagination();
        this.initInfiniteScroll();
    }

    /**
     * Load settings from localStorage
     */
    loadSettings() {
        const mode = Storage.get('loading_mode');
        if (mode) {
            this.loadingMode = mode;
        }
    }

    /**
     * Display search results
     */
    displayResults(results, query = '') {
        this.results = results;
        this.currentPage = 1;
        this.allResultsLoaded = false;

        const resultsSection = DOMUtils.getId('results-section');
        const resultsGrid = DOMUtils.getId('results-grid');
        const resultsTotal = DOMUtils.getId('results-total');

        if (!resultsSection || !resultsGrid) return;

        // Show results section
        UI.show(resultsSection);

        // Update total count
        if (resultsTotal) {
            resultsTotal.textContent = results.length;
        }

        // Clear previous results
        resultsGrid.innerHTML = '';

        // Check if empty
        if (results.length === 0) {
            UI.showEmptyState(resultsGrid, 'No results found. Try a different query.');
            this.hidePaginationControls();
            return;
        }

        // Render based on loading mode
        if (this.loadingMode === 'pagination') {
            this.renderPage(1);
            this.updatePaginationControls();
        } else {
            this.renderPage(1);
            this.showLoadMoreButton();
        }

        // Scroll to results
        UI.scrollTo(resultsSection);
    }

    /**
     * Render a page of results
     */
    renderPage(page) {
        const resultsGrid = DOMUtils.getId('results-grid');
        if (!resultsGrid) return;

        const startIdx = (page - 1) * this.resultsPerPage;
        const endIdx = Math.min(startIdx + this.resultsPerPage, this.results.length);

        // Clear grid if pagination mode
        if (this.loadingMode === 'pagination') {
            resultsGrid.innerHTML = '';
        }

        // Render results
        for (let i = startIdx; i < endIdx; i++) {
            const result = this.results[i];
            const card = this.createResultCard(result);
            resultsGrid.appendChild(card);
        }

        // Check if all results loaded
        if (endIdx >= this.results.length) {
            this.allResultsLoaded = true;
        }

        this.currentPage = page;
    }

    /**
     * Create a result card element
     */
    createResultCard(result) {
        const card = document.createElement('div');
        card.className = 'result-card';
        card.dataset.imageId = result.image_id;

        // Image container
        const imageContainer = document.createElement('div');
        imageContainer.className = 'result-image-container';

        // Image
        const img = document.createElement('img');
        img.className = 'result-image';
        img.alt = result.filename;

        // Lazy load image
        UI.lazyLoadImage(img, result.image_path);

        // Score badge
        const scoreClass = UI.getScoreColor(result.score);
        const scoreBadge = document.createElement('div');
        scoreBadge.className = `result-score ${scoreClass}`;
        scoreBadge.textContent = `${result.score.toFixed(1)}%`;

        imageContainer.appendChild(img);
        imageContainer.appendChild(scoreBadge);

        // Info container
        const infoContainer = document.createElement('div');
        infoContainer.className = 'result-info';

        // Filename
        const filename = document.createElement('div');
        filename.className = 'result-filename';
        filename.textContent = result.filename;
        filename.title = result.filename;

        // Feedback buttons
        const feedbackContainer = document.createElement('div');
        feedbackContainer.className = 'result-feedback';
        feedbackContainer.innerHTML = `
            <button class="feedback-button like-btn" data-type="like" title="Like">
                <span class="feedback-icon">👍</span>
            </button>
            <button class="feedback-button favorite-btn" data-type="favorite" title="Favorite">
                <span class="feedback-icon">⭐</span>
            </button>
            <button class="feedback-button irrelevant-btn" data-type="irrelevant" title="Not relevant">
                <span class="feedback-icon">👎</span>
            </button>
        `;

        infoContainer.appendChild(filename);
        infoContainer.appendChild(feedbackContainer);

        card.appendChild(imageContainer);
        card.appendChild(infoContainer);

        // Click to view details
        card.addEventListener('click', (e) => {
            // Don't trigger if clicking feedback button
            if (e.target.closest('.feedback-button')) return;

            modalManager.showImageDetail(result);
        });

        // Attach feedback handlers
        this.attachFeedbackHandlers(card, result);

        return card;
    }

    /**
     * Attach feedback button handlers
     */
    attachFeedbackHandlers(card, result) {
        const feedbackButtons = card.querySelectorAll('.feedback-button');

        feedbackButtons.forEach(button => {
            button.addEventListener('click', async (e) => {
                e.stopPropagation();

                const feedbackType = button.dataset.type;
                const query = window.searchManager ? window.searchManager.getCurrentQuery() : '';

                try {
                    await window.feedbackManager.recordFeedback(
                        query,
                        result.image_id,
                        feedbackType
                    );

                    // Toggle active state
                    feedbackButtons.forEach(btn => btn.classList.remove('active'));
                    button.classList.add('active');

                    UI.showSuccess(`Marked as ${feedbackType}`);

                } catch (error) {
                    UI.showError(`Failed to record feedback: ${error.message}`);
                    console.error('Feedback error:', error);
                }
            });
        });
    }

    /**
     * Initialize pagination controls
     */
    initPagination() {
        const prevBtn = DOMUtils.getId('prev-page-btn');
        const nextBtn = DOMUtils.getId('next-page-btn');

        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                if (this.currentPage > 1) {
                    this.renderPage(this.currentPage - 1);
                    this.updatePaginationControls();
                    UI.scrollTo(DOMUtils.getId('results-section'));
                }
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                const totalPages = Math.ceil(this.results.length / this.resultsPerPage);
                if (this.currentPage < totalPages) {
                    this.renderPage(this.currentPage + 1);
                    this.updatePaginationControls();
                    UI.scrollTo(DOMUtils.getId('results-section'));
                }
            });
        }
    }

    /**
     * Update pagination controls
     */
    updatePaginationControls() {
        const paginationControls = DOMUtils.getId('pagination-controls');
        const prevBtn = DOMUtils.getId('prev-page-btn');
        const nextBtn = DOMUtils.getId('next-page-btn');
        const pageInfo = DOMUtils.getId('page-info');

        if (!paginationControls) return;

        const totalPages = Math.ceil(this.results.length / this.resultsPerPage);

        // Show/hide controls
        if (this.loadingMode === 'pagination' && totalPages > 1) {
            UI.show(paginationControls);
        } else {
            UI.hide(paginationControls);
        }

        // Update buttons
        if (prevBtn) {
            prevBtn.disabled = this.currentPage <= 1;
        }

        if (nextBtn) {
            nextBtn.disabled = this.currentPage >= totalPages;
        }

        // Update page info
        if (pageInfo) {
            pageInfo.textContent = `Page ${this.currentPage} of ${totalPages}`;
        }
    }

    /**
     * Hide pagination controls
     */
    hidePaginationControls() {
        const paginationControls = DOMUtils.getId('pagination-controls');
        if (paginationControls) {
            UI.hide(paginationControls);
        }
    }

    /**
     * Initialize infinite scroll
     */
    initInfiniteScroll() {
        const loadMoreBtn = DOMUtils.getId('load-more-btn');

        if (loadMoreBtn) {
            loadMoreBtn.addEventListener('click', () => {
                if (!this.allResultsLoaded) {
                    this.renderPage(this.currentPage + 1);
                    this.updateLoadMoreButton();
                }
            });
        }
    }

    /**
     * Show load more button
     */
    showLoadMoreButton() {
        const loadMoreBtn = DOMUtils.getId('load-more-btn');

        if (loadMoreBtn && this.loadingMode === 'infinite') {
            UI.show(loadMoreBtn);
            this.updateLoadMoreButton();
        }
    }

    /**
     * Update load more button
     */
    updateLoadMoreButton() {
        const loadMoreBtn = DOMUtils.getId('load-more-btn');

        if (!loadMoreBtn) return;

        if (this.allResultsLoaded) {
            loadMoreBtn.textContent = 'All results loaded';
            loadMoreBtn.disabled = true;
        } else {
            const remaining = this.results.length - (this.currentPage * this.resultsPerPage);
            loadMoreBtn.textContent = `Load More (${remaining} remaining)`;
            loadMoreBtn.disabled = false;
        }
    }

    /**
     * Switch loading mode
     */
    setLoadingMode(mode) {
        this.loadingMode = mode;
        Storage.set('loading_mode', mode);

        // Re-render current results if any
        if (this.results.length > 0) {
            this.displayResults(this.results, this.currentQuery);
        }
    }

    /**
     * Get current loading mode
     */
    getLoadingMode() {
        return this.loadingMode;
    }
}

// Initialize results manager on DOM load
let resultsManager;
document.addEventListener('DOMContentLoaded', () => {
    resultsManager = new ResultsManager();
    window.resultsManager = resultsManager;
});
