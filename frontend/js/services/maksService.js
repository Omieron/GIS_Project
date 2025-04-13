import { renderBuildingStats } from '../events/infoHandler.js';

export const offsetX = 0;
export const offsetY = -0.0158;

export function applyOffset(features) {
  if (!features || !Array.isArray(features.features)) return features;

  // Derin kopya oluştur
  const offsetData = JSON.parse(JSON.stringify(features));

  offsetData.features.forEach(feature => {
    const geom = feature.geometry;
    if (geom?.type === 'MultiPolygon') {
      geom.coordinates.forEach(polygon => {
        polygon.forEach(ring => {
          ring.forEach(coord => {
            coord[0] += offsetX; // longitude
            coord[1] += offsetY; // latitude
          });
        });
      });
    } else if (geom?.type === 'Polygon') {
      geom.coordinates.forEach(ring => {
        ring.forEach(coord => {
          coord[0] += offsetX;
          coord[1] += offsetY;
        });
      });
    }
  });

  return offsetData;
}

export function fetchBuildingHandler(map) {
  window.addEventListener('circle:created', async (e) => {
    if (e.detail.type !== 'bina') return;

    const marker = e.detail.marker;
    const radius = 500;

    // İlk yükleme + drag sonrası güncelleme için
    async function fetchAndRender(lat, lng) {
      try {
        // Offset uygulanmamış haliyle istek at
        const lonQuery = lng - offsetX;
        const latQuery = lat - offsetY;

        const url = `http://localhost:8001/maks/bina?lon=${lonQuery}&lat=${latQuery}&radius=${radius}`;
        const response = await fetch(url);
        const rawData = await response.json();

        if (!rawData || !rawData.features) {
          console.warn('⚠️ Geçersiz GeoJSON verisi:', rawData);
          return;
        }

        // Offset uygula
        const data = applyOffset(rawData);

        // ✅ CACHE'E YAZ
        window.buildingCache = data;

        if (map.getSource('building-source')) {
          map.getSource('building-source').setData(data);
        } else {
          map.addSource('building-source', {
            type: 'geojson',
            data: data
          });

          map.addLayer({
            id: 'building-layer',
            type: 'fill-extrusion',
            source: 'building-source',
            paint: {
              'fill-extrusion-color': [
                'interpolate',
                ['linear'],
                ['get', 'ZEMINUSTUKATSAYISI'],
                0, '#b3e5fc',
                1, '#81d4fa',
                2, '#4fc3f7',
                3, '#29b6f6',
                4, '#03a9f4',
                5, '#039be5',
                6, '#0288d1',
                7, '#0277bd',
                8, '#01579b',
                10, '#003B73'
              ],
              'fill-extrusion-height': ['*', ['get', 'ZEMINUSTUKATSAYISI'], 3.2],
              'fill-extrusion-base': 0,
              'fill-extrusion-opacity': 0.85
            }
          });
        }

        console.log(`🏢 ${data.features.length} bina bulundu ve çizildi.`);

        // 1️⃣ Filtre alanlarını sıfırla
        const filters = document.querySelectorAll('#bina-tab [data-filter]');
        filters.forEach(el => {
          if (el.tagName === 'SELECT') {
            el.selectedIndex = 0; // "Tümü"ne döner
          } else if (el.type === 'checkbox') {
            el.checked = false;
          }
        });

        // 2️⃣ Tüm veriyle yeniden çiz
        window.buildingCache = data;
        map.getSource('building-source').setData(data);

        renderBuildingStats(data.features);

        const uniqueIds = new Set(data.features.map(f => f.properties?.ID)).size;
        console.log(`🔢 Gerçek bina sayısı (benzersiz ID): ${uniqueIds}`);/*  */

      } catch (err) {
        console.error('❌ Bina verisi alınamadı:', err);
      }
    }

    // Başlangıçta bir kez çağır
    const { lng, lat } = marker.getLngLat();
    fetchAndRender(lat, lng);

    // Drag sonrası her değişimde tekrar veri al
    marker.on('dragend', () => {
      const newCenter = marker.getLngLat();
      fetchAndRender(newCenter.lat, newCenter.lng);
    });
  });
}