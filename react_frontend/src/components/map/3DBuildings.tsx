export class Buildings3D {
  private map: mapboxgl.Map;
  private isAdded: boolean = false;
  private minZoomLevel: number = 15;

  constructor(map: mapboxgl.Map, minZoom: number = 15) {
    this.map = map;
    this.minZoomLevel = minZoom;
  }

  /**
   * 3D binaları haritaya ekler
   */
  public addBuildings(): void {
    // Style yüklenmemişse bekle
    if (!this.map.isStyleLoaded()) {
      return;
    }

    // Eğer layer zaten varsa, eklemeye çalışma
    if (this.map.getLayer('3d-buildings')) {
      this.isAdded = true;
      return;
    }

    try {
      // Sky layer (atmosfer efekti) ekle
      this.addSkyLayer();
      
      // 3D buildings layer ekle
      this.add3DBuildingsLayer();
      
      // Zoom event listener ekle
      this.setupZoomListener();
      
      this.isAdded = true;
      console.log('3D buildings başarıyla eklendi');
    } catch (error) {
      console.error('3D buildings eklenirken hata:', error);
    }
  }

  /**
   * Sky layer ekler (atmosfer efekti için)
   */
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

  /**
   * 3D buildings layer'ını ekler
   */
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
          // Bina yüksekliğine göre renklendirme
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
          // Bina yüksekliği
          'fill-extrusion-height': [
            'interpolate',
            ['linear'],
            ['zoom'],
            this.minZoomLevel, 0,
            this.minZoomLevel + 0.05, ['get', 'height']
          ],
          // Bina taban yüksekliği
          'fill-extrusion-base': [
            'interpolate',
            ['linear'],
            ['zoom'],
            this.minZoomLevel, 0,
            this.minZoomLevel + 0.05, ['get', 'min_height']
          ],
          'fill-extrusion-opacity': 0.6
        }
      }, labelLayerId); // Label'lardan önce ekle

      // Başlangıçta gizli yap
      this.map.setLayoutProperty('3d-buildings', 'visibility', 'none');
    }
  }

  /**
   * Zoom seviyesi değişikliklerini dinler
   */
  private setupZoomListener(): void {
    this.map.on('zoom', () => {
      this.updateBuildingsVisibility();
    });

    // İlk yükleme için de kontrol et
    this.updateBuildingsVisibility();
  }

  /**
   * Zoom seviyesine göre binaların görünürlüğünü günceller
   */
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

  /**
   * Minimum zoom seviyesini günceller
   */
  public setMinZoom(zoom: number): void {
    this.minZoomLevel = zoom;
    this.updateBuildingsVisibility();
  }

  /**
   * 3D binaları kaldırır
   */
  public removeBuildings(): void {
    try {
      if (this.map.getLayer('3d-buildings')) {
        this.map.removeLayer('3d-buildings');
        console.log('3D buildings layer kaldırıldı');
      }
      
      if (this.map.getLayer('sky')) {
        this.map.removeLayer('sky');
        console.log('Sky layer kaldırıldı');
      }
    } catch (error) {
      // Style değişimi sırasında layer zaten silinmiş olabilir
      console.warn('Layer removal warning:', error);
    }
    
    this.isAdded = false;
  }

  /**
   * Style değişikliği sonrası durumu resetler
   */
  public resetState(): void {
    this.isAdded = false;
    console.log('3D buildings state resetlendi');
  }

  /**
   * 3D binaların durumunu kontrol eder
   */
  public isEnabled(): boolean {
    return this.isAdded && this.map.getLayer('3d-buildings') !== undefined;
  }

  /**
   * Bina renklerini günceller
   */
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

  /**
   * Şeffaflığı günceller
   */
  public updateOpacity(opacity: number): void {
    if (this.map.getLayer('3d-buildings')) {
      this.map.setPaintProperty('3d-buildings', 'fill-extrusion-opacity', opacity);
    }
  }
}

// Utility fonksiyonlar
export const createBuildings3D = (map: mapboxgl.Map, minZoom: number = 15): Buildings3D => {
  return new Buildings3D(map, minZoom);
};

export default Buildings3D;