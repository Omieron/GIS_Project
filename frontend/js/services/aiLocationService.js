// AI Location Service - Doğal dil sorgusu ile konum arama servisi

const BASE_URL = 'http://localhost:8001';

/**
 * Doğal dil kullanarak konum sorgusu yapar
 * @param {string} query - Kullanıcının konum sorgusu
 * @returns {Promise} - Konum verisi ile API yanıtı
 */
export async function processLocationQuery(query) {
  try {
    // The backend expects the prompt as a query parameter, not in the request body
    const encodedPrompt = encodeURIComponent(query);
    const url = `${BASE_URL}/api/location/?prompt=${encodedPrompt}`;
    
    console.log('🔍 Sending location query:', url);
    
    const response = await fetch(url, {
      method: 'POST'
      // No body needed as we're using query parameters
    });
    
    if (!response.ok) {
      throw new Error(`API hatası: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('❌ Konum sorgusu hatası:', error);
    throw error;
  }
}

/**
 * Gelişmiş konum sorgusu ile OpenStreetMap entegrasyonu
 * @param {string} query - Kullanıcının konum sorgusu
 * @param {string} language - Dil kodu (varsayılan: 'tr')
 * @returns {Promise} - Gelişmiş konum verisi ile API yanıtı
 */
export async function processEnhancedQuery(query, language = 'tr') {
  try {
    // The backend expects the parameters as query parameters, not in the request body
    const encodedPrompt = encodeURIComponent(query);
    const url = `${BASE_URL}/api/enhanced-location/?prompt=${encodedPrompt}&language=${language}`;
    
    console.log('🔎 Sending enhanced query:', url);
    
    const response = await fetch(url, {
      method: 'POST'
      // No body needed as we're using query parameters
    });
    
    if (!response.ok) {
      throw new Error(`API hatası: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('❌ Gelişmiş konum sorgusu hatası:', error);
    throw error;
  }
}

/**
 * Belirli bir konumun yakınındaki tesisleri arar
 * @param {string} amenityType - Tesis türü (restaurant, cafe, vb.)
 * @param {number} lat - Enlem
 * @param {number} lon - Boylam
 * @param {number} radius - Arama yarıçapı (metre)
 * @returns {Promise} - Tesisler verisi ile API yanıtı
 */
export async function getOsmAmenities(amenityType, lat, lon, radius = 1000) {
  let url = `${BASE_URL}/api/osm/amenities/?amenity_type=${encodeURIComponent(amenityType)}&radius=${radius}`;
  
  if (lat && lon) {
    url += `&lat=${lat}&lon=${lon}`;
  }
  
  try {
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`API hatası: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('❌ OSM tesisleri sorgusu hatası:', error);
    throw error;
  }
}
