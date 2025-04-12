// harita sistemi kontrolleri
import { add3DBuildings } from './3d-buildings.js';
import { bindMenuToggle } from '../UI/leftMenuToggle.js';
import { bindTabSwitching } from '../UI/leftMenuToggle.js';

export function addControls(map) {
  // default gelen mapbox kontrolculeri  
  map.addControl(new mapboxgl.NavigationControl(), 'top-right');
  map.addControl(new mapboxgl.FullscreenControl(), 'top-right');


  // 3d harita gorunumu icin olan toggle
  //add3DToggleControl(map);
  bindMenuToggle();                 // left menü toggle setup
  bindTabSwitching();               // left bottom menu setup
}

// 3d harita gorunumu icin acik olan kod blogu
function add3DToggleControl(map) {
  const toggleContainer = document.createElement('label');
  toggleContainer.style.position = 'absolute';
  toggleContainer.style.top = '10px';
  toggleContainer.style.left = '10px';
  toggleContainer.style.zIndex = '999';
  toggleContainer.style.background = 'white';
  toggleContainer.style.padding = '5px';
  toggleContainer.style.borderRadius = '4px';

  toggleContainer.innerHTML = `
    <label class="switch">
      <input type="checkbox" id="toggle3D" checked>
      <span class="slider"></span>
    </label>
  `;
  document.body.appendChild(toggleContainer);

  const toggle3D = document.getElementById('toggle3D');
  toggle3D.addEventListener('change', (e) => {
    const layerExists = map.getLayer('3d-buildings');
    if (e.target.checked && !layerExists) {
      add3DBuildings(map);
    } else if (!e.target.checked && layerExists) {
      map.removeLayer('3d-buildings');
    }
  });

  add3DBuildings(map); // başlangıçta açık
}