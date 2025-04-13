import { initMap } from './map/mapInitializer.js';
import { addControls } from './map/controls.js';
import { bindUIEvents } from './events/circle-handlers.js';
import { bindFoursquareEvents } from './events/foursquareHandler.js';
import { bindOverpassEvents } from './events/overpassHandler.js';
import { fetchBuildingHandler } from './services/maksService.js';
import { adjustAi } from './ai_chat/chatbox.js';
//import { addDefaultLayers } from './map/Layers.js';
//import { bindMapEvents } from './map/Events.js';

window.buildingCache = null; // bina cache
const map = initMap();         // harita oluştur
addControls(map);              // kontrol ekle
bindUIEvents(map);        // cember olayi eklendi
bindFoursquareEvents(map); //foursquare datasi ekleniyor
bindOverpassEvents(map);

document.addEventListener('DOMContentLoaded', () => {
    adjustAi();
    fetchBuildingHandler(map);
  });