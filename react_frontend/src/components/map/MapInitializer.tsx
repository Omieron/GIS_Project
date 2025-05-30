import { useRef, useEffect, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { rotateGlobe, flyToLocation } from './mapAnimation';
import { Buildings3D } from './3DBuildings';
import LayersButton from './LayersButton';
import StartButton from '../ui/StartButton';
import SettingsPanel from '../ui/SettingsPanel';
import ChatBot from '../chat/ChatBot';
import '../../styles/MapInitializer.css';

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN;

const MapInitializer: React.FC = () => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const buildings3DRef = useRef<Buildings3D | null>(null);
  const [mapLoaded, setMapLoaded] = useState<boolean>(false);
  const [showButton, setShowButton] = useState<boolean>(true);
  const [currentMapStyle, setCurrentMapStyle] = useState<string>('streets');
  const [is3DBuildingsEnabled, setIs3DBuildingsEnabled] = useState<boolean>(true);
  const [activeLayers, setActiveLayers] = useState<string[]>([]);
  const [isChatMinimized, setIsChatMinimized] = useState<boolean>(true);

  // Style mapping
  const getMapboxStyle = (styleId: string): string => {
    const styleMap: Record<string, string> = {
      'streets': 'mapbox://styles/mapbox/streets-v12',
      'satellite': 'mapbox://styles/mapbox/satellite-v9',
      'satellite-streets': 'mapbox://styles/mapbox/satellite-streets-v12',
      'outdoors': 'mapbox://styles/mapbox/outdoors-v12',
      'light': 'mapbox://styles/mapbox/light-v11',
      'dark': 'mapbox://styles/mapbox/dark-v11',
      'navigation-day': 'mapbox://styles/mapbox/navigation-day-v1'
    };
    return styleMap[styleId] || styleMap['streets'];
  };

  // Dark mode computed property
  const isDarkMode = currentMapStyle === 'dark';

  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Container'ı tamamen temizle
    mapContainerRef.current.innerHTML = '';

    const map = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: getMapboxStyle(currentMapStyle),
      center: [0, 0],
      zoom: 1.5,
      bearing: 0,
      pitch: 0,
      antialias: true,
      projection: 'globe'
    });

    map.on('load', () => {
      mapRef.current = map;
      rotateGlobe(map);
      
      buildings3DRef.current = new Buildings3D(map, 15);
      if (is3DBuildingsEnabled) {
        buildings3DRef.current.addBuildings();
      }
      
      setMapLoaded(true);
    });

    return () => {
      if (buildings3DRef.current) {
        buildings3DRef.current.removeBuildings();
      }
      if (mapRef.current) {
        map.remove();
      }
    };
  }, []);

  const handleStartClick = (): void => {
    if (mapRef.current) {
      flyToLocation(mapRef.current);
      setShowButton(false);
      // ChatBot'u otomatik olarak aç
      setIsChatMinimized(false);
    }
  };

  const handleStyleChange = (styleId: string): void => {
    setCurrentMapStyle(styleId);
    
    if (mapRef.current && buildings3DRef.current) {
      const newStyle = getMapboxStyle(styleId);
      
      // 3D buildings'i kaldır
      buildings3DRef.current.removeBuildings();   
      
      // Yeni style'ı uygula
      mapRef.current.setStyle(newStyle);
      
      // Style yüklendikten sonra 3D buildings'i geri ekle
      mapRef.current.once('styledata', () => {
        const checkStyleLoaded = () => {
          if (mapRef.current?.isStyleLoaded() && buildings3DRef.current) {
            buildings3DRef.current.resetState();
            if (is3DBuildingsEnabled) {
              buildings3DRef.current.addBuildings();
            }
          } else {
            setTimeout(checkStyleLoaded, 50);
          }
        };
        setTimeout(checkStyleLoaded, 100);
      });
    }
  };

  const handleLayerToggle = (layerId: string, enabled: boolean): void => {
    if (enabled) {
      setActiveLayers(prev => [...prev, layerId]);
    } else {
      setActiveLayers(prev => prev.filter(id => id !== layerId));
    }
    
    // TODO: Burada gerçek katman işlemleri yapılacak
    console.log(`Layer ${layerId} ${enabled ? 'açıldı' : 'kapatıldı'}`, { activeLayers });
  };

  const handleDarkModeToggle = (enabled: boolean): void => {
    const newStyle = enabled ? 'dark' : 'streets';
    handleStyleChange(newStyle);
  };

  const handle3DBuildingsToggle = (enabled: boolean): void => {
    setIs3DBuildingsEnabled(enabled);
    if (buildings3DRef.current) {
      if (enabled) {
        buildings3DRef.current.addBuildings();
      } else {
        buildings3DRef.current.removeBuildings();
      }
    }
  };

  // ChatBot event handlers
  const handleLocationRequest = (lat: number, lng: number, address?: string): void => {
    if (mapRef.current) {
      mapRef.current.flyTo({
        center: [lng, lat],
        zoom: 16,
        pitch: 45,
        bearing: 0,
        speed: 0.8,
        curve: 1.2,
        essential: true
      });

      // Add a marker for the location
      new mapboxgl.Marker({ color: '#ef4444' })
        .setLngLat([lng, lat])
        .setPopup(new mapboxgl.Popup().setHTML(`
          <div style="padding: 8px;">
            <strong>📍 Konum</strong><br>
            ${address || `${lat.toFixed(6)}, ${lng.toFixed(6)}`}
          </div>
        `))
        .addTo(mapRef.current);
    }
  };

  const handleMapAction = (action: string, data?: any): void => {
    console.log('Map action triggered:', action, data);
    
    switch (action) {
      case 'showRestaurants':
        // Restoran katmanını aktif et
        handleLayerToggle('restaurants', true);
        break;
      case 'showHospitals':
        // Hastane katmanını aktif et
        handleLayerToggle('hospitals', true);
        break;
      case 'showTraffic':
        // Trafik katmanını aktif et
        handleLayerToggle('traffic', true);
        break;
      case 'showTransport':
        // Ulaşım katmanını aktif et
        handleLayerToggle('transport', true);
        break;
      case 'showShopping':
        // Alışveriş katmanını aktif et
        handleLayerToggle('shopping', true);
        break;
      case 'showParks':
        // Park katmanını aktif et
        handleLayerToggle('parks', true);
        break;
      default:
        console.log('Unknown action:', action);
    }
  };

  const handleChatToggle = (): void => {
    setIsChatMinimized(!isChatMinimized);
  };

  return (
    <div className="map-wrapper">
      <div 
        ref={mapContainerRef} 
        id="map" 
        className="map-container"
      />
      
      <StartButton 
        onClick={handleStartClick}
        isVisible={showButton && mapLoaded}
      />

      <LayersButton
        onLayerToggle={handleLayerToggle}
        isVisible={mapLoaded}
      />

      <SettingsPanel
        isDarkMode={isDarkMode}
        onDarkModeToggle={handleDarkModeToggle}
        is3DBuildingsEnabled={is3DBuildingsEnabled}
        on3DBuildingsToggle={handle3DBuildingsToggle}
        isVisible={mapLoaded}
      />

      <ChatBot
        isVisible={mapLoaded}
      />
    </div>
  );
};

export default MapInitializer;