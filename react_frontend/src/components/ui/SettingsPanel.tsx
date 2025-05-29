import React, { useState } from 'react';
import '../../styles/SettingsPanel.css';

interface SettingsPanelProps {

  isDarkMode: boolean;

  onDarkModeToggle: (enabled: boolean) => void;

  is3DBuildingsEnabled: boolean;

  on3DBuildingsToggle: (enabled: boolean) => void;

  isVisible?: boolean;
}

const SettingsPanel: React.FC<SettingsPanelProps> = ({
  isDarkMode,
  onDarkModeToggle,
  is3DBuildingsEnabled,
  on3DBuildingsToggle,
  isVisible = true
}) => {
  const [isOpen, setIsOpen] = useState<boolean>(false);

  if (!isVisible) {
    return null;
  }

  const togglePanel = (): void => {
    setIsOpen(!isOpen);
  };

  return (
    <div className={`settings-panel ${isOpen ? 'open' : ''}`}>
      {/* Settings Button */}
      <button 
        className="settings-toggle"
        onClick={togglePanel}
        aria-label="Ayarları aç/kapat"
      >
        <svg 
          width="24" 
          height="24" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="2"
        >
          <circle cx="12" cy="12" r="3"></circle>
          <path d="M12 1v6m0 6v6m11-7h-6m-6 0H1m17-4a4 4 0 01-8 0 4 4 0 018 0zM7 21a4 4 0 01-8 0 4 4 0 018 0z"></path>
        </svg>
      </button>

      {/* Settings Content */}
      <div className="settings-content">
        <div className="settings-header">
          <h3>Ayarlar</h3>
        </div>

        <div className="settings-options">
          {/* Dark Mode Toggle */}
          <div className="setting-item">
            <div className="setting-info">
              <span className="setting-icon">🌙</span>
              <div className="setting-text">
                <label htmlFor="dark-mode-toggle">Karanlık Mod</label>
                <span className="setting-description">
                  Harita temasını değiştir
                </span>
              </div>
            </div>
            <label className="toggle-switch">
              <input
                id="dark-mode-toggle"
                type="checkbox"
                checked={isDarkMode}
                onChange={(e) => onDarkModeToggle(e.target.checked)}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>

          {/* 3D Buildings Toggle */}
          <div className="setting-item">
            <div className="setting-info">
              <span className="setting-icon">🏢</span>
              <div className="setting-text">
                <label htmlFor="buildings-toggle">3D Binalar</label>
                <span className="setting-description">
                  Yakınlaştığında 3D binaları göster
                </span>
              </div>
            </div>
            <label className="toggle-switch">
              <input
                id="buildings-toggle"
                type="checkbox"
                checked={is3DBuildingsEnabled}
                onChange={(e) => on3DBuildingsToggle(e.target.checked)}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>
        </div>
      </div>

      {/* Overlay for mobile */}
      {isOpen && (
        <div 
          className="settings-overlay"
          onClick={togglePanel}
          aria-hidden="true"
        />
      )}
    </div>
  );
};

export default SettingsPanel;