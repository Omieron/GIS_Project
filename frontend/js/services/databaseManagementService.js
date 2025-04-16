import { showNotification, showLoading, hideLoading, updateLoadingMessage } from '../events/notificationHandler.js';

const settingsToggle = document.getElementById("settings-toggle");

export async function restoreService() {
    try {
        
        showLoading("Veritabanı sıfırlanıyor, lütfen bekleyiniz...");
        settingsToggle.click();

        const response = await fetch("http://localhost:8001/maks/yapi/restore", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // Başarılı mesajını göstermeden doğrudan kapatıyoruz
            hideLoading();
            
            // Ve notification göster
            showNotification("Veritabanı başarıyla geri yüklendi.", "SUCCESS");
        } else {
            // Hata durumunda
            hideLoading();
            showNotification("Geri yükleme sırasında bir hata oluştu.", "ERROR");
        }
    } catch (error) {
        console.error("İstek sırasında bir hata oluştu:", error);
        hideLoading();
        showNotification("Bağlantı hatası ya da sunucu yanıt vermiyor.", "ERROR");
    }
}

export async function cloneService() {
    try {
        
        showLoading("Veritabanı yedekleniyor, lütfen bekleyiniz...");
        settingsToggle.click();

        const response = await fetch("http://localhost:8001/maks/yapi/clone", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // Başarılı mesajını göstermeden doğrudan kapatıyoruz
            hideLoading();
            
            // Ve notification göster
            showNotification("Veritabanı başarıyla yedeklendi.", "SUCCESS");
        } else {
            // Hata durumunda
            hideLoading();
            showNotification("Yedekleme sırasında bir hata oluştu.", "ERROR");
        }
    } catch (error) {
        console.error("İstek sırasında bir hata oluştu:", error);
        hideLoading();
        showNotification("Bağlantı hatası ya da sunucu yanıt vermiyor.", "ERROR");
    }
}