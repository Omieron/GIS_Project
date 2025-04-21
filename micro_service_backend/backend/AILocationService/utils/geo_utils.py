"""
Geospatial utility functions for coordinate transformations and distance calculations
"""
import math
from typing import Dict, Tuple, List, Any

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth
    
    Args:
        lat1: Latitude of point 1
        lon1: Longitude of point 1
        lat2: Latitude of point 2
        lon2: Longitude of point 2
        
    Returns:
        Distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of Earth in kilometers
    return c * r

def process_coordinates(lat: float, lon: float) -> Dict[str, Any]:
    """
    Process coordinates and validate them
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Dictionary with processed coordinate information
    """
    # Check if coordinates are valid
    if not (-90 <= lat <= 90):
        raise ValueError(f"Invalid latitude: {lat}. Must be between -90 and 90.")
    
    if not (-180 <= lon <= 180):
        raise ValueError(f"Invalid longitude: {lon}. Must be between -180 and 180.")
    
    # Return processed data
    return {
        "latitude": lat,
        "longitude": lon,
        "valid": True,
        "format": "decimal_degrees",
    }

def create_buffer_polygon(lat: float, lon: float, radius_meters: float, 
                         points: int = 32) -> List[Tuple[float, float]]:
    """
    Create a circular buffer polygon around a point
    
    Args:
        lat: Latitude of center point
        lon: Longitude of center point
        radius_meters: Radius in meters
        points: Number of points in the polygon
        
    Returns:
        List of (lon, lat) tuples representing the polygon vertices
    """
    # Convert radius from meters to approximate degrees
    # This is a rough approximation and works best for small distances
    radius_deg_lat = radius_meters / 111000  # 1 degree latitude is approx 111km
    radius_deg_lon = radius_meters / (111000 * math.cos(math.radians(lat)))
    
    # Generate circle points
    polygon = []
    for i in range(points):
        angle = (2 * math.pi * i) / points
        x = lon + radius_deg_lon * math.cos(angle)
        y = lat + radius_deg_lat * math.sin(angle)
        polygon.append((x, y))
    
    # Close the polygon
    polygon.append(polygon[0])
    
    return polygon
