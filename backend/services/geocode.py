from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from geopy.extra.rate_limiter import RateLimiter
import requests
import json

geolocator = Nominatim(user_agent="text-to-location", timeout=10)
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# Hard-coded coordinates for common Turkish cities for backup
TURKISH_CITIES = {
    "ankara": {"latitude": 39.9255, "longitude": 32.8662},
    "istanbul": {"latitude": 41.0082, "longitude": 28.9784},
    "izmir": {"latitude": 38.4237, "longitude": 27.1428},
    "balikesir": {"latitude": 39.6484, "longitude": 27.8826},
    "antalya": {"latitude": 36.8969, "longitude": 30.7133},
    "bursa": {"latitude": 40.1885, "longitude": 29.0610},
}

# Edremit and surrounding areas specific locations
EDREMIT_LOCATIONS = {
    "edremit": {"latitude": 39.5942, "longitude": 27.0246, "description": "Edremit district center in Balıkesir province"},
    "akcay": {"latitude": 39.5776, "longitude": 26.9184, "description": "Popular seaside resort town in Edremit"},
    "altinoluk": {"latitude": 39.5691, "longitude": 26.7353, "description": "Coastal town in Edremit with beaches"},
    "zeytinli": {"latitude": 39.5829, "longitude": 26.9823, "description": "Town in Edremit known for olive groves"},
    "gure": {"latitude": 39.5866, "longitude": 26.8835, "description": "Town in Edremit with thermal springs"},
    "kaz dağları": {"latitude": 39.7083, "longitude": 26.8733, "description": "Mount Ida (Kaz Dağları) National Park"},
    "şahindere kanyonu": {"latitude": 39.6689, "longitude": 26.9583, "description": "Scenic canyon in Kaz Mountains"},
    "hasanboğuldu": {"latitude": 39.6694, "longitude": 26.9319, "description": "Waterfall and recreation area near Edremit"},
}

def get_precise_coordinates(place: str):
    print(f"Searching for coordinates of: {place}")
    
    # Clean up the place name for better geocoding
    cleaned_place = clean_place_name(place)
    print(f"Cleaned place name: {cleaned_place}")
    
    # First priority: check for Edremit-specific locations
    lower_place = cleaned_place.lower()
    
    # Special case: if 'edremit' is mentioned anywhere, prioritize Edremit in Balıkesir
    if "edremit" in lower_place:
        print("Found reference to Edremit, prioritizing Edremit in Balıkesir")
        edremit = EDREMIT_LOCATIONS["edremit"]
        return {
            "place": "Edremit, Balıkesir",
            "latitude": edremit["latitude"],
            "longitude": edremit["longitude"],
            "description": edremit["description"]
        }
    
    # Check for specific Edremit locations
    for location, data in EDREMIT_LOCATIONS.items():
        if location in lower_place:
            print(f"Found coordinates for {location} in Edremit area data")
            return {
                "place": location.title(),
                "latitude": data["latitude"],
                "longitude": data["longitude"],
                "description": data["description"]
            }
    
    # Check if it's a known Turkish city
    for city, coords in TURKISH_CITIES.items():
        if city in lower_place:
            print(f"Found coordinates for {city} in hardcoded data")
            return {
                "place": place,
                "latitude": coords["latitude"],
                "longitude": coords["longitude"]
            }
    
    # Try with Nominatim
    try:
        # First try with country context
        location = geocode(f"{cleaned_place}, Turkey")
        if not location:
            # Try without country context
            location = geocode(cleaned_place)
        
        if location:
            print(f"Found coordinates: {location.latitude}, {location.longitude}")
            return {
                "place": place,
                "latitude": location.latitude,
                "longitude": location.longitude
            }
        else:
            # Fallback to Photon geocoder if Nominatim fails
            return photon_geocode(cleaned_place)
    except GeocoderTimedOut:
        print("Geocoder timeout. Falling back to Photon")
        return photon_geocode(cleaned_place)
    except GeocoderServiceError:
        print("Geocoder service error. Falling back to Photon")
        return photon_geocode(cleaned_place)
    except Exception as e:
        print(f"Unexpected error in geocoding: {str(e)}")
        # Check if we have a fallback for locations in the name
        
        # First check Edremit locations
        for location, data in EDREMIT_LOCATIONS.items():
            if location in lower_place:
                return {
                    "place": location.title(),
                    "latitude": data["latitude"],
                    "longitude": data["longitude"],
                    "description": data["description"]
                }
        
        # Then check other Turkish cities
        for city, coords in TURKISH_CITIES.items():
            if city in lower_place:
                return {
                    "place": place,
                    "latitude": coords["latitude"],
                    "longitude": coords["longitude"]
                }
        
        # Default to Edremit center if nothing else is found
        print("No specific location found, defaulting to Edremit center")
        edremit = EDREMIT_LOCATIONS["edremit"]
        return {
            "place": "Edremit, Balıkesir",
            "latitude": edremit["latitude"],
            "longitude": edremit["longitude"],
            "description": edremit["description"],
            "note": "Default location used as specific location not found"
        }

def clean_place_name(place: str) -> str:
    """Clean up place name for better geocoding"""
    # Remove apostrophes and replace with space
    place = place.replace("'", " ")
    
    # Handle common Turkish place phrases
    place = place.replace("'de", "")
    place = place.replace("'da", "")
    place = place.replace("de bir", "")
    place = place.replace("da bir", "")
    
    # Strip extra whitespace
    return place.strip()

def photon_geocode(place: str):
    """Alternative geocoding using Photon API"""
    try:
        url = f"https://photon.komoot.io/api/?q={place}&limit=1"
        response = requests.get(url)
        data = response.json()
        
        if data and "features" in data and len(data["features"]) > 0:
            feature = data["features"][0]
            coords = feature["geometry"]["coordinates"]
            # Photon returns [lon, lat] order
            print(f"Found coordinates with Photon: {coords[1]}, {coords[0]}")
            return {
                "place": place,
                "latitude": coords[1],  # Photon returns [lon, lat] not [lat, lon]
                "longitude": coords[0]
            }
    except Exception as e:
        print(f"Photon geocoding error: {str(e)}")
    
    # If we get here, both geocoders failed
    return {"error": "Location not found with any geocoder."}
