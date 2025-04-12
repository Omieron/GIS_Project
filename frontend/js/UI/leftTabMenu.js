import { removeCircle } from '../map/circleRegistry.js'; // 🔥 import et

export function bindTabSwitching() {
  const tabs = document.querySelectorAll('.tab');
  const panels = document.querySelectorAll('.tab-panel');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.tab;

      // Sekme aktifliği
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      // İçerik aktifliği
      panels.forEach(panel => panel.classList.remove('active'));
      document.getElementById(target).classList.add('active');
    });
  });
}

export function showInfoCard(tabId, label) {
  const card = document.querySelector('.info-card');
  const tabHeader = document.getElementById('tab-header');
  const tabContent = document.getElementById('tab-content');

  if (!card || !tabHeader) return;

  card.style.display = 'flex';

  let existingTab = tabHeader.querySelector(`[data-tab="${tabId}"]`);
  if (!existingTab) {
    const newTab = document.createElement('div');
    newTab.classList.add('tab');
    newTab.dataset.tab = tabId;

    const labelSpan = document.createElement('span');
    labelSpan.textContent = label;

    const closeBtn = document.createElement('span');
    closeBtn.className = 'tab-close';
    closeBtn.textContent = '✕';
    closeBtn.title = 'Kapat';

    // ✅ Tıklanınca çemberi ve sekmeyi sil
    closeBtn.addEventListener('click', (e) => {
      e.stopPropagation();

      removeCircle(label.toLowerCase()); // ← "foursquare", "overpass", "tomtom" gibi

      newTab.remove();
      const panel = document.getElementById(tabId);
      if (panel) panel.classList.remove('active');

      // başka tab varsa ilkini aktif et
      const remainingTabs = tabHeader.querySelectorAll('.tab');
      if (remainingTabs.length > 0) {
        const firstTabId = remainingTabs[0].dataset.tab;
        activateTab(firstTabId);
      }

      hideInfoCardIfNoTabs();
    });

    newTab.appendChild(labelSpan);
    newTab.appendChild(closeBtn);

    newTab.addEventListener('click', () => {
      activateTab(tabId);
    });

    tabHeader.appendChild(newTab);
  }

  activateTab(tabId);
}

export function hideInfoCardIfNoTabs() {
  const tabHeader = document.getElementById('tab-header');
  const card = document.querySelector('.info-card');
  if (tabHeader && card && tabHeader.children.length === 0) {
    card.style.display = 'none';
  }
}

function activateTab(tabId) {
  const tabs = document.querySelectorAll('.tab');
  const panels = document.querySelectorAll('.tab-panel');

  tabs.forEach(t => t.classList.remove('active'));
  panels.forEach(p => p.classList.remove('active'));

  const activeTab = document.querySelector(`.tab[data-tab="${tabId}"]`);
  const activePanel = document.getElementById(tabId);

  if (activeTab && activePanel) {
    activeTab.classList.add('active');
    activePanel.classList.add('active');
  }
}

export function enableFoursquareSwipe() {
  const container = document.getElementById('fsq-container');
  const leftPanel = document.getElementById('foursquare-card');
  const rightPanel = document.getElementById('foursquare-info');
  const dotLeft = document.getElementById('dot-left');
  const dotRight = document.getElementById('dot-right');

  if (!container || !leftPanel || !rightPanel || !dotLeft || !dotRight) {
    console.warn("🛑 Swipe için gerekli DOM elemanları bulunamadı.");
    return;
  }

  let startX = 0;

  function setDotActive(which) {
    dotLeft.classList.remove('active-dot');
    dotRight.classList.remove('active-dot');
    if (which === 'left') dotLeft.classList.add('active-dot');
    if (which === 'right') dotRight.classList.add('active-dot');
  }

  container.addEventListener('touchstart', (e) => {
    startX = e.touches[0].clientX;
  });

  container.addEventListener('touchend', (e) => {
    const endX = e.changedTouches[0].clientX;
    const deltaX = endX - startX;

    if (deltaX < -50) {
      leftPanel.classList.remove('active');
      rightPanel.classList.add('active');
      setDotActive('right');
    }

    if (deltaX > 50) {
      rightPanel.classList.remove('active');
      leftPanel.classList.add('active');
      setDotActive('left');
    }
  });

  // Başlangıçta sol panel aktif
  leftPanel.classList.add('active');
  rightPanel.classList.remove('active');
  setDotActive('left');
}

const highwayColors = {
  motorway: '#ff0000',
  trunk: '#ff7f00',
  primary: '#ffa500',
  secondary: '#ffff00',
  tertiary: '#9acd32',
  residential: '#00bfff',
  unclassified: '#cccccc',
  service: '#999999',
  footway: '#00ff7f',
  path: '#228b22',
  cycleway: '#8a2be2',
  unknown: '#888888'
};

const highlightLayers = new Set(); // aktif highlight'ları takip et

export function renderOverpassLegend(map) {
  const legendContainer = document.getElementById('road-legend');
  if (!legendContainer || !map) return;

  legendContainer.innerHTML = '<strong>Görünen Yol Tipleri</strong><br><br>';

  const source = map.getSource('overpass-roads');
  const geojson = source?._data || source?._options?.data;
  if (!geojson || !geojson.features) {
    legendContainer.innerHTML += '<em>Yol verisi bulunamadı.</em>';
    return;
  }

  const foundTypes = new Set();

  geojson.features.forEach(f => {
    const type = f.properties?.highway;
    if (type) foundTypes.add(type);
  });

  [...foundTypes].sort().forEach(type => {
    const color = highwayColors[type] || highwayColors.unknown;

    const item = document.createElement('div');
    item.style.display = 'flex';
    item.style.alignItems = 'center';
    item.style.marginBottom = '6px';
    item.style.cursor = 'pointer';
    item.dataset.type = type;

    const colorBox = document.createElement('div');
    colorBox.style.width = '16px';
    colorBox.style.height = '16px';
    colorBox.style.marginRight = '8px';
    colorBox.style.backgroundColor = color;
    colorBox.style.border = '1px solid #ccc';
    colorBox.style.borderRadius = '4px';

    const label = document.createElement('span');
    label.textContent = type.charAt(0).toUpperCase() + type.slice(1);

    item.appendChild(colorBox);
    item.appendChild(label);
    legendContainer.appendChild(item);

    // 👇 Highlight ekle
    item.addEventListener('click', () => {
      const layerId = `highlight-${type}`;
      if (highlightLayers.has(layerId)) {
        // varsa kaldır
        if (map.getLayer(layerId)) map.removeLayer(layerId);
        if (map.getSource(layerId)) map.removeSource(layerId);
        highlightLayers.delete(layerId);
        item.style.opacity = '0.5';
      } else {
        // yoksa sadece o highway türünü filtrele
        const filtered = geojson.features.filter(f => f.properties?.highway === type);
        const highlightGeoJSON = {
          type: 'FeatureCollection',
          features: filtered
        };

        map.addSource(layerId, {
          type: 'geojson',
          data: highlightGeoJSON
        });

        map.addLayer({
          id: layerId,
          type: 'line',
          source: layerId,
          layout: {},
          paint: {
            'line-color': '#000', // siyah ya da parlak bir şey
            'line-width': 4,
            'line-opacity': 0.9
          }
        });

        highlightLayers.add(layerId);
        item.style.opacity = '1';
      }
    });
  });
}