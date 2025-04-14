"""
Foursquare Places API integration for location searches
"""
import requests
from typing import Dict, Any, List, Optional
import math

from AILocationService.config import FOURSQUARE_API_KEY, DEFAULT_RESULTS_LIMIT

# Increased search radius for better context coverage
DEFAULT_SEARCH_RADIUS = 5000  # 5km search radius
EXPANDED_SEARCH_RADIUS = 10000  # 10km for landmarks and expanded searches
from AILocationService.services.geocode import get_precise_coordinates, EDREMIT_LOCATIONS

# Foursquare API endpoints
PLACES_SEARCH_URL = "https://api.foursquare.com/v3/places/search"
PLACES_NEARBY_URL = "https://api.foursquare.com/v3/places/nearby"

# Food and cuisine mappings
FOOD_CATEGORY_MAPPING = {
    "iskender": ["Turkish Restaurant", "Kebab Restaurant"],
    "döner": ["Turkish Restaurant", "Kebab Restaurant", "Fast Food Restaurant"],
    "mantı": ["Turkish Restaurant", "Dumpling Restaurant"],
    "köfte": ["Turkish Restaurant", "Meatball Restaurant"],
    "pide": ["Turkish Restaurant", "Pizza Restaurant"],
    "lahmacun": ["Turkish Restaurant", "Fast Food Restaurant"],
    "kebap": ["Turkish Restaurant", "Kebab Restaurant"],
    "baklava": ["Dessert Shop", "Bakery", "Turkish Restaurant"],
    "künefe": ["Dessert Shop", "Turkish Restaurant"],
    # Edremit specialty foods
    "zeytinyağlı": ["Turkish Restaurant", "Mediterranean Restaurant", "Seafood Restaurant"],
    "balık": ["Seafood Restaurant", "Fish Restaurant"],
    "ot yemekleri": ["Turkish Restaurant", "Mediterranean Restaurant"],
    "ot": ["Turkish Restaurant", "Mediterranean Restaurant"],
    "kahvaltı": ["Breakfast Spot", "Cafe", "Restaurant"],
}

# Known landmark category IDs for Foursquare
LANDMARK_CATEGORIES = [
    "16000",  # Monument / Landmark
    "16003",  # Historic Site
    "16007",  # Tourist Attraction
    "16025",  # Museum
    "16031",  # Palace
    "16032",  # Castle
    "16034",  # Temple
    "16035",  # Mosque
    "16036",  # Church
    "16038",  # Temple
]

def find_place(query: str, location: str = None, latitude: float = None, 
              longitude: float = None, radius: int = DEFAULT_SEARCH_RADIUS, 
              limit: int = DEFAULT_RESULTS_LIMIT) -> Dict[str, Any]:
    """
    Find a place using Foursquare Places API
    
    Args:
        query: Search query (e.g., "coffee", "pharmacy")
        location: Location name (e.g., "Bilkent University")
        latitude: Latitude for search (overrides location if provided)
        longitude: Longitude for search (overrides location if provided)
        radius: Search radius in meters
        limit: Maximum number of results
        
    Returns:
        Dictionary with search results
    """
    # Set up headers with API key
    headers = {
        "Accept": "application/json",
        "Authorization": FOURSQUARE_API_KEY
    }
    
    # Special handling for Edremit and surrounding areas
    if location is None:
        # First check if query exactly matches an Edremit location
        query_lower = query.lower()
        if query_lower in EDREMIT_LOCATIONS:
            location_data = EDREMIT_LOCATIONS[query_lower]
            return {
                "place": query.title(),
                "latitude": location_data["latitude"],
                "longitude": location_data["longitude"],
                "address": f"{query.title()}, Edremit, Balıkesir, Turkey",
                "categories": ["Location"],
                "description": location_data["description"],
                "source": "edremit-mapping",
                "place_type": "edremit-location"
            }
            
        # Then check for direct city queries
        elif query_lower in ["ankara", "istanbul", "izmir", "bursa", "antalya", "balikesir"]:
            from AILocationService.services.geocode import TURKISH_CITIES
            city = query_lower
            if city in TURKISH_CITIES:
                # Return city information directly
                coords = TURKISH_CITIES[city]
                return {
                    "place": query.title(),
                    "latitude": coords["latitude"],
                    "longitude": coords["longitude"],
                    "address": f"{query.title()}, Turkey",
                    "categories": ["City"],
                    "source": "direct-mapping",
                    "place_type": "city"
                }
    
    # Set up parameters
    params = {
        "query": query,
        "radius": radius,
        "limit": limit,
        "sort": "RELEVANCE"
    }
    
    # If we have coordinates, use them
    if latitude is not None and longitude is not None:
        params["ll"] = f"{latitude},{longitude}"
    # Otherwise if we have a location name, geocode it first
    elif location:
        # Special case for Edremit - prioritize Edremit in all searches
        if location.lower() == "edremit":
            location = "Edremit, Balıkesir"
            
        coords = get_precise_coordinates(location)
        if "latitude" in coords and "longitude" in coords:
            params["ll"] = f"{coords['latitude']},{coords['longitude']}"
            # Save the location coordinates for the result
            latitude, longitude = coords["latitude"], coords["longitude"]
        else:
            return {"error": f"Could not geocode location: {location}"}
    else:
        return {"error": "Either location name or coordinates must be provided"}
    
    try:
        # Make API request
        print(f"Searching Foursquare for: {query} near {params.get('ll')}")
        response = requests.get(PLACES_SEARCH_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Process results
        if "results" in data and data["results"]:
            place = data["results"][0]  # Get the first/most relevant result
            
            # Parse the place data
            result = {
                "place": place.get("name", "Unknown place"),
                "latitude": place.get("geocodes", {}).get("main", {}).get("latitude"),
                "longitude": place.get("geocodes", {}).get("main", {}).get("longitude"),
                "address": place.get("location", {}).get("formatted_address", ""),
                "categories": [cat.get("name") for cat in place.get("categories", [])],
                "fsq_id": place.get("fsq_id"),
                "distance": place.get("distance"),
                "source": "foursquare",
                "place_type": query,
                "context": location
            }
            
            # Include alternatives if there are multiple results
            alternatives = []
            if len(data["results"]) > 1:
                for alt_place in data["results"][1:limit]:
                    alternatives.append({
                        "place": alt_place.get("name", "Unknown place"),
                        "latitude": alt_place.get("geocodes", {}).get("main", {}).get("latitude"),
                        "longitude": alt_place.get("geocodes", {}).get("main", {}).get("longitude"),
                        "distance": alt_place.get("distance")
                    })
                result["alternatives"] = alternatives
                
            return result
        
        # Fall back to OpenStreetMap if no results
        elif FOURSQUARE_API_KEY is None or FOURSQUARE_API_KEY == "":
            print("No Foursquare API key provided")
            return fallback_search(query, location, latitude, longitude)
        else:
            print(f"No results found in Foursquare for {query} near {location}")
            return fallback_search(query, location, latitude, longitude)
    
    except Exception as e:
        print(f"Error in Foursquare search: {str(e)}")
        return fallback_search(query, location, latitude, longitude)

def find_expanded_query(query: str, location: str = None) -> Dict[str, Any]:
    """
    Process a complex query that might involve multiple place types or criteria
    
    Args:
        query: The complex query (e.g., "Places to visit with kids in Chicago")
        location: The general location area (e.g., "Chicago")
        
    Returns:
        Dictionary with search results
    """
    # For expanded queries, we use a larger search radius
    radius = EXPANDED_SEARCH_RADIUS
    
    # Extract place type from query
    place_type = "tourist attraction"
    
    # Look for specific place types in the query
    if any(word in query.lower() for word in ["restaurant", "eat", "food", "dining", "lokanta", "restoran"]):
        place_type = "restaurant"
    elif any(word in query.lower() for word in ["hotel", "stay", "accommodation", "otel", "konaklama"]):
        place_type = "hotel"
    elif any(word in query.lower() for word in ["museum", "art", "exhibit", "müze", "sanat"]):
        place_type = "museum"
    elif any(word in query.lower() for word in ["park", "garden", "outdoor", "nature", "park", "doğa"]):
        place_type = "park"
    elif any(word in query.lower() for word in ["shopping", "mall", "store", "shop", "alisveris", "mağaza"]):
        place_type = "shopping"
    elif any(word in query.lower() for word in ["beach", "sea", "ocean", "plaj", "deniz"]):
        place_type = "beach"
    elif any(word in query.lower() for word in ["cafe", "coffee", "kahve", "kafe"]):
        place_type = "cafe"
    elif any(word in query.lower() for word in ["bar", "pub", "drink", "night", "gece"]):
        place_type = "bar"
    elif any(word in query.lower() for word in ["historic", "history", "tarihi", "tarih"]):
        place_type = "historic site"
    
    # Use a more tailored search if the query specifically mentions children
    if any(word in query.lower() for word in ["kid", "child", "family", "çocuk", "aile"]):
        if place_type == "restaurant":
            place_type = "family restaurant"
        elif place_type == "tourist attraction":
            place_type = "theme park"
    
    # Now use the regular find_place function with the expanded parameters
    result = find_place(query=place_type, location=location, radius=radius, limit=10)
    
    # Add metadata about the expanded query
    result["query_type"] = "expanded"
    result["original_query"] = query
    result["extracted_place_type"] = place_type
    
    return result

def find_food_place(food: str = None, location: str = None) -> Dict[str, Any]:
    """
    Find a restaurant serving a specific food
    
    Args:
        food: The food to search for (e.g., "iskender")
        location: The location to search in (e.g., "Bursa")
        
    Returns:
        Dictionary with restaurant information
    """
    # Handle missing parameters
    if food is None:
        food = "yemek"  # Default to generic "food" in Turkish
        print(f"Warning: Missing food parameter in find_food_place, using default: {food}")
        
    if location is None:
        # Default to Edremit center if no location specified
        location = "Edremit"
        print(f"Warning: Missing location parameter in find_food_place, using default: {location}")
    
    print(f"Looking for {food} in {location}")
    
    # First try a direct search for the food by name
    result = find_place(query=f"{food} restaurant", location=location, radius=3000)
    
    # If successful, return the result
    if "error" not in result:
        result["food"] = food
        return result
    
    # If not found, try using category mappings
    # Check for food category mapping
    if food and food.lower() in FOOD_CATEGORY_MAPPING:
        categories = FOOD_CATEGORY_MAPPING[food.lower()]
        
        # Try each category in order
        for category in categories:
            result = find_place(query=category, location=location, radius=3000)
            if "error" not in result:
                result["food"] = food
                return result
    
    # If all else fails, just look for any restaurant
    final_result = find_place(query="restaurant", location=location, radius=3000)
    if "error" not in final_result:
        final_result["food"] = food
    return final_result

def find_landmark(landmark_name: str) -> Dict[str, Any]:
    """Find a famous landmark or tourist attraction with expanded search radius"""
    # Use expanded search radius for landmarks
    radius = EXPANDED_SEARCH_RADIUS
    """
    Find a famous landmark or tourist attraction
    
    Args:
        landmark_name: Name of the landmark to find
        
    Returns:
        Dictionary with landmark information
    """
    # Set up headers with API key
    headers = {
        "Accept": "application/json",
        "Authorization": FOURSQUARE_API_KEY
    }
    
    # Try to get a more precise search by adding "landmark" to the query
    # if it's not already in the name
    query = landmark_name
    if "landmark" not in landmark_name.lower() and "monument" not in landmark_name.lower():
        for suffix in ["landmark", "tourist attraction", "monument", "historic site"]:
            # Try different queries to increase chance of finding the landmark
            params = {
                "query": f"{landmark_name}",
                "categories": ",".join(LANDMARK_CATEGORIES),
                "limit": 3,
                "sort": "RELEVANCE"
            }
            
            try:
                response = requests.get(PLACES_SEARCH_URL, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                if "results" in data and data["results"]:
                    # We found the landmark, so parse and return it
                    landmark = data["results"][0]
                    
                    result = {
                        "place": landmark.get("name", landmark_name),
                        "latitude": landmark.get("geocodes", {}).get("main", {}).get("latitude"),
                        "longitude": landmark.get("geocodes", {}).get("main", {}).get("longitude"),
                        "address": landmark.get("location", {}).get("formatted_address", ""),
                        "categories": [cat.get("name") for cat in landmark.get("categories", [])],
                        "fsq_id": landmark.get("fsq_id"),
                        "source": "foursquare",
                        "is_landmark": True,
                        "photos": [], # Placeholder for photos that could be fetched later
                        "description": "" # Placeholder for description that could be fetched later
                    }
                    
                    # Include alternatives if there are multiple results
                    alternatives = []
                    if len(data["results"]) > 1:
                        for alt_landmark in data["results"][1:3]:
                            alternatives.append({
                                "place": alt_landmark.get("name", "Unknown place"),
                                "latitude": alt_landmark.get("geocodes", {}).get("main", {}).get("latitude"),
                                "longitude": alt_landmark.get("geocodes", {}).get("main", {}).get("longitude"),
                                "categories": [cat.get("name") for cat in alt_landmark.get("categories", [])]
                            })
                    
                    if alternatives:
                        result["alternatives"] = alternatives
                        
                    return result
            except Exception as e:
                print(f"Error in landmark search for {landmark_name}: {str(e)}")
                continue
    
    # If we get here, we didn't find the landmark with specialized queries
    # Try a general place search as fallback
    return find_place(query=landmark_name, radius=5000)

def fallback_search(query: str, location: str = None, latitude: float = None, 
                  longitude: float = None) -> Dict[str, Any]:
    """
    Fallback search using OpenStreetMap when Foursquare fails
    
    This is a simplified version that uses direct OpenStreetMap queries
    """
    from AILocationService.services.places import find_place_near_location
    
    if location:
        # Use the OpenStreetMap search
        osm_result = find_place_near_location(place_type=query, context=location)
        if osm_result and "latitude" in osm_result:
            # Format to match our response structure
            return {
                "place": osm_result.get("place", query),
                "latitude": osm_result["latitude"],
                "longitude": osm_result["longitude"],
                "place_type": query,
                "context": location,
                "source": "openstreetmap"
            }
    
    # If we have coordinates but no location name
    elif latitude is not None and longitude is not None:
        # TODO: Implement coordinate-based search with OSM
        pass
    
    return {"error": f"Could not find {query} near {location}"}

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in kilometers"""
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r
