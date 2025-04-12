import { createDraggableCircle } from '../map/circle.js';
import { circleRegistry } from '../map/circleRegistry.js';
import { fetchFoursquarePlaces } from '../services/foursquareService.js';

const categoryIcons = {
  // ☕ Cafe
  13032: '../js/assets/cofee.png',
  13033: '../js/assets/cofee.png',
  13034: '../js/assets/cofee.png',
  13035: '../js/assets/cofee.png',
  13036: '../js/assets/cofee.png',
  13063: '../js/assets/cofee.png',
  13372: '../js/assets/cofee.png',
  11126: '../js/assets/cofee.png',
  17063: '../js/assets/cofee.png',

  // 💊 Pharmacy
  17145: '../js/assets/pharmacy.png',
  17035: '../js/assets/pharmacy.png',

  // 🏥 Hospital
  15013: '../js/assets/hospital.png',
  15014: '../js/assets/hospital.png',
  15058: '../js/assets/hospital.png',
  15059: '../js/assets/hospital.png',

  // 🛒 Market / Grocery
  11185: '../js/assets/market.png',
  11186: '../js/assets/market.png',
  11193: '../js/assets/market.png',
  13062: '../js/assets/market.png',
  14009: '../js/assets/market.png',
  14010: '../js/assets/market.png',
  14011: '../js/assets/market.png',
  14012: '../js/assets/market.png',
  14013: '../js/assets/market.png',
  14014: '../js/assets/market.png',
  17054: '../js/assets/market.png',
  17055: '../js/assets/market.png',
  17057: '../js/assets/market.png',
  17065: '../js/assets/market.png',
  17066: '../js/assets/market.png',
  17069: '../js/assets/market.png',
  17070: '../js/assets/market.png',
  17114: '../js/assets/market.png',
  17115: '../js/assets/market.png',
  17142: '../js/assets/market.png',
  17144: '../js/assets/market.png',
  11056: '../js/assets/market.png',
  11057: '../js/assets/market.png',
  11058: '../js/assets/market.png',
  17058: '../js/assets/market.png',
  17059: '../js/assets/market.png',
  17060: '../js/assets/market.png',
  17061: '../js/assets/market.png',
  17062: '../js/assets/market.png',
  17064: '../js/assets/market.png',
  17067: '../js/assets/market.png',
  17068: '../js/assets/market.png',
  17071: '../js/assets/market.png',
  17072: '../js/assets/market.png',
  17073: '../js/assets/market.png',
  17074: '../js/assets/market.png',
  17075: '../js/assets/market.png',
  17076: '../js/assets/market.png',
  17077: '../js/assets/market.png',
  17078: '../js/assets/market.png',
  17079: '../js/assets/market.png',
  17080: '../js/assets/market.png',

  // ⛽ Fuel
  19007: '../js/assets/gas.png',
  19006: '../js/assets/gas.png',

  // 🌳 Park
  10001: '../js/assets/park.png',
  10055: '../js/assets/park.png',
  10058: '../js/assets/park.png',
  12114: '../js/assets/park.png',
  16032: '../js/assets/park.png',
  16033: '../js/assets/park.png',
  16034: '../js/assets/park.png',
  16035: '../js/assets/park.png',
  16036: '../js/assets/park.png',
  16037: '../js/assets/park.png',
  16038: '../js/assets/park.png',
  16039: '../js/assets/park.png',
  18055: '../js/assets/park.png',
  19020: '../js/assets/park.png',
  19025: '../js/assets/park.png'
};

const categoryMapping = {
  cafe: [11126, 13032, 13033, 13034, 13035, 13036, 13063, 13372, 17063],
  pharmacy: [17145, 17035],
  hospital: [15013, 15014, 15058, 15059],
  market: [
    11185, 11186, 11193, 13062,
    14009, 14010, 14011, 14012, 14013, 14014,
    17054, 17055, 17065, 17066, 17069, 17070,
    17114, 17115, 17142, 17144,
    11056, 11057, 11058,
    17057, 17058, 17059, 17060, 17061, 17062, 17064,
    17067, 17068, 17071, 17072, 17073, 17074, 17075,
    17076, 17077, 17078, 17079, 17080
  ],
  fuel: [19007, 19006],
  park: [10001, 10055, 10058, 12114, 16032, 16033, 16034, 16035, 16036, 16037, 16038, 16039, 18055, 19020, 19025]
};

// Store fetched places in memory to avoid redundant API calls
let placesCache = {}; // Structure: { circleId: { category: [...places] } }
let activeMarkerLayer = [];
let currentCircleId = null;
let circleMoveTimeout = null;

export function bindFoursquareEvents(map) {
  // Listen for circle creation - this is triggered by the bindUIEvents function
  window.addEventListener('circle:created', (e) => {
    const { type, marker, id } = e.detail;
    if (type !== 'foursquare') return;

    console.log("🟢 Foursquare çemberi oluşturuldu, panel açılıyor...");
    currentCircleId = id || 'foursquare';
    
    // Reset cache for this new circle
    placesCache[currentCircleId] = {};
    
    // Set up the dragend event handler directly from the marker
    marker.on('dragend', () => {
      const newCenter = marker.getLngLat();
      console.log(`🎯 Yeni hedef koordinat: ${newCenter.lng}, ${newCenter.lat}`);
      
      // Clear any existing timeout
      if (circleMoveTimeout) clearTimeout(circleMoveTimeout);
      
      // Set a small timeout to avoid multiple rapid updates
      circleMoveTimeout = setTimeout(() => {
        console.log("🔄 Çember taşındı, yeni konuma göre veri güncelleniyor...");
        
        // Reset cache for this circle
        placesCache[currentCircleId] = {}; 
        
        // Refresh the markers based on current selection
        updateFoursquareMarkers(map, marker);
      }, 500);
    });

    const card = document.getElementById('foursquare-card');
    card.style.display = 'block';

    // Panel içeriğini temizle ve yeniden oluştur
    card.innerHTML = '<strong>Foursquare Kategorileri</strong><br/><br/>';

    // Tümünü Seç Toggle
    const toggleAllLabel = document.createElement('label');
    toggleAllLabel.style.display = 'flex';
    toggleAllLabel.style.alignItems = 'center';
    toggleAllLabel.style.marginBottom = '12px';
    toggleAllLabel.style.fontWeight = 'bold';

    const toggleAllInput = document.createElement('input');
    toggleAllInput.type = 'checkbox';
    toggleAllInput.style.marginRight = '8px';
    toggleAllInput.dataset.toggleAll = 'true';

    toggleAllInput.addEventListener('change', async () => {
      const allCheckboxes = card.querySelectorAll('input[type="checkbox"]:not([data-toggle-all])');
      allCheckboxes.forEach(cb => cb.checked = toggleAllInput.checked);

      await updateFoursquareMarkers(map, marker);
    });

    toggleAllLabel.appendChild(toggleAllInput);
    toggleAllLabel.appendChild(document.createTextNode('Tümünü Seç'));
    card.appendChild(toggleAllLabel);

    // Kategori checkboxları
    Object.entries(categoryMapping).forEach(([key, value]) => {
      const label = document.createElement('label');
      label.style.cssText = 'display: flex; align-items: center; margin-bottom: 6px;';

      const input = document.createElement('input');
      input.type = 'checkbox';
      input.style.marginRight = '8px';
      input.dataset.category = key;

      input.addEventListener('change', async () => {
        await updateFoursquareMarkers(map, marker);
      });

      label.appendChild(input);
      label.appendChild(document.createTextNode(key));
      card.appendChild(label);
    });
  });
}

async function updateFoursquareMarkers(map, marker) {
  const card = document.getElementById('foursquare-card');
  const selected = getSelectedCategories(card);
  
  if (selected.length === 0) {
    clearFoursquareMarkers();
    return;
  }
  
  const coord = marker.getLngLat();
  clearFoursquareMarkers();
  
  // Create a loading indicator
  const loadingDiv = document.createElement('div');
  loadingDiv.id = 'fsq-loading';
  loadingDiv.textContent = 'Yükleniyor...';
  loadingDiv.style.cssText = 'position: absolute; top: 10px; right: 10px; background: white; padding: 5px; border-radius: 4px; z-index: 1000;';
  document.body.appendChild(loadingDiv);
  
  try {
    const allPlaces = await fetchCategoriesInChunks(selected, coord);
    addFoursquareMarkers(map, allPlaces);
  } catch (error) {
    console.error('Error fetching places:', error);
  } finally {
    // Remove loading indicator
    const loader = document.getElementById('fsq-loading');
    if (loader) loader.remove();
  }
}

function getSelectedCategories(card) {
  const selected = [];
  card.querySelectorAll('input[type="checkbox"]:not([data-toggle-all])').forEach((cb) => {
    if (cb.checked) selected.push(cb.dataset.category);
  });
  return selected;
}

async function fetchCategoriesInChunks(selectedCategories, coord) {
  // Get all category IDs for the selected categories
  const allCategoryIds = selectedCategories.reduce((acc, category) => {
    const ids = categoryMapping[category];
    if (ids) acc.push(...ids);
    return acc;
  }, []);
  
  // Initialize the places array
  let allPlaces = [];
  
  // Check if we already have cached results for these categories
  const cachedCategories = selectedCategories.filter(cat => 
    placesCache[currentCircleId] && placesCache[currentCircleId][cat]
  );
  
  // Use cached results if available
  cachedCategories.forEach(cat => {
    allPlaces = [...allPlaces, ...placesCache[currentCircleId][cat]];
  });
  
  // Calculate which categories we need to fetch
  const categoriesToFetch = selectedCategories.filter(cat => 
    !placesCache[currentCircleId] || !placesCache[currentCircleId][cat]
  );
  
  if (categoriesToFetch.length === 0) {
    return allPlaces; // Return only cached results if everything is cached
  }
  
  // For categories we need to fetch, get their IDs
  const idsToFetch = categoriesToFetch.reduce((acc, category) => {
    const ids = categoryMapping[category];
    if (ids) acc.push(...ids);
    return acc;
  }, []);
  
  // Create chunks of max 30 category IDs (Foursquare API limit)
  const chunks = [];
  for (let i = 0; i < idsToFetch.length; i += 30) {
    chunks.push(idsToFetch.slice(i, i + 30));
  }
  
  // Initialize placesCache for this circle if it doesn't exist
  if (!placesCache[currentCircleId]) {
    placesCache[currentCircleId] = {};
  }
  
  // Fetch places for each chunk
  let newPlaces = [];
  for (const chunk of chunks) {
    try {
      const placesChunk = await fetchFoursquarePlaces(coord, 500, chunk);
      newPlaces = [...newPlaces, ...placesChunk];
      
      // Cache the results by category
      for (const place of placesChunk) {
        const categoryId = place.categories?.[0]?.id;
        if (categoryId) {
          // Find which category this ID belongs to
          for (const [category, ids] of Object.entries(categoryMapping)) {
            if (ids.includes(categoryId)) {
              if (!placesCache[currentCircleId][category]) {
                placesCache[currentCircleId][category] = [];
              }
              // Avoid duplicates in cache
              if (!placesCache[currentCircleId][category].find(p => p.fsq_id === place.fsq_id)) {
                placesCache[currentCircleId][category].push(place);
              }
              break;
            }
          }
        }
      }
    } catch (error) {
      console.error(`Error fetching chunk: ${chunk}`, error);
    }
  }
  
  // Return combination of cached and new places
  return [...allPlaces, ...newPlaces];
}

function clearFoursquareMarkers() {
  activeMarkerLayer.forEach((marker) => marker.remove());
  activeMarkerLayer = [];
}

function addFoursquareMarkers(map, places) {
  // Remove duplicates by fsq_id
  const uniquePlaces = Array.from(
    new Map(places.map(place => [place.fsq_id, place])).values()
  );
  
  for (const place of uniquePlaces) {
    const categoryId = place.categories?.[0]?.id;
    let iconUrl = categoryIcons[categoryId];
    
    // If no direct icon mapping is found, try to determine the appropriate icon
    if (!iconUrl) {
      // Check if it's a market category
      if (categoryMapping.market.includes(categoryId)) {
        iconUrl = '../js/assets/market.png';
      } 
      // If not market, check if it's a cafe
      else if (categoryMapping.cafe.includes(categoryId)) {
        iconUrl = '../js/assets/cofee.png';
      }
      // Skip places without a mapped icon
      else {
        continue; // Skip this place entirely
      }
    }

    const el = document.createElement('div');
    el.className = 'fsq-marker';
    el.style.backgroundImage = `url(${iconUrl})`;
    el.style.width = '32px';
    el.style.height = '32px';
    el.style.backgroundSize = 'cover';
    el.style.borderRadius = '50%';

    const marker = new mapboxgl.Marker(el)
      .setLngLat([place.geocodes.main.longitude, place.geocodes.main.latitude])
      .setPopup(
        new mapboxgl.Popup()
          .setHTML(`
            <strong>${place.name}</strong><br/>
            ${place.categories?.[0]?.name || ''}<br/>
            ${place.location?.address || ''}
          `)
      )
      .addTo(map);

    activeMarkerLayer.push(marker);
  }
  
  console.log(`🎯 Toplam ${activeMarkerLayer.length} nokta haritaya eklendi.`);
}