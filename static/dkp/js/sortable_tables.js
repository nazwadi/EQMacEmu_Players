function initSortableTable(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;

    const headers = table.querySelectorAll('th[data-sort]');
    let currentCol = null;
    let currentDir = 'asc';

    headers.forEach(th => {
        th.style.cursor = 'pointer';
        th.style.userSelect = 'none';

        // Add sort indicator
        const indicator = document.createElement('span');
        indicator.className = 'sort-indicator';
        indicator.style.cssText = 'margin-left:5px; color:#555; font-size:10px;';
        indicator.textContent = '↕';
        th.appendChild(indicator);

        th.addEventListener('click', function() {
            const col = this.dataset.sort;
            const type = this.dataset.type || 'string';

            if (currentCol === col) {
                currentDir = currentDir === 'asc' ? 'desc' : 'asc';
            } else {
                currentCol = col;
                currentDir = 'asc';
            }

            // Update indicators
            headers.forEach(h => h.querySelector('.sort-indicator').textContent = '↕');
            headers.forEach(h => h.querySelector('.sort-indicator').style.color = '#555');
            this.querySelector('.sort-indicator').textContent = currentDir === 'asc' ? '↑' : '↓';
            this.querySelector('.sort-indicator').style.color = '#fcc721';

            sortTable(table, col, type, currentDir);
        });
    });
}

function sortTable(table, col, type, dir) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    rows.sort((a, b) => {
        const aCell = a.querySelector(`td[data-col="${col}"]`);
        const bCell = b.querySelector(`td[data-col="${col}"]`);
        if (!aCell || !bCell) return 0;

        let aVal = aCell.dataset.value || aCell.textContent.trim();
        let bVal = bCell.dataset.value || bCell.textContent.trim();

        if (type === 'number') {
            aVal = parseFloat(aVal) || 0;
            bVal = parseFloat(bVal) || 0;
            return dir === 'asc' ? aVal - bVal : bVal - aVal;
        } else if (type === 'date') {
            aVal = new Date(aVal);
            bVal = new Date(bVal);
            return dir === 'asc' ? aVal - bVal : bVal - aVal;
        } else {
            return dir === 'asc'
                ? aVal.localeCompare(bVal)
                : bVal.localeCompare(aVal);
        }
    });

    rows.forEach(row => tbody.appendChild(row));
}

// In sortable_tables.js — auto-init any table with data-sortable attribute
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('table[data-sortable]').forEach(table => {
        if (table.id) initSortableTable(table.id);
    });
});