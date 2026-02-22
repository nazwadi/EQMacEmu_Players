// base.js - global site JS

document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.querySelector('.side-nav');
    const toggle = document.querySelector('.side-nav-toggle');

    if (!sidebar || !toggle) return;

    const STORAGE_KEY = 'sideNavCollapsed';
    const isSmallScreen = window.innerWidth <= 1400;

    // Determine initial state:
    // - Small screens default to collapsed unless user explicitly opened it
    // - Large screens default to open unless user explicitly closed it
    function shouldStartCollapsed() {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored !== null) return stored === 'true';
        return isSmallScreen;
    }

    function setCollapsed(collapsed) {
        if (collapsed) {
            sidebar.classList.add('collapsed');
            toggle.classList.add('collapsed');
            toggle.title = 'Expand navigation';
            toggle.textContent = '\u203A'; // ›
        } else {
            sidebar.classList.remove('collapsed');
            toggle.classList.remove('collapsed');
            toggle.title = 'Collapse navigation';
            toggle.textContent = '\u2039'; // ‹
        }
        localStorage.setItem(STORAGE_KEY, collapsed);
    }

    // Apply initial state without transition flash
    sidebar.style.transition = 'none';
    toggle.style.transition = 'none';
    setCollapsed(shouldStartCollapsed());

    // Re-enable transitions after initial paint
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            sidebar.style.transition = '';
            toggle.style.transition = '';
        });
    });

    // Toggle on click
    toggle.addEventListener('click', function () {
        const isCollapsed = sidebar.classList.contains('collapsed');
        setCollapsed(!isCollapsed);
    });
});
