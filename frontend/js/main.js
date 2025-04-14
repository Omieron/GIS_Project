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
window.map = initMap();      // harita oluştur ve global yap
addControls(window.map);     // kontrol ekle
bindUIEvents(window.map);    // cember olayi eklendi
bindFoursquareEvents(window.map); //foursquare datasi ekleniyor
bindOverpassEvents(window.map);

document.addEventListener('DOMContentLoaded', () => {
    adjustAi(window.map);    // Harita referansını gönder
    fetchBuildingHandler(window.map);
  });