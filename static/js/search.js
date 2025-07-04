document.addEventListener('DOMContentLoaded', function () {
    const searchModal = new bootstrap.Modal(document.getElementById('searchModal'));
    const searchModalElement = document.getElementById('searchModal');
    const searchButton = document.querySelector('.btn.btn-outline-secondary.fas.fa-search');
    const searchInput = document.getElementById('searchInput');
    const clearSearchBtn = document.getElementById('clearSearchBtn');

    let searchTimeout;
    let currentRequest;
    let selectedIndex = -1;
    let announceTimeout;

    // Show/hide clear button based on input content and handle search
    searchInput.addEventListener('input', function (e) {
        const query = e.target.value.trim();

        // Show clear button if there's text, hide if empty
        if (query.length > 0) {
            clearSearchBtn.classList.remove('d-none');
        } else {
            clearSearchBtn.classList.add('d-none');
        }

        // Search functionality
        clearTimeout(searchTimeout);
        if (currentRequest) {
            currentRequest.abort();
        }

        if (query.length < 3) {
            showDefaultState();
            return;
        }

        searchTimeout = setTimeout(() => {
            performSearch(query);
        }, 500);
    });

    // Clear search functionality
    clearSearchBtn.addEventListener('click', function () {
        searchInput.value = '';
        clearSearchBtn.classList.add('d-none');
        showDefaultState();
        searchInput.focus();
    });

    // Focus input when modal is fully shown
    searchModalElement.addEventListener('shown.bs.modal', function () {
        // Store the element that had focus before modal opened
        const activeElement = document.activeElement;
        searchModalElement.setAttribute('data-previous-focus', activeElement.id || '');

        clearSearchBtn.classList.add('d-none');
        searchInput.focus();
        searchInput.select();
    });

    // Restore focus when modal is hidden
    searchModalElement.addEventListener('hidden.bs.modal', function () {
        const previousFocusId = searchModalElement.getAttribute('data-previous-focus');
        if (previousFocusId) {
            const previousElement = document.getElementById(previousFocusId);
            if (previousElement) {
                previousElement.focus();
            }
        }
    });

    // Open modal when search button is clicked
    if (searchButton) {
        searchButton.addEventListener('click', function () {
            searchModal.show();
        });
    }

    // Open modal with keyboard shortcuts
    document.addEventListener('keydown', function (e) {
        if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
            e.preventDefault();
            searchModal.show();
        }

        if (e.key === '/' && (e.ctrlKey || e.metaKey)) {
            e.preventDefault();
            searchModal.show();
        }

        if (e.key === 'Escape' && document.activeElement === searchInput) {
            searchModal.hide();
        }
    });

    // Enhanced keyboard navigation
    searchInput.addEventListener('keydown', function (e) {
        const items = document.querySelectorAll('#searchResults .list-group-item');

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
            updateSelection(items);
            announceCurrentSelection(items);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedIndex = Math.max(selectedIndex - 1, -1);
            updateSelection(items);
            announceCurrentSelection(items);
        } else if (e.key === 'Enter' && selectedIndex >= 0) {
            e.preventDefault();
            items[selectedIndex].click();
        } else if (e.key === 'Home' && items.length > 0) {
            e.preventDefault();
            selectedIndex = 0;
            updateSelection(items);
            announceCurrentSelection(items);
        } else if (e.key === 'End' && items.length > 0) {
            e.preventDefault();
            selectedIndex = items.length - 1;
            updateSelection(items);
            announceCurrentSelection(items);
        }
    });

    // Focus trap within modal
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Tab' && searchModalElement.classList.contains('show')) {
            const focusableElements = searchModalElement.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];

            if (e.shiftKey) {
                if (document.activeElement === firstElement) {
                    e.preventDefault();
                    lastElement.focus();
                }
            } else {
                if (document.activeElement === lastElement) {
                    e.preventDefault();
                    firstElement.focus();
                }
            }
        }
    });

    function updateSelection(items) {
        items.forEach((item, index) => {
            if (index === selectedIndex) {
                item.classList.add('active');
                item.scrollIntoView({ block: 'nearest' });
            } else {
                item.classList.remove('active');
            }
        });
    }

    function announceCurrentSelection(items) {
        if (selectedIndex >= 0 && items[selectedIndex]) {
            const itemText = items[selectedIndex].querySelector('.fw-medium').textContent;
            const itemDesc = items[selectedIndex].querySelector('small')?.textContent || '';
            announceToScreenReader(`Selected ${itemText} ${itemDesc}`);
        }
    }

    function announceToScreenReader(message) {
        clearTimeout(announceTimeout);

        let announcer = document.getElementById('searchAnnouncer');
        if (!announcer) {
            announcer = document.createElement('div');
            announcer.id = 'searchAnnouncer';
            announcer.setAttribute('aria-live', 'polite');
            announcer.setAttribute('aria-atomic', 'true');
            announcer.className = 'visually-hidden';
            document.body.appendChild(announcer);
        }

        announcer.textContent = '';
        announceTimeout = setTimeout(() => {
            announcer.textContent = message;
        }, 100);
    }

    function showDefaultState() {
        searchInput.setAttribute('aria-expanded', 'false');

        document.getElementById('searchResults').innerHTML = `
            <div class="text-center text-muted">
                <p>Start typing to search across all categories...</p>
            </div>
        `;
    }

    function performSearch(query) {
        document.getElementById('searchResults').innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2 text-muted">Searching...</p>
            </div>
        `;

        const controller = new AbortController();
        currentRequest = controller;

        fetch(`/common/api/search/?q=${encodeURIComponent(query)}`, {
            method: 'GET',
            signal: controller.signal
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            displaySearchResults(data);
        })
        .catch(error => {
            if (error.name !== 'AbortError') {
                console.error('Search error:', error);
                document.getElementById('searchResults').innerHTML = `
                    <div class="text-center text-danger">
                        <p>Search failed. Please try again.</p>
                    </div>
                `;
            }
        })
        .finally(() => {
            currentRequest = null;
        });
    }

    function displaySearchResults(data) {
        selectedIndex = -1;
        const resultsContainer = document.getElementById('searchResults');
        const results = data.results;

        const totalResults = Object.values(results).reduce((sum, category) => sum + category.length, 0);

        searchInput.setAttribute('aria-expanded', totalResults > 0 ? 'true' : 'false');

        if (totalResults === 0) {
            resultsContainer.innerHTML = `
                <div class="text-center text-muted">
                    <p>No results found. Try a different search term.</p>
                </div>
            `;
            announceToScreenReader("No results found");
            return;
        }

        let html = '';

        Object.entries(results).forEach(([category, items]) => {
            if (items.length > 0) {
                const categoryName = category.charAt(0).toUpperCase() + category.slice(1);
                html += `
                    <div class="mb-4">
                        <h6 class="text-muted text-uppercase fw-bold mb-2" id="${category}-heading">${categoryName} (${items.length})</h6>
                        <div class="list-group list-group-flush" role="group" aria-labelledby="${category}-heading">
                `;

                items.forEach((item, index) => {
                    html += createResultItem(item, category, index);
                });

                html += `
                        </div>
                    </div>
                `;
            }
        });

        if (totalResults > 0) {
            html += `
                <div class="border-top pt-3 mt-3">
                    <a href="/search?q=${encodeURIComponent(searchInput.value)}"
                       class="btn btn-outline-primary btn-sm w-100 search-result-link"
                       role="button">
                        View all results for "${searchInput.value}"
                    </a>
                </div>
            `;
        }

        resultsContainer.innerHTML = html;
        addResultClickHandlers();

        announceToScreenReader(`Found ${totalResults} results across ${Object.keys(results).filter(cat => results[cat].length > 0).length} categories`);
    }

    function createResultItem(item, category, index) {
        let extraInfo = '';

        switch (category) {
            case 'items':
                extraInfo = item.icon ? `<small class="text-muted">Icon: <img src="${item.icon_url}" alt="${item.icon}"></small>` : '';
                break;
            case 'npcs':
                extraInfo = item.level ? `<small class="text-muted">Level ${item.level}</small>&nbsp;|&nbsp;` : '';
                extraInfo += item.race ? `<small class="text-muted">${item.race}</small>&nbsp;|&nbsp;` : '';
                extraInfo += item.class ? `<small class="text-muted">${item.class}</small>&nbsp;|&nbsp;` : '';
                extraInfo += item.body_type ? `<small class="text-muted">${item.body_type}</small>&nbsp;|&nbsp;` : '';
                extraInfo += item.hp ? `<small class="text-muted">HP ${item.hp}</small>&nbsp;|&nbsp;` : '';
                extraInfo += item.MR ? `<small class="text-muted">MR ${item.MR}</small>` : '';
                break;
            case 'spells':
                extraInfo = item.mana ? `<small class="text-muted">${item.mana} Mana</small>` : '';
                break;
            case 'zones':
                extraInfo = item.short_name ? `<small class="text-muted">(${item.short_name})</small>` : '';
                break;
            case 'recipes':
                extraInfo = item.tradeskill ? `<small class="text-muted">Tradeskill ${item.tradeskill}</small>` : '';
                break;
        }

        return `
            <a href="${item.url}" 
               class="list-group-item list-group-item-action d-flex justify-content-between align-items-center search-result-link"
               role="option"
               aria-describedby="${category}-${index}-desc">
                <div>
                    <div class="fw-medium">${item.name}</div>
                    <div id="${category}-${index}-desc">${extraInfo}</div>
                </div>
                <i class="fas fa-arrow-right text-muted" aria-hidden="true"></i>
            </a>
        `;
    }

    function addResultClickHandlers() {
        document.querySelectorAll('.search-result-link').forEach(link => {
            link.addEventListener('click', function() {
                setTimeout(() => {
                    searchModal.hide();
                }, 100);
            });
        });
    }
});