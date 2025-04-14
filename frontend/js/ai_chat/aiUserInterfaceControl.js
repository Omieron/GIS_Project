import { circleRegistry, removeCircle } from '../map/circleRegistry.js';
import { createDraggableCircle } from '../map/circle.js';
import { showInfoCard  } from '../UI/leftTabMenu.js';

// Data dogru mu diye bakar.
export function simulateCircleCreation(map, serviceType, coordinates = [27.024772, 39.596321], radius = 500) {
  const type = mapServiceTypeToCircleType(serviceType);

  if (!type) {
    console.warn(`🚫 Geçersiz serviceType: "${serviceType}"`);
    return 'Olmadi gibi knk';
  }

  const [lng, lat] = coordinates;

  if (!circleRegistry || typeof circleRegistry.has !== 'function') {
    console.warn('🚫 circleRegistry tanımlı değil veya has fonksiyonu yok');
    return 'Çember sistemi hazır değil gibi knk 🧨';
  }

  console.log(type + " aiuserinterfacedeki bu");
  if (circleRegistry.has(type)) {
    removeCircle(type);
  }

  const marker = createDraggableCircle(map, type, radius, { lng, lat });
  circleRegistry.set(type, marker);

  const event = new CustomEvent('circle:created', {
    detail: { type, marker, id: type }
  });
  window.dispatchEvent(event);

  const tabId = `${type}-tab`;
  const title = type.charAt(0).toUpperCase() + type.slice(1);
  showInfoCard(tabId, title);

  return `✅ ${type} çemberi haritaya başarıyla eklendi.`;
}


function isValidCircleType(serviceType) {
  return !!mapServiceTypeToCircleType(serviceType);
}

function mapServiceTypeToCircleType(serviceType) {
    const mapping = {
      'foursquare_service': 'foursquare',
      'overpass_service': 'overpass',
      'maks_service': 'bina'
    };
  
    return mapping[serviceType.toLowerCase()] || null;
  }
  