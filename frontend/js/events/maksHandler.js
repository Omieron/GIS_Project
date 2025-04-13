export function initBuildingFilters(map) {
  document.getElementById('apply-filters-btn')?.addEventListener('click', () => {
    applyBuildingFilters(map);
  });
}

export function applyBuildingFilters(map) {
  const source = map.getSource('building-source');
  if (!source || !source._data) return;

  const allData = window.buildingCache;
  if (!allData || !allData.features) return;

  const allFeatures = allData.features;

  const filtered = allFeatures.filter(f => {
    const p = f.properties || {};
    let ok = true;

    const zeminUstu = document.querySelector('[data-filter="zeminustu"]').value;
    if (zeminUstu && parseInt(p.ZEMINUSTUKATSAYISI ?? -1) < parseInt(zeminUstu)) ok = false;

    const zeminAlti = document.querySelector('[data-filter="zeminalti"]').value;
    if (zeminAlti && parseInt(p.ZEMINALTIKATSAYISI ?? -1) < parseInt(zeminAlti)) ok = false;

    const durum = document.querySelector('[data-filter="durum"]').value;
    if (durum && String(p.DURUM ?? '') !== durum) ok = false;

    const tip = document.querySelector('[data-filter="tip"]').value;
    if (tip && String(p.TIP ?? '') !== tip) ok = false;

    const sera = document.querySelector('[data-filter="seragazi"]').value;
    if (sera && String(p.SERAGAZEMISYONSINIF ?? '') !== sera) ok = false;

    return ok;
  });

  console.log("🎯 Örnek özellikler:", allFeatures[0]?.properties);
  const filteredGeoJSON = {
    type: "FeatureCollection",
    features: filtered
  };

  map.getSource('building-source').setData(filteredGeoJSON);
  console.log(`✅ ${filtered.length} bina filtrelendi.`);

  updateBinaList(filtered);

}

function updateBinaList(filtered) {
  const statsContainer = document.getElementById('kat-istatistik');
  if (!statsContainer) return;

  const counter = {};
  filtered.forEach(f => {
    const kat = f.properties.ZEMINUSTUKATSAYISI;
    if (kat !== undefined) {
      counter[kat] = (counter[kat] || 0) + 1;
    }
  });

  if (Object.keys(counter).length === 0) {
    statsContainer.innerHTML = "<li>Şuan da herhangi bir bina verisi bulunmamaktadır</li>";
  } else {
    statsContainer.innerHTML = Object.keys(counter)
      .sort((a, b) => a - b)
      .map(k => `<li>${k}+ katlı bina: ${counter[k]} adet</li>`)
      .join('');
  }
}