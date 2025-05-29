import { useRef, useEffect, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { rotateGlobe, flyToLocation } from './mapAnimation';
import { Buildings3D } from './3DBuildings';
import StartButton from '../ui/StartButton';
import '../../styles/MapInitializer.css';

// Mapbox access token
mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN;

const MapInitializer: React.FC = () => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const buildings3DRef = useRef<Buildings3D | null>(null);
  const [mapLoaded, setMapLoaded] = useState<boolean>(false);
  const [showButton, setShowButton] = useState<boolean>(true);

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
      
      // 3D Buildings manager'ını oluştur ve ekle
      buildings3DRef.current = new Buildings3D(map, 15);
      buildings3DRef.current.addBuildings();
      
      setMapLoaded(true);
    });

    // Cleanup function
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
    </div>
  );
};

export default MapInitializer;