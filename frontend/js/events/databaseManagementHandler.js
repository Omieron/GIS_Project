import { restoreService } from '../services/databaseManagementService.js'; 

export function initDatabaseManagement(){
    restoreDatabase();
    console.log("Database yonetim sistemi hazirlandi!");
}

function restoreDatabase() {
    const btn = document.getElementById("restore-btn");
    if (!btn) return;

    btn.addEventListener("click", async function () {
        const confirmed = confirm("Veritabanını sıfırlamak istediğinize emin misiniz?");
        if (!confirmed) return;

        await restoreService();
    });
}
