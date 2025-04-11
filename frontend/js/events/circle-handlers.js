import { createDraggableCircle } from '../map/circle.js';
import { circleRegistry } from '../map/circleRegistry.js';

export function bindUIEvents(map) {
  document.getElementById('btn-foursquare')?.addEventListener('click', () => {
    if (!circleRegistry.has('foursquare')) {
      console.log("✅ Yeni Foursquare circle oluşturuluyor");
      const marker = createDraggableCircle(map, 'foursquare');
      circleRegistry.set('foursquare', marker);
    } else {
      console.log("⚠️ Foursquare çemberi zaten var");
    }
  });

  document.getElementById('btn-overpass')?.addEventListener('click', () => {
    if (!circleRegistry.has('overpass')) {
      const marker = createDraggableCircle(map, 'overpass');
      circleRegistry.set('overpass', marker);
    } else {
      console.log('⚠️ Overpass çemberi zaten var');
    }
  });

  document.getElementById('btn-tomtom')?.addEventListener('click', () => {
    if (!circleRegistry.has('tomtom')) {
      const marker = createDraggableCircle(map, 'tomtom');
      circleRegistry.set('tomtom', marker);
    } else {
      console.log('⚠️ TomTom çemberi zaten var');
    }
  });
}