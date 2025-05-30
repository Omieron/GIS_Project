import React, { useState } from 'react';
import '../../styles/ChatBot.css';

interface ChatBotProps {
  isVisible?: boolean;
}

const ChatBot: React.FC<ChatBotProps> = ({ isVisible = true }) => {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [inputValue, setInputValue] = useState<string>('');

  if (!isVisible) return null;

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const handleSend = () => {
    if (inputValue.trim()) {
      // TODO: Mesaj gönderme işlevselliği buraya eklenecek
      console.log('Mesaj gönderildi:', inputValue);
      setInputValue('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={`chatbot-container ${isOpen ? 'open' : 'minimized'}`}>
      {/* Chat Header */}
      <div className="chatbot-header" onClick={toggleChat}>
        <div className="chatbot-header-info">
          <div className="chatbot-avatar">
            <span className="chatbot-avatar-icon">🤖</span>
            <div className="chatbot-status-dot"></div>
          </div>
          <div className="chatbot-header-text">
            <h4>AI Harita Asistanı</h4>
            <span className="chatbot-status">Çevrimiçi</span>
          </div>
        </div>
        
        <button className="chatbot-toggle">
          <svg 
            className={`chatbot-toggle-icon ${isOpen ? 'rotated' : ''}`}
            width="20" 
            height="20" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2"
          >
            <polyline points="6,9 12,15 18,9"></polyline>
          </svg>
        </button>
      </div>

      {/* Chat Messages */}
      {isOpen && (
        <>
          <div className="chatbot-messages">
            {/* Bot Welcome Message */}
            <div className="message bot">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="message-text">
                  Merhaba! 🌍 Size AI destekli harita asistanınız olarak yardımcı olabilirim. 
                  Herhangi bir konumu arayabilir, yol tarifi alabilir veya çevrenizde ilginç yerler keşfedebilirsiniz.
                </div>
                <div className="message-suggestions">
                  <button className="suggestion-button">Yakındaki restoranları bul</button>
                  <button className="suggestion-button">Hastane ara</button>
                  <button className="suggestion-button">Trafik durumu</button>
                  <button className="suggestion-button">Rota planla</button>
                </div>
                <div className="message-time">
                  {new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>

            {/* Example User Message */}
            <div className="message user">
              <div className="message-avatar user-avatar">👤</div>
              <div className="message-content">
                <div className="message-text">
                  Yakındaki restoranları göster
                </div>
                <div className="message-time">
                  {new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>

            {/* Example Bot Response */}
            <div className="message bot">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="message-text">
                  🍽️ Yakınınızdaki en iyi restoranları buldum! Haritada işaretliyorum. 
                  Hangi mutfağı tercih ediyorsunuz?
                </div>
                <div className="message-suggestions">
                  <button className="suggestion-button">İtalyan</button>
                  <button className="suggestion-button">Türk</button>
                  <button className="suggestion-button">Çin</button>
                  <button className="suggestion-button">Fast Food</button>
                </div>
                <div className="message-time">
                  {new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          </div>

          {/* Chat Input */}
          <div className="chatbot-input-container">
            <div className="chatbot-input-wrapper">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Mesajınızı yazın..."
                className="chatbot-input"
                maxLength={500}
              />
              <button
                onClick={handleSend}
                disabled={!inputValue.trim()}
                className="chatbot-send-button"
                aria-label="Mesaj gönder"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="22" y1="2" x2="11" y2="13"></line>
                  <polygon points="22,2 15,22 11,13 2,9 22,2"></polygon>
                </svg>
              </button>
            </div>
            
            {/* Quick Actions */}
            <div className="chatbot-quick-actions">
              <button className="quick-action-button" title="Restoranlar">🍽️</button>
              <button className="quick-action-button" title="Rota">🗺️</button>
              <button className="quick-action-button" title="Trafik">🚦</button>
              <button className="quick-action-button" title="Hastaneler">🏥</button>
              <button className="quick-action-button" title="Konumum">📍</button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default ChatBot;