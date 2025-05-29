import { useRef, useEffect, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { rotateGlobe, flyToLocation } from './mapAnimation';
import { Buildings3D } from './3DBuildings';
import StartButton from '../ui/StartButton';
import SettingsPanel from '../ui/SettingsPanel';
import '../../styles/MapInitializer.css';

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN;

const MapInitializer: React.FC = () => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const buildings3DRef = useRef<Buildings3D | null>(null);
  const [mapLoaded, setMapLoaded] = useState<boolean>(false);
  const [showButton, setShowButton] = useState<boolean>(true);
  const [isDarkMode, setIsDarkMode] = useState<boolean>(false);
  const [is3DBuildingsEnabled, setIs3DBuildingsEnabled] = useState<boolean>(true);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Container'ı tamamen temizle
    mapContainerRef.current.innerHTML = '';

    const map = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: 'mapbox://styles/mapbox/streets-v12',
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
    }
  };

  const handleDarkModeToggle = (enabled: boolean): void => {
  setIsDarkMode(enabled);
  
  if (mapRef.current && buildings3DRef.current) {
    const style = enabled
      ? 'mapbox://styles/mapbox/dark-v11'
      : 'mapbox://styles/mapbox/streets-v12';

    buildings3DRef.current.removeBuildings();   
    mapRef.current.setStyle(style);
    
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

      <SettingsPanel
        isDarkMode={isDarkMode}
        onDarkModeToggle={handleDarkModeToggle}
        is3DBuildingsEnabled={is3DBuildingsEnabled}
        on3DBuildingsToggle={handle3DBuildingsToggle}
        isVisible={mapLoaded}
      />
    </div>
  );
};

export default MapInitializer;