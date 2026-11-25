// Sustainable Farming Platform - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('🌱 Sustainable Farming Platform initialized');

    // Animate hero stats on load
    const stats = document.querySelectorAll('.hero-stats h3');
    stats.forEach(stat => {
        const finalValue = parseInt(stat.textContent.replace(/[^0-9]/g, ''));
        let currentValue = 0;
        const increment = finalValue / 100;

        const timer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= finalValue) {
                stat.textContent = finalValue.toLocaleString() + '+';
                clearInterval(timer);
            } else {
                stat.textContent = Math.floor(currentValue).toLocaleString() + '+';
            }
        }, 20);
    });

    // Add hover effects to feature cards
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.transition = 'transform 0.3s ease';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
});

// Utility functions
function showToast(message, type = 'info') {
    // Simple toast notification
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
    toast.textContent = message;
    toast.style.zIndex = '9999';

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Export for global access
window.FarmQuest = {
    showToast
};
