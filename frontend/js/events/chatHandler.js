/**
 * Handler for chat functionality with mode switching between location and building filter services
 */

import { processIntegratedQuery } from './integrationHandler.js';
import { processFilterQuery, applyBuildingFilters } from '../services/aiBuildingFilterService.js';
import { enableChatboxPin } from '../ai_chat/chatbox.js';
import { enableSpeechToText } from '../ai_chat/speechToText.js';

// Chat DOM elements
let chatInput;
let chatMessages;
let sendButton;
let modeToggle;

// Map reference
let mapInstance = null;

// Create global array for location markers
window.locationMarkers = window.locationMarkers || [];

// Current AI mode
let isFilterMode = false;

/**
 * Initialize the chat handler
 * @param {Object} mapObj - Reference to the map object
 */
export function initChatHandler(mapObj) {
  // Store map reference
  if (mapObj) {
    mapInstance = mapObj;
    console.log('✅ Map instance received in chatHandler.js');
  } else {
    // Use window.map as fallback
    mapInstance = window.map;
    console.log('⚠️ Using window.map as fallback in chatHandler.js');
  }
  // Get DOM elements
  chatInput = document.getElementById('chat-input');
  chatMessages = document.getElementById('chat-messages');
  sendButton = document.getElementById('chat-send');
  modeToggle = document.getElementById('ai-mode-toggle');
  
  // Initialize mode labels
  const locationLabel = document.querySelector('.mode-label:first-of-type');
  if (locationLabel) {
    locationLabel.classList.add('active');
  }

  // Add event listeners
  chatInput.addEventListener('keypress', handleKeyPress);
  sendButton.addEventListener('click', sendMessage);
  modeToggle.addEventListener('change', switchAIMode);
  
  // Set initial UI state based on default mode (location mode)
  //document.querySelector('.chatbox-header').style.background = '#2196F3';
  enableChatboxPin();
  enableSpeechToText();
  console.log('🤖 Chat handler initialized');
}

/**
 * Handle Enter key press in chat input
 */
function handleKeyPress(e) {
  if (e.key === 'Enter') {
    sendMessage();
  }
}

/**
 * Switch between location and building filter modes
 */
function switchAIMode() {
  isFilterMode = modeToggle.checked;
  
  // Get the header element and mode labels
  const chatHeader = document.querySelector('.chatbox-header');
  const locationLabel = document.querySelector('.mode-label:first-of-type');
  const filterLabel = document.querySelector('.mode-label:last-of-type');
  
  // Update UI based on mode
  if (isFilterMode) {
    // Building Filter Mode - Orange color
    if (chatHeader) chatHeader.style.background = '#FF9800';
    if (chatInput) chatInput.placeholder = 'Bina filtreleri için doğal dil sorgusu yazın...';
    console.log('🔄 Switched to Building Filter mode');
    
    // Update label styles
    if (locationLabel) locationLabel.classList.remove('active');
    if (filterLabel) filterLabel.classList.add('active');
  } else {
    // Location Mode - Blue color
    if (chatHeader) chatHeader.style.background = '#2196F3';
    if (chatInput) chatInput.placeholder = 'Konum sorgusu yazın...';
    console.log('🔄 Switched to Location Search mode');
    
    // Update label styles
    // Update label styles - NULL KONTROLÜ EKLE
    if (locationLabel) locationLabel.classList.add('active');
    if (filterLabel) filterLabel.classList.remove('active');
  }
  
  // Add a system message indicating the mode change
  const modeMessage = isFilterMode 
    ? 'Bina Filtre moduna geçildi. Binalar için filtreleme sorgularınızı yazabilirsiniz. Örnek: "5 katın üzerindeki apartmanları göster" veya "yüksek deprem riskli binalar"'
    : 'Konum Arama moduna geçildi. Konum sorgularınızı yazabilirsiniz. Örnek: "Edremit\'te kafeler nerede?" veya "Akçay\'da bir eczane bul"';
  
  appendMessage('system', modeMessage);
}

/**
 * Send a message to the appropriate AI service
 */
function sendMessage() {
  const query = chatInput.value.trim();
  
  if (!query) return;
  
  // Display the user's message
  appendMessage('user', query);
  
  // Clear the input
  chatInput.value = '';
  
  // Append a thinking message
  const thinkingId = appendMessage('thinking', 'Düşünüyor...');
  
  if (isFilterMode) {
    // Use the Building Filter service
    processFilterQuery(query)
      .then(filterParams => {
        // Remove the thinking message
        removeMessage(thinkingId);
        
        // Show the filter parameters
        let responseMessage = filterParams.processed_query || 'Filtreler uygulanıyor...';
        
        if (filterParams.error) {
          responseMessage = `Hata: ${filterParams.error}`;
        }
        
        appendMessage('ai', responseMessage);
        
        // Apply the filter parameters
        if (!filterParams.error) {
          applyBuildingFilters(filterParams);
        }
      })
      .catch(error => {
        // Remove the thinking message
        removeMessage(thinkingId);
        
        // Show the error
        appendMessage('ai', `Hata: ${error.message}`);
      });
  } else {
    // Use the Location service
    processIntegratedQuery(query, mapInstance, appendMessage)
      .then(() => {
        // Remove the thinking message
        removeMessage(thinkingId);
        // processIntegratedQuery handles its own messaging
      })
      .catch(error => {
        // Remove the thinking message
        removeMessage(thinkingId);
        
        // Show the error
        appendMessage('ai', `Hata: ${error.message}`);
      });
  }
}

/**
 * Append a message to the chat window
 * @param {string} sender - 'user', 'ai', 'system', or 'thinking'
 * @param {string} message - The message text
 * @returns {string} The ID of the message element
 */
export function appendMessage(sender, message) {
  const messageId = `msg-${Date.now()}`;
  const messageDiv = document.createElement('div');
  
  messageDiv.id = messageId;
  messageDiv.className = `chatbox-message ${sender}-message`;
  
  // Add sender icon
  let icon = '';
  switch (sender) {
    case 'user':
      icon = '👤';
      break;
    case 'ai':
      icon = '🤖';
      break;
    case 'system':
      icon = '🔔';
      break;
    case 'thinking':
      icon = '⏳';
      break;
  }
  
  messageDiv.innerHTML = `<span class="message-icon">${icon}</span> ${message}`;
  chatMessages.appendChild(messageDiv);
  
  // Scroll to bottom
  chatMessages.scrollTop = chatMessages.scrollHeight;
  
  return messageId;
}

/**
 * Remove a message from the chat window
 * @param {string} messageId - The ID of the message to remove
 */
function removeMessage(messageId) {
  const messageDiv = document.getElementById(messageId);
  if (messageDiv) {
    messageDiv.remove();
  }
}
