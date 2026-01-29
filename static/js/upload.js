/**
 * File Upload Management
 * Handles drag-drop and file selection for image uploads
 */

class UploadManager {
    constructor() {
        this.init();
    }

    init() {
        this.initSingleImageUpload();
        this.initMultimodalUpload();
        this.initMultiImageUpload();
    }

    /**
     * Initialize single image upload (Image Search tab)
     */
    initSingleImageUpload() {
        const dropZone = DOMUtils.getId('image-drop-zone');
        const fileInput = DOMUtils.getId('image-upload');
        const preview = DOMUtils.getId('image-preview');
        const previewImg = DOMUtils.getId('image-preview-img');
        const removeBtn = DOMUtils.getId('image-remove-btn');
        const searchBtn = DOMUtils.getId('image-search-btn');
        const topKSlider = DOMUtils.getId('image-top-k');

        // Store selected file in closure
        let selectedFile = null;

        // Load default top_k from settings
        const defaultTopK = Storage.get('default_top_k') || 20;
        if (topKSlider) topKSlider.value = defaultTopK;

        if (dropZone && fileInput) {
            // Click to select
            dropZone.addEventListener('click', () => fileInput.click());

            // File selection
            fileInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file && file.type.startsWith('image/')) {
                    selectedFile = file;
                    this.showPreview(file, preview, previewImg);
                    UI.show(searchBtn);
                } else if (file) {
                    UI.showWarning('Please select an image file');
                }
            });

            // Drag and drop
            this.setupDragAndDrop(dropZone, (file) => {
                selectedFile = file;
                this.showPreview(file, preview, previewImg);
                UI.show(searchBtn);
            });

            // Remove button
            if (removeBtn) {
                removeBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    selectedFile = null;
                    fileInput.value = '';
                    UI.hide(preview);
                    UI.hide(searchBtn);
                });
            }

            // Search button
            if (searchBtn) {
                searchBtn.addEventListener('click', async () => {
                    if (!selectedFile) {
                        UI.showWarning('Please select an image');
                        return;
                    }

                    try {
                        UI.showLoading('Searching...');

                        const topK = topKSlider ? parseInt(topKSlider.value) : 20;
                        const results = await api.searchImage(selectedFile, {
                            topK: topK
                        });

                        if (window.searchManager) {
                            window.searchManager.setCurrentQuery('[image search]');
                        }

                        if (window.resultsManager) {
                            window.resultsManager.displayResults(results.results);
                        }

                        UI.hideLoading();
                        UI.showSuccess(`Found ${results.total_results} results`);

                    } catch (error) {
                        UI.hideLoading();
                        UI.showError(`Search failed: ${error.message}`);
                        console.error('Image search error:', error);
                    }
                });
            }
        }
    }

    /**
     * Initialize multimodal upload (Multimodal tab)
     */
    initMultimodalUpload() {
        const dropZone = DOMUtils.getId('multimodal-drop-zone');
        const fileInput = DOMUtils.getId('multimodal-upload');
        const preview = DOMUtils.getId('multimodal-preview');
        const previewImg = DOMUtils.getId('multimodal-preview-img');
        const removeBtn = DOMUtils.getId('multimodal-remove-btn');
        const searchBtn = DOMUtils.getId('multimodal-search-btn');
        const queryInput = DOMUtils.getId('multimodal-query');
        const alphaSlider = DOMUtils.getId('multimodal-alpha');
        const topKSlider = DOMUtils.getId('multimodal-top-k');

        // Store selected file in closure
        let selectedFile = null;

        // Load default top_k from settings
        const defaultTopK = Storage.get('default_top_k') || 20;
        if (topKSlider) topKSlider.value = defaultTopK;

        if (dropZone && fileInput) {
            // Click to select
            dropZone.addEventListener('click', () => fileInput.click());

            // File selection
            fileInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file && file.type.startsWith('image/')) {
                    selectedFile = file;
                    this.showPreview(file, preview, previewImg);
                    this.checkMultimodalReady(queryInput, selectedFile, searchBtn);
                } else if (file) {
                    UI.showWarning('Please select an image file');
                }
            });

            // Drag and drop
            this.setupDragAndDrop(dropZone, (file) => {
                selectedFile = file;
                this.showPreview(file, preview, previewImg);
                this.checkMultimodalReady(queryInput, selectedFile, searchBtn);
            });

            // Remove button
            if (removeBtn) {
                removeBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    selectedFile = null;
                    fileInput.value = '';
                    UI.hide(preview);
                    this.checkMultimodalReady(queryInput, selectedFile, searchBtn);
                });
            }

            // Query input change
            if (queryInput) {
                queryInput.addEventListener('input', () => {
                    this.checkMultimodalReady(queryInput, selectedFile, searchBtn);
                });
            }

            // Search button
            if (searchBtn) {
                searchBtn.addEventListener('click', async () => {
                    const query = queryInput ? queryInput.value.trim() : '';

                    if (!query || !selectedFile) {
                        UI.showWarning('Please enter a query and select an image');
                        return;
                    }

                    try {
                        UI.showLoading('Searching...');

                        const alpha = alphaSlider ? parseFloat(alphaSlider.value) : 0.5;
                        const topK = topKSlider ? parseInt(topKSlider.value) : 20;

                        const results = await api.searchMultimodal(query, selectedFile, {
                            alpha: alpha,
                            topK: topK
                        });

                        if (window.searchManager) {
                            window.searchManager.setCurrentQuery(`[multimodal] ${query}`);
                        }

                        if (window.resultsManager) {
                            window.resultsManager.displayResults(results.results);
                        }

                        UI.hideLoading();
                        UI.showSuccess(`Found ${results.total_results} results`);

                    } catch (error) {
                        UI.hideLoading();
                        UI.showError(`Search failed: ${error.message}`);
                        console.error('Multimodal search error:', error);
                    }
                });
            }
        }
    }

    /**
     * Initialize multi-image upload (Multi-Image tab)
     */
    initMultiImageUpload() {
        const dropZone = DOMUtils.getId('multi-image-drop-zone');
        const fileInput = DOMUtils.getId('multi-image-upload');
        const previewsContainer = DOMUtils.getId('multi-image-previews');
        const searchBtn = DOMUtils.getId('multi-image-search-btn');
        const topKSlider = DOMUtils.getId('multi-image-top-k');

        // Store selected files in closure
        let selectedFiles = [];

        // Load default top_k from settings
        const defaultTopK = Storage.get('default_top_k') || 20;
        if (topKSlider) topKSlider.value = defaultTopK;

        if (dropZone && fileInput) {
            // Click to select
            dropZone.addEventListener('click', () => fileInput.click());

            // File selection
            fileInput.addEventListener('change', (e) => {
                const files = Array.from(e.target.files).filter(f => f.type.startsWith('image/'));
                if (files.length > 0) {
                    selectedFiles = files.slice(0, 10); // Max 10 images
                    this.showMultiPreviews(selectedFiles, previewsContainer, () => {
                        // Callback when file is removed
                        if (selectedFiles.length === 0) {
                            UI.hide(searchBtn);
                        }
                    });
                    UI.show(searchBtn);
                } else {
                    UI.showWarning('Please select image files');
                }
            });

            // Drag and drop
            this.setupDragAndDrop(dropZone, (files) => {
                selectedFiles = files.slice(0, 10);
                this.showMultiPreviews(selectedFiles, previewsContainer, () => {
                    if (selectedFiles.length === 0) {
                        UI.hide(searchBtn);
                    }
                });
                UI.show(searchBtn);
            }, true);

            // Search button
            if (searchBtn) {
                searchBtn.addEventListener('click', async () => {
                    if (selectedFiles.length === 0) {
                        UI.showWarning('Please select at least one image');
                        return;
                    }

                    try {
                        UI.showLoading('Searching...');

                        const topK = topKSlider ? parseInt(topKSlider.value) : 20;
                        const results = await api.searchMultiImage(selectedFiles, {
                            topK: topK
                        });

                        if (window.searchManager) {
                            window.searchManager.setCurrentQuery(`[multi-image: ${selectedFiles.length}]`);
                        }

                        if (window.resultsManager) {
                            window.resultsManager.displayResults(results.results);
                        }

                        UI.hideLoading();
                        UI.showSuccess(`Found ${results.total_results} results`);

                    } catch (error) {
                        UI.hideLoading();
                        UI.showError(`Search failed: ${error.message}`);
                        console.error('Multi-image search error:', error);
                    }
                });
            }
        }
    }

    /**
     * Setup drag and drop for a drop zone
     */
    setupDragAndDrop(dropZone, onDrop, multiple = false) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.add('dragover');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.remove('dragover');
            });
        });

        dropZone.addEventListener('drop', (e) => {
            const files = Array.from(e.dataTransfer.files).filter(file =>
                file.type.startsWith('image/')
            );

            if (files.length > 0) {
                if (multiple) {
                    onDrop(files);
                } else {
                    onDrop(files[0]);
                }
            } else {
                UI.showWarning('Please drop image files only');
            }
        });
    }

    /**
     * Show single image preview
     */
    showPreview(file, previewContainer, previewImg) {
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImg.src = e.target.result;
            UI.show(previewContainer);
        };
        reader.readAsDataURL(file);
    }

    /**
     * Show multiple image previews
     */
    showMultiPreviews(files, container, onRemoveCallback) {
        container.innerHTML = '';

        files.forEach((file, index) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const previewItem = document.createElement('div');
                previewItem.className = 'image-preview-item';

                const img = document.createElement('img');
                img.src = e.target.result;
                img.alt = file.name;

                const removeBtn = document.createElement('button');
                removeBtn.className = 'image-remove-item';
                removeBtn.textContent = '×';
                removeBtn.onclick = () => {
                    previewItem.remove();
                    // Remove from files array
                    files.splice(index, 1);
                    if (onRemoveCallback) {
                        onRemoveCallback();
                    }
                };

                previewItem.appendChild(img);
                previewItem.appendChild(removeBtn);
                container.appendChild(previewItem);
            };
            reader.readAsDataURL(file);
        });

        // Show count
        if (files.length > 0) {
            const countDiv = document.createElement('div');
            countDiv.className = 'image-count';
            countDiv.textContent = `${files.length} image${files.length > 1 ? 's' : ''} selected`;
            container.appendChild(countDiv);
        }
    }

    /**
     * Check if multimodal search is ready
     */
    checkMultimodalReady(queryInput, file, searchBtn) {
        const query = queryInput ? queryInput.value.trim() : '';
        if (query && file) {
            UI.show(searchBtn);
        } else {
            UI.hide(searchBtn);
        }
    }

    /**
     * Create FileList from array of files
     */
    createFileList(files) {
        const dt = new DataTransfer();
        files.forEach(file => dt.items.add(file));
        return dt.files;
    }
}

// Initialize upload manager on DOM load
let uploadManager;
document.addEventListener('DOMContentLoaded', () => {
    uploadManager = new UploadManager();
});
