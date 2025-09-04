function switchSection(section) {
    // Update main nav active state
    document.querySelectorAll('.navbar-nav .nav-link').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.section === section) {
            item.classList.add('active');
        }
    });

    // Hide all side nav sections
    document.querySelectorAll('.side-nav-section').forEach(section => {
        section.style.display = 'none';
    });

    // Show relevant side nav section
    const targetSection = document.getElementById(section + '-nav');
    if (targetSection) {
        targetSection.style.display = 'block';
    }
}

// Add click handlers for main nav
document.querySelectorAll('.navbar-nav .nav-link[data-section]').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        switchSection(item.dataset.section);
    });
});