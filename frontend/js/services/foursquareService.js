import { FOURSQUARE_API_KEY } from '../../config.js';
import { showNotification, showLoading, hideLoading } from '../events/notificationHandler.js';

export async function fetchFoursquarePlaces(center, radius = 500, categoryIds = []) {
  if (!categoryIds.length) return [];

  const url = `https://api.foursquare.com/v3/places/search?ll=${center.lat},${center.lng}&radius=${radius}&categories=${categoryIds.join(',')}&limit=30`;
  
  showLoading("Foursquare bilgileri gelmektedir, lütfen bekleyiniz...");
  
  const res = await fetch(url, {
    headers: {
      Accept: 'application/json',
      Authorization: FOURSQUARE_API_KEY
    }
  });

  hideLoading();

  if (!res.ok) {
    hideLoading();
    console.error('Foursquare API hatası:', res.statusText);
    showNotification("Foursquare verileri alınamadı", "ERROR");
    return [];
  }

  const data = await res.json();
  return data.results || [];
}