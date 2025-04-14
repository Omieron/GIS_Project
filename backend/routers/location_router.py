"""
Location service router with endpoints for processing location-related queries
"""
from fastapi import APIRouter, Request, Depends, Query
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

# Import database connection from GIS_Project
from database.database import get_db
# Database is available by default in GIS_Project
db_available = True
from services.gpt import interpret_location
from services.user_location import get_user_current_location
from services.foursquare_service import find_place, find_food_place, find_landmark, find_expanded_query

# Create API router
router = APIRouter(
    prefix="/api",
    tags=["location"],
    responses={404: {"description": "Not found"}},
)

@router.post("/location/", summary="Process a location query")
async def process_location(
    prompt: str, 
    request: Request,
    include_buildings: bool = Query(False, description="Whether to include nearby buildings in the response"),
    building_radius: int = Query(500, description="Radius in meters to search for buildings"),
    db: Session = Depends(get_db)
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
    
    result = None
    
    # User's own location
    if interpretation["action"] == "user-location":
        user_ip = request.client.host
        location = get_user_current_location(user_ip)
        result = {"type": "user-location", "location": location}
        print(f"User location result: {result}")

    # Defined location (e.g., "Where is Bilkent University?")
    elif interpretation["action"] == "defined-location":
        location_name = interpretation.get("location_name")
        
        # Direct handling for Turkish cities
        if location_name.lower() in ["ankara", "istanbul", "izmir", "bursa", "antalya", "balikesir"]:
            from services.geocode import TURKISH_CITIES
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
        print(f"Defined location result: {result}")

    # Contextual location (e.g., "Coffee near Bilkent")
    elif interpretation["action"] == "contextual-location":
        place_type = interpretation.get("location_name", "")
        context = interpretation.get("context", "")
        
        result = find_place(query=place_type, location=context)
        result["type"] = "contextual-location"
        print(f"Contextual location result: {result}")
    
    # Relative location - disabled as conversation history is removed
    elif interpretation["action"] == "relative-location":
        result = {"error": "Relative location queries are not supported in this version. Please provide a complete location query."}
        
    # Expanded query (e.g., "Places to visit with kids in Ankara")
    elif interpretation["action"] == "expanded-query":
        query = interpretation.get("query")
        location = interpretation.get("location")
        
        print(f"Processing expanded query: {query} in {location}")
        
        result = find_expanded_query(query=query, location=location)
        result["type"] = "expanded-query"
        print(f"Expanded query result: {result}")
    
    # Food location (e.g., "Iskender in Bursa")
    elif interpretation["action"] == "food-location":
        food = interpretation.get("food")
        location = interpretation.get("location")
        
        print(f"Looking for {food} in {location}")
        
        result = find_food_place(food=food, location=location)
        result["type"] = "food-location"
        result["food"] = food
        print(f"Found food location: {result}")
    
    # Landmark queries (e.g., "Where is Anıtkabir?")
    elif interpretation["action"] == "landmark":
        landmark_name = interpretation.get("name")
        print(f"Looking for landmark: {landmark_name}")
        
        result = find_landmark(landmark_name)
        result["type"] = "landmark"
        print(f"Found landmark: {result}")
    
    # Unknown action type
    else:
        result = {"error": "Unknown action"}
    
    # No conversation to update
    if result is None:
        result = {"error": "Failed to process request"}
    
    # If buildings are requested and we have coordinates, add buildings data
    if include_buildings and result and not result.get("error"):
        # Extract coordinates from different result types
        lat, lon = None, None
        
        if result.get("type") == "user-location" and result.get("location"):
            lat = result["location"].get("latitude")
            lon = result["location"].get("longitude")
        elif "latitude" in result and "longitude" in result:
            lat = result["latitude"]
            lon = result["longitude"]
        
        if lat is not None and lon is not None:
            # Check if database is available
            if db_available and db is not None:
                try:
                    # SQL query using PostGIS to find buildings within radius
                    query = text("""
                        SELECT jsonb_build_object(
                            'type', 'FeatureCollection',
                            'features', jsonb_agg(feature)
                        ) AS geojson
                        FROM (
                            SELECT jsonb_build_object(
                                'type', 'Feature',
                                'geometry', ST_AsGeoJSON(ST_Transform(geom, 4326))::jsonb,
                                'properties', to_jsonb(row) - 'geom'
                            ) AS feature
                            FROM (
                                SELECT * FROM "YAPI"
                                WHERE ST_DWithin(
                                    ST_Transform(geom, 4326)::geography,
                                    ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
                                    :radius
                                )
                            ) row
                        ) features;
                    """)
                    
                    buildings_result = db.execute(query, {"lon": lon, "lat": lat, "radius": building_radius}).fetchone()
                    
                    if buildings_result and buildings_result[0]:
                        result["buildings"] = buildings_result[0]
                    else:
                        result["buildings"] = {"type": "FeatureCollection", "features": []}
                except Exception as e:
                    result["buildings_error"] = f"Database error: {str(e)}"
            else:
                # Database not available
                result["buildings_error"] = "Database connection not available"
    
    return result
