/**
 * Shared permission toggle logic for all Magelo character pages.
 * Handles CSRF token resolution, the fetch call, toast feedback,
 * and reverting the toggle on failure.
 */

async function updatePermission(permission, value, characterName) {
    try {
        let csrftoken = null;

        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        if (csrfMeta) csrftoken = csrfMeta.getAttribute('content');

        if (!csrftoken) {
            const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
            if (csrfInput) csrftoken = csrfInput.value;
        }

        if (!csrftoken) {
            for (const cookie of document.cookie.split(';')) {
                const c = cookie.trim();
                if (c.startsWith('csrftoken=')) {
                    csrftoken = c.substring('csrftoken='.length);
                    break;
                }
            }
        }

        if (!csrftoken) throw new Error('CSRF token not found');

        const response = await fetch('/magelo/update_permission/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({ permission, value, character_name: characterName })
        });

        const result = await response.json();

        if (!response.ok) throw new Error(result.error || 'Failed to update permission');

        if (result.success) {
            showPermissionToast(`${permission.replace(/_/g, ' ')} ${value ? 'enabled' : 'disabled'} for ${characterName}`);
            setTimeout(() => window.location.reload(), 1000);
        } else {
            showPermissionToast(result.error || 'Failed to update permission', 'danger');
            const el = document.getElementById(`${permission}Toggle`);
            if (el) el.checked = !value;
        }
    } catch (error) {
        console.error('Error updating permission:', error);
        showPermissionToast(error.message || 'Error updating permission', 'danger');
        const el = document.getElementById(`${permission}Toggle`);
        if (el) el.checked = !value;
    }
}

function showPermissionToast(message, type = 'success') {
    const container = document.createElement('div');
    container.style.cssText = 'position:fixed;top:20px;right:20px;z-index:1050;';

    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto"
                    data-bs-dismiss="toast" aria-label="Close"></button>
        </div>`;

    container.appendChild(toast);
    document.body.appendChild(container);

    const bsToast = new bootstrap.Toast(toast, { autohide: true, delay: 3000 });
    bsToast.show();
    toast.addEventListener('hidden.bs.toast', () => container.remove());
}
