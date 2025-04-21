"""
Service to integrate Overpass API data with GPT interpretation
Allows for enhanced location queries using OpenStreetMap data
"""
from typing import Dict, Any, List, Optional
import json
from services.overpass_service import find_amenities, find_poi_in_edremit
from services.gpt import interpret_location

# Common OpenStreetMap amenity and POI types
OSM_AMENITY_TYPES = [
    "restaurant", "cafe", "fast_food", "bar", 
    "hospital", "pharmacy", "school", "university", 
    "bank", "atm", "police", "fire_station",
    "parking", "fuel", "toilets", "bench", 
    "marketplace", "place_of_worship", "mosque"
]

OSM_POI_TYPES = {
    "shop": ["supermarket", "convenience", "clothes", "bakery", "butcher"],
    "tourism": ["hotel", "guest_house", "museum", "attraction", "viewpoint"],
    "leisure": ["park", "garden", "playground", "sports_centre"],
    "natural": ["beach", "peak", "water", "bay"]
}

# Default Edremit coordinates
EDREMIT_LAT = 39.5942
EDREMIT_LON = 27.0242

async def enhanced_location_query(prompt: str, language: str = "tr") -> Dict[str, Any]:
    """
    Process a location query with enhanced OpenStreetMap data
    
    Args:
        prompt: Natural language query
        language: Language of the query (default: Turkish)
        
    Returns:
        Enhanced results combining GPT interpretation and OSM data
    """
    # First, get the basic interpretation
    interpretation = await interpret_location(prompt, language)
    
    # Base result with the interpretation
    result = {
        "interpretation": interpretation,
        "osm_data": None
    }
    
    # Extract the action and query details
    action = interpretation.get("action")
    
    # For defined locations or contextual locations, add OSM data
    if action in ["defined-location", "contextual-location"]:
        location_name = interpretation.get("location_name", "")
        context = interpretation.get("context", "")
        
        # If we have a location name that might be an amenity type
        if location_name.lower() in OSM_AMENITY_TYPES:
            # Try to get amenities of this type
            osm_data = find_amenities(location_name.lower())
            result["osm_data"] = osm_data
        
        # If we have a context that indicates a specific place in Edremit
        if "edremit" in context.lower():
            # Try to search for the location by name
            for category, types in OSM_POI_TYPES.items():
                if any(poi_type in location_name.lower() for poi_type in types):
                    # Found a matching POI type
                    osm_data = find_poi_in_edremit(category, {"name": location_name})
                    result["osm_data"] = osm_data
                    break
    
    # For food locations, try to find restaurants with that cuisine
    elif action == "food-location":
        food = interpretation.get("food", "")
        location = interpretation.get("location", "")
        
        # If location is in Edremit
        if "edremit" in location.lower():
            # Try to find restaurants with this cuisine/food
            osm_data = find_amenities("restaurant")
            # Filter for those that might mention the food in their name or cuisine tag
            if "features" in osm_data:
                filtered_features = []
                for feature in osm_data["features"]:
                    props = feature.get("properties", {})
                    name = props.get("name", "").lower()
                    cuisine = props.get("cuisine", "").lower()
                    
                    if food.lower() in name or food.lower() in cuisine:
                        filtered_features.append(feature)
                
                if filtered_features:
                    result["osm_data"] = {
                        "type": "FeatureCollection",
                        "features": filtered_features
                    }
    
    # For expanded queries, add relevant POI data
    elif action == "expanded-query":
        query = interpretation.get("query", "")
        location = interpretation.get("location", "")
        
        # If query mentions common categories, add relevant OSM data
        for category, poi_types in OSM_POI_TYPES.items():
            for poi_type in poi_types:
                if poi_type in query.lower():
                    osm_data = find_poi_in_edremit(category)
                    result["osm_data"] = osm_data
                    break
    
    return result
