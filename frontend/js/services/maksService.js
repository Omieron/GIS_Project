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
            type: 'fill',
            source: 'building-source',
            paint: {
              'fill-color': '#ff6600',
              'fill-opacity': 0.5
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