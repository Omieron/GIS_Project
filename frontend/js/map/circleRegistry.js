export const circleRegistry = new Map();

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

    // 📦 Bina özel katmanı
    if (id === 'bina') {
      if (map.getLayer('building-layer')) {
        map.removeLayer('building-layer');
        console.log("🏗️ Bina layer'ı silindi.");
      }
      if (map.getSource('building-source')) {
        map.removeSource('building-source');
        console.log("🏗️ Bina source'u silindi.");
      }
      window.buildingCache = null;

      // Bilgi panelini güncelle
      const statsEl = document.getElementById('kat-istatistik');
      if (statsEl) {
        statsEl.innerHTML = `
      <li>Şuan da herhangi bir bina verisi bulunmamaktadır</li>
    `;
      }
      
    }

  } else {
    console.warn('❌ Map ya da layer/source erişimi başarısız.');
  }

  circleRegistry.delete(id);
  return true;
}