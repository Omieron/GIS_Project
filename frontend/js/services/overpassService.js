import { showNotification, showLoading, hideLoading } from '../events/notificationHandler.js';

export async function fetchOverpassData(lat, lon, radius = 500) {
  const query = `
    [out:json][timeout:25];
    (
      way["highway"](around:${radius},${lat},${lon});
    );
    out geom;
  `;

  showLoading("Yol bilgileri gelmektedir, lütfen bekleyiniz...");

  const response = await fetch('https://overpass-api.de/api/interpreter', {
    method: 'POST',
    body: query,
    headers: {
      'Content-Type': 'text/plain'
    }
  });

  hideLoading();

  if (!response.ok){ 
    hideLoading();
    showNotification("Yol verileri alınamadı", "ERROR");
    throw new Error('Overpass API hatası');
  }
  return await response.json();
}