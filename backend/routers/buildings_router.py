"""
Buildings API router for GIS building data from PostgreSQL/PostGIS
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

# Import database connection from GIS_Project
from database.database import get_db
# Database is available by default in GIS_Project
db_available = True

# Create API router
router = APIRouter(
    prefix="/api",
    tags=["buildings"],
    responses={404: {"description": "Not found"}},
)

@router.get("/buildings/", summary="Get buildings within radius")
async def get_buildings_within_radius(
    lon: float = Query(..., description="Center longitude"),
    lat: float = Query(..., description="Center latitude"),
    radius: int = Query(750, description="Radius in meters"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    # Check if database is available
    if not db_available or db is None:
        raise HTTPException(
            status_code=503,
            detail="Database connection not available. Buildings API requires a database connection."
        )
    """
    Find buildings within a specified radius of a point
    
    - **lon**: Longitude of the center point
    - **lat**: Latitude of the center point
    - **radius**: Search radius in meters (default: 750)
    
    Returns a GeoJSON FeatureCollection of buildings.
    """
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

        # Execute the query
        result = db.execute(query, {"lon": lon, "lat": lat, "radius": radius}).fetchone()

        if result and result[0]:
            return result[0]
        else:
            raise HTTPException(status_code=404, detail="No buildings found within the specified radius.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/buildings/address", summary="Search buildings by address")
async def search_buildings_by_address(
    address: str = Query(..., description="Address text to search for"),
    limit: int = Query(10, description="Maximum number of results"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Search buildings by address text
    
    - **address**: Address text to search for
    - **limit**: Maximum number of results to return
    
    Returns a GeoJSON FeatureCollection of matching buildings.
    """
    # This is a placeholder - actual implementation will depend on the database schema
    # and whether there's a text search functionality available
    raise HTTPException(status_code=501, detail="Not implemented yet")

@router.get("/buildings/natural-query", summary="Natural language building query")
async def natural_language_building_query(
    query: str = Query(..., description="Natural language query about buildings"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Process a natural language query about buildings
    
    - **query**: Natural language question (e.g., "Show me all apartment buildings near Edremit center")
    
    Returns relevant building information based on the query.
    """
    # This will be implemented once we understand the database schema better
    # and can integrate with our AI understanding capabilities
    raise HTTPException(status_code=501, detail="AI building query not implemented yet")
