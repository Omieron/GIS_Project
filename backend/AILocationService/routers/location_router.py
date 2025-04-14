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
    
    # Set edremit context for all responses
    edremit_context = {
        "region": "Edremit, Balıkesir",
        "focus_area": True,  # Default to True for all queries since this is an Edremit-focused service
        "service_type": service_type
    }
    
    result = None
    
    # User's own location
    if interpretation["action"] == "user-location":
        user_ip = request.client.host
        location = get_user_current_location(user_ip)
        result = {
            "type": "user-location", 
            "location": location, 
            "service_type": service_type,
            "edremit_context": edremit_context
        }
        print(f"User location result: {result}")

    # Defined location (e.g., "Where is Edremit Anadolu Lisesi?")
    elif interpretation["action"] == "defined-location":
        location_name = interpretation.get("location_name")
        location_type = interpretation.get("location_type", "")
        
        # Check for Edremit-specific locations first
        from AILocationService.services.geocode import EDREMIT_LOCATIONS
        location_lower = location_name.lower()
        
        if location_lower in EDREMIT_LOCATIONS:
            # Direct lookup in our expanded Edremit dataset
            location_data = EDREMIT_LOCATIONS[location_lower]
            result = {
                "place": location_name.title(),
                "latitude": location_data["latitude"],
                "longitude": location_data["longitude"],
                "description": location_data["description"],
                "address": f"{location_name.title()}, Edremit, Balıkesir, Turkey",
                "categories": [location_data.get("type", "Location")],
                "source": "edremit-mapping",
                "place_type": location_data.get("type", "location")
            }
        # Direct handling for Turkish cities
        elif location_lower in ["ankara", "istanbul", "izmir", "bursa", "antalya", "balikesir"]:
            from AILocationService.services.geocode import TURKISH_CITIES
            city = location_lower
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
            # Look for type-based matches in Edremit locations
            potential_matches = []
            if location_type:
                for name, data in EDREMIT_LOCATIONS.items():
                    if data.get("type") == location_type.lower() or data.get("type") in location_type.lower():
                        potential_matches.append({
                            "name": name,
                            "data": data,
                            "similarity": 0  # We'll calculate similarity below
                        })
                
                # If we found type matches, use the closest one or provide alternatives
                if potential_matches:
                    # For simplicity, just take the first match
                    # In a production system, you'd implement fuzzy matching here
                    match = potential_matches[0]
                    result = {
                        "place": match["name"].title(),
                        "latitude": match["data"]["latitude"],
                        "longitude": match["data"]["longitude"],
                        "description": match["data"]["description"],
                        "address": f"{match['name'].title()}, Edremit, Balıkesir, Turkey",
                        "categories": [match["data"].get("type", "Location")],
                        "source": "edremit-type-match",
                        "place_type": match["data"].get("type", "location"),
                        "alternatives": [{
                            "place": pm["name"].title(),
                            "description": pm["data"]["description"]
                        } for pm in potential_matches[1:3]] if len(potential_matches) > 1 else []
                    }
                else:
                    # Use regular place search for non-matches
                    result = find_place(query=location_name)
            else:
                # Use regular place search for non-matches without type
                result = find_place(query=location_name)
            
        result["type"] = "defined-location"
        result["service_type"] = service_type
        result["edremit_context"] = edremit_context
        print(f"Defined location result: {result}")

    # Contextual location (e.g., "Coffee near Akçay" or "Ice cream near a high school in Edremit")
    elif interpretation["action"] == "contextual-location":
        place_type = interpretation.get("location_name", "")
        context = interpretation.get("context", "")
        location_type = interpretation.get("location_type", "")
        
        # For schools and contextual searches
        if "school" in location_type.lower() or "lise" in location_type.lower() or "okul" in location_type.lower():
            # Find nearby schools in our dataset
            from AILocationService.services.geocode import EDREMIT_LOCATIONS
            schools = []
            for name, data in EDREMIT_LOCATIONS.items():
                if data.get("type") == "school":
                    schools.append({
                        "name": name,
                        "latitude": data["latitude"],
                        "longitude": data["longitude"],
                        "description": data["description"]
                    })
            
            if schools and len(schools) > 0:
                # Use the first school as center point
                school = schools[0]
                result = find_place(
                    query=place_type, 
                    latitude=school["latitude"], 
                    longitude=school["longitude"],
                    radius=1000  # Search within 1km of the school
                )
                
                # Add contextual information
                result["context_location"] = {
                    "name": school["name"].title(),
                    "description": school["description"],
                    "type": "school",
                    "latitude": school["latitude"],
                    "longitude": school["longitude"]
                }
                result["alternatives"] = [{
                    "name": s["name"].title(),
                    "description": s["description"]
                } for s in schools[1:3]] if len(schools) > 1 else []
            else:
                # If no schools found, fall back to regular search
                result = find_place(query=place_type, location=context)
        # For beach or coastal searches
        elif "beach" in location_type.lower() or "plaj" in context.lower() or "deniz" in context.lower():
            # Find beaches or coastal areas
            from AILocationService.services.geocode import EDREMIT_LOCATIONS
            beaches = []
            for name, data in EDREMIT_LOCATIONS.items():
                if data.get("type") == "beach" or "plaj" in name:
                    beaches.append({
                        "name": name,
                        "latitude": data["latitude"],
                        "longitude": data["longitude"],
                        "description": data["description"]
                    })
            
            if beaches and len(beaches) > 0:
                # Use the first beach as center point
                beach = beaches[0]
                result = find_place(
                    query=place_type, 
                    latitude=beach["latitude"], 
                    longitude=beach["longitude"],
                    radius=1000  # Search within 1km of the beach
                )
                
                # Add contextual information
                result["context_location"] = {
                    "name": beach["name"].title(),
                    "description": beach["description"],
                    "type": "beach",
                    "latitude": beach["latitude"],
                    "longitude": beach["longitude"]
                }
                result["alternatives"] = [{
                    "name": b["name"].title(),
                    "description": b["description"]
                } for b in beaches[1:3]] if len(beaches) > 1 else []
            else:
                # If no beaches found, fall back to regular search
                result = find_place(query=place_type, location=context)
        else:
            # Regular contextual search
            result = find_place(query=place_type, location=context)
            
        result["type"] = "contextual-location"
        result["service_type"] = service_type
        result["edremit_context"] = edremit_context
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
        # Extract information, with fallbacks
        food = interpretation.get("food") or interpretation.get("location_name")
        location = interpretation.get("location") or interpretation.get("context", "Edremit")
        
        # Ensure location is present with default to Edremit
        if not location:
            location = "Edremit"
            print(f"No location specified, defaulting to {location}")
            
        # Ensure food is present with default
        if not food:
            food = "yemek"  # Generic "food" in Turkish
            print(f"No food specified, defaulting to {food}")
        
        print(f"Looking for {food} in {location}")
        
        # Handle special cases
        if "deniz" in prompt.lower() or "sahil" in prompt.lower():
            if location == "Edremit" or "akçay" in location.lower() or "akcay" in location.lower():
                # If searching for food near the beach, default to Akçay beach restaurants
                print(f"Beach restaurant search detected, directing to Akçay")
                result = find_place("restaurant", "Akçay sahil", radius=500) 
                result["place_type"] = f"{food} restaurant"
                result["context"] = "Akçay sahil"
                result["food"] = food
            else:
                result = find_food_place(food=food, location=location)
        else:
            result = find_food_place(food=food, location=location)
            
        result["type"] = "food-location"
        result["service_type"] = service_type
        print(f"Found food location: {result}")
    # Landmark search (e.g., "Where is Kaz Dağları?")
    elif interpretation["action"] == "landmark-search":
        landmark_name = interpretation.get("landmark_name")
        context = interpretation.get("context")
        
        # Handle missing landmark name
        if not landmark_name and "location_name" in interpretation:
            landmark_name = interpretation.get("location_name")
            
        # Import EDREMIT_LOCATIONS
        from AILocationService.services.geocode import EDREMIT_LOCATIONS

        # Special handling for commonly searched places in Edremit
        if landmark_name and landmark_name.lower() in ["kaymakamlık", "kaymakamligi", "belediye", "hükümet konağı", "devlet"]:
            # Hard-coded locations for common government buildings
            if context is None or context.lower() == "edremit":
                result = {
                    "place": "Edremit Kaymakamlığı",
                    "latitude": 39.5951, 
                    "longitude": 27.0234,
                    "address": "Edremit, Balıkesir",
                    "categories": ["Government Building"],
                    "source": "local-mapping",
                    "place_type": "government",
                    "context": "Edremit, Balıkesir"
                }
            else:
                # For other areas, fall back to general search
                result = find_place(landmark_name, context)
        # Check for direct matches in Edremit locations
        elif landmark_name and landmark_name.lower() in EDREMIT_LOCATIONS:
            # Direct lookup in our expanded Edremit dataset
            location_data = EDREMIT_LOCATIONS[landmark_name.lower()]
            result = {
                "place": landmark_name.title(),
                "latitude": location_data["latitude"],
                "longitude": location_data["longitude"],
                "description": location_data.get("description", ""),
                "address": f"{landmark_name.title()}, Edremit, Balıkesir, Turkey",
                "categories": [location_data.get("type", "Location")],
                "source": "edremit-mapping",
                "place_type": location_data.get("type", "landmark")
            }
        # For all other landmark searches
        else:
            # For landmarks, we do a broader search with a larger radius
            if landmark_name:
                result = find_landmark(landmark_name)
            else:
                # If no landmark specified, return an error
                result = {"error": "No landmark specified"}
                
        result["type"] = "landmark"
        result["service_type"] = service_type
        print(f"Found landmark: {result}")
    # Unknown action type
    else:
        result = {"error": "Unknown action", "service_type": service_type}
    
    # Set edremit context for all responses
    result["edremit_context"] = {
        "region": "Edremit, Balıkesir",
        "focus_area": True,  # Default to True for all queries since this is an Edremit-focused service
        "service_type": service_type
    }
    
    # Add error handling for common failure cases
    if "error" in result:
        print(f"Error in result: {result['error']}")
        
        # Provide fallback values for common fields that might be missing
        if interpretation.get("action") == "food-location" and "food" not in result:
            result["food"] = interpretation.get("food") or interpretation.get("location_name", "yemek")
        
        if interpretation.get("action") == "contextual-location" and "context" not in result:
            result["context"] = interpretation.get("context", "Edremit")
            
        if "place_type" not in result and "location_type" in interpretation:
            result["place_type"] = interpretation.get("location_type")
    
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
        # Process the interpretation first to get service type
        interpretation = await interpret_location(prompt, language=language)
        service_type = interpretation.get("service_type", "default_service")
        
        # Add Edremit context to the enhanced query
        edremit_context = {
            "region": "Edremit, Balıkesir",
            "focus_area": True,
            "service_type": service_type
        }
        
        # Process the enhanced query
        result = await enhanced_location_query(prompt, language)
        
        # Add service_type and edremit_context to the result
        result["service_type"] = service_type
        result["edremit_context"] = edremit_context
        
        return result
    except Exception as e:
        return {"error": f"Error processing enhanced location query: {str(e)}"}
