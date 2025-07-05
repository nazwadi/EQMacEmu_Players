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

    // Search history management
    const MAX_HISTORY_ITEMS = 5;
    const STORAGE_KEY = 'searchHistory';

    // Placeholder suggestions
    const placeholderSuggestions = [
        "Search items, spells, NPCs, zones...",
        "Try searching for 'banded mail'",
        "Try searching for 'claws of veeshan'",
        "Try searching for 'lady vox'",
        "Try searching for 'guards of qeynos'",
        "Try searching for 'complete heal'",
        "Try searching for 'fire'",
        "Try searching for 'shadow'",
        "Try searching for 'temple of veeshan'",
        "Try searching for 'vex thal'"
    ];

    let currentPlaceholderIndex = 0;
    let placeholderInterval;

    function getCSRFToken() {
        // First try to get from meta tag (most reliable)
        const metaToken = document.querySelector('meta[name="csrf-token"]');
        if (metaToken) {
            return metaToken.getAttribute('content');
        }

        // Try to get from existing form on the page
        const formToken = document.querySelector('[name="csrfmiddlewaretoken"]');
        if (formToken) {
            return formToken.value;
        }

        // Get from cookie (requires js-cookie or custom function)
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }

        return '';
    }

    function rotatePlaceholder() {
        // Only rotate if input is empty and modal is visible
        if (searchInput.value.trim() !== '' || !searchModalElement.classList.contains('show')) {
            return;
        }

        // Fade out current placeholder
        searchInput.style.opacity = '0.7';

        setTimeout(() => {
            // Change to next suggestion
            currentPlaceholderIndex = (currentPlaceholderIndex + 1) % placeholderSuggestions.length;
            searchInput.placeholder = placeholderSuggestions[currentPlaceholderIndex];

            // Fade back in
            searchInput.style.opacity = '1';
        }, 150);
    }

    function startPlaceholderRotation() {
        // Clear any existing interval
        stopPlaceholderRotation();

        // Start rotation every 3 seconds
        placeholderInterval = setInterval(rotatePlaceholder, 3000);
    }

    function stopPlaceholderRotation() {
        if (placeholderInterval) {
            clearInterval(placeholderInterval);
            placeholderInterval = null;
        }
    }

    function resetToDefaultPlaceholder() {
        searchInput.placeholder = placeholderSuggestions[0];
        searchInput.style.opacity = '1';
        currentPlaceholderIndex = 0;
    }

    function getSearchHistory() {
        try {
            const history = localStorage.getItem(STORAGE_KEY);
            return history ? JSON.parse(history) : [];
        } catch (e) {
            console.warn('Failed to load search history:', e);
            return [];
        }
    }

    function saveSearchHistory(query) {
        try {
            let history = getSearchHistory();

            // Remove if already exists (to move to top)
            history = history.filter(item => item.toLowerCase() !== query.toLowerCase());

            // Add to beginning
            history.unshift(query);

            // Keep only MAX_HISTORY_ITEMS
            history = history.slice(0, MAX_HISTORY_ITEMS);

            localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
        } catch (e) {
            console.warn('Failed to save search history:', e);
        }
    }

    function removeFromHistory(query) {
        try {
            let history = getSearchHistory();
            history = history.filter(item => item.toLowerCase() !== query.toLowerCase());
            localStorage.setItem(STORAGE_KEY, JSON.stringify(history));

            // Refresh the display if we're showing history
            if (searchInput.value.trim() === '') {
                showSearchHistory();
            }
        } catch (e) {
            console.warn('Failed to remove from search history:', e);
        }
    }

    function clearSearchHistory() {
        try {
            localStorage.removeItem(STORAGE_KEY);
            showDefaultState();
        } catch (e) {
            console.warn('Failed to clear search history:', e);
        }
    }

    function showSearchHistory() {
        const history = getSearchHistory();

        if (history.length === 0) {
            showDefaultState();
            return;
        }

        let html = `
            <div class="p-2">
                <div class="search-history-header d-flex justify-content-between align-items-center">
                    <span>Recent Searches</span>
                    <span class="search-history-clear" onclick="clearSearchHistory()">Clear All</span>
                </div>
        `;

        history.forEach(query => {
            html += `
                <div class="search-history-item" data-query="${query.replace(/"/g, '&quot;')}">
                    <i class="fas fa-history history-icon"></i>
                    <span class="history-text">${query}</span>
                    <i class="fas fa-times remove-history" data-query="${query.replace(/"/g, '&quot;')}" title="Remove from history"></i>
                </div>
            `;
        });

        html += '</div>';

        document.getElementById('searchResults').innerHTML = html;

        // Add click handlers
        document.querySelectorAll('.search-history-item').forEach(item => {
            item.addEventListener('click', function (e) {
                // Don't trigger if clicking the remove button
                if (e.target.classList.contains('remove-history')) {
                    e.stopPropagation();
                    const query = e.target.dataset.query;
                    removeFromHistory(query);
                    return;
                }

                const query = this.dataset.query;
                searchInput.value = query;
                clearSearchBtn.classList.remove('d-none');
                performSearch(query);
            });
        });

        // Add remove button handlers
        document.querySelectorAll('.remove-history').forEach(btn => {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                const query = this.dataset.query;
                removeFromHistory(query);
            });
        });
    }

    // Show/hide clear button based on input content and handle search
    searchInput.addEventListener('input', function (e) {
        const query = e.target.value.trim();

        // Stop placeholder rotation when user starts typing
        if (query.length > 0) {
            stopPlaceholderRotation();
            resetToDefaultPlaceholder();
        }

        // Show clear button if there's text, hide if empty
        if (query.length > 0) {
            clearSearchBtn.classList.remove('d-none');
        } else {
            clearSearchBtn.classList.add('d-none');
            showSearchHistory(); // Show history when input is empty

            // Restart placeholder rotation when input is empty
            setTimeout(startPlaceholderRotation, 1000); // Small delay before starting rotation
            return;
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
        showSearchHistory(); // Show history when cleared
        searchInput.focus();

        // Restart placeholder rotation after clearing
        setTimeout(startPlaceholderRotation, 1000);
    });

    // Focus input when modal is fully shown
    searchModalElement.addEventListener('shown.bs.modal', function () {
        // Store the element that had focus before modal opened
        const activeElement = document.activeElement;
        searchModalElement.setAttribute('data-previous-focus', activeElement.id || '');

        clearSearchBtn.classList.add('d-none');
        searchInput.focus();
        searchInput.select();

        // Show search history if input is empty
        if (searchInput.value.trim() === '') {
            showSearchHistory();
            // Start placeholder rotation after a delay
            setTimeout(startPlaceholderRotation, 2000);
        }
    });

    // Restore focus when modal is hidden
    searchModalElement.addEventListener('hidden.bs.modal', function () {
        // Stop placeholder rotation when modal closes
        stopPlaceholderRotation();
        resetToDefaultPlaceholder();
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
        const items = document.querySelectorAll('#searchResults .list-group-item, #searchResults .search-history-item');

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
    document.addEventListener('keydown', function (e) {
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
                item.scrollIntoView({block: 'nearest'});
            } else {
                item.classList.remove('active');
            }
        });
    }

    function announceCurrentSelection(items) {
        if (selectedIndex >= 0 && items[selectedIndex]) {
            const itemText = items[selectedIndex].querySelector('.fw-medium, .history-text')?.textContent || '';
            announceToScreenReader(`Selected ${itemText}`);
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
        // Save to search history
        if (query.trim().length >= 3) {
            saveSearchHistory(query.trim());
        }

        document.getElementById('searchResults').innerHTML = `
        <div>
            <!-- Items skeleton -->
            <div class="mb-4">
                <div class="skeleton skeleton-category mb-2"></div>
                <div class="skeleton-item d-flex align-items-center">
                    <div class="skeleton skeleton-icon"></div>
                    <div class="flex-grow-1">
                        <div class="skeleton skeleton-text wide"></div>
                        <div class="skeleton skeleton-text narrow"></div>
                    </div>
                </div>
                <div class="skeleton-item d-flex align-items-center">
                    <div class="skeleton skeleton-icon"></div>
                    <div class="flex-grow-1">
                        <div class="skeleton skeleton-text wide"></div>
                        <div class="skeleton skeleton-text narrow"></div>
                    </div>
                </div>
                <div class="skeleton-item d-flex align-items-center">
                    <div class="skeleton skeleton-icon"></div>
                    <div class="flex-grow-1">
                        <div class="skeleton skeleton-text wide"></div>
                        <div class="skeleton skeleton-text narrow"></div>
                    </div>
                </div>
            </div>
            
            <!-- NPCs skeleton -->
            <div class="mb-4">
                <div class="skeleton skeleton-category mb-2"></div>
                <div class="skeleton-item d-flex align-items-center">
                    <div class="flex-grow-1">
                        <div class="skeleton skeleton-text wide"></div>
                        <div class="skeleton skeleton-text narrow"></div>
                    </div>
                </div>
                <div class="skeleton-item d-flex align-items-center">
                    <div class="flex-grow-1">
                        <div class="skeleton skeleton-text wide"></div>
                        <div class="skeleton skeleton-text narrow"></div>
                    </div>
                </div>
            </div>
            
            <!-- Other categories skeleton -->
            <div class="mb-4">
                <div class="skeleton skeleton-category mb-2"></div>
                <div class="skeleton-item d-flex align-items-center">
                    <div class="flex-grow-1">
                        <div class="skeleton skeleton-text wide"></div>
                        <div class="skeleton skeleton-text narrow"></div>
                    </div>
                </div>
            </div>
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

    function getSearchSuggestions(query) {
        const suggestions = [];
        const lowerQuery = query.toLowerCase();

        // Suggest corrections for common misspellings
        const commonCorrections = {
            'swrd': 'sword',
            'sheild': 'shield',
            'armour': 'armor',
            'rouge': 'rogue',
            'pally': 'paladin',
            'zerker': 'berserker',
            'shaman': 'shaman',
            'kunark': 'kunark',
            'velious': 'velious'
        };

        // Check for potential corrections
        for (const [misspelled, correct] of Object.entries(commonCorrections)) {
            if (lowerQuery.includes(misspelled)) {
                suggestions.push(`Did you mean <strong>${correct}</strong>?`);
                break;
            }
        }

        // Suggest broader categories based on query
        if (lowerQuery.includes('weapon') || lowerQuery.includes('sword') || lowerQuery.includes('axe')) {
            suggestions.push('Try searching for specific weapon types like <strong>blade</strong>, <strong>staff</strong>, or <strong>bow</strong>');
        }

        if (lowerQuery.includes('armor') || lowerQuery.includes('plate') || lowerQuery.includes('chain')) {
            suggestions.push('Try searching for <strong>helm</strong>, <strong>chest</strong>, or <strong>boots</strong>');
        }

        if (lowerQuery.includes('spell') || lowerQuery.includes('magic')) {
            suggestions.push('Try searching for spell effects like <strong>heal</strong>, <strong>buff</strong>, or <strong>damage</strong>');
        }

        if (lowerQuery.includes('zone') || lowerQuery.includes('area')) {
            suggestions.push('Try searching for zone names like <strong>crushbone</strong>, <strong>gfay</strong>, or <strong>cazic</strong>');
        }

        // If no specific suggestions, provide general ones
        if (suggestions.length === 0) {
            if (query.length < 3) {
                suggestions.push('Search terms must be at least 3 characters long');
            } else if (query.length > 20) {
                suggestions.push('Try using shorter, more specific search terms');
            } else {
                suggestions.push('Try searching for broader terms or check the popular searches above');
            }
        }

        if (suggestions.length > 0) {
            return `
            <div class="mt-3">
                <div class="alert alert-info border-0 bg-primary bg-opacity-10">
                    <h6 class="alert-heading mb-2">
                        <i class="fas fa-info-circle me-2"></i>Suggestions
                    </h6>
                    ${suggestions.map(suggestion => `<p class="mb-1 small">${suggestion}</p>`).join('')}
                </div>
            </div>
        `;
        }

        return '';
    }

    function displaySearchResults(data) {
        selectedIndex = -1;
        const resultsContainer = document.getElementById('searchResults');
        const results = data.results;

        const totalResults = Object.values(results).reduce((sum, category) => sum + category.length, 0);

        searchInput.setAttribute('aria-expanded', totalResults > 0 ? 'true' : 'false');

        if (totalResults === 0) {
            const currentQuery = searchInput.value.trim();

            resultsContainer.innerHTML = `
        <div class="p-4">
            <div class="text-center text-muted mb-4">
                <i class="fas fa-search-minus mb-3" style="font-size: 2.5rem; opacity: 0.5;"></i>
                <h6 class="mb-2">No results found for "${currentQuery}"</h6>
                <p class="mb-4">We couldn't find anything matching your search. Try these suggestions:</p>
            </div>
            
            <div class="row g-3">
                <div class="col-md-6">
                    <div class="card border-0 bg-light">
                        <div class="card-body p-3">
                            <h6 class="card-title mb-2">
                                <i class="fas fa-lightbulb text-warning me-2"></i>Search Tips
                            </h6>
                            <ul class="mb-0 small text-muted">
                                <li>Check your spelling</li>
                                <li>Try shorter or more general terms</li>
                                <li>Use single words instead of phrases</li>
                                <li>Try alternative names or abbreviations</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="card border-0 bg-light">
                        <div class="card-body p-3">
                            <h6 class="card-title mb-2">
                                <i class="fas fa-star text-primary me-2"></i>Popular Searches
                            </h6>
                            <div class="d-flex flex-wrap gap-1">
                                <span class="badge bg-secondary cursor-pointer popular-search-tag" data-search="sword">sword</span>
                                <span class="badge bg-secondary cursor-pointer popular-search-tag" data-search="heal">heal</span>
                                <span class="badge bg-secondary cursor-pointer popular-search-tag" data-search="ring">ring</span>
                                <span class="badge bg-secondary cursor-pointer popular-search-tag" data-search="dragon">dragon</span>
                                <span class="badge bg-secondary cursor-pointer popular-search-tag" data-search="cleric">cleric</span>
                                <span class="badge bg-secondary cursor-pointer popular-search-tag" data-search="fire">fire</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            ${getSearchSuggestions(currentQuery)}
        </div>
    `;

            // Add click handlers for popular searches
            document.querySelectorAll('.popular-search-tag').forEach(tag => {
                tag.addEventListener('click', function () {
                    const searchTerm = this.dataset.search;
                    searchInput.value = searchTerm;
                    clearSearchBtn.classList.remove('d-none');
                    performSearch(searchTerm);
                });
            });

            announceToScreenReader(`No results found for ${currentQuery}. Try checking spelling or using different search terms.`);
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

        // Add this to your displaySearchResults function where the "View all results" button was:

        if (totalResults > 0) {
            const currentQuery = searchInput.value.trim();

            html += `
        <div class="border-top pt-3 mt-3">
            <p class="text-center text-muted small mb-2">Need more results? Search specific categories:</p>
            <div class="d-flex flex-wrap gap-1 justify-content-center">
    `;

            // Only show buttons for categories that have results
            if (results.items && results.items.length > 0) {
                html += `
            <form action="/items/search" method="POST" class="d-inline" target="_blank">
                <input type="hidden" name="csrfmiddlewaretoken" value="${getCSRFToken()}">
                <input type="hidden" name="item_name" value="${currentQuery}">
                <input type="hidden" name="query_limit" value="200">
                <button type="submit" class="btn btn-outline-secondary btn-sm">
                    More Items (${results.items.length}+)
                </button>
            </form>
        `;
            }

            if (results.spells && results.spells.length > 0) {
                html += `
            <form action="/spells/search" method="POST" class="d-inline" target="_blank">
                <input type="hidden" name="csrfmiddlewaretoken" value="${getCSRFToken()}">
                <input type="hidden" name="spell_name" value="${currentQuery}">
                <button type="submit" class="btn btn-outline-secondary btn-sm">
                    More Spells (${results.spells.length}+)
                </button>
            </form>
        `;
            }

            if (results.npcs && results.npcs.length > 0) {
                html += `
            <form action="/npcs/search" method="POST" class="d-inline" target="_blank">
                <input type="hidden" name="csrfmiddlewaretoken" value="${getCSRFToken()}">
                <input type="hidden" name="npc_name" value="${currentQuery}">
                <button type="submit" class="btn btn-outline-secondary btn-sm">
                    More NPCs (${results.npcs.length}+)
                </button>
            </form>
        `;
            }

            if (results.recipes && results.recipes.length > 0) {
                html += `
            <form action="/recipes/search" method="POST" class="d-inline" target="_blank">
                <input type="hidden" name="csrfmiddlewaretoken" value="${getCSRFToken()}">
                <input type="hidden" name="recipe_name" value="${currentQuery}">
                <button type="submit" class="btn btn-outline-secondary btn-sm">
                    More Recipes (${results.recipes.length}+)
                </button>
            </form>
        `;
            }

            if (results.factions && results.factions.length > 0) {
                html += `
            <form action="/factions/search" method="POST" class="d-inline" target="_blank">
                <input type="hidden" name="csrfmiddlewaretoken" value="${getCSRFToken()}">
                <input type="hidden" name="faction_name" value="${currentQuery}">
                <button type="submit" class="btn btn-outline-secondary btn-sm">
                    More Factions (${results.factions.length}+)
                </button>
            </form>
        `;
            }

            // Add other categories as needed...

            html += `
            </div>
        </div>
    `;
        }

        resultsContainer.innerHTML = html;
        addResultClickHandlers();

        announceToScreenReader(`Found ${totalResults} results across ${Object.keys(results).filter(cat => results[cat].length > 0).length} categories`);
    }

    function createResultItem(item, category, index) {
        let extraInfo = '';
        let iconHtml = '';

        switch (category) {
            case 'items':
                iconHtml = item.icon ? `<img src="${item.icon_url}" alt="Item icon" class="me-2" style="width: 24px; height: 24px;">` : '';
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
                iconHtml = item.custom_icon ? `<img src="/static/images/icons/${item.custom_icon}.gif" alt="${item.custom_icon}.gif" class="me-2" style="width: 24px; height: 24px;"/>` : '';
                extraInfo = item.mana ? `<small class="text-muted">${item.mana} Mana</small>` : '';
                break;
            case 'zones':
                extraInfo = item.short_name ? `<small class="text-muted">(${item.short_name})</small>` : '';
                break;
            case 'recipes':
                extraInfo = item.tradeskill ? `<small class="text-muted">${item.tradeskill}</small>` : '';
                break;
        }

        return `
            <a href="${item.url}" 
               class="list-group-item list-group-item-action d-flex justify-content-between align-items-center search-result-link"
               role="option"
               aria-describedby="${category}-${index}-desc">
               <div class="d-flex align-items-center">
                <div>
                    <div class="fw-medium">${iconHtml} ${item.name}</div>
                    <div id="${category}-${index}-desc">${extraInfo}</div>
                </div>
                </div>
                <i class="fas fa-arrow-right text-muted" aria-hidden="true"></i>
            </a>
        `;
    }

    function addResultClickHandlers() {
        document.querySelectorAll('.search-result-link').forEach(link => {
            link.addEventListener('click', function () {
                setTimeout(() => {
                    searchModal.hide();
                }, 100);
            });
        });
    }

    // Make clearSearchHistory available globally for onclick
    window.clearSearchHistory = clearSearchHistory;
});