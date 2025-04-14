"""
Overpass API service for querying OpenStreetMap data
Focused on Turkey and specifically Balıkesir Edremit region
"""
import overpy
import json
from typing import Dict, Any, List, Optional

# Default coordinates for Edremit, Balıkesir
EDREMIT_LAT = 39.5942
EDREMIT_LON = 27.0242
EDREMIT_BBOX = (27.0000, 39.5800, 27.0500, 39.6100)  # (min_lon, min_lat, max_lon, max_lat)

class OverpassService:
    def __init__(self):
        self.api = overpy.Overpass()
        
    def query_amenities(self, amenity_type: str, lat: float = EDREMIT_LAT, lon: float = EDREMIT_LON, radius: int = 1000) -> Dict[str, Any]:
        """
        Query amenities of a specific type around a location
        
        Args:
            amenity_type: Type of amenity (restaurant, cafe, school, etc.)
            lat: Latitude of center point (defaults to Edremit)
            lon: Longitude of center point (defaults to Edremit)
            radius: Search radius in meters
            
        Returns:
            GeoJSON formatted results
        """
        # Build the Overpass query
        query = f"""
        [out:json];
        (
          node["amenity"="{amenity_type}"](around:{radius},{lat},{lon});
          way["amenity"="{amenity_type}"](around:{radius},{lat},{lon});
          relation["amenity"="{amenity_type}"](around:{radius},{lat},{lon});
        );
        out center;
        """
        
        try:
            result = self.api.query(query)
            return self._format_as_geojson(result, amenity_type)
        except Exception as e:
            print(f"Error querying Overpass API: {str(e)}")
            return {"type": "FeatureCollection", "features": [], "error": str(e)}
    
    def query_poi_in_edremit(self, poi_type: str, tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Query points of interest in Edremit region with specified tags
        
        Args:
            poi_type: General type of POI (amenity, shop, tourism, etc.)
            tags: Dictionary of additional tags to filter by
            
        Returns:
            GeoJSON formatted results
        """
        # Build the tag filter part of the query
        tag_filters = ""
        if tags:
            for key, value in tags.items():
                tag_filters += f'["{key}"="{value}"]'
        
        # Use the Edremit bounding box
        min_lon, min_lat, max_lon, max_lat = EDREMIT_BBOX
        
        # Build the Overpass query
        query = f"""
        [out:json];
        (
          node["{poi_type}"{tag_filters}]({min_lat},{min_lon},{max_lat},{max_lon});
          way["{poi_type}"{tag_filters}]({min_lat},{min_lon},{max_lat},{max_lon});
          relation["{poi_type}"{tag_filters}]({min_lat},{min_lon},{max_lat},{max_lon});
        );
        out center;
        """
        
        try:
            result = self.api.query(query)
            return self._format_as_geojson(result, poi_type)
        except Exception as e:
            print(f"Error querying Overpass API: {str(e)}")
            return {"type": "FeatureCollection", "features": [], "error": str(e)}
    
    def search_by_name(self, name: str, region: str = "Edremit") -> Dict[str, Any]:
        """
        Search for places by name in a specific region
        
        Args:
            name: Name or part of name to search for
            region: Region to search in (defaults to Edremit)
            
        Returns:
            GeoJSON formatted results
        """
        # Build the Overpass query with name search
        query = f"""
        [out:json];
        (
          node["name"~"{name}",i]["name:tr"~"{region}",i];
          way["name"~"{name}",i]["name:tr"~"{region}",i];
          relation["name"~"{name}",i]["name:tr"~"{region}",i];
        );
        out center;
        """
        
        try:
            result = self.api.query(query)
            return self._format_as_geojson(result, "search_result")
        except Exception as e:
            print(f"Error querying Overpass API: {str(e)}")
            return {"type": "FeatureCollection", "features": [], "error": str(e)}
    
    def get_administrative_boundaries(self) -> Dict[str, Any]:
        """
        Get administrative boundaries for Edremit
        
        Returns:
            GeoJSON formatted boundaries
        """
        # Query for administrative boundaries
        query = """
        [out:json];
        (
          relation["boundary"="administrative"]["name"="Edremit"];
        );
        out geom;
        """
        
        try:
            result = self.api.query(query)
            return self._format_boundaries_as_geojson(result)
        except Exception as e:
            print(f"Error querying Overpass API for boundaries: {str(e)}")
            return {"type": "FeatureCollection", "features": [], "error": str(e)}
    
    def _format_as_geojson(self, result: overpy.Result, feature_type: str) -> Dict[str, Any]:
        """
        Format Overpass API results as GeoJSON
        """
        features = []
        
        # Process nodes
        for node in result.nodes:
            properties = {tag.k: tag.v for tag in node.tags}
            properties["osm_id"] = node.id
            properties["feature_type"] = feature_type
            
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(node.lon), float(node.lat)]
                },
                "properties": properties
            }
            features.append(feature)
        
        # Process ways (using center points)
        for way in result.ways:
            if hasattr(way, 'center_lat') and hasattr(way, 'center_lon'):
                properties = {tag.k: tag.v for tag in way.tags}
                properties["osm_id"] = way.id
                properties["feature_type"] = feature_type
                
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(way.center_lon), float(way.center_lat)]
                    },
                    "properties": properties
                }
                features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": features
        }
    
    def _format_boundaries_as_geojson(self, result: overpy.Result) -> Dict[str, Any]:
        """
        Format boundary relations as GeoJSON
        """
        features = []
        
        for relation in result.relations:
            properties = {tag.k: tag.v for tag in relation.tags}
            properties["osm_id"] = relation.id
            
            # Extract outer ways to form polygons
            outer_members = [member for member in relation.members if member.role == "outer"]
            
            # Simple case: single polygon
            if len(outer_members) == 1 and hasattr(outer_members[0], 'geometry'):
                coords = [[float(node.lon), float(node.lat)] for node in outer_members[0].geometry]
                
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [coords]
                    },
                    "properties": properties
                }
                features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": features
        }

# Create singleton instance
overpass_service = OverpassService()

def find_amenities(amenity_type: str, lat: float = None, lon: float = None, radius: int = 1000) -> Dict[str, Any]:
    """
    Find amenities of a specific type
    
    Args:
        amenity_type: Type of amenity (restaurant, cafe, etc.)
        lat: Latitude (defaults to Edremit)
        lon: Longitude (defaults to Edremit)
        radius: Search radius in meters
        
    Returns:
        GeoJSON of amenities
    """
    # Default to Edremit if no coordinates provided
    lat = lat if lat is not None else EDREMIT_LAT
    lon = lon if lon is not None else EDREMIT_LON
    
    return overpass_service.query_amenities(amenity_type, lat, lon, radius)

def find_poi_in_edremit(poi_type: str, tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Find points of interest in Edremit
    
    Args:
        poi_type: Type of POI (amenity, shop, tourism, etc.)
        tags: Additional tags to filter by
        
    Returns:
        GeoJSON of POIs
    """
    return overpass_service.query_poi_in_edremit(poi_type, tags)

def search_osm_by_name(name: str, region: str = "Edremit") -> Dict[str, Any]:
    """
    Search OpenStreetMap by name in a region
    
    Args:
        name: Name to search for
        region: Region to search in (defaults to Edremit)
        
    Returns:
        GeoJSON of search results
    """
    return overpass_service.search_by_name(name, region)

def get_edremit_boundaries() -> Dict[str, Any]:
    """
    Get Edremit administrative boundaries
    
    Returns:
        GeoJSON of boundaries
    """
    return overpass_service.get_administrative_boundaries()
