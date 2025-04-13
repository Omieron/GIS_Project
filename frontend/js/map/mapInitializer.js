import { MAPBOX_API_KEY } from '../../config.js';
import { rotateGlobe, mapFlyTo } from './mapAnimation.js';

export function initMap() {
  mapboxgl.accessToken = MAPBOX_API_KEY;

  const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/streets-v12',
    center: [0, 0],          // Dünya ortası
    zoom: 1.5,               // Dünya görünsün
    bearing: 0,
    pitch: 0,
    antialias: true
  });

  map.on('load', () => {
    console.log('✅ Harita yüklendi');
    console.log('🌍 Dünya dönmeye başladı');
    rotateGlobe(map);

    // ✈️ Animasyonla hedef koordinata uç
    mapFlyTo(map);

    if (typeof onLoadCallback === 'function') {
      onLoadCallback(map);
    }
  });

  return map;
}