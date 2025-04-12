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

// js/events/foursquareSwipe.js

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