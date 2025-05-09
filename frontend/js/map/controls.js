// harita sistemi kontrolleri
import { bindMenuToggle } from '../UI/leftTopMenuToggle.js';
import { bindTabSwitching } from '../UI/leftTabMenu.js';
import { bindSettingsToggle, add3DToggleControl, bindDarkModeToggle } from '../UI/settings.js';
import { initBuildingFilters } from '../events/maksHandler.js';

export function addControls(map) {
  // default gelen mapbox kontrolculeri  
  map.addControl(new mapboxgl.NavigationControl(), 'top-right');
  map.addControl(new mapboxgl.FullscreenControl(), 'top-right');


  // 3d harita gorunumu icin olan toggle

  bindMenuToggle();                 // left menü toggle setup
  bindTabSwitching();               // left bottom menu setup
  bindSettingsToggle();
  document.addEventListener('DOMContentLoaded', () => {
    add3DToggleControl(map);
    bindDarkModeToggle(map);
    initBuildingFilters(map);
  });
  
}

