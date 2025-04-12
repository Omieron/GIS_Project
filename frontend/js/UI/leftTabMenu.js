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