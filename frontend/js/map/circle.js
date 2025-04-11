export function createDraggableCircle(map, id, radiusInMeters = 500, initialCenter = null) {
    const center = initialCenter || map.getCenter(); // 💡 varsayılan merkez: harita merkezi
    const sourceId = `circle-source-${id}`;
    const layerId = `circle-layer-${id}`;

    const circleGeoJSON = createCircleGeoJSON([center.lng, center.lat], radiusInMeters);

    if (map.getLayer(layerId)) map.removeLayer(layerId);
    if (map.getSource(sourceId)) map.removeSource(sourceId);

    map.addSource(sourceId, {
        type: 'geojson',
        data: circleGeoJSON
    });

    map.addLayer({
        id: layerId,
        type: 'fill',
        source: sourceId,
        paint: {
            'fill-color': '#00BFFF',
            'fill-opacity': 0.3
        }
    });

    const marker = new mapboxgl.Marker({ draggable: true })
        .setLngLat([center.lng, center.lat])
        .addTo(map);

    marker.on('dragend', () => {
        const newCenter = marker.getLngLat();
        const updatedGeoJSON = createCircleGeoJSON([newCenter.lng, newCenter.lat], radiusInMeters);
        map.getSource(sourceId).setData(updatedGeoJSON);
        console.log(`🎯 Yeni hedef koordinat: ${newCenter.lng}, ${newCenter.lat}`);
    });

    return marker;
}

function createCircleGeoJSON(center, radiusInMeters, points = 64) {
    const coords = [];
    const distanceX = radiusInMeters / (111.32 * 1000 * Math.cos(center[1] * Math.PI / 180));
    const distanceY = radiusInMeters / 110574;

    for (let i = 0; i < points; i++) {
        const angle = (i * 360 / points) * Math.PI / 180;
        const dx = distanceX * Math.cos(angle);
        const dy = distanceY * Math.sin(angle);
        coords.push([center[0] + dx, center[1] + dy]);
    }
    coords.push(coords[0]); // polygonu kapat

    return {
        type: 'FeatureCollection',
        features: [{
            type: 'Feature',
            geometry: {
                type: 'Polygon',
                coordinates: [coords]
            }
        }]
    };
}


