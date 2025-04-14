// AI Location Service Handler
import { processLocationQuery, processEnhancedQuery, getOsmAmenities } from '../services/aiLocationService.js';

// Marker mapping for different result types
const MARKER_COLORS = {
  'defined-location': '#2196F3', // Blue
  'contextual-location': '#FF9800', // Orange
  'expanded-query': '#4CAF50', // Green
  'food-location': '#F44336', // Red
  'landmark': '#9C27B0',  // Purple
  'user-location': '#795548' // Brown
};

// Handle location query processing
export async function processQueryAndDisplayOnMap(query, map, appendMessage) {
  try {
    // Try enhanced location API first with fallback to basic
    let response;
    try {
      response = await processEnhancedQuery(query, 'tr');
      console.log('🔍 Enhanced location response:', response);
    } catch (error) {
      console.warn('⚠️ Enhanced location API failed, falling back to regular API');
      response = await processLocationQuery(query);
      console.log('🔍 Basic location response:', response);
    }
    
    if (response?.error) {
      console.error('❌ Location API error:', response.error);
      appendMessage('ai', `Üzgünüm, bir hata oluştu: ${response.error}`);
      return;
    }
    
    displayLocationOnMap(response, map, appendMessage);
    return response;
  } catch (error) {
    console.error('❌ Location processing error:', error);
    appendMessage('ai', 'Üzgünüm, şu anda sorgunuzu işleyemiyorum. Lütfen daha sonra tekrar deneyin.');
    return null;
  }
}

// Handle display of location results on map
export function displayLocationOnMap(response, map, appendMessage) {
  if (!response || !map) return;
  
  // Clear existing markers if any
  if (window.locationMarkers) {
    window.locationMarkers.forEach(marker => marker.remove());
  }
  window.locationMarkers = [];
  
  // Single location result
  if (response.latitude && response.longitude) {
    // Center map on location
    map.flyTo({
      center: [response.longitude, response.latitude],
      zoom: 15,
      essential: true
    });
    
    // Create marker
    const markerColor = MARKER_COLORS[response.type] || '#2196F3';
    const marker = new mapboxgl.Marker({ color: markerColor })
      .setLngLat([response.longitude, response.latitude])
      .addTo(map);
      
    window.locationMarkers.push(marker);
    
    // Format response message
    let placeName = response.place || 'Belirtilen konum';
    let address = response.address ? `<br>Adres: ${response.address}` : '';
    let categories = response.categories && response.categories.length ? 
      `<br>Kategori: ${response.categories.join(', ')}` : '';
    
    appendMessage('ai', `<strong>${placeName}</strong>${address}${categories}<br>` +
      `<em>Koordinatlar: ${response.latitude.toFixed(6)}, ${response.longitude.toFixed(6)}</em>`);
  } 
  // Multiple results (expanded query)
  else if (response.results && Array.isArray(response.results)) {
    if (response.results.length === 0) {
      appendMessage('ai', 'Üzgünüm, belirtilen kriterlerle eşleşen bir yer bulamadım.');
      return;
    }
    
    // Create markers for all results
    const bounds = new mapboxgl.LngLatBounds();
    
    response.results.forEach(place => {
      if (place.longitude && place.latitude) {
        // Add marker
        const markerColor = MARKER_COLORS[response.type] || '#4CAF50';
        const marker = new mapboxgl.Marker({ color: markerColor })
          .setLngLat([place.longitude, place.latitude])
          .addTo(map);
          
        window.locationMarkers.push(marker);
        
        // Extend bounds to include this point
        bounds.extend([place.longitude, place.latitude]);
      }
    });
    
    // Fit map to bounds of all markers
    if (!bounds.isEmpty()) {
      map.fitBounds(bounds, {
        padding: 50,
        maxZoom: 15
      });
    }
    
    // Format response message with list of places
    let messageHtml = `<strong>${response.results.length} yer bulundu:</strong><br><ul>`;
    response.results.slice(0, 5).forEach(place => {
      messageHtml += `<li>${place.name || 'İsimsiz yer'}`;
      if (place.categories && place.categories.length) {
        messageHtml += ` (${place.categories[0]})`;
      }
      messageHtml += '</li>';
    });
    
    if (response.results.length > 5) {
      messageHtml += `<li>...ve ${response.results.length - 5} yer daha</li>`;
    }
    
    messageHtml += '</ul>';
    appendMessage('ai', messageHtml);
  } else {
    appendMessage('ai', 'Üzgünüm, belirtilen konumu bulamadım.');
  }
}

// Fetch nearby amenities using OSM
export async function fetchNearbyAmenities(amenityType, location, map, appendMessage) {
  try {
    const response = await getOsmAmenities(amenityType, location.lat, location.lng);
    
    if (response.features && response.features.length > 0) {
      // Display results on map
      // Implementation would depend on your map library
      appendMessage('ai', `${response.features.length} adet ${amenityType} bulundu.`);
    } else {
      appendMessage('ai', `Üzgünüm, belirtilen bölgede ${amenityType} bulamadım.`);
    }
    
    return response;
  } catch (error) {
    console.error(`❌ Amenity search error for ${amenityType}:`, error);
    appendMessage('ai', `Üzgünüm, ${amenityType} arama sırasında bir hata oluştu.`);
    return null;
  }
}
