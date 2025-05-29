let animationFrameId: number | null = null;

export function rotateGlobe(map: mapboxgl.Map): void {
    let angle = 0;

    function animate(): void {
        angle = (angle + 0.1) % 360;

        const baseLng = 35;
        const currentLng = baseLng - angle;

        map.setCenter([currentLng, 10]); 
        map.setZoom(1.05);
        animationFrameId = requestAnimationFrame(animate);
    }

    animate();
}

export function stopRotation(): void {
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
        animationFrameId = null;
    }
}

export function flyToLocation(map: mapboxgl.Map): void {
    stopRotation(); // 🌪️ Dönmeyi durdur

    map.flyTo({
        center: [27.024772, 39.596321], 
        zoom: 15,
        pitch: 60,
        bearing: -17.6,
        speed: 0.5,
        curve: 1.5,
        essential: true
    });

    // Hide on start elementlerini göster
    document.querySelectorAll('.hide-on-start').forEach((el: Element) => {
        el.classList.add('show-after-start');
    });
}