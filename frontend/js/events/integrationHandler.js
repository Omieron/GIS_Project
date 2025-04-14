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
  foursquare: ['foursquare', 'fsq', 'yeme', 'içme', 'kafe', 'restoran', 'mekan', 'yer', 'cafe', 'restaurant', 'dondurma', 'kahvaltı', 'balık'],
  maks: ['maks', 'bina', 'yapı', 'building', 'mimari', 'ev', 'daire', 'inşaat', 'okul', 'lise', 'üniversite', 'hastane'],
  overpass: ['overpass', 'yol', 'sokak', 'cadde', 'bulvar', 'highway', 'road', 'street', 'plaj', 'sahil', 'kıyı', 'deniz']
};

// Edremit-specific location types for better visualization
const EDREMIT_LOCATION_TYPES = {
  settlement: { icon: '🏙️', label: 'Yerleşim' },
  landmark: { icon: '🏞️', label: 'Doğal Alan' },
  beach: { icon: '🏖️', label: 'Plaj' },
  school: { icon: '🏫', label: 'Okul' },
  restaurant: { icon: '🍽️', label: 'Restoran' },
  shopping: { icon: '🛍️', label: 'Alışveriş' },
  icecream: { icon: '🍦', label: 'Dondurma' }
};

/**
 * Process a location query and integrate with other services based on keywords
 * @param {string} query - User query text
 * @param {object} map - Mapbox map instance
 * @param {function} appendMessage - Function to append messages to chat
 */
export async function processIntegratedQuery(query, map, appendMessage) {

  return new Promise(async (resolve, reject) => {
    let responseText = '<div class="ai-response">';
    
    try {
      // Show loader
      appendMessage('ai', '<div class="loading-message">İşleniyor...</div>');
      
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
      
      // Extract service type from the AI response (more accurate than our local detection)
      const serviceType = locationResponse.service_type || localServiceType || 'foursquare_service';
      console.log(`🤖 AI detected service type: ${serviceType}`);
      
      // Debug assistance for failures
      const actionType = locationResponse.action || 'unknown';
      console.log(`🔍 Action type: ${actionType}, Query: ${query}`);
      
      // Check for missing fields that should be present based on action type
      if (actionType === 'contextual-location' && (!locationResponse.location_name || !locationResponse.context)) {
        console.warn('⚠️ Missing required fields for contextual-location action:', locationResponse);
        // Add fallback values if needed
        locationResponse.location_name = locationResponse.location_name || query;
        locationResponse.context = locationResponse.context || 'Edremit';
      }
      
      if (actionType === 'food-location' && (!locationResponse.food || !locationResponse.location)) {
        console.warn('⚠️ Missing required fields for food-location action:', locationResponse);
        // Add fallback values
        locationResponse.food = locationResponse.food || query;
        locationResponse.location = locationResponse.location || 'Edremit';
      }
      
      // Check for Edremit context metadata
      const edremitContext = locationResponse.edremit_context || { focus_area: true }; // Default to true
      
      // Adjust response for Edremit-specific context
      if (edremitContext.focus_area) {
        responseText += `<div class="edremit-context"><small>🏞️ Edremit bölgesinde arama yapılıyor</small></div>`;
      }
      
      // Enhance the response with location type information if available
      if (locationResponse.location_type) {
        const locationType = locationResponse.location_type;
        const locationTypeDisplay = locationType.charAt(0).toUpperCase() + locationType.slice(1);
        responseText += `<div class="location-type-info"><small>📍 Tür: ${locationTypeDisplay}</small></div>`;
      }
      
      // If no specific service is detected or if it's the default service, we're done
      if (serviceType === 'default_service') {
        console.log(`ℹ️ Using default service for query: "${query}"`);
        appendMessage('ai', responseText);
        resolve(locationResponse);
        return;
      }
      
      // Map the service_type from backend to our service names
      const mappedServiceType = mapServiceType(serviceType);
      
      // Create a circle at the location for the service integration
      //createServiceCircle(map, coords, mappedServiceType, locationResponse);
      simulateCircleCreation(map, serviceType, [coords.lng, coords.lat]);
      // Add service-specific information to response
      responseText += `<br><br><div class="service-integration">
        <strong>${getServiceTitle(serviceType)}</strong> verilerini yüklüyorum...
      </div>`;
      

      appendMessage('ai', responseText);
      
      resolve(locationResponse);
    } catch (error) {
      console.error('❌ Integration error:', error);
      appendMessage('ai', `Üzgünüm, bir hata oluştu: ${error.message}`);
      reject(error);
    }

  });

}

/**
 * Detect which service is being requested in the query
 */
function detectServiceType(query) {
  // Normalize the query: lowercase and remove Turkish accents for more reliable matching
  const normalizedQuery = query.toLowerCase()
    .replace(/ç/g, 'c')  // ç -> c
    .replace(/ü/g, 'u')  // ü -> u
    .replace(/ş/g, 's')  // ş -> s
    .replace(/ı/g, 'i')  // ı -> i
    .replace(/ö/g, 'o')  // ö -> o
    .replace(/ğ/g, 'g'); // ğ -> g
    
  // Check each service's keywords with normalized comparison
  for (const [service, keywords] of Object.entries(KEYWORD_MAPPING)) {
    // For each keyword, also generate a non-accented version for matching
    const normalizedKeywords = keywords.map(kw => {
      return kw.toLowerCase()
        .replace(/ç/g, 'c')
        .replace(/ü/g, 'u')
        .replace(/ş/g, 's')
        .replace(/ı/g, 'i')
        .replace(/ö/g, 'o')
        .replace(/ğ/g, 'g');
    });
    
    // Check both original keywords and normalized versions
    if (keywords.some(keyword => query.toLowerCase().includes(keyword)) ||
        normalizedKeywords.some(keyword => normalizedQuery.includes(keyword))) {
      console.log(`🔎 Service detected: ${service} from keyword match`);
      return service;
    }
  }
  
  // For single-word queries that are likely places, use edremit service
  if (query.split(' ').length <= 2 && !query.includes('?')) {
    const edremitLocations = ['edremit', 'akcay', 'akçay', 'altinoluk', 'altınoluk', 'zeytinli', 'gure', 'güre'];
    const normalizedLocations = edremitLocations.map(loc => loc.toLowerCase()
      .replace(/ç/g, 'c')
      .replace(/ü/g, 'u')
      .replace(/ş/g, 's')
      .replace(/ı/g, 'i')
      .replace(/ö/g, 'o')
      .replace(/ğ/g, 'g'));
      
    if (edremitLocations.some(loc => query.toLowerCase().includes(loc)) ||
        normalizedLocations.some(loc => normalizedQuery.includes(loc))) {
      console.log(`🔎 Location detected as part of Edremit region`);
      return 'edremit';
    }
  }
  
  // Default to foursquare for better handling of most queries
  console.log(`ℹ️ No specific service detected, defaulting to foursquare`);
  return 'foursquare';
}


/**
 * Map the service_type from backend to our service names
 */
function mapServiceType(serviceType) {
  switch (serviceType) {
    case 'foursquare_service': return 'foursquare';
    case 'maks_service': return 'maks';
    case 'overpass_service': return 'overpass';
    case 'edremit_service': return 'edremit';
    case 'default_service': return 'location';
    // Handle cases where our local detection already gave us the mapped type
    case 'foursquare': return 'foursquare';
    case 'maks': return 'maks';
    case 'overpass': return 'overpass';
    case 'edremit': return 'edremit';
    default: return 'location';
  }
}


/**
 * Get service title for display
 */
function getServiceTitle(serviceType) {
  switch (serviceType) {
    case 'foursquare_service':
    case 'foursquare': return 'Foursquare mekan';
    case 'maks_service':
    case 'maks': return 'MAKS bina';
    case 'overpass_service':
    case 'overpass': return 'OpenStreetMap yol';
    case 'edremit_service': return 'Edremit yerel veri';
    default: return 'Konum';
  }
}

/**
 * Format location response as HTML
 */
function formatLocationResponse(response) {
  // Handle error responses
  if (response.error) {
    console.error(`🚨 Error in location response: ${response.error}`);
    return `<div class="error-message">
      <strong>⚠️ Bir hata oluştu:</strong><br>
      ${response.error}
      <small>Lütfen başka bir sorgu deneyin veya daha spesifik olun.</small>
    </div>`;
  }
  
  // Single location result
  if (response.latitude && response.longitude) {
    let placeName = response.place || response.location_name || 'Belirtilen konum';
    let address = response.address ? `<br>Adres: ${response.address}` : '';
    
    // Enhanced category display with icons for Edremit locations
    let categories = '';
    if (response.categories && response.categories.length) {
      const category = response.categories[0].toLowerCase();
      const edremitType = EDREMIT_LOCATION_TYPES[category];
      if (edremitType) {
        categories = `<br>${edremitType.icon} ${edremitType.label}: ${response.categories.join(', ')}`;
      } else {
        categories = `<br>Kategori: ${response.categories.join(', ')}`;
      }
    }
    
    let description = response.description ? `<br>${response.description}` : '';
    
    // Check for context location (for contextual searches like "near a school")
    let contextInfo = '';
    if (response.context_location) {
      const ctx = response.context_location;
      const ctxType = EDREMIT_LOCATION_TYPES[ctx.type] || { icon: '📍', label: 'Konum' };
      contextInfo = `<div class="context-location">
        <span class="context-icon">${ctxType.icon}</span> ${ctx.name}: ${ctx.description}
      </div>`;
    } else if (response.context) {
      // Fallback for when we have context string but not full context_location
      const contextName = response.context.charAt(0).toUpperCase() + response.context.slice(1);
      contextInfo = `<div class="context-location">
        <span class="context-icon">📍</span> Konum: ${contextName}
      </div>`;
    }
    
    // Check for alternatives
    let alternativesHtml = '';
    if (response.alternatives && response.alternatives.length) {
      alternativesHtml = `<div class="alternatives">
        <details>
          <summary>Diğer seçenekler (${response.alternatives.length})</summary>
          <ul class="alt-list">`;
      
      response.alternatives.forEach(alt => {
        alternativesHtml += `<li>${alt.place || alt.name}: ${alt.description || ''}</li>`;
      });
      
      alternativesHtml += `</ul>
        </details>
      </div>`;
    }
    
    // Source information
    let sourceInfo = '';
    if (response.source) {
      let sourceLabel = '';
      switch (response.source) {
        case 'edremit-mapping':
          sourceLabel = 'Edremit Yerel Veri';
          break;
        case 'foursquare':
          sourceLabel = 'Foursquare';
          break;
        case 'openstreetmap':
          sourceLabel = 'OpenStreetMap';
          break;
        default:
          sourceLabel = response.source;
      }
      sourceInfo = `<small class="source-info">Kaynak: ${sourceLabel}</small>`;
    }
    
    return `<div class="location-result">
      <strong>${placeName}</strong>${address}${categories}${description}<br>
      <em>Koordinatlar: ${response.latitude.toFixed(6)}, ${response.longitude.toFixed(6)}</em>
      ${contextInfo}
      ${alternativesHtml}
      ${sourceInfo}
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

      let name = result.name || `Sonuç ${index+1}`;
      
      // Check for Edremit-specific location types
      let category = '';
      if (result.categories && result.categories.length) {
        const categoryName = result.categories[0].toLowerCase();
        const edremitType = EDREMIT_LOCATION_TYPES[categoryName];
        if (edremitType) {
          category = ` <span class="category-tag">${edremitType.icon} ${result.categories[0]}</span>`;
        } else {
          category = ` <span class="category-tag">(${result.categories[0]})</span>`;
        }
      }
      
      // Add description if available
      let description = result.description ? ` - ${result.description}` : '';
      
      resultsHtml += `<li>${name}${category}${description}</li>`;

    });

    resultsHtml += '</ul></div>';
    return resultsHtml;
  }

  return '<div class="info-message">Konum bilgisi işlendi.</div>';
}
