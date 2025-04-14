import { enableSpeechToText } from './speechToText.js';
import { processIntegratedQuery } from '../events/integrationHandler.js';

// Reference to the map object
let mapInstance = null;

// Create global array for location markers
window.locationMarkers = window.locationMarkers || [];

export function adjustAi(mapObj) {
  // Store the map reference if provided
  if (mapObj) {
    mapInstance = mapObj;
    console.log('✅ Map instance received in chatbox.js');
  } else {
    // Use window.map as fallback
    mapInstance = window.map;
    console.log('⚠️ Using window.map as fallback');
  }
  
  // Check if map is available
  if (!mapInstance) {
    console.error('❌ Map instance not available in chatbox.js');
  }
  
  initChatBox();
  enableChatboxPin();
  enableSpeechToText();
}

function initChatBox() {
  const input = document.getElementById('chat-input');
  const sendBtn = document.getElementById('chat-send');
  const messages = document.getElementById('chat-messages');

  if (!input || !sendBtn || !messages) {
    console.warn("🛑 Chatbox elemanları bulunamadı.");
    return;
  }
  
  // Show initial message
  setTimeout(() => {
    appendMessage('ai', "Merhaba! Konum veya yer hakkında sorularınızı yanıtlayabilirim. Örneğin: 'Edremit'te kafeler nerede?' ya da 'Akçay'da bir eczane bul'");
  }, 500);

  // Gönder butonuna tıklama
  sendBtn.addEventListener('click', () => {
    const text = input.value.trim();
    if (text) {
      appendMessage('user', text);
      input.value = '';
      handleLocationQuery(text);
    }
  });

  // Enter tuşuna basıldığında da mesaj gönder
  input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault(); // form submit varsa engelle
      sendBtn.click();
    }
  });
}

// Global function to handle location queries
async function handleLocationQuery(text) {
  // Show loading indicator
  const loadingId = showLoading();
  
  try {
    console.log('💬 Processing location query:', text);
    
    // Check for service integration keywords
    const needsIntegration = checkForIntegrationKeywords(text.toLowerCase());
    
    if (needsIntegration) {
      console.log('🔗 Using integrated service query processing');
      // Hide initial loading indicator
      hideLoading(loadingId);
      
      // Use the integrated handler - it will manage its own messages
      await processIntegratedQuery(text, mapInstance, appendMessage);
      return;
    }
    
    // Standard location processing if no integration needed
    console.log('🗺️ Using standard location query processing');
    
    // Make API call to the location service
    const encodedPrompt = encodeURIComponent(text);
    const response = await fetch(`http://localhost:8001/api/location/?prompt=${encodedPrompt}`, {
      method: 'POST'
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    // Parse the response
    const result = await response.json();
    console.log('✅ API response:', result);
    
    // Hide loading indicator
    hideLoading(loadingId);
    
    // Format and display response
    const message = formatLocationResponse(result);
    appendMessage('ai', message);
    
    // Display location on map
    displayLocationsOnMap(result);
  } catch (error) {
    console.error('❌ API error:', error);
    hideLoading(loadingId);
    appendMessage('ai', `Üzgünüm, bir hata oluştu: ${error.message}`);
  }
}

// Check if query contains keywords for integration with other services
function checkForIntegrationKeywords(text) {
  const integrationKeywords = [
    // Foursquare related
    'foursquare', 'fsq', 'yeme', 'içme', 'kafe', 'restoran', 'mekan', 'yer', 'cafe', 'restaurant',
    
    // MAKS related
    'maks', 'bina', 'yapı', 'building', 'mimari', 'ev', 'daire', 'inşaat',
    
    // Overpass related
    'overpass', 'yol', 'sokak', 'cadde', 'bulvar', 'highway', 'road', 'street'
  ];
  
  return integrationKeywords.some(keyword => text.includes(keyword));
}

// Helper function to format the location response for display
function formatLocationResponse(response) {
  // Handle error response
  if (response.error) {
    return `<div class="error-message">Üzgünüm, bir hata oluştu: ${response.error}</div>`;
  }
  
  // For a single location result
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
  
  // For multiple results (expanded query)
  if (response.results && Array.isArray(response.results)) {
    if (response.results.length === 0) {
      return '<div class="warning-message">Belirtilen kriterlere uygun sonuç bulunamadı.</div>';
    }
    
    let resultsHtml = `<div class="location-results">
      <strong>${response.results.length} sonuç bulundu:</strong><br>
      <ul class="results-list">`;
    
    response.results.forEach((result, index) => {
      let name = result.name || `Sonuç ${index+1}`;
      let category = result.categories && result.categories.length ? 
        ` (${result.categories[0]})` : '';
      let coord = result.latitude && result.longitude ? 
        ` - ${result.latitude.toFixed(4)}, ${result.longitude.toFixed(4)}` : '';
      
      resultsHtml += `<li>${name}${category}${coord}</li>`;
    });
    
    resultsHtml += '</ul></div>';
    return resultsHtml;
  }
  
  // For unknown response format, return JSON
  return `<pre>${JSON.stringify(response, null, 2)}</pre>`;
}

// Display locations on the map
function displayLocationsOnMap(result) {
  // Get map instance (fallback to window.map if needed)
  const map = mapInstance || window.map;
  if (!map) {
    console.error('❌ No map instance available for displaying locations');
    return;
  }
  
  // Clear existing markers
  if (window.locationMarkers && window.locationMarkers.length > 0) {
    window.locationMarkers.forEach(marker => marker.remove());
    window.locationMarkers = [];
  }
  
  try {
    // Handle single location
    if (result.latitude && result.longitude) {
      console.log('📍 Centering map on single location');
      
      // Fly to location
      map.flyTo({
        center: [result.longitude, result.latitude],
        zoom: 15,
        essential: true
      });
      
      // Add marker
      const marker = addLocationMarker(result.latitude, result.longitude, result.place || 'Konum');
      if (marker) window.locationMarkers.push(marker);
    }
    // Handle multiple locations
    else if (result.results && Array.isArray(result.results) && result.results.length > 0) {
      console.log(`📍 Displaying ${result.results.length} locations`);
      
      const bounds = new mapboxgl.LngLatBounds();
      let markersAdded = 0;
      
      // Add markers for each result with coordinates
      result.results.forEach(location => {
        if (location.latitude && location.longitude) {
          const marker = addLocationMarker(
            location.latitude, 
            location.longitude, 
            location.name || `Sonuç ${markersAdded+1}`
          );
          
          if (marker) {
            window.locationMarkers.push(marker);
            bounds.extend([location.longitude, location.latitude]);
            markersAdded++;
          }
        }
      });
      
      // Fit map to show all markers if we added any
      if (markersAdded > 0 && !bounds.isEmpty()) {
        map.fitBounds(bounds, { padding: 50, maxZoom: 15 });
      }
    }
  } catch (error) {
    console.error('❌ Error displaying locations on map:', error);
  }
}

// Add a location marker to the map
function addLocationMarker(lat, lon, title) {
  const map = mapInstance || window.map;
  if (!map) {
    console.error('❌ No map instance available for adding marker');
    return null;
  }
  
  try {
    // Create marker element
    const el = document.createElement('div');
    el.className = 'ai-marker';
    el.style.width = '25px';
    el.style.height = '25px';
    el.style.backgroundImage = 'url("../js/assets/location-pin.png")';
    el.style.backgroundSize = 'cover';
    
    // Create and add marker
    const marker = new mapboxgl.Marker(el)
      .setLngLat([lon, lat])
      .setPopup(new mapboxgl.Popup({ offset: 25 })
        .setHTML(`<h3>${title || 'Konum'}</h3>`))
      .addTo(map);
    
    return marker;
  } catch (error) {
    console.error('❌ Error adding marker:', error);
    return null;
  }
}

// Show loading indicator
function showLoading() {
  const container = document.getElementById('chat-messages');
  const loadingDiv = document.createElement('div');
  loadingDiv.className = 'chatbox-message ai loading';
  loadingDiv.textContent = 'Düşünüyorum...';
  container.appendChild(loadingDiv);
  container.scrollTop = container.scrollHeight;
  return Date.now(); // Unique ID
}

// Hide loading indicator
function hideLoading(id) {
  const loadingMessages = document.querySelectorAll('.chatbox-message.loading');
  if (loadingMessages.length > 0) {
    loadingMessages[loadingMessages.length - 1].remove();
  }
}

// Add a message to the chat
function appendMessage(role, text) {
  const container = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = `chatbox-message ${role}`;
  div.innerHTML = text; // Use innerHTML to handle HTML content
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function enableChatboxPin() {
  const wrapper = document.getElementById('chatbox-wrapper');
  const pinButton = document.getElementById('pin-toggle');

  if (!wrapper || !pinButton) return;

  pinButton.addEventListener('click', () => {
    wrapper.classList.toggle('pinned');
    pinButton.textContent = wrapper.classList.contains('pinned') ? '📍' : '📌';
  });
}