const FSQ_API_KEY = 'YOUR_FOURSQUARE_API_KEY'; // 🔐 kendi API key'ini buraya koy

export async function fetchFoursquarePlaces(center, radius = 500, categoryIds = []) {
  if (!categoryIds.length) return [];

  const url = `https://api.foursquare.com/v3/places/search?ll=${center.lat},${center.lng}&radius=${radius}&categories=${categoryIds.join(',')}&limit=30`;

  const res = await fetch(url, {
    headers: {
      Accept: 'application/json',
      Authorization: FSQ_API_KEY
    }
  });

  if (!res.ok) {
    console.error('Foursquare API hatası:', res.statusText);
    return [];
  }

  const data = await res.json();
  return data.results || [];
}