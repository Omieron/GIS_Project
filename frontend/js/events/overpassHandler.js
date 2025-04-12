import { fetchOverpassData } from '../services/overpassService.js';
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
        // ✅ Overpass'tan doğrudan koordinatlarla veri çek (out geom)
        const query = `
      [out:json];
      (
        way["highway"](around:${radius},${lat},${lng});
      );
      out geom;
    `;
        const response = await fetch('https://overpass-api.de/api/interpreter', {
            method: "POST",
            body: query,
            headers: { "Content-Type": "text/plain" }
        });

        const data = await response.json();

        // ✅ Turf çember ve bbox
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

            // 🔍 TAMAMEN içeride OLAN ya da sınırı geçen yollar
            const isInside = turf.booleanWithin(line, circle);
            const intersects = turf.booleanIntersects(line, circle);

            if (isInside || intersects) {
                const clipped = turf.bboxClip(line, bbox); // sadece görsel sadeleştirme
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

        console.log(`🛣 ${clippedFeatures.length} yol çember içinde kesilerek gösterildi.`);
    } catch (err) {
        console.error('❌ Overpass API hatası:', err);
    }
}