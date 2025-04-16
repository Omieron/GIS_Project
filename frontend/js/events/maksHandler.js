import { updateLayerColorByRisk } from '../services/maksService.js'

export function initBuildingFilters(map) {
  // ✅ Toggle olayını sayfa yüklenince aktif et
  checkDepremToggle(map);

  // ✅ Filtre butonu
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

    const deprem_riski_toggle = document.getElementById('deprem-toggle')?.checked;
    const deprem_riski = document.querySelector('[data-filter="deprem_riski"]')?.value;
    if (deprem_riski_toggle && deprem_riski && String(p.RISKSKORU ?? '') !== deprem_riski) ok = false;

    return ok;
  });

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

  if (!filtered.length) {
    statsContainer.innerHTML = "<li>Şuan da herhangi bir bina verisi bulunmamaktadır</li>";
    return;
  }

  const katCounter = {};
  const riskCounter = {};

  filtered.forEach(({ properties: p }) => {
    const kat = p?.ZEMINUSTUKATSAYISI;
    const risk = p?.RISKSKORU;

    if (kat !== undefined) katCounter[kat] = (katCounter[kat] || 0) + 1;
    if (risk != null) riskCounter[risk] = (riskCounter[risk] || 0) + 1;
  });

  const katList = Object.entries(katCounter)
    .sort((a, b) => a[0] - b[0])
    .map(([k, v]) => `<li>${k}+ katlı bina: ${v} adet</li>`)
    .join('');

  const riskLabels = {
    1: "🟢 Çok Düşük Risk",
    2: "🟡 Düşük Risk",
    3: "🟠 Orta Risk",
    4: "🔴 Yüksek Risk",
    5: "🟥 Çok Yüksek Risk"
  };

  const riskList = Object.entries(riskCounter)
    .sort((a, b) => a[0] - b[0])
    .map(([r, v]) => `<li>${riskLabels[r] || `Risk ${r}`}: ${v} bina</li>`)
    .join('');

  statsContainer.innerHTML = `
    <li><strong>Kat Sayısı Dağılımı</strong></li>
    ${katList}
    <li style="margin-top: 20px;"><strong>Deprem Riski Dağılımı</strong></li>
    ${riskList || "<li>Risk verisi bulunamadı</li>"}
  `;
}


export function checkDepremToggle(map) {
  const toggle = document.getElementById('deprem-toggle');
  const filterWrapper = document.getElementById('deprem-filter-wrapper');

  if (!toggle || !filterWrapper) {
    console.warn("❗ Toggle ya da filterWrapper bulunamadı.");
    return;
  }

  // ✅ Sayfa ilk açıldığında toggle kapalıysa dropdown gizli başlasın
  filterWrapper.style.display = toggle.checked ? 'block' : 'none';

  toggle.addEventListener('change', () => {
    const isActive = toggle.checked;

    filterWrapper.style.display = isActive ? 'block' : 'none';

    // Toggle kapandıysa dropdown'u sıfırla
    const riskFilter = document.querySelector('[data-filter="deprem_riski"]');
    if (riskFilter) riskFilter.selectedIndex = 0;

    // Renk güncellemesi (kat rengine mi risk rengine mi geçilecek)
    updateLayerColorByRisk(map);
  });
}

export function resetAllBuildingFilters(map) {
  const filters = document.querySelectorAll('#bina-tab [data-filter]');
  filters.forEach(el => {
    if (el.tagName === 'SELECT') {
      el.selectedIndex = 0;
    } else if (el.type === 'checkbox') {
      el.checked = false;
    }

    const depremToggle = document.getElementById('deprem-toggle');
    if (depremToggle) depremToggle.checked = false;

    // 👇 wrapper'ı da gizle, seçimi sıfırla
    document.getElementById('deprem-filter-wrapper').style.display = 'none';

  });

  resetDepremFilterUI(map); // özel deprem filtresi de sıfırlansın
}

