import React, { useState } from 'react';
import '../../styles/LayersButton.css';

export interface CustomLayer {
  id: string;
  name: string;
  icon: string;
  description: string;
  color: string;
  enabled: boolean;
}

interface LayersButtonProps {
  layers?: CustomLayer[];
  onLayerToggle: (layerId: string, enabled: boolean) => void;
  isVisible?: boolean;
}

// Custom katmanlar - şimdilik sadece UI için
const defaultLayers: CustomLayer[] = [
  {
    id: 'traffic',
    name: 'Trafik',
    icon: '🚦',
    description: 'Trafik yoğunluğu ve durumu',
    color: '#ef4444',
    enabled: false
  },
  {
    id: 'restaurants',
    name: 'Restoranlar',
    icon: '🍽️',
    description: 'Yakındaki restoranlar',
    color: '#f59e0b',
    enabled: false
  },
  {
    id: 'hospitals',
    name: 'Hastaneler',
    icon: '🏥',
    description: 'Sağlık kuruluşları',
    color: '#dc2626',
    enabled: false
  },
  {
    id: 'schools',
    name: 'Okullar',
    icon: '🏫',
    description: 'Eğitim kurumları',
    color: '#2563eb',
    enabled: false
  },
  {
    id: 'shopping',
    name: 'Alışveriş',
    icon: '🛍️',
    description: 'AVM ve mağazalar',
    color: '#7c3aed',
    enabled: false
  },
  {
    id: 'transport',
    name: 'Ulaşım',
    icon: '🚌',
    description: 'Otobüs ve metro durağı',
    color: '#059669',
    enabled: false
  },
  {
    id: 'parks',
    name: 'Parklar',
    icon: '🌳',
    description: 'Yeşil alanlar ve parklar',
    color: '#65a30d',
    enabled: false
  },
  {
    id: 'gas-stations',
    name: 'Benzinlikler',
    icon: '⛽',
    description: 'Yakıt istasyonları',
    color: '#ea580c',
    enabled: false
  }
];

const LayersButton: React.FC<LayersButtonProps> = ({
  layers = defaultLayers,
  onLayerToggle,
  isVisible = true
}) => {
  const [isOpen, setIsOpen] = useState<boolean>(false);

  if (!isVisible) {
    return null;
  }

  const togglePanel = (): void => {
    setIsOpen(!isOpen);
  };

  const handleLayerToggle = (layerId: string, currentEnabled: boolean): void => {
    onLayerToggle(layerId, !currentEnabled);
    // Panel'i açık bırak - birden fazla katman seçimi yapılabilsin
  };

  const activeLayersCount = layers.filter(layer => layer.enabled).length;

  return (
    <div className={`layers-button-wrapper ${isOpen ? 'open' : ''}`}>
      {/* Layers Toggle Button */}
      <button 
        className="layers-button"
        onClick={togglePanel}
        aria-label="Katmanları aç/kapat"
        title="Harita Katmanları"
      >
        <div className="layers-button-content">
          <span className="layers-icon">🗂️</span>
          <span className="layers-text">Katmanlar</span>
          {activeLayersCount > 0 && (
            <span className="layers-badge">{activeLayersCount}</span>
          )}
          <svg 
            className="layers-arrow"
            width="12" 
            height="12" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2"
          >
            <polyline points="6,9 12,15 18,9"></polyline>
          </svg>
        </div>
      </button>

      {/* Layers Panel */}
      <div className="layers-panel">
        <div className="layers-header">
          <h3>Harita Katmanları</h3>
          <p>Görmek istediğiniz katmanları seçin</p>
        </div>

        <div className="layers-list">
          {layers.map((layer) => (
            <div
              key={layer.id}
              className={`layer-item ${layer.enabled ? 'active' : ''}`}
            >
              <div className="layer-info">
                <div className="layer-icon-wrapper">
                  <span 
                    className="layer-icon"
                    style={{ color: layer.color }}
                  >
                    {layer.icon}
                  </span>
                </div>
                <div className="layer-details">
                  <span className="layer-name">{layer.name}</span>
                  <span className="layer-description">{layer.description}</span>
                </div>
              </div>
              
              <label className="layer-toggle">
                <input
                  type="checkbox"
                  checked={layer.enabled}
                  onChange={() => handleLayerToggle(layer.id, layer.enabled)}
                  aria-label={`${layer.name} katmanını aç/kapat`}
                />
                <span className="layer-toggle-slider"></span>
              </label>
            </div>
          ))}
        </div>

        {activeLayersCount > 0 && (
          <div className="layers-footer">
            <button
              className="clear-all-button"
              onClick={() => {
                layers.forEach(layer => {
                  if (layer.enabled) {
                    onLayerToggle(layer.id, false);
                  }
                });
              }}
            >
              Tümünü Temizle
            </button>
          </div>
        )}
      </div>

      {/* Overlay for mobile */}
      {isOpen && (
        <div 
          className="layers-overlay"
          onClick={togglePanel}
          aria-hidden="true"
        />
      )}
    </div>
  );
};

export default LayersButton;