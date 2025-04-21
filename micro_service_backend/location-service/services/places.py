import requests
import math
from typing import Dict, Any, Optional, List, Tuple
from services.geocode import get_precise_coordinates

def find_place_near_location(place_type: str, context: str, radius=2000, previous_result=None):
    coords = get_precise_coordinates(context)
    if "latitude" not in coords:
        return None  # Context çözümleme başarısız

    lat, lon = coords["latitude"], coords["longitude"]

    # place_type → OpenStreetMap tag: e.g. cafe = amenity=cafe
    tag_mapping = {
        # Coffee shops and cafes
        "coffee shop": "amenity=cafe",
        "cafe": "amenity=cafe",
        "kafe": "amenity=cafe",
        "kahve": "amenity=cafe",
        "kahveci": "amenity=cafe",
        "coffee": "amenity=cafe",
        
        # Medical facilities
        "hospital": "amenity=hospital",
        "hastane": "amenity=hospital",
        "pharmacy": "amenity=pharmacy",
        "eczane": "amenity=pharmacy",
        
        # Recreation
        "park": "leisure=park",
        
        # Food
        "restaurant": "amenity=restaurant",
        "restoran": "amenity=restaurant",
        "lokanta": "amenity=restaurant",
        "food": "amenity=restaurant",
        "yemek": "amenity=restaurant",
        
        # Shopping
        "market": "shop=supermarket",
        "süpermarket": "shop=supermarket",
        "bakkal": "shop=convenience",
        "shop": "shop=convenience",
        "dükkan": "shop=convenience",
        "mağaza": "shop=mall",
        
        # General fallbacks
        "place": "amenity=cafe",  # Default to cafe if generic
        "yer": "amenity=cafe"     # Turkish for place
    }

    tag = tag_mapping.get(place_type.lower())
    if not tag:
        print(f"Unknown place type: {place_type}")
        # Default to cafe if type not found - most likely it's a cafe or restaurant
        tag = "amenity=cafe"

    # Overpass API query
    query = f"""
    [out:json][timeout:10];
    (
      node[{tag}](around:{radius},{lat},{lon});
      way[{tag}](around:{radius},{lat},{lon});
      relation[{tag}](around:{radius},{lat},{lon});
    );
    out center 1;
    """

    response = requests.post("http://overpass-api.de/api/interpreter", data={"data": query})
    data = response.json()

    if data.get("elements"):
        # Sort elements by distance from reference point if we have multiple results
        elements = data["elements"]
        if len(elements) > 1:
            for element in elements:
                element_lat = element.get("lat") or element.get("center", {}).get("lat")
                element_lon = element.get("lon") or element.get("center", {}).get("lon")
                element["distance"] = haversine_distance(lat, lon, element_lat, element_lon)
            elements.sort(key=lambda x: x.get("distance", float('inf')))
        
        # Get the first suitable result
        element = elements[0]
        name = element["tags"].get("name", place_type)
        lat = element.get("lat") or element.get("center", {}).get("lat")
        lon = element.get("lon") or element.get("center", {}).get("lon")
        return {
            "place": name,
            "latitude": lat,
            "longitude": lon,
            "context": context
        }
    else:
        return {"error": "No nearby place found"}

def find_relative_location(place_type: str, modifier: str, reference_location: Dict[str, Any], city_context: Optional[str] = None):
    """Find a location relative to a previous search result
    
    Args:
        place_type: Type of place to find (e.g., 'pharmacy')
        modifier: Direction modifier (e.g., 'more towards the center')
        reference_location: Previous location result
        city_context: City context if available
        
    Returns:
        Location information dictionary
    """
    if not reference_location or "latitude" not in reference_location:
        return {"error": "No reference location found"}
    
    # Extract reference coordinates
    ref_lat = reference_location["latitude"]
    ref_lon = reference_location["longitude"]
    
    # Get the city center if we have a city context
    city = city_context or reference_location.get("context")
    if not city:
        return {"error": "No city context available"}
    
    city_coords = get_precise_coordinates(city)
    if "latitude" not in city_coords:
        return {"error": f"Could not find coordinates for {city}"}
    
    city_lat = city_coords["latitude"]
    city_lon = city_coords["longitude"]
    
    # Determine new search area based on the modifier
    if "merkez" in modifier.lower() or "center" in modifier.lower():
        # Calculate point between reference and city center, weighted towards center
        search_lat = ref_lat + 0.6 * (city_lat - ref_lat)
        search_lon = ref_lon + 0.6 * (city_lon - ref_lon)
        radius = 2000  # Larger radius for center area
    elif "uzak" in modifier.lower() or "away" in modifier.lower() or "further" in modifier.lower():
        # Calculate point away from city center
        search_lat = ref_lat + 1.2 * (ref_lat - city_lat)
        search_lon = ref_lon + 1.2 * (ref_lon - city_lon)
        radius = 2000
    else:
        # Default: slight move towards city center
        search_lat = ref_lat + 0.3 * (city_lat - ref_lat)
        search_lon = ref_lon + 0.3 * (city_lon - ref_lon)
        radius = 2000
    
    # Use our existing function to find places near the new search location
    tag_mapping = {
        "coffee shop": "amenity=cafe",
        "kafe": "amenity=cafe",
        "hospital": "amenity=hospital",
        "hastane": "amenity=hospital",
        "pharmacy": "amenity=pharmacy",
        "eczane": "amenity=pharmacy",
        "park": "leisure=park",
        "restaurant": "amenity=restaurant",
        "restoran": "amenity=restaurant",
        "lokanta": "amenity=restaurant",
        "market": "shop=supermarket",
        "süpermarket": "shop=supermarket",
        "bakkal": "shop=convenience"
    }
    
    tag = tag_mapping.get(place_type.lower())
    if not tag:
        print(f"Unknown place type in relative search: {place_type}")
        # Default to cafe if type not found - most likely it's a cafe or restaurant
        tag = "amenity=cafe"
    
    # Overpass API query for the new location
    query = f"""
    [out:json][timeout:10];
    (
      node[{tag}](around:{radius},{search_lat},{search_lon});
      way[{tag}](around:{radius},{search_lat},{search_lon});
      relation[{tag}](around:{radius},{search_lat},{search_lon});
    );
    out center 1;
    """
    
    response = requests.post("http://overpass-api.de/api/interpreter", data={"data": query})
    data = response.json()
    
    if data.get("elements"):
        element = data["elements"][0]
        name = element["tags"].get("name", place_type)
        lat = element.get("lat") or element.get("center", {}).get("lat")
        lon = element.get("lon") or element.get("center", {}).get("lon")
        return {
            "place": name,
            "latitude": lat,
            "longitude": lon,
            "context": city,
            "relative_to": reference_location.get("place", "previous location")
        }
    else:
        return {"error": f"No {place_type} found in the specified direction"}

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points on earth"""
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r
