import { renderBuildingStats } from '../events/infoHandler.js';
import { resetAllBuildingFilters } from '../events/maksHandler.js';
import { showNotification, showLoading, hideLoading } from '../events/notificationHandler.js';

export const offsetX = 0;
export const offsetY = -0.0158;

export function applyOffset(features) {
  if (!features || !Array.isArray(features.features)) return features;

  const offsetData = JSON.parse(JSON.stringify(features));

  offsetData.features.forEach(feature => {
    const geom = feature.geometry;
    if (geom?.type === 'MultiPolygon') {
      geom.coordinates.forEach(polygon => {
        polygon.forEach(ring => {
          ring.forEach(coord => {
            coord[0] += offsetX;
            coord[1] += offsetY;
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

    showLoading("Bina bilgileri veritabanından gelmektedir, lütfen bekleyiniz...");

    const marker = e.detail.marker;
    const radius = 500;

    async function fetchAndRender(lat, lng) {
      try {
        const lonQuery = lng - offsetX;
        const latQuery = lat - offsetY;

        const url = `http://localhost:8001/maks/bina?lon=${lonQuery}&lat=${latQuery}&radius=${radius}`;
        const response = await fetch(url);
        const rawData = await response.json();

        if (!rawData || !rawData.features) {
          console.warn('⚠️ Geçersiz GeoJSON verisi:', rawData);
          return;
        }

        const data = applyOffset(rawData);
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
            paint: getPaintProperties()
          });
        }

        updateLayerColorByRisk(map);
        renderBuildingStats(data.features);

        const uniqueIds = new Set(data.features.map(f => f.properties?.ID)).size;
        console.log(`🏢 ${data.features.length} bina bulundu. Benzersiz ID: ${uniqueIds}`);
      } catch (err) {
        console.error('❌ Bina verisi alınamadı:', err);
        hideLoading();
        showNotification("Bina verileri alınamadı", "ERROR");
      }
    }

    const { lng, lat } = marker.getLngLat();
    fetchAndRender(lat, lng);

    marker.on('dragend', () => {
      const { lng, lat } = marker.getLngLat();
      fetchAndRender(lat, lng);
      resetAllBuildingFilters(map);
    });
  });

  const riskFilter = document.querySelector('[data-filter="deprem_riski"]');
  if (riskFilter) {
    riskFilter.addEventListener('change', () => updateLayerColorByRisk(map));
  }

  hideLoading();

}

function getPaintProperties(byRisk = false) {
  const color = byRisk
    ? [
      'case',
      ['has', 'RISKSKORU'],
      [
        'interpolate',
        ['linear'],
        ['get', 'RISKSKORU'],
        1, '#ffff00',  // Sarı - çok düşük risk
        2, '#ffa500',  // Turuncu - düşük risk
        3, '#ff4500',  // Koyu turuncu - orta risk
        4, '#ff0000',  // Kırmızı - yüksek risk
        5, '#8b0000'   // Bordo - çok yüksek risk
      ],
      'rgba(0,0,0,0)' // ❌ RISKSKORU yoksa görünmesin
    ]
    : [
      'interpolate',
      ['linear'],
      ['get', 'ZEMINUSTUKATSAYISI'],
      0, '#bbdefb',
      1, '#64b5f6',
      2, '#42a5f5',
      3, '#2196f3',
      4, '#1e88e5',
      5, '#1976d2',
      6, '#1565c0',
      7, '#0d47a1',
      8, '#0b3c91',
      10, '#082567'
    ];

  return {
    'fill-extrusion-color': color,
    'fill-extrusion-height': ['*', ['get', 'ZEMINUSTUKATSAYISI'], 3.2],
    'fill-extrusion-base': 0,
    'fill-extrusion-opacity': 0.95  // biraz daha canlı görünüm
  };
}


export function updateLayerColorByRisk(map) {
  const toggle = document.getElementById('deprem-toggle');
  const riskMode = toggle?.checked;

  const paint = getPaintProperties(riskMode);

  Object.entries(paint).forEach(([key, value]) => {
    map.setPaintProperty('building-layer', key, value);
  });

  console.log(`🎨 Katman rengi güncellendi. Risk modu: ${riskMode}`);
}

