// checkbox-cookie-manager.js
document.addEventListener('DOMContentLoaded', function () {
    const questId = getQuestIdFromPage();

    processTaskLists(questId);
    initializeCheckboxes(questId);

    function getQuestIdFromPage() {
        const pathParts = window.location.pathname.split('/');
        const id = pathParts[pathParts.length - 1];
        if (id && !isNaN(id)) return id;
        const title = document.querySelector('.quest-title');
        if (title) return title.textContent.trim();
        return window.location.pathname;
    }

    // Enhance markdown2 task list output:
    //  - adds unique IDs to each checkbox
    //  - wraps the text node in a <span> for the strikethrough CSS rule
    //  - wraps <input> + <span> in a <label> for a full-row click target and
    //    proper screen-reader association
    //  - appends a single "Reset progress" button after the last task list
    function processTaskLists(questId) {
        const content = document.querySelector('.quest-description-content');
        if (!content) return;

        const safeId = questId.replace(/[^a-z0-9]/gi, '_');
        let globalIndex = 0;
        let lastTaskList = null;

        content.querySelectorAll('ul').forEach(list => {
            const checkboxItems = list.querySelectorAll('li input[type="checkbox"]');
            if (checkboxItems.length === 0) return;

            list.classList.add('task-list');
            lastTaskList = list;

            checkboxItems.forEach(checkbox => {
                const li = checkbox.closest('li');
                const uid = `task-cb-${safeId}-${globalIndex++}`;
                checkbox.id = uid;

                // Wrap text node in a <span> so the :checked + span rule works
                const textNode = Array.from(li.childNodes).find(
                    n => n.nodeType === Node.TEXT_NODE && n.textContent.trim() !== ''
                );
                let span;
                if (textNode) {
                    span = document.createElement('span');
                    span.textContent = textNode.textContent;
                    textNode.replaceWith(span);
                }

                // Wrap checkbox + span in a <label> for full-row hit target + a11y
                const label = document.createElement('label');
                label.htmlFor = uid;
                label.className = 'task-label';
                li.insertBefore(label, checkbox);
                label.appendChild(checkbox);
                if (span) label.appendChild(span);
            });
        });

        if (lastTaskList) {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'task-reset-btn';
            btn.textContent = 'Reset progress';
            btn.setAttribute('aria-label', 'Uncheck all task list items');
            lastTaskList.after(btn);
        }
    }

    function initializeCheckboxes(questId) {
        const checkboxes = document.querySelectorAll('.quest-description-content input[type="checkbox"]');
        if (checkboxes.length === 0) return;

        const savedStates = getSavedCheckboxStates(questId);

        checkboxes.forEach((checkbox, index) => {
            checkbox.setAttribute('data-checkbox-id', index);

            if (savedStates && savedStates[index] !== undefined) {
                checkbox.checked = savedStates[index];
            }

            // Drive visual state via class — bypasses the deferred :checked
            // repaint that some browsers apply to inputs previously rendered
            // as disabled (which markdown2's task_list extension does).
            checkbox.classList.toggle('is-checked', checkbox.checked);

            // Keep class in sync immediately on every click (fires after the
            // browser has already toggled checkbox.checked).
            checkbox.addEventListener('click', function () {
                this.classList.toggle('is-checked', this.checked);
            });

            checkbox.addEventListener('change', function () {
                saveCheckboxState(questId);
            });
        });

        // Reset button: uncheck everything and clear the saved cookie
        const resetBtn = document.querySelector('.quest-description-content .task-reset-btn');
        if (resetBtn) {
            resetBtn.addEventListener('click', function () {
                checkboxes.forEach(cb => {
                    cb.checked = false;
                    cb.classList.remove('is-checked');
                });
                const cookieName = `quest_checkboxes_${questId.replace(/[^a-z0-9]/gi, '_')}`;
                document.cookie = `${cookieName}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; SameSite=Lax`;
            });
        }
    }

    function saveCheckboxState(questId) {
        const checkboxes = document.querySelectorAll('.quest-description-content input[type="checkbox"]');
        const states = {};
        checkboxes.forEach((checkbox, index) => {
            states[index] = checkbox.checked;
        });
        const cookieName = `quest_checkboxes_${questId.replace(/[^a-z0-9]/gi, '_')}`;
        const expiryDate = new Date();
        expiryDate.setDate(expiryDate.getDate() + 30);
        document.cookie = `${cookieName}=${JSON.stringify(states)}; expires=${expiryDate.toUTCString()}; path=/; SameSite=Lax`;
    }

    function getSavedCheckboxStates(questId) {
        const cookieName = `quest_checkboxes_${questId.replace(/[^a-z0-9]/gi, '_')}`;
        for (const cookie of document.cookie.split(';')) {
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
