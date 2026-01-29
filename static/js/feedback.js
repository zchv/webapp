/**
 * User Feedback Management
 */

class FeedbackManager {
    constructor() {
        this.feedbackCache = new Map();
        this.init();
    }

    init() {
        // Feedback is attached to individual result cards
        // in results.js via attachFeedbackHandlers
    }

    /**
     * Record user feedback
     */
    async recordFeedback(query, imageId, feedbackType) {
        if (!['like', 'favorite', 'irrelevant'].includes(feedbackType)) {
            throw new Error('Invalid feedback type');
        }

        try {
            const response = await api.recordFeedback(query, imageId, feedbackType);

            // Update cache
            const cacheKey = `${imageId}`;
            if (this.feedbackCache.has(cacheKey)) {
                const stats = this.feedbackCache.get(cacheKey);
                stats[feedbackType] = (stats[feedbackType] || 0) + 1;
            }

            return response;

        } catch (error) {
            console.error('Failed to record feedback:', error);
            throw error;
        }
    }

    /**
     * Get feedback stats for an image
     */
    async getFeedbackStats(imageId) {
        const cacheKey = `${imageId}`;

        // Check cache first
        if (this.feedbackCache.has(cacheKey)) {
            return this.feedbackCache.get(cacheKey);
        }

        try {
            const response = await api.getFeedbackStats(imageId);
            const stats = response.stats;

            // Cache the result
            this.feedbackCache.set(cacheKey, stats);

            return stats;

        } catch (error) {
            console.error('Failed to get feedback stats:', error);
            return { like: 0, favorite: 0, irrelevant: 0 };
        }
    }

    /**
     * Get top-rated images
     */
    async getTopRatedImages(limit = 20) {
        try {
            const response = await api.getTopRatedImages(limit);
            return response.images;

        } catch (error) {
            console.error('Failed to get top-rated images:', error);
            throw error;
        }
    }

    /**
     * Clear feedback cache
     */
    clearCache() {
        this.feedbackCache.clear();
    }

    /**
     * Show feedback summary in modal
     */
    showFeedbackSummary(imageId) {
        this.getFeedbackStats(imageId).then(stats => {
            const content = `
                <div class="feedback-stats">
                    <div class="stat-item">
                        <span class="stat-icon">👍</span>
                        <span class="stat-label">Likes:</span>
                        <span class="stat-count">${stats.like}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-icon">⭐</span>
                        <span class="stat-label">Favorites:</span>
                        <span class="stat-count">${stats.favorite}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-icon">👎</span>
                        <span class="stat-label">Irrelevant:</span>
                        <span class="stat-count">${stats.irrelevant}</span>
                    </div>
                </div>
            `;

            modalManager.showAlert('Feedback Statistics', content);
        });
    }
}

// Initialize feedback manager on DOM load
let feedbackManager;
document.addEventListener('DOMContentLoaded', () => {
    feedbackManager = new FeedbackManager();
    window.feedbackManager = feedbackManager;
});
