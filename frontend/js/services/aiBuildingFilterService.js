/**
 * Service for interacting with the AI Building Filter API
 */

import { checkDepremToggle } from '../events/maksHandler.js';
import { updateLayerColorByRisk } from './maksService.js';

// Base URL for the API
const API_BASE_URL = 'http://localhost:8001';

/**
 * Process a natural language building filter query
 * @param {string} query - Natural language query for filtering buildings
 * @returns {Promise<Object>} - Filter parameters extracted from the query
 */
/**
 * Execute a SQL update query against the buildings
 * @param {string} sqlQuery - The SQL query to execute
 * @returns {Promise<Object>} - Result of the update operation
 */
export async function executeUpdateQuery(sqlQuery) {
  try {
    console.log(`🔄 Executing SQL update query: ${sqlQuery}`);
    
    // Get building IDs from cache - if no buildings are filtered/selected, don't proceed
    if (!window.buildingCache || !window.buildingCache.features || window.buildingCache.features.length === 0) {
      console.error('❌ No buildings are filtered/selected. Cannot perform update.');
      throw new Error('Güncellenecek bina bulunamadı. Lütfen önce bir bölge seçin.');
    }
    
    // Extract the IDs from the filtered buildings
    const buildingIds = window.buildingCache.features
      .map(feature => feature.properties?.ID)
      .filter(id => id); // Remove any undefined or null IDs
    
    if (buildingIds.length === 0) {
      console.error('❌ No valid building IDs found in the filtered set.');
      throw new Error('Filtrelenmiş binalar için geçerli ID bulunamadı.');
    }
    
    console.log(`🔍 Updating ${buildingIds.length} filtered buildings`);
    
    const response = await fetch(`${API_BASE_URL}/maks/update`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        sql_query: sqlQuery,
        building_ids: buildingIds 
      }),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`❌ Error executing update query: ${errorText}`);
      throw new Error(`SQL sorgusu çalıştırılırken hata: ${response.status} ${response.statusText}`);
    }
    
    const result = await response.json();
    console.log(`✅ Update query executed successfully:`, result);
    
    // Show toast notification if available
    if (window.showToast) {
      window.showToast({
        message: `${result.affected_rows} bina güncellendi`,
        type: 'success',
        duration: 3000
      });
    }
    
    return result;
  } catch (error) {
    console.error(`❌ Error in executeUpdateQuery: ${error.message}`);
    
    // Show toast notification if available
    if (window.showToast) {
      window.showToast({
        message: `Güncelleme başarısız: ${error.message}`,
        type: 'error',
        duration: 4000
      });
    }
    
    throw error;
  }
}

export async function processFilterQuery(query) {
  try {
    console.log(`🔍 Processing building filter query: ${query}`);
    
    const response = await fetch(`${API_BASE_URL}/ai-filter/filter/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt: query }),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`❌ Error processing filter query: ${errorText}`);
      throw new Error(`Sorgu işlenirken hata oluştu: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log(`✅ Filter parameters extracted: `, data);
    
    // Log SQL query if present
    if (data.sql_query) {
      console.log(`🔄 SQL sorgusu: ${data.sql_query}`);
      
      // If this is an update request, execute the SQL query
      if (data.is_update_request) {
        console.log("🔄 Update isteği tespit edildi, SQL sorgusu çalıştırılıyor...");
        try {
          await executeUpdateQuery(data.sql_query);
        } catch (updateError) {
          console.error("❌ Update sorgusu çalıştırılırken hata:", updateError);
          // Continue - still return the data even if update fails
        }
      }
    }
    
    return data;
  } catch (error) {
    console.error(`❌ Error in AI building filter service: ${error.message}`);
    throw error;
  }
}

/**
 * Apply the extracted filter parameters to the MAKS building filter UI
 * @param {Object} filterParams - Filter parameters extracted from natural language query
 */
export function applyBuildingFilters(filterParams) {
  try {
    console.log(`🔧 Applying building filters:`, filterParams);
    
    // Set zeministu (floors above ground) filter
    if (filterParams.zeminustu !== undefined && filterParams.zeminustu !== null) {
      const zeminustuInput = document.querySelector('[data-filter="zeminustu"]');
      if (zeminustuInput) {
        zeminustuInput.value = filterParams.zeminustu;
        console.log(`✅ Set zeminustu filter to ${filterParams.zeminustu}`);
      }
    }
    
    // Set zeminalti (floors below ground) filter
    if (filterParams.zeminalti !== undefined && filterParams.zeminalti !== null) {
      const zeminaltiInput = document.querySelector('[data-filter="zeminalti"]');
      if (zeminaltiInput) {
        zeminaltiInput.value = filterParams.zeminalti;
        console.log(`✅ Set zeminalti filter to ${filterParams.zeminalti}`);
      }
    }
    
    // Set durum (building status) filter
    if (filterParams.durum) {
      const durumSelect = document.querySelector('[data-filter="durum"]');
      if (durumSelect) {
        durumSelect.value = filterParams.durum;
        console.log(`✅ Set durum filter to ${filterParams.durum}`);
      }
    }
    
    // Set tip (building type) filter
    if (filterParams.tip) {
      const tipSelect = document.querySelector('[data-filter="tip"]');
      if (tipSelect) {
        tipSelect.value = filterParams.tip;
        console.log(`✅ Set tip filter to ${filterParams.tip}`);
      }
    }
    
    // Set seragazi (greenhouse emissions) filter
    if (filterParams.seragazi) {
      const seragaziSelect = document.querySelector('[data-filter="seragazi"]');
      if (seragaziSelect) {
        seragaziSelect.value = filterParams.seragazi;
        console.log(`✅ Set seragazi filter to ${filterParams.seragazi}`);
      }
    }
    
    // Set deprem_riski (earthquake risk) filter
    if (filterParams.deprem_riski) {
      // First ensure the toggle is ON
      const depremToggle = document.getElementById('deprem-toggle');
      if (depremToggle) {
        depremToggle.checked = true;
        console.log(`✅ Set deprem_toggle to true (required for deprem_riski)`);
        checkDepremToggle(map);
        updateLayerColorByRisk(map);
        
        // Then show the deprem_riski dropdown
        const filterWrapper = document.getElementById('deprem-filter-wrapper');
        if (filterWrapper) {
          filterWrapper.style.display = 'block';
          console.log(`✅ Showed deprem_riski dropdown`);
        }
        
        // Finally set the dropdown value
        const depremRiskiSelect = document.querySelector('[data-filter="deprem_riski"]');
        if (depremRiskiSelect) {
          depremRiskiSelect.value = filterParams.deprem_riski;
          console.log(`✅ Set deprem_riski to ${filterParams.deprem_riski}`);
        }
      }
    }
    
    // Set deprem_toggle (earthquake risk toggle) filter
    if (filterParams.deprem_toggle !== undefined) {
      const depremToggle = document.getElementById('deprem-toggle');
      if (depremToggle) {
        depremToggle.checked = filterParams.deprem_toggle;
        console.log(`✅ Set deprem_toggle to ${filterParams.deprem_toggle}`);
        
        // Show/hide the deprem_riski dropdown based on toggle state
        const filterWrapper = document.getElementById('deprem-filter-wrapper');
        if (filterWrapper) {
          filterWrapper.style.display = filterParams.deprem_toggle ? 'block' : 'none';
          console.log(`✅ ${filterParams.deprem_toggle ? 'Showed' : 'Hid'} deprem_riski dropdown`);
        }
      }
    }
    
    // Trigger filter application
    const filterButton = document.getElementById('apply-filters-btn');
    if (filterButton) {
      filterButton.click();
      console.log(`🔄 Triggered filter application`);
    } else {
      // If no button exists, dispatch a custom event
      document.dispatchEvent(new CustomEvent('building:filter:applied'));
      console.log(`🔄 Dispatched filter applied event`);
    }
    
    return true;
  } catch (error) {
    console.error(`❌ Error applying building filters: ${error.message}`);
    return false;
  }
}