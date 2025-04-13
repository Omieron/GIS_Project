let animationFrameId = null;

export function rotateGlobe(map) {
    let angle = 0;

    function animate() {
        angle = (angle + 0.1) % 360;

        // Başlangıç noktası Türkiye: ~35E boylam
        const baseLng = 35;
        const currentLng = baseLng - angle;

        map.setCenter([currentLng, 10]); // 39: Türkiye'nin enlemi
        map.setZoom(1.05);
        animationFrameId = requestAnimationFrame(animate);
    }

    animate();
}

export function stopRotation() {
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
        animationFrameId = null;
    }
}

export function mapFlyTo(map) {
    document.getElementById('start-btn')?.addEventListener('click', () => {
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

        // Butonu gizle
        document.getElementById('start-btn').style.display = 'none';

        document.querySelectorAll('.hide-on-start').forEach(el => {
            el.classList.add('show-after-start');
        });

    });


}