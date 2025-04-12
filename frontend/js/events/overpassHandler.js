import { fetchOverpassData } from '../services/overpassService.js';
import { renderOverpassLegend } from '../UI/leftTabMenu.js';
import * as turf from 'https://cdn.skypack.dev/@turf/turf';

let overpassTimeout = null;

const highwayColorMap = [
    'match',
    ['get', 'highway'],
    'motorway', '#ff0000',
    'trunk', '#ff7f00',
    'primary', '#ffa500',
    'secondary', '#ffff00',
    'tertiary', '#9acd32',
    'residential', '#00bfff',
    'unclassified', '#cccccc',
    'service', '#999999',
    'footway', '#00ff7f',
    'path', '#228b22',
    'cycleway', '#8a2be2',
    '#888888'
];

export function bindOverpassEvents(map) {
    window.addEventListener('circle:created', (e) => {
        const { type, marker } = e.detail;
        if (type !== 'overpass') return;

        console.log("🟠 Overpass çemberi oluşturuldu.");

        marker.on('dragend', () => {
            const { lng, lat } = marker.getLngLat();

            if (overpassTimeout) clearTimeout(overpassTimeout);
            overpassTimeout = setTimeout(() => {
                handleOverpassCircle(marker, map);
            }, 500);
        });

        handleOverpassCircle(marker, map);
    });
}

export async function handleOverpassCircle(marker, map) {
    const { lng, lat } = marker.getLngLat();
    const radius = 500;
  
    try {
      const data = await fetchOverpassData(lat, lng, radius); // ⬅️ dışa alınan fetch
  
      const circle = turf.circle([lng, lat], radius / 1000, { steps: 64, units: 'kilometers' });
      const bbox = turf.bbox(circle);
  
      const clippedFeatures = [];
  
      for (const el of data.elements) {
        if (el.type !== 'way' || !el.geometry) continue;
  
        const coords = el.geometry.map(p => [p.lon, p.lat]);
        const line = turf.lineString(coords, {
          id: el.id,
          highway: el.tags?.highway || 'unknown'
        });
  
        const isInside = turf.booleanWithin(line, circle);
        const intersects = turf.booleanIntersects(line, circle);
  
        if (isInside || intersects) {
          const clipped = turf.bboxClip(line, bbox);
          clippedFeatures.push(clipped);
        }
      }
  
      const finalGeoJSON = turf.featureCollection(clippedFeatures);
  
      if (map.getSource('overpass-roads')) {
        map.getSource('overpass-roads').setData(finalGeoJSON);
      } else {
        map.addSource('overpass-roads', {
          type: 'geojson',
          data: finalGeoJSON
        });
  
        map.addLayer({
          id: 'overpass-roads-layer',
          type: 'line',
          source: 'overpass-roads',
          layout: {
            'line-join': 'round',
            'line-cap': 'round'
          },
          paint: {
            'line-color': highwayColorMap,
            'line-width': 2
          }
        });
      }
  
      renderOverpassLegend(map);
      console.log(`🛣 ${clippedFeatures.length} yol çember içinde kesilerek gösterildi.`);
    } catch (err) {
      console.error('❌ Overpass API hatası:', err);
    }
  }