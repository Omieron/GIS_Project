// Integration Handler for combining AI Location Service with other services
import { createDraggableCircle } from '../map/circle.js';
import { circleRegistry } from '../map/circleRegistry.js';
import { processLocationQuery } from '../services/aiLocationService.js';

// Import services for integration
import { fetchFoursquarePlaces } from '../services/foursquareService.js';
import { fetchOverpassData } from '../services/overpassService.js';
import { fetchBuildingHandler } from '../services/maksService.js';

// Service-specific event handlers
import { bindFoursquareEvents } from './foursquareHandler.js';
import { displayLocationOnMap } from './aiLocationHandler.js';

import { simulateCircleCreation } from '../ai_chat/aiUserInterfaceControl.js';

// Keywords for detection in prompts
const KEYWORD_MAPPING = {
  foursquare: ['foursquare', 'fsq', 'yeme', 'içme', 'kafe', 'restoran', 'mekan', 'yer', 'cafe', 'restaurant'],
  maks: ['maks', 'bina', 'yapı', 'building', 'mimari', 'ev', 'daire', 'inşaat'],
  overpass: ['overpass', 'yol', 'sokak', 'cadde', 'bulvar', 'highway', 'road', 'street']
};

/**
 * Process a location query and integrate with other services based on keywords
 * @param {string} query - User query text
 * @param {object} map - Mapbox map instance
 * @param {function} appendMessage - Function to append messages to chat
 */
export async function processIntegratedQuery(query, map, appendMessage) {
  // Show loader
  appendMessage('ai', '<div class="loading-message">İşleniyor...</div>');

  try {
    // First, parse query for service type locally (as fallback)
    const localServiceType = detectServiceType(query.toLowerCase());
    console.log(`🔄 Locally detected service type: ${localServiceType}`);

    // Process location query
    const locationResponse = await processLocationQuery(query);

    // Handle location errors
    if (!locationResponse || locationResponse.error) {
      throw new Error(locationResponse?.error || 'Konum bulunamadı');
    }

    // Display location marker on map
    displayLocationOnMap(locationResponse, map, (role, message) => {
      // Replace default response with our custom one
      // We'll generate a better response later
    });

    // Get coordinates
    let coords = { lat: 0, lng: 0 };

    if (locationResponse.latitude && locationResponse.longitude) {
      // Single location result
      coords = {
        lat: locationResponse.latitude,
        lng: locationResponse.longitude
      };
    } else if (locationResponse.results && locationResponse.results.length > 0) {
      // First result from multiple results
      const firstResult = locationResponse.results[0];
      coords = {
        lat: firstResult.latitude,
        lng: firstResult.longitude
      };
    } else {
      throw new Error('Geçerli koordinatlar bulunamadı');
    }

    // Format initial response
    let responseText = formatLocationResponse(locationResponse);

    // Get service type from the AI response (more accurate than our local detection)
    const serviceType = locationResponse.service_type || localServiceType;
    console.log(`🤖 AI detected service type: ${serviceType}`);

    // If no specific service is detected or if it's the default service, we're done
    if (serviceType === 'default_service') {
      appendMessage('ai', responseText);
      return locationResponse;
    }

    // Map the service_type from backend to our service names
    //const mappedServiceType = mapServiceType(serviceType);

    // Create a circle at the location for the service integration
    //createServiceCircle(map, coords, mappedServiceType);

    console.log(coords.lng);
    console.log(coords.lat);
    simulateCircleCreation(map, serviceType, [coords.lng, coords.lat]);

    // Add service-specific information to response
    responseText += `<br><br><div class="service-integration">
      <strong>${getServiceTitle(serviceType)}</strong> verilerini yüklüyorum...
    </div>`;

    appendMessage('ai', responseText);

    return locationResponse;
  } catch (error) {
    console.error('❌ Integration error:', error);
    appendMessage('ai', `Üzgünüm, bir hata oluştu: ${error.message}`);
    return null;
  }
}

/**
 * Detect which service is being requested in the query
 */
function detectServiceType(query) {
  // Check each service's keywords
  for (const [service, keywords] of Object.entries(KEYWORD_MAPPING)) {
    if (keywords.some(keyword => query.includes(keyword))) {
      return service;
    }
  }

  // Default to just location
  return 'location';
}

/**
 * Create a draggable circle for service integration
 */
// function createServiceCircle(map, coords, serviceType) {
//   // First trigger a custom event to close any existing cards
//   document.dispatchEvent(new CustomEvent('circle:close-all'));

//   // Create the circle
//   const options = {
//     color: getServiceColor(serviceType),
//     radius: 500, // 500m radius is standard
//     type: serviceType
//   };

//   // This will trigger the appropriate service handler via the circle:created event
//   createDraggableCircle(map, [coords.lng, coords.lat], options);
// }

/**
 * Map the service_type from backend to our service names
 */
function mapServiceType(serviceType) {
  switch (serviceType) {
    case 'foursquare_service': return 'foursquare';
    case 'maks_service': return 'maks';
    case 'overpass_service': return 'overpass';
    case 'default_service': return 'location';
    // Handle cases where our local detection already gave us the mapped type
    case 'foursquare': return 'foursquare';
    case 'maks': return 'maks';
    case 'overpass': return 'overpass';
    default: return 'location';
  }
}

/**
 * Get service color for the circle
 */
function getServiceColor(serviceType) {
  switch (serviceType) {
    case 'foursquare': return '#F44336'; // Red
    case 'maks': return '#2196F3'; // Blue
    case 'overpass': return '#4CAF50'; // Green
    default: return '#FF9800'; // Orange
  }
}

/**
 * Get service title for display
 */
function getServiceTitle(serviceType) {
  switch (serviceType) {
    case 'foursquare': return 'Foursquare mekan';
    case 'maks': return 'MAKS bina';
    case 'overpass': return 'OpenStreetMap yol';
    default: return 'Konum';
  }
}

/**
 * Format location response as HTML
 */
function formatLocationResponse(response) {
  // Single location result
  if (response.latitude && response.longitude) {
    let placeName = response.place || 'Belirtilen konum';
    let address = response.address ? `<br>Adres: ${response.address}` : '';
    let categories = response.categories && response.categories.length ?
      `<br>Kategori: ${response.categories.join(', ')}` : '';
    let description = response.description ? `<br>${response.description}` : '';

    return `<div class="location-result">
      <strong>${placeName}</strong>${address}${categories}${description}<br>
      <em>Koordinatlar: ${response.latitude.toFixed(6)}, ${response.longitude.toFixed(6)}</em>
    </div>`;
  }

  // Multiple results
  if (response.results && Array.isArray(response.results)) {
    if (response.results.length === 0) {
      return '<div class="warning-message">Belirtilen kriterlere uygun sonuç bulunamadı.</div>';
    }

    let resultsHtml = `<div class="location-results">
      <strong>${response.results.length} sonuç bulundu:</strong><br>
      <ul class="results-list">`;

    response.results.forEach((result, index) => {
      let name = result.name || `Sonuç ${index + 1}`;
      let category = result.categories && result.categories.length ?
        ` (${result.categories[0]})` : '';

      resultsHtml += `<li>${name}${category}</li>`;
    });

    resultsHtml += '</ul></div>';
    return resultsHtml;
  }

  return '<div class="info-message">Konum bilgisi işlendi.</div>';
}
