import { createDraggableCircle } from '../map/circle.js';
import { circleRegistry } from '../map/circleRegistry.js';
import { fetchFoursquarePlaces } from '../services/foursquareService.js';

const categoryIcons = {
  13032: '../js/assets/cofee.png',     // cafe
  17145: '../js/assets/pharmacy.png', // pharmacy
  15014: '../js/assets/hospital.png', // hospital
  17144: '../js/assets/market.png',   // market
  19007: '../js/assets/gas.png',      // fuel
  16032: '../js/assets/park.png'      // park
};

let activeMarkerLayer = [];

export function bindFoursquareEvents(map) {
  window.addEventListener('circle:created', (e) => {
    const { type, marker } = e.detail;
    if (type !== 'foursquare') return;

    console.log("🟢 Foursquare çemberi oluşturuldu, panel açılıyor...");

    const card = document.getElementById('foursquare-card');
    card.style.display = 'block';

    // Panel içeriğini temizle ve yeniden oluştur
    card.innerHTML = '<strong>Foursquare Kategorileri</strong><br/><br/>';

    const categoryMapping = {
      cafe: 13032,
      pharmacy: 17145,
      hospital: 15014,
      market: 17144,
      fuel: 19007,
      park: 16032
    };

    // Tümünü Seç Toggle
    const toggleAllLabel = document.createElement('label');
    toggleAllLabel.style.display = 'flex';
    toggleAllLabel.style.alignItems = 'center';
    toggleAllLabel.style.marginBottom = '12px';
    toggleAllLabel.style.fontWeight = 'bold';

    const toggleAllInput = document.createElement('input');
    toggleAllInput.type = 'checkbox';
    toggleAllInput.style.marginRight = '8px';
    toggleAllInput.dataset.toggleAll = 'true';

    toggleAllInput.addEventListener('change', async () => {
      const allCheckboxes = card.querySelectorAll('input[type="checkbox"]:not([data-toggle-all])');
      allCheckboxes.forEach(cb => cb.checked = toggleAllInput.checked);

      const selected = getSelectedCategories(card);
      const coord = marker.getLngLat();
      clearFoursquareMarkers();
      const places = await fetchFoursquarePlaces(coord, 500, selected);
      addFoursquareMarkers(map, places);
    });

    toggleAllLabel.appendChild(toggleAllInput);
    toggleAllLabel.appendChild(document.createTextNode('Tümünü Seç'));
    card.appendChild(toggleAllLabel);

    // Kategori checkboxları
    Object.entries(categoryMapping).forEach(([key, value]) => {
      const label = document.createElement('label');
      label.style.cssText = 'display: flex; align-items: center; margin-bottom: 6px;';

      const input = document.createElement('input');
      input.type = 'checkbox';
      input.style.marginRight = '8px';
      input.dataset.catId = value;

      input.addEventListener('change', async () => {
        const selected = getSelectedCategories(card);
        const coord = marker.getLngLat();
        clearFoursquareMarkers();
        const places = await fetchFoursquarePlaces(coord, 500, selected);
        addFoursquareMarkers(map, places);
      });

      label.appendChild(input);
      label.appendChild(document.createTextNode(key));
      card.appendChild(label);
    });
  });
}

function getSelectedCategories(card) {
  const selected = [];
  card.querySelectorAll('input[type="checkbox"]:not([data-toggle-all])').forEach((cb) => {
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
    const categoryId = place.categories?.[0]?.id;
    const iconUrl = categoryIcons[categoryId];

    const el = document.createElement('div');
    el.className = 'fsq-marker';

    if (iconUrl) {
      el.style.backgroundImage = `url(${iconUrl})`;
      el.style.width = '32px';
      el.style.height = '32px';
      el.style.backgroundSize = 'cover';
      el.style.borderRadius = '50%';
    } else {
      el.style.width = '10px';
      el.style.height = '10px';
      el.style.backgroundColor = 'red';
      el.style.borderRadius = '50%';
    }

    const marker = new mapboxgl.Marker(el)
      .setLngLat([place.geocodes.main.longitude, place.geocodes.main.latitude])
      .setPopup(new mapboxgl.Popup().setText(place.name))
      .addTo(map);

    activeMarkerLayer.push(marker);
  }
}