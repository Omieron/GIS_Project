import { add3DBuildings } from '../map/3d-buildings.js';

export function bindSettingsToggle() {
    const toggleBtn = document.getElementById('settings-toggle');
    const card = document.getElementById('settings-card');
  
    if (!toggleBtn || !card) return;
  
    toggleBtn.addEventListener('click', () => {
      card.classList.toggle('show');
    });
  }

// 3d harita gorunumu icin acik olan kod blogu
export function add3DToggleControl(map) {
    const toggle3D = document.getElementById('toggle-3d');
    if (!toggle3D) {
      console.warn('❌ 3D toggle bulunamadı');
      return;
    }
  
    toggle3D.addEventListener('change', (e) => {
      const layerExists = map.getLayer('3d-buildings');
      if (e.target.checked && !layerExists) {
        add3DBuildings(map);
      } else if (!e.target.checked && layerExists) {
        map.removeLayer('3d-buildings');
      }
    });
  
    // 🔐 Harita hazır olmadan 3D eklemeye çalışma!
    map.once('style.load', () => {
      if (toggle3D.checked) {
        add3DBuildings(map);
      }
    });
  }

  export function bindDarkModeToggle(map) {
    const darkToggle = document.getElementById('toggle-dark');
    if (!darkToggle) {
      console.warn('🌘 Dark mode toggle bulunamadı');
      return;
    }
  
    darkToggle.addEventListener('change', () => {
      const isDark = darkToggle.checked;
    
      if (isDark) {
        map.setStyle('mapbox://styles/mapbox/dark-v11');
        document.body.classList.add('dark-mode');
      } else {
        map.setStyle('mapbox://styles/mapbox/streets-v12');
        document.body.classList.remove('dark-mode');
      }
    
      if (document.getElementById('toggle-3d').checked) {
        add3DToggleControl(map);
      }
    });
  }