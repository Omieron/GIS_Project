"""
Location service router with endpoints for processing location-related queries
"""
from fastapi import APIRouter, Request, Query
from typing import Dict, Any, Optional, List
from AILocationService.services.gpt import interpret_location
from AILocationService.services.user_location import get_user_current_location
from AILocationService.services.foursquare_service import find_place, find_food_place, find_landmark, find_expanded_query
from AILocationService.services.overpass_service import find_amenities, find_poi_in_edremit, search_osm_by_name, get_edremit_boundaries
from AILocationService.services.enhanced_location import enhanced_location_query

# Create API router
router = APIRouter(
    prefix="/api",
    tags=["location"],
    responses={404: {"description": "Not found"}},
)

@router.post("/location/", summary="Process a location query")
async def process_location(
    prompt: str, 
    request: Request
) -> Dict[str, Any]:
    """
    Process a natural language location query
    
    - **prompt**: The natural language query (e.g., "Find coffee near Bilkent")
    
    Returns location information based on the query type.
    """
    # Default to Turkish language
    language = "tr"  
    
    # Process the prompt directly without conversation history
    interpretation = await interpret_location(
        prompt,
        language=language
    )
    
    print(f"Interpretation: {interpretation}")
    
    # Extract service type from interpretation
    service_type = interpretation.get("service_type", "default_service")
    
    result = None
    
    # User's own location
    if interpretation["action"] == "user-location":
        user_ip = request.client.host
        location = get_user_current_location(user_ip)
        result = {"type": "user-location", "location": location, "service_type": service_type}
        print(f"User location result: {result}")

    # Defined location (e.g., "Where is Bilkent University?")
    elif interpretation["action"] == "defined-location":
        location_name = interpretation.get("location_name")
        
        # Direct handling for Turkish cities
        if location_name.lower() in ["ankara", "istanbul", "izmir", "bursa", "antalya", "balikesir"]:
            from AILocationService.services.geocode import TURKISH_CITIES
            city = location_name.lower()
            coords = TURKISH_CITIES[city]
            result = {
                "place": location_name.title(),
                "latitude": coords["latitude"],
                "longitude": coords["longitude"],
                "address": f"{location_name.title()}, Turkey",
                "categories": ["City"],
                "source": "direct-mapping",
                "place_type": "city"
            }
        else:
            # Use regular place search for non-cities
            result = find_place(query=location_name)
            
        result["type"] = "defined-location"
        result["service_type"] = service_type
        print(f"Defined location result: {result}")

    # Contextual location (e.g., "Coffee near Bilkent")
    elif interpretation["action"] == "contextual-location":
        place_type = interpretation.get("location_name", "")
        context = interpretation.get("context", "")
        
        result = find_place(query=place_type, location=context)
        result["type"] = "contextual-location"
        result["service_type"] = service_type
        print(f"Contextual location result: {result}")
    
    # Relative location - disabled as conversation history is removed
    elif interpretation["action"] == "relative-location":
        result = {"error": "Relative location queries are not supported in this version. Please provide a complete location query.", "service_type": service_type}
        
    # Expanded query (e.g., "Places to visit with kids in Ankara")
    elif interpretation["action"] == "expanded-query":
        query = interpretation.get("query")
        location = interpretation.get("location")
        
        print(f"Processing expanded query: {query} in {location}")
        
        result = find_expanded_query(query=query, location=location)
        result["type"] = "expanded-query"
        result["service_type"] = service_type
        print(f"Expanded query result: {result}")
    
    # Food location (e.g., "Iskender in Bursa")
    elif interpretation["action"] == "food-location":
        food = interpretation.get("food")
        location = interpretation.get("location")
        
        print(f"Looking for {food} in {location}")
        
        result = find_food_place(food=food, location=location)
        result["type"] = "food-location"
        result["food"] = food
        result["service_type"] = service_type
        print(f"Found food location: {result}")
    
    # Landmark queries (e.g., "Where is Anıtkabir?")
    elif interpretation["action"] == "landmark":
        landmark_name = interpretation.get("name")
        print(f"Looking for landmark: {landmark_name}")
        
        result = find_landmark(landmark_name)
        result["type"] = "landmark"
        result["service_type"] = service_type
        print(f"Found landmark: {result}")
    
    # Unknown action type
    else:
        result = {"error": "Unknown action", "service_type": service_type}
    
    # No conversation to update
    if result is None:
        result = {"error": "Failed to process request", "service_type": service_type}
    

    
    return result


@router.get("/osm/amenities/", summary="Find amenities via OpenStreetMap")
async def get_osm_amenities(
    amenity_type: str = Query(..., description="Type of amenity (restaurant, cafe, school, etc.)"),
    lat: Optional[float] = Query(None, description="Latitude (defaults to Edremit center if not provided)"),
    lon: Optional[float] = Query(None, description="Longitude (defaults to Edremit center if not provided)"),
    radius: int = Query(1000, description="Search radius in meters")
) -> Dict[str, Any]:
    """
    Find amenities of a specific type in OpenStreetMap
    
    - **amenity_type**: Type of amenity (restaurant, cafe, hospital, etc.)
    - **lat**: Latitude (defaults to Edremit center)
    - **lon**: Longitude (defaults to Edremit center)
    - **radius**: Search radius in meters
    
    Returns a GeoJSON FeatureCollection of amenities.
    """
    try:
        results = find_amenities(amenity_type, lat, lon, radius)
        return results
    except Exception as e:
        return {"error": str(e)}


@router.get("/osm/poi/", summary="Find points of interest in Edremit")
async def get_osm_poi(
    poi_type: str = Query(..., description="Type of POI (amenity, shop, tourism, etc.)"),
    name: Optional[str] = Query(None, description="Filter by name (optional)")
) -> Dict[str, Any]:
    """
    Find points of interest in Edremit region
    
    - **poi_type**: Type of POI (amenity, shop, tourism, etc.)
    - **name**: Filter by name (optional)
    
    Returns a GeoJSON FeatureCollection of points of interest.
    """
    try:
        # Apply name filter if provided
        tags = {"name": name} if name else None
        results = find_poi_in_edremit(poi_type, tags)
        return results
    except Exception as e:
        return {"error": str(e)}


@router.get("/osm/search/", summary="Search OpenStreetMap by name")
async def search_openstreetmap(
    name: str = Query(..., description="Name to search for"),
    region: str = Query("Edremit", description="Region to search in (defaults to Edremit)")
) -> Dict[str, Any]:
    """
    Search for places by name in OpenStreetMap
    
    - **name**: Name or part of name to search for
    - **region**: Region to search in (defaults to Edremit)
    
    Returns a GeoJSON FeatureCollection of search results.
    """
    try:
        results = search_osm_by_name(name, region)
        return results
    except Exception as e:
        return {"error": str(e)}


@router.get("/osm/boundaries/", summary="Get Edremit administrative boundaries")
async def get_boundaries() -> Dict[str, Any]:
    """
    Get administrative boundaries for Edremit
    
    Returns a GeoJSON FeatureCollection of boundaries.
    """
    try:
        results = get_edremit_boundaries()
        return results
    except Exception as e:
        return {"error": str(e)}


@router.post("/enhanced-location/", summary="Enhanced location query with OSM data")
async def process_enhanced_location(
    prompt: str,
    language: str = Query("tr", description="Language of the query (tr or en)")
) -> Dict[str, Any]:
    """
    Process a location query with enhanced OpenStreetMap data
    
    - **prompt**: Natural language query about locations
    - **language**: Language of the query (default: Turkish)
    
    Returns enhanced results combining GPT interpretation and OpenStreetMap data.
    """
    try:
        result = await enhanced_location_query(prompt, language)
        return result
    except Exception as e:
        return {"error": f"Error processing enhanced location query: {str(e)}"}
