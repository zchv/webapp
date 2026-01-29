/**
 * Modal Management
 */

class ModalManager {
    constructor() {
        this.modals = new Map();
    }

    /**
     * Create a modal
     */
    create(id, title, content, options = {}) {
        const modal = UI.createElement('div', {
            className: 'modal',
            id: `modal-${id}`
        }, [
            UI.createElement('div', { className: 'modal-content' }, [
                UI.createElement('div', { className: 'modal-header' }, [
                    UI.createElement('h3', { className: 'modal-title' }, [title]),
                    UI.createElement('button', {
                        className: 'modal-close',
                        onClick: () => this.close(id)
                    }, ['×'])
                ]),
                UI.createElement('div', {
                    className: 'modal-body',
                    id: `modal-body-${id}`
                }, typeof content === 'string' ? [content] : []),
                options.footer ? UI.createElement('div', {
                    className: 'modal-footer',
                    id: `modal-footer-${id}`
                }) : null
            ].filter(Boolean))
        ]);

        document.body.appendChild(modal);
        this.modals.set(id, modal);

        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.close(id);
            }
        });

        // Close on Escape key
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                this.close(id);
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);

        return modal;
    }

    /**
     * Show a modal
     */
    show(id) {
        const modal = this.modals.get(id) || DOMUtils.getId(`modal-${id}`);
        if (modal) {
            DOMUtils.addClass(modal, 'show');
        }
    }

    /**
     * Close a modal
     */
    close(id) {
        const modal = this.modals.get(id) || DOMUtils.getId(`modal-${id}`);
        if (modal) {
            DOMUtils.removeClass(modal, 'show');
        }
    }

    /**
     * Destroy a modal
     */
    destroy(id) {
        const modal = this.modals.get(id);
        if (modal) {
            modal.remove();
            this.modals.delete(id);
        }
    }

    /**
     * Update modal content
     */
    updateContent(id, content) {
        const body = DOMUtils.getId(`modal-body-${id}`);
        if (body) {
            if (typeof content === 'string') {
                body.innerHTML = content;
            } else if (content instanceof Node) {
                body.innerHTML = '';
                body.appendChild(content);
            }
        }
    }

    /**
     * Update modal footer
     */
    updateFooter(id, content) {
        const footer = DOMUtils.getId(`modal-footer-${id}`);
        if (footer) {
            if (typeof content === 'string') {
                footer.innerHTML = content;
            } else if (content instanceof Node) {
                footer.innerHTML = '';
                footer.appendChild(content);
            }
        }
    }

    /**
     * Show image detail modal
     */
    showImageDetail(imageData) {
        const modalId = 'image-detail';

        // Destroy existing modal if any
        this.destroy(modalId);

        const content = UI.createElement('div', { className: 'image-detail-container' }, [
            UI.createElement('img', {
                src: imageData.image_path,
                alt: imageData.filename,
                style: {
                    width: '100%',
                    height: 'auto',
                    borderRadius: '8px'
                }
            }),
            UI.createElement('div', { className: 'image-detail-info' }, [
                UI.createElement('p', {}, [
                    UI.createElement('strong', {}, ['Filename: ']),
                    imageData.filename
                ]),
                UI.createElement('p', {}, [
                    UI.createElement('strong', {}, ['Similarity Score: ']),
                    `${imageData.score.toFixed(2)}%`
                ]),
                imageData.metadata ? UI.createElement('div', { className: 'metadata' }, [
                    UI.createElement('strong', {}, ['Metadata:']),
                    UI.createElement('pre', {}, [
                        JSON.stringify(imageData.metadata, null, 2)
                    ])
                ]) : null
            ].filter(Boolean))
        ]);

        this.create(modalId, 'Image Details', '', { footer: true });
        this.updateContent(modalId, content);

        const footerContent = UI.createElement('button', {
            className: 'button',
            onClick: () => this.close(modalId)
        }, ['Close']);
        this.updateFooter(modalId, footerContent);

        this.show(modalId);
    }

    /**
     * Show confirmation modal
     */
    showConfirm(title, message, onConfirm) {
        const modalId = 'confirm';

        this.destroy(modalId);
        this.create(modalId, title, message, { footer: true });

        const footerContent = UI.createElement('div', {
            style: { display: 'flex', gap: '1rem' }
        }, [
            UI.createElement('button', {
                className: 'button secondary',
                onClick: () => this.close(modalId)
            }, ['Cancel']),
            UI.createElement('button', {
                className: 'button',
                onClick: () => {
                    onConfirm();
                    this.close(modalId);
                }
            }, ['Confirm'])
        ]);

        this.updateFooter(modalId, footerContent);
        this.show(modalId);
    }

    /**
     * Show alert modal
     */
    showAlert(title, message) {
        const modalId = 'alert';

        this.destroy(modalId);
        this.create(modalId, title, message, { footer: true });

        const footerContent = UI.createElement('button', {
            className: 'button',
            onClick: () => this.close(modalId)
        }, ['OK']);

        this.updateFooter(modalId, footerContent);
        this.show(modalId);
    }
}

// Global modal manager instance
const modalManager = new ModalManager();
