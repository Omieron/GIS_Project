"""
Service for finding restaurants that serve specific dishes.
"""
import requests
from typing import Dict, Any, Optional, List
from services.geocode import get_precise_coordinates

# Dictionary of famous Turkish dishes and the types of places that serve them
DISH_PLACE_MAPPING = {
    "iskender": ["restaurant", "kebap", "cuisine=turkish"],
    "döner": ["restaurant", "kebap", "fast_food"],
    "mantı": ["restaurant", "cuisine=turkish"],
    "köfte": ["restaurant", "meatball", "cuisine=turkish"],
    "baklava": ["patisserie", "dessert", "sweets"],
    "kebap": ["restaurant", "kebap"],
    "pide": ["restaurant", "pide"],
    "lahmacun": ["restaurant", "fast_food"],
    "künefe": ["dessert", "patisserie", "sweets"],
    "türk kahvesi": ["cafe", "coffee_shop"],
    "çay": ["cafe", "tea_house"]
}

def find_restaurant_for_dish(dish: str, location: str) -> Dict[str, Any]:
    """Find a restaurant that serves a specific dish in a given location"""
    print(f"Looking for a place to eat {dish} in {location}")
    
    # Get coordinates for the location
    location_coords = get_precise_coordinates(location)
    if "error" in location_coords:
        return {"error": f"Could not find location: {location}"}
    
    lat, lon = location_coords["latitude"], location_coords["longitude"]
    
    # Get place types for this dish
    place_types = DISH_PLACE_MAPPING.get(dish.lower(), ["restaurant"])
    print(f"Searching for place types: {place_types}")
    
    # Try each place type until we find a match
    for place_type in place_types:
        result = find_place_by_type_and_name(place_type, dish, lat, lon)
        if result and "error" not in result:
            result["dish"] = dish
            result["context"] = location
            return result
    
    # If we didn't find a specific restaurant with the dish name, just return any restaurant of the right type
    for place_type in place_types:
        result = find_place_by_type(place_type, lat, lon)
        if result and "error" not in result:
            result["dish"] = dish
            result["context"] = location
            return result
    
    return {"error": f"Could not find a place serving {dish} in {location}"}

def find_place_by_type_and_name(place_type: str, name: str, lat: float, lon: float, radius: int = 3000) -> Optional[Dict[str, Any]]:
    """Find a place with a specific type and name in the search area"""
    # Convert OSM tag format
    if "=" not in place_type:
        if place_type in ["restaurant", "cafe", "fast_food", "kebap"]:
            tag = f"amenity={place_type}"
        elif place_type in ["meatball", "dessert", "patisserie", "tea_house", "coffee_shop"]:
            tag = f"shop={place_type}"
        else:
            tag = place_type
    else:
        tag = place_type
    
    # Build a query that looks for the name in the name or description fields
    query = f"""
    [out:json][timeout:15];
    (
      node[{tag}](around:{radius},{lat},{lon});
      way[{tag}](around:{radius},{lat},{lon});
      relation[{tag}](around:{radius},{lat},{lon});
    );
    out center 1;
    """
    
    try:
        response = requests.post("http://overpass-api.de/api/interpreter", data={"data": query})
        data = response.json()
        
        if data.get("elements"):
            # First, try to find a place with the dish name in it
            for element in data["elements"]:
                name_tag = element.get("tags", {}).get("name", "").lower()
                if name.lower() in name_tag:
                    return extract_place_info(element)
            
            # If no matching name, just return the first element
            element = data["elements"][0]
            return extract_place_info(element)
    except Exception as e:
        print(f"Error finding place by type and name: {str(e)}")
    
    return None

def find_place_by_type(place_type: str, lat: float, lon: float, radius: int = 3000) -> Optional[Dict[str, Any]]:
    """Find a place with a specific type in the search area"""
    # Convert OSM tag format
    if "=" not in place_type:
        if place_type in ["restaurant", "cafe", "fast_food", "kebap"]:
            tag = f"amenity={place_type}"
        elif place_type in ["meatball", "dessert", "patisserie", "tea_house", "coffee_shop"]:
            tag = f"shop={place_type}"
        else:
            tag = place_type
    else:
        tag = place_type
    
    query = f"""
    [out:json][timeout:15];
    (
      node[{tag}](around:{radius},{lat},{lon});
      way[{tag}](around:{radius},{lat},{lon});
      relation[{tag}](around:{radius},{lat},{lon});
    );
    out center 1;
    """
    
    try:
        response = requests.post("http://overpass-api.de/api/interpreter", data={"data": query})
        data = response.json()
        
        if data.get("elements"):
            element = data["elements"][0]
            return extract_place_info(element)
    except Exception as e:
        print(f"Error finding place by type: {str(e)}")
    
    return None

def extract_place_info(element: Dict[str, Any]) -> Dict[str, Any]:
    """Extract place information from an OSM element"""
    name = element.get("tags", {}).get("name", "Restaurant")
    cuisine = element.get("tags", {}).get("cuisine", "")
    
    lat = element.get("lat") or element.get("center", {}).get("lat")
    lon = element.get("lon") or element.get("center", {}).get("lon")
    
    return {
        "place": name,
        "latitude": lat,
        "longitude": lon,
        "cuisine": cuisine
    }
