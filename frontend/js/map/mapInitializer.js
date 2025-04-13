import { MAPBOX_API_KEY } from '../../config.js';

export function initMap() {
  mapboxgl.accessToken = MAPBOX_API_KEY;

  const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/streets-v12',
    center: [27.024772, 39.596321],
    zoom: 15,
    pitch: 60,
    bearing: -17.6,
    antialias: true
  });

  map.on('load', () => {
    console.log('✅ Harita yüklendi');
    if (typeof onLoadCallback === 'function') {
      onLoadCallback(map);
    }
  });

  return map;
}