import { createDraggableCircle } from '../map/circle.js';
import { circleRegistry } from '../map/circleRegistry.js';
import { fetchFoursquarePlaces } from '../services/foursquareService.js';

let activeMarkerLayer = [];

export function bindFoursquareEvents(map) {
  document.getElementById('btn-foursquare')?.addEventListener('click', () => {
    if (circleRegistry.has('foursquare')) {
      console.log("⚠️ Foursquare çemberi zaten var.");
      return;
    }

    console.log("✅ Yeni Foursquare çemberi oluşturuluyor.");
    const marker = createDraggableCircle(map, 'foursquare', 500);
    circleRegistry.set('foursquare', marker);

    // 🔥 Paneli göster
    const card = document.getElementById('foursquare-card');
    card.style.display = 'block';

    // 🔁 Dinleyicileri her input’a ekle
    card.querySelectorAll('input[type="checkbox"]').forEach((input) => {
      if (input.dataset.bound) return; // tekrar bind edilmesin

      input.addEventListener('change', async () => {
        const selected = getSelectedCategories(card);
        const coord = marker.getLngLat();

        clearFoursquareMarkers();
        const places = await fetchFoursquarePlaces(coord, 500, selected);
        addFoursquareMarkers(map, places);
      });

      input.dataset.bound = 'true'; // bir kere bind edildi
    });
  });
}

function getSelectedCategories(card) {
  const selected = [];
  card.querySelectorAll('input[type="checkbox"]').forEach((cb) => {
    if (cb.checked) selected.push(cb.dataset.catId);
  });
  return selected;
}

function clearFoursquareMarkers() {
  activeMarkerLayer.forEach((marker) => marker.remove());
  activeMarkerLayer = [];
}

function addFoursquareMarkers(map, places) {
  for (const place of places) {
    const marker = new mapboxgl.Marker()
      .setLngLat([place.geocodes.main.longitude, place.geocodes.main.latitude])
      .setPopup(new mapboxgl.Popup().setText(place.name))
      .addTo(map);

    activeMarkerLayer.push(marker);
  }
}