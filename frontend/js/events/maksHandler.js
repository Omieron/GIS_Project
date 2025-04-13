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
    let { lng, lat } = marker.getLngLat();
    const radius = 500;
    
    try {
        
      console.log(lng - offsetX);
      console.log(lat - offsetY);
      lng = lng - offsetX;
      lat = lat - offsetY;
      // Merkez koordinatları offset UYGULANMADAN kullan
      const url = `http://localhost:8001/maks/bina?lon=${lng}&lat=${lat}&radius=${radius}`;
      const response = await fetch(url);
      const rawData = await response.json();
      
      if (!rawData || !rawData.features) {
        console.warn('⚠️ Geçersiz GeoJSON verisi:', rawData);
        return;
      }
      
      // Veriyi göstermeden ÖNCE offset uygula
      const data = applyOffset(rawData);
      
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
    } catch (err) {
      console.error('❌ Bina verisi alınamadı:', err);
    }
  });
}