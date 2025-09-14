// Auto-refresh of metrics every 30 seconds
setInterval(function() {
    fetch('{% url "admin_api_metrics" %}')
        .then(response => response.json())
        .then(data => {
            // Update metrics in real-time
            updateMetrics(data);
        })
        .catch(error => console.log('Error updating metrics:', error));
}, 30000);

function updateMetrics(data) {
    // Implement metric updates
    console.log('Metrics updated:', data);
}

// Bootstrap tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
});

// Initialize admin panel
document.addEventListener('DOMContentLoaded', function() {
    // Initialize any admin-specific functionality
    console.log('Admin panel initialized');
});
