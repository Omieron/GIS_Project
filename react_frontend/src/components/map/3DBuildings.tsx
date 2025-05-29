export class Buildings3D {
  private map: mapboxgl.Map;
  private isAdded: boolean = false;
  private minZoomLevel: number = 15;

  constructor(map: mapboxgl.Map, minZoom: number = 15) {
    this.map = map;
    this.minZoomLevel = minZoom;
  }

  
  public addBuildings(): void {
    if (this.isAdded || !this.map.isStyleLoaded()) {
      return;
    }

    try {

      this.addSkyLayer();
      
      this.add3DBuildingsLayer();
      
      this.setupZoomListener();
      
      this.isAdded = true;
    } catch (error) {
      console.error('3D buildings eklenirken hata:', error);
    }
  }

  
  private addSkyLayer(): void {
    if (!this.map.getLayer('sky')) {
      this.map.addLayer({
        'id': 'sky',
        'type': 'sky',
        'paint': {
          'sky-type': 'atmosphere',
          'sky-atmosphere-sun': [0.0, 0.0],
          'sky-atmosphere-sun-intensity': 15
        }
      });
    }
  }

  
  private add3DBuildingsLayer(): void {
    if (!this.map.getLayer('3d-buildings')) {
      // Label layer'larını bul
      const layers = this.map.getStyle().layers;
      let labelLayerId: string | undefined;
      
      // İlk label layer'ını bul (POI, text vs.)
      for (const layer of layers) {
        if (layer.type === 'symbol' && layer.layout && layer.layout['text-field']) {
          labelLayerId = layer.id;
          break;
        }
      }

      this.map.addLayer({
        'id': '3d-buildings',
        'source': 'composite',
        'source-layer': 'building',
        'filter': ['==', 'extrude', 'true'],
        'type': 'fill-extrusion',
        'minzoom': this.minZoomLevel,
        'paint': {
          'fill-extrusion-color': [
            'interpolate',
            ['linear'],
            ['get', 'height'],
            0, 'rgba(232, 232, 232, 0.7)',
            50, 'rgba(212, 212, 212, 0.7)',
            100, 'rgba(192, 192, 192, 0.7)',
            200, 'rgba(168, 168, 168, 0.7)',
            300, 'rgba(144, 144, 144, 0.7)'
          ],
          'fill-extrusion-height': [
            'interpolate',
            ['linear'],
            ['zoom'],
            this.minZoomLevel, 0,
            this.minZoomLevel + 0.05, ['get', 'height']
          ],
          'fill-extrusion-base': [
            'interpolate',
            ['linear'],
            ['zoom'],
            this.minZoomLevel, 0,
            this.minZoomLevel + 0.05, ['get', 'min_height']
          ],
          'fill-extrusion-opacity': 0.6
        }
      }, labelLayerId); 

      this.map.setLayoutProperty('3d-buildings', 'visibility', 'none');
    }
  }

  
  private setupZoomListener(): void {
    this.map.on('zoom', () => {
      this.updateBuildingsVisibility();
    });

    this.updateBuildingsVisibility();
  }

  
  private updateBuildingsVisibility(): void {
    const currentZoom = this.map.getZoom();
    const shouldShow = currentZoom >= this.minZoomLevel;
    
    if (this.map.getLayer('3d-buildings')) {
      const currentVisibility = this.map.getLayoutProperty('3d-buildings', 'visibility');
      const newVisibility = shouldShow ? 'visible' : 'none';
      
      if (currentVisibility !== newVisibility) {
        this.map.setLayoutProperty('3d-buildings', 'visibility', newVisibility);
      }
    }
  }

  
  public setMinZoom(zoom: number): void {
    this.minZoomLevel = zoom;
    this.updateBuildingsVisibility();
  }

  
  public removeBuildings(): void {
    if (this.map.getLayer('3d-buildings')) {
      this.map.removeLayer('3d-buildings');
    }
    
    if (this.map.getLayer('sky')) {
      this.map.removeLayer('sky');
    }
    
    this.isAdded = false;
  }

  public isEnabled(): boolean {
    return this.isAdded && this.map.getLayer('3d-buildings') !== undefined;
  }
  
  public updateColors(colorStops: { height: number; color: string }[]): void {
    if (!this.map.getLayer('3d-buildings')) return;

    const colorExpression = [
      'interpolate' as const,
      ['linear'] as const,
      ['get', 'height'] as const,
      ...colorStops.flatMap(stop => [stop.height, stop.color])
    ];

    this.map.setPaintProperty('3d-buildings', 'fill-extrusion-color', colorExpression as any);
  }

  
  public updateOpacity(opacity: number): void {
    if (this.map.getLayer('3d-buildings')) {
      this.map.setPaintProperty('3d-buildings', 'fill-extrusion-opacity', opacity);
    }
  }
}


export const createBuildings3D = (map: mapboxgl.Map, minZoom: number = 15): Buildings3D => {
  return new Buildings3D(map, minZoom);
};

export default Buildings3D;