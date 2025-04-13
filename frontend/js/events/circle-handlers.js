import { createDraggableCircle } from '../map/circle.js';
import { circleRegistry } from '../map/circleRegistry.js';
import { showInfoCard  } from '../UI/leftTabMenu.js';

export function bindUIEvents(map) {
  document.getElementById('btn-foursquare')?.addEventListener('click', () => {
    if (!circleRegistry.has('foursquare')) {
      const marker = createDraggableCircle(map, 'foursquare');
      circleRegistry.set('foursquare', marker);
  
      // 💥 Özel event fırlat
      const event = new CustomEvent('circle:created', {
        detail: { type: 'foursquare', marker }
      });
      window.dispatchEvent(event);

      // foursquare tabını aktif et
      showInfoCard('foursquare-tab', 'Foursquare');

    } else {
      console.log("⚠️ Foursquare çemberi zaten var");
    }
  });

  document.getElementById('btn-overpass')?.addEventListener('click', () => {
    if (!circleRegistry.has('overpass')) {
      const marker = createDraggableCircle(map, 'overpass');
      circleRegistry.set('overpass', marker);

      const event = new CustomEvent('circle:created', {
        detail: { type: 'overpass', marker, id: 'overpass' }
      });
      window.dispatchEvent(event);

      // overpass tabını aktif et
      showInfoCard('overpass-tab', 'Overpass');
    } else {
      console.log('⚠️ Overpass çemberi zaten var');
    }
  });

  document.getElementById('btn-bina')?.addEventListener('click', () => {
    if (!circleRegistry.has('bina')) {
      const marker = createDraggableCircle(map, 'bina');
      circleRegistry.set('bina', marker);
  
      // 💥 Eksik olan event fırlatma
      const event = new CustomEvent('circle:created', {
        detail: { type: 'bina', marker, id: 'bina' }
      });
      window.dispatchEvent(event);
  
      // bina tabını aktif et
      showInfoCard('bina-tab', 'Bina');
    } else {
      console.log('⚠️ Bina çemberi zaten var');
    }
  });
}


