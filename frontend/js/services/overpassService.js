export async function fetchOverpassData(lat, lon, radius = 500) {
    const query = `
      [out:json][timeout:25];
      (
        way["highway"](around:${radius},${lat},${lon});
      );
      out body;
      >;
      out skel qt;
    `;
  
    const response = await fetch('https://overpass-api.de/api/interpreter', {
      method: 'POST',
      body: query,
    });
  
    if (!response.ok) throw new Error('Overpass API hatası');
    return await response.json();
  }