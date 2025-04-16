export async function restoreService() {
    try {
        alert("Sıfırlama işlemi başlatıldı, lütfen bekleyiniz!");

        const response = await fetch("http://localhost:8001/maks/yapi/restore", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        });

        const result = await response.json();

        if (response.ok) {
            alert(result.message || "✅ Geri yükleme başarılı.");
        } else {
            alert(result.detail || "🔥 Bir hata oluştu.");
        }
    } catch (error) {
        console.error("İstek sırasında bir hata oluştu:", error);
        alert("❌ Bağlantı hatası ya da sunucu yanıt vermiyor.");
    }
}
