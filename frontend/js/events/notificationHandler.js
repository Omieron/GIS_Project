// Notification Types
const notificationTypes = {
    SUCCESS: {
        title: 'Başarılı'
    },
    ERROR: {
        title: 'Hata'
    },
    WARNING: {
        title: 'Uyarı'
    },
    INFO: {
        title: 'Bilgi'
    }
};

// Show notification
function showNotification(message, type = 'SUCCESS', duration = 2000) { // Süreyi 1 saniye olarak değiştirdik
    const container = document.getElementById('notification-container');
    const notificationType = notificationTypes[type];
    const notificationId = 'notification-' + Date.now();
    
    const notification = document.createElement('div');
    notification.className = `notification ${type.toLowerCase()}`;
    notification.id = notificationId;
    
    notification.innerHTML = `
        <div class="notification-content">
            <div class="notification-title">${notificationType.title}</div>
            <p class="notification-message">${message}</p>
        </div>
        <button class="notification-close">&times;</button>
    `;
    
    container.appendChild(notification);
    
    // Trigger animation
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Auto-close after duration
    const timeoutId = setTimeout(() => {
        closeNotification(notificationId);
    }, duration);
    
    // Close button handler
    notification.querySelector('.notification-close').addEventListener('click', () => {
        clearTimeout(timeoutId);
        closeNotification(notificationId);
    });
    
    return notificationId;
}

// Close notification
function closeNotification(id) {
    const notification = document.getElementById(id);
    if (!notification) return;
    
    notification.classList.add('slide-out-right'); // Sağa kayma sınıfını ekledik
    
    setTimeout(() => {
        notification.remove();
    }, 300);
}

// Loading overlay functions
function showLoading(message = 'İşlem gerçekleştiriliyor...') {
    const loader = document.getElementById('loading-overlay');
    loader.querySelector('.loading-text').textContent = message;
    loader.classList.add('visible');
}

function hideLoading() {
    const loader = document.getElementById('loading-overlay');
    loader.classList.remove('visible');
}

// Update loading message
function updateLoadingMessage(message) {
    const loader = document.getElementById('loading-overlay');
    if (!loader) return;
    
    const textElement = loader.querySelector('.loading-text');
    if (textElement) {
        textElement.textContent = message;
    }
    
    // İsteğe bağlı: Başarılı durumunda spinner'ı yeşil yapabilirsiniz
    if (message.includes("✅")) {
        const spinnerElement = loader.querySelector('.notification-loader');
        if (spinnerElement) {
            spinnerElement.style.borderTopColor = "#4CAF50";
            spinnerElement.style.animation = "none"; // Spinning durdurmak için
            spinnerElement.style.borderColor = "rgba(76, 175, 80, 0.3)";
            spinnerElement.style.borderTopColor = "#4CAF50";
        }
    }
}

// Export functions
export {
    showNotification,
    closeNotification,
    showLoading,
    hideLoading,
    updateLoadingMessage
};