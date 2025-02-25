// checkbox-cookie-manager.js
document.addEventListener('DOMContentLoaded', function() {
    // Process markdown2 task list output to match GitHub style
    processTaskLists();

    // Get the quest ID from the page
    const questId = getQuestIdFromPage();

    // Initialize checkboxes when the page loads
    initializeCheckboxes(questId);

    // Function to get the quest ID from the page
    function getQuestIdFromPage() {
        // Try to get quest ID directly from URL path
        // Example: if URL is /quests/view/123, extract 123
        const pathParts = window.location.pathname.split('/');
        const questIdFromPath = pathParts[pathParts.length - 1];
        if (questIdFromPath && !isNaN(questIdFromPath)) {
            return questIdFromPath;
        }

        // Try to get from quest title
        const questTitle = document.querySelector('.quest-title');
        if (questTitle) {
            return questTitle.textContent.trim();
        }

        // If all else fails, use the full page URL as a unique identifier
        return window.location.pathname;
    }

    // Process markdown2 task list output to match GitHub style
    function processTaskLists() {
        const content = document.querySelector('.quest-description-content');
        if (!content) return;

        // Find all lists in the content
        const lists = content.querySelectorAll('ul');

        lists.forEach(list => {
            // Check if this list contains checkbox items
            const checkboxItems = list.querySelectorAll('li input[type="checkbox"]');

            if (checkboxItems.length > 0) {
                // This is a task list
                list.classList.add('task-list');

                // Process each list item with a checkbox
                checkboxItems.forEach(checkbox => {
                    const li = checkbox.closest('li');

                    // Wrap text after checkbox in a span
                    const textNode = Array.from(li.childNodes).find(node =>
                        node.nodeType === Node.TEXT_NODE && node.textContent.trim() !== ''
                    );

                    if (textNode) {
                        const span = document.createElement('span');
                        span.textContent = textNode.textContent;
                        textNode.replaceWith(span);
                    }
                });
            }
        });
    }

    // Initialize checkboxes based on saved cookie data
    function initializeCheckboxes(questId) {
        // Get all checkboxes in the quest description content area
        const checkboxes = document.querySelectorAll('.quest-description-content input[type="checkbox"]');

        if (checkboxes.length === 0) {
            return; // No checkboxes found, nothing to do
        }

        // Get saved checkbox states from cookie
        const savedStates = getSavedCheckboxStates(questId);

        // Apply saved states to checkboxes and add event listeners
        checkboxes.forEach((checkbox, index) => {
            // Set a unique identifier for each checkbox
            checkbox.setAttribute('data-checkbox-id', index);

            // Apply saved state if it exists
            if (savedStates && savedStates[index] !== undefined) {
                checkbox.checked = savedStates[index];
            }

            // Add event listener to save state on change
            checkbox.addEventListener('change', function() {
                saveCheckboxState(questId);
            });
        });
    }

    // Save the state of all checkboxes to a cookie
    function saveCheckboxState(questId) {
        const checkboxes = document.querySelectorAll('.quest-description-content input[type="checkbox"]');
        const states = {};

        checkboxes.forEach((checkbox, index) => {
            states[index] = checkbox.checked;
        });

        // Create cookie name using the quest ID
        const cookieName = `quest_checkboxes_${questId.replace(/[^a-z0-9]/gi, '_')}`;

        // Save to cookie (expires in 30 days)
        const expiryDate = new Date();
        expiryDate.setDate(expiryDate.getDate() + 30);

        document.cookie = `${cookieName}=${JSON.stringify(states)}; expires=${expiryDate.toUTCString()}; path=/; SameSite=Lax`;
    }

    // Get saved checkbox states from cookie
    function getSavedCheckboxStates(questId) {
        const cookieName = `quest_checkboxes_${questId.replace(/[^a-z0-9]/gi, '_')}`;
        const cookies = document.cookie.split(';');

        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === cookieName && value) {
                try {
                    return JSON.parse(value);
                } catch (e) {
                    console.error('Error parsing cookie value:', e);
                    return null;
                }
            }
        }

        return null;
    }
});