"""
Foursquare Places API integration for location searches.
"""
import os
import requests
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API keys from environment variables
FOURSQUARE_API_KEY = os.getenv("FOURSQUARE_API_KEY")

# Foursquare API endpoints
PLACES_SEARCH_URL = "https://api.foursquare.com/v3/places/search"
PLACES_NEARBY_URL = "https://api.foursquare.com/v3/places/nearby"

def search_places(query: str, location: str = None, latitude: float = None, longitude: float = None, 
                  radius: int = 1000, limit: int = 5) -> Dict[str, Any]:
    """
    Search for places using Foursquare Places API
    
    Args:
        query: Search query (e.g., "coffee", "pharmacy")
        location: Location name (e.g., "Bilkent University")
        latitude: Latitude for search (overrides location)
        longitude: Longitude for search (overrides location)
        radius: Search radius in meters
        limit: Maximum number of results
        
    Returns:
        Dictionary with search results
    """
    if not FOURSQUARE_API_KEY:
        return {"error": "Foursquare API key not found in environment variables"}
    
    # Set up headers
    headers = {
        "Accept": "application/json",
        "Authorization": FOURSQUARE_API_KEY
    }
    
    # Set up parameters
    params = {
        "query": query,
        "radius": radius,
        "limit": limit
    }
    
    # If we have coordinates, use them
    if latitude is not None and longitude is not None:
        params["ll"] = f"{latitude},{longitude}"
    # Otherwise if we have a location name, geocode it first
    elif location:
        from services.geocode import get_precise_coordinates
        coords = get_precise_coordinates(location)
        if "latitude" in coords and "longitude" in coords:
            params["ll"] = f"{coords['latitude']},{coords['longitude']}"
        else:
            return {"error": f"Could not geocode location: {location}"}
    else:
        return {"error": "Either location name or coordinates must be provided"}
    
    # Make API request
    try:
        print(f"Searching Foursquare for: {query} near {params.get('ll')}")
        response = requests.get(PLACES_SEARCH_URL, headers=headers, params=params)
        response.raise_for_status()  # Raise exception for 4XX/5XX status codes
        data = response.json()
        
        # Process results
        if data.get("results"):
            places = []
            for place in data["results"]:
                places.append({
                    "place": place.get("name", "Unknown place"),
                    "latitude": place.get("geocodes", {}).get("main", {}).get("latitude"),
                    "longitude": place.get("geocodes", {}).get("main", {}).get("longitude"),
                    "address": place.get("location", {}).get("formatted_address", ""),
                    "categories": [cat.get("name") for cat in place.get("categories", [])],
                    "fsq_id": place.get("fsq_id"),
                    "distance": place.get("distance")
                })
            
            # Get the first place as the main result
            main_result = places[0] if places else None
            
            return {
                "place": main_result.get("place") if main_result else None,
                "latitude": main_result.get("latitude") if main_result else None,
                "longitude": main_result.get("longitude") if main_result else None,
                "address": main_result.get("address") if main_result else None,
                "categories": main_result.get("categories") if main_result else [],
                "alternatives": places[1:] if len(places) > 1 else [],
                "query": query,
                "location": location
            }
        else:
            return {"error": f"No places found for query: {query}"}
    
    except requests.exceptions.RequestException as e:
        print(f"Foursquare API error: {str(e)}")
        return {"error": f"Error fetching data from Foursquare: {str(e)}"}

def find_place_near_location(place_type: str, location: str, radius: int = 1000) -> Dict[str, Any]:
    """
    Find places of a specific type near a location using Foursquare
    
    Args:
        place_type: Type of place to search for (e.g., "coffee shop", "pharmacy")
        location: Location to search near
        radius: Search radius in meters
        
    Returns:
        Dictionary with search results
    """
    return search_places(query=place_type, location=location, radius=radius)

def find_relative_place(place_type: str, reference_lat: float, reference_lon: float, 
                        radius: int = 1000) -> Dict[str, Any]:
    """
    Find places of a specific type near specific coordinates
    
    Args:
        place_type: Type of place to search for
        reference_lat: Reference latitude
        reference_lon: Reference longitude
        radius: Search radius in meters
        
    Returns:
        Dictionary with search results
    """
    return search_places(query=place_type, latitude=reference_lat, longitude=reference_lon, radius=radius)
