import { initMap } from './map/mapInitializer.js';
import { addControls } from './map/controls.js';
import { bindUIEvents } from './events/circle-handlers.js';
import { bindFoursquareEvents } from './events/foursquareHandler.js';
//import { addDefaultLayers } from './map/Layers.js';
//import { bindMapEvents } from './map/Events.js';

const map = initMap();         // harita oluştur
addControls(map);              // kontrol ekle
bindUIEvents(map);        // cember olayi eklendi
bindFoursquareEvents(map); //foursquare datasi ekleniyor
