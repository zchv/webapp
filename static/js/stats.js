/**
 * Statistics Page Management
 */

class StatsManager {
    constructor() {
        this.init();
        this.loadStats();
    }

    init() {
        const refreshBtn = DOMUtils.getId('refresh-stats-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadStats());
        }
    }

    /**
     * Load all statistics
     */
    async loadStats() {
        UI.showLoading('Loading statistics...');

        try {
            // Load in parallel
            await Promise.all([
                this.loadIndexStats(),
                this.loadPopularQueries(),
                this.loadTopRatedImages()
            ]);

            UI.hideLoading();
            UI.showSuccess('Statistics loaded');

        } catch (error) {
            UI.hideLoading();
            UI.showError(`Failed to load statistics: ${error.message}`);
            console.error('Stats error:', error);
        }
    }

    /**
     * Load index statistics
     */
    async loadIndexStats() {
        try {
            const data = await api.getSearchStats();
            const stats = data.index_stats;

            // Update UI
            const totalVectors = DOMUtils.getId('total-vectors');
            const dimension = DOMUtils.getId('dimension');
            const indexType = DOMUtils.getId('index-type');
            const device = DOMUtils.getId('device');

            if (totalVectors) totalVectors.textContent = stats.total_vectors || '-';
            if (dimension) dimension.textContent = stats.dimension || '-';
            if (indexType) indexType.textContent = 'Flat IP';
            if (device) {
                // Get device from health endpoint
                const health = await api.healthCheck();
                device.textContent = health.device.toUpperCase() || '-';
            }

        } catch (error) {
            console.error('Failed to load index stats:', error);
        }
    }

    /**
     * Load popular queries
     */
    async loadPopularQueries() {
        try {
            const data = await api.getSearchStats();
            const queries = data.popular_queries || [];

            const container = DOMUtils.getId('popular-queries-container');
            if (!container) return;

            if (queries.length === 0) {
                UI.showEmptyState(container, 'No search queries yet');
                return;
            }

            // Create query list
            const list = document.createElement('ul');
            list.className = 'query-list';

            queries.forEach(query => {
                const item = document.createElement('li');
                item.className = 'query-item';

                const text = document.createElement('div');
                text.className = 'query-text';
                text.textContent = query.query;

                const stats = document.createElement('div');
                stats.className = 'query-stats';

                const count = document.createElement('div');
                count.className = 'query-stat';
                count.innerHTML = `<span>🔍</span> ${query.search_count} searches`;

                const score = document.createElement('div');
                score.className = 'query-stat';
                score.innerHTML = `<span>📊</span> ${(query.avg_top_score * 100).toFixed(1)}% avg`;

                stats.appendChild(count);
                stats.appendChild(score);

                item.appendChild(text);
                item.appendChild(stats);
                list.appendChild(item);
            });

            container.innerHTML = '';
            container.appendChild(list);

        } catch (error) {
            console.error('Failed to load popular queries:', error);
            const container = DOMUtils.getId('popular-queries-container');
            if (container) {
                UI.showErrorState(container, 'Failed to load popular queries');
            }
        }
    }

    /**
     * Load top rated images
     */
    async loadTopRatedImages() {
        try {
            const data = await window.feedbackManager.getTopRatedImages(12);

            const container = DOMUtils.getId('top-rated-container');
            if (!container) return;

            if (data.length === 0) {
                UI.showEmptyState(container, 'No rated images yet');
                return;
            }

            // Create grid
            const grid = document.createElement('div');
            grid.className = 'top-rated-grid';

            data.forEach(item => {
                const card = document.createElement('div');
                card.className = 'top-rated-item';

                // Create image element
                if (item.image_path) {
                    const img = document.createElement('img');
                    img.src = item.image_path;
                    img.alt = item.filename || `Image ${item.image_id}`;
                    img.loading = 'lazy';
                    card.appendChild(img);
                } else {
                    // Fallback placeholder if no image path
                    const placeholder = document.createElement('div');
                    placeholder.style.cssText = 'width:100%;height:100%;background:#f0f0f0;display:flex;align-items:center;justify-content:center';
                    placeholder.textContent = `#${item.image_id}`;
                    card.appendChild(placeholder);
                }

                // Create badge
                const badge = document.createElement('div');
                badge.className = 'top-rated-badge';

                const likes = item.likes || 0;
                const favorites = item.favorites || 0;
                const total = likes + (favorites * 2);

                badge.innerHTML = `
                    <span>⭐</span>
                    <span>${total}</span>
                `;

                card.appendChild(badge);

                // Click to view details
                card.addEventListener('click', () => {
                    if (item.image_path) {
                        modalManager.showImageDetail({
                            image_path: item.image_path,
                            filename: item.filename,
                            image_id: item.image_id,
                            score: total / 10  // Normalize score for display
                        });
                    }
                });

                grid.appendChild(card);
            });

            container.innerHTML = '';
            container.appendChild(grid);

        } catch (error) {
            console.error('Failed to load top rated images:', error);
            const container = DOMUtils.getId('top-rated-container');
            if (container) {
                UI.showErrorState(container, 'Failed to load top rated images');
            }
        }
    }
}

// Initialize stats manager on DOM load
let statsManager;
document.addEventListener('DOMContentLoaded', () => {
    statsManager = new StatsManager();
});
