document.addEventListener('DOMContentLoaded', function () {
    const searchModal = new bootstrap.Modal(document.getElementById('searchModal'));
    const searchModalElement = document.getElementById('searchModal');
    const searchButton = document.querySelector('.btn.btn-outline-secondary.fas.fa-search');
    const searchInput = document.getElementById('searchInput');

    let searchTimeout;
    let currentRequest;

    // Focus input when modal is fully shown
    searchModalElement.addEventListener('shown.bs.modal', function () {
        searchInput.focus();
        searchInput.select();
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

    // Search functionality
    searchInput.addEventListener('input', function (e) {
        const query = e.target.value.trim();

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

    // Placeholder functions - we'll implement these next
    function showDefaultState() {
        document.getElementById('searchResults').innerHTML = `
            <div class="text-center text-muted">
                <p>Start typing to search across all categories...</p>
            </div>
        `;
    }

    function performSearch(query) {
        // Show loading state
        document.getElementById('searchResults').innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2 text-muted">Searching...</p>
        </div>
    `;

        // Create abort controller for this request
        const controller = new AbortController();
        currentRequest = controller;

        // Make the search request
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

    let selectedIndex = -1;
    const resultItems = [];

    searchInput.addEventListener('keydown', function (e) {
        const items = document.querySelectorAll('#searchResults .list-group-item');

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
            updateSelection(items);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedIndex = Math.max(selectedIndex - 1, -1);
            updateSelection(items);
        } else if (e.key === 'Enter' && selectedIndex >= 0) {
            e.preventDefault();
            items[selectedIndex].click();
        }
    });

    function updateSelection(items) {
        items.forEach((item, index) => {
            if (index === selectedIndex) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    }


    function displaySearchResults(data) {
        selectedIndex = -1; // Reset selection
        const resultsContainer = document.getElementById('searchResults');
        const results = data.results;

        // Count total results
        const totalResults = Object.values(results).reduce((sum, category) => sum + category.length, 0);

        if (totalResults === 0) {
            resultsContainer.innerHTML = `
            <div class="text-center text-muted">
                <p>No results found. Try a different search term.</p>
            </div>
        `;
            return;
        }

        let html = '';

        // Display each category that has results
        Object.entries(results).forEach(([category, items]) => {
            if (items.length > 0) {
                const categoryName = category.charAt(0).toUpperCase() + category.slice(1);
                html += `
                <div class="mb-4">
                    <h6 class="text-muted text-uppercase fw-bold mb-2">${categoryName} (${items.length})</h6>
                    <div class="list-group list-group-flush">
            `;

                items.forEach(item => {
                    html += createResultItem(item, category);
                });

                html += `
                    </div>
                </div>
            `;
            }
        });
        // Add this at the end of displaySearchResults, before setting innerHTML
        if (totalResults > 0) {
            html += `
        <div class="border-top pt-3 mt-3">
            <a href="/search?q=${encodeURIComponent(document.getElementById('searchInput').value)}"
               class="btn btn-outline-primary btn-sm w-100">
                View all results for "${document.getElementById('searchInput').value}"
            </a>
        </div>
    `;
        }

        resultsContainer.innerHTML = html;
    }

    function createResultItem(item, category) {
        let extraInfo = '';

        // Add category-specific extra information
        switch (category) {
            case 'items':
                extraInfo = item.icon ? `<small class="text-muted">Icon: ${item.icon}</small>` : '';
                break;
            case 'npcs':
                extraInfo = item.level ? `<small class="text-muted">Level ${item.level}</small>` : '';
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
        <a href="${item.url}" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
            <div>
                <div class="fw-medium">${item.name}</div>
                ${extraInfo}
            </div>
            <i class="fas fa-arrow-right text-muted"></i>
        </a>
    `;
    }

});
