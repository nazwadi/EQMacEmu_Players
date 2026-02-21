// Include these in your HTML:
// <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
// <script src="https://unpkg.com/@popperjs/core@2"></script>
// <script src="https://unpkg.com/tippy.js@6"></script>
// First, include the Tippy.js library in your HTML
// <script src="https://unpkg.com/@popperjs/core@2"></script>
// <script src="https://unpkg.com/tippy.js@6"></script>

document.addEventListener('DOMContentLoaded', () => {
  // Create the button element
  const button = document.createElement('button');
  button.id = 'tooltipTarget';
  button.textContent = 'Hover me';
  button.className = 'tooltip-button';
  document.body.appendChild(button);

  // Add loading state
  let loadingSpan = document.createElement('span');
  loadingSpan.textContent = 'Loading...';
  loadingSpan.style.display = 'none';
  document.body.appendChild(loadingSpan);

  // Initialize tooltip with loading state
  const tooltipInstance = tippy('#tooltipTarget', {
    content: 'Loading...',
    allowHTML: true,
    interactive: true,
    placement: 'right',
    theme: 'light'
  })[0]; // Get the first instance since tippy() returns an array

  // Fetch data when the page loads
  async function fetchTooltipData() {
    try {
      loadingSpan.style.display = 'block';
      const response = await fetch('/items/api/items/31401/');

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const tooltipData = await response.json();

      // Update tooltip content with the fetched data
      const content = `
        <div class="tooltip-content">
          <h3>${tooltipData.Name || 'Item Details'}</h3>
          <p>${tooltipData.id || 'No description available'}</p>
        </div>
      `;

      tooltipInstance.setProps({ content }); // Use setProps instead of setContent
      loadingSpan.style.display = 'none';

    } catch (error) {
      console.error('Error fetching tooltip data:', error);
      tooltipInstance.setProps({ content: 'Error loading data' });
      loadingSpan.style.display = 'none';
    }
  }

  // Start the data fetch
  fetchTooltipData();
});

// Optional: Add some basic styles
const styles = `
  .tooltip-button {
    padding: 8px 16px;
    background-color: #3490dc;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  .tooltip-button:hover {
    background-color: #2779bd;
  }

  .tooltip-content {
    padding: 10px;
  }

  .tooltip-content h3 {
    margin: 0 0 8px 0;
    font-size: 16px;
  }

  .tooltip-content p {
    margin: 0;
    font-size: 14px;
  }
`;

const styleSheet = document.createElement('style');
styleSheet.textContent = styles;
document.head.appendChild(styleSheet);