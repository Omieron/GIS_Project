import { createDraggableCircle } from '../map/circle.js';
import { circleRegistry } from '../map/circleRegistry.js';
import { showInfoCard } from '../UI/leftMenuToggle.js';

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

  document.getElementById('btn-tomtom')?.addEventListener('click', () => {
    if (!circleRegistry.has('tomtom')) {
      const marker = createDraggableCircle(map, 'tomtom');
      circleRegistry.set('tomtom', marker);

      // tomtom tabını aktif et
      showInfoCard('tomtom-tab', 'TomTom');

    } else {
      console.log('⚠️ TomTom çemberi zaten var');
    }
  });
}


export function removeCircle(id) {
  if (!circleRegistry.has(id)) return false;

  const marker = circleRegistry.get(id);

  const map = marker?.__map;
  const sourceId = marker?.__circleSourceId;
  const layerId = marker?.__circleLayerId;

  if (marker && typeof marker.remove === 'function') {
    marker.remove();
  }

  if (map && sourceId && layerId) {
    if (map.getLayer(layerId)) {
      map.removeLayer(layerId);
      console.log(`✅ Layer '${layerId}' silindi.`);
    }
    if (map.getSource(sourceId)) {
      map.removeSource(sourceId);
      console.log(`✅ Source '${sourceId}' silindi.`);
    }

    // 🛣️ Overpass özel katmanları
    if (id === 'overpass') {
      if (map.getLayer('overpass-roads-layer')) {
        map.removeLayer('overpass-roads-layer');
        console.log("🧹 Overpass roads layer silindi.");
      }
      if (map.getSource('overpass-roads')) {
        map.removeSource('overpass-roads');
        console.log("🧹 Overpass roads source silindi.");
      }
    }

    // 📍 Foursquare özel marker'lar
    if (id === 'foursquare') {
      // DOM'daki tüm .fsq-marker öğelerini kaldır
      document.querySelectorAll('.fsq-marker').forEach(m => m.remove());
      // Yükleniyor div'i varsa kaldır
      document.getElementById('fsq-loading')?.remove();
      // Sol alttaki Foursquare panelini gizle
      document.getElementById('foursquare-card')?.style.setProperty('display', 'none', 'important');
      // Cache varsa sıfırla
      if (window.placesCache) window.placesCache.foursquare = {};
      console.log("🧽 Foursquare marker'ları temizlendi.");
    }

  } else {
    console.warn('❌ Map ya da layer/source erişimi başarısız.');
  }

  circleRegistry.delete(id);
  return true;
}