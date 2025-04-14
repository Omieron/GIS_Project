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
    # Main settlements
    "edremit": {"latitude": 39.5942, "longitude": 27.0246, "description": "Edremit district center in Balıkesir province", "type": "settlement"},
    "akcay": {"latitude": 39.5788, "longitude": 26.9401, "description": "Popular seaside resort town in Edremit with many hotels", "type": "settlement"},
    "akçay": {"latitude": 39.5788, "longitude": 26.9401, "description": "Popular seaside resort town in Edremit with many hotels", "type": "settlement"},
    "altinoluk": {"latitude": 39.5688, "longitude": 26.7338, "description": "Coastal town in Edremit with beaches and pensions", "type": "settlement"},
    "altınoluk": {"latitude": 39.5688, "longitude": 26.7338, "description": "Coastal town in Edremit with beaches and pensions", "type": "settlement"},
    "zeytinli": {"latitude": 39.5886, "longitude": 27.0106, "description": "Town in Edremit known for olive groves", "type": "settlement"},
    "gure": {"latitude": 39.5546, "longitude": 26.9074, "description": "Town in Edremit with thermal springs and spa hotels", "type": "settlement"},
    "güre": {"latitude": 39.5546, "longitude": 26.9074, "description": "Town in Edremit with thermal springs and spa hotels", "type": "settlement"},
    "kızılkeçili": {"latitude": 39.6124, "longitude": 26.9976, "description": "Mountain village in Edremit region", "type": "settlement"},
    "küçükkuyu": {"latitude": 39.5509, "longitude": 26.6165, "description": "Coastal settlement part of Ayvacık district", "type": "settlement"},
    
    # Default locations for incomplete queries
    "sahil kenarı": {"latitude": 39.5957, "longitude": 27.0234, "description": "Edremit Sahil", "type": "beach"},
    "eczane": {"latitude": 39.5952, "longitude": 27.0245, "description": "Eczaneler", "type": "pharmacy"},
    "market": {"latitude": 39.5950, "longitude": 27.0241, "description": "Local market in Edremit center", "type": "shopping"},
    
    # Natural landmarks
    "kaz dağları": {"latitude": 39.7083, "longitude": 26.8733, "description": "Mount Ida (Kaz Dağları) National Park", "type": "landmark"},
    "şahindere kanyonu": {"latitude": 39.6689, "longitude": 26.9583, "description": "Scenic canyon in Kaz Mountains", "type": "landmark"},
    "hasanboğuldu": {"latitude": 39.6694, "longitude": 26.9319, "description": "Waterfall and recreation area near Edremit", "type": "landmark"},
    "sırtçamçam şelalesi": {"latitude": 39.6557, "longitude": 26.9611, "description": "Beautiful waterfall in Kaz Mountains", "type": "landmark"},
    "sıkrıbuğaz kanyonu": {"latitude": 39.6833, "longitude": 26.9583, "description": "Canyon with hiking trails", "type": "landmark"},
    "edremit körfezi": {"latitude": 39.5384, "longitude": 26.8677, "description": "Gulf of Edremit with scenic coastline", "type": "landmark"},
    
    # Beaches and coastal areas
    "akçay plajı": {"latitude": 39.5718, "longitude": 26.9105, "description": "Popular beach in Akçay", "type": "beach"},
    "altınoluk plajı": {"latitude": 39.5676, "longitude": 26.7339, "description": "Clean beach with facilities in Altınoluk", "type": "beach"},
    "güre plajı": {"latitude": 39.5825, "longitude": 26.8798, "description": "Beach area near Güre's thermal facilities", "type": "beach"},
    "akçay kordon": {"latitude": 39.5739, "longitude": 26.9145, "description": "Seaside promenade with restaurants in Akçay", "type": "landmark"},
    "altınoluk marina": {"latitude": 39.5684, "longitude": 26.7367, "description": "Marina area with seafood restaurants", "type": "landmark"},
    
    # Schools and educational institutions
    "edremit anadolu lisesi": {"latitude": 39.5962, "longitude": 27.0201, "description": "Well-established high school in Edremit center", "type": "school"},
    "edremit fen lisesi": {"latitude": 39.5949, "longitude": 27.0187, "description": "Science-focused high school", "type": "school"},
    "10 kasım anadolu lisesi": {"latitude": 39.5939, "longitude": 27.0233, "description": "Vocational high school in Edremit", "type": "school"},
    "edremit ilkokulu": {"latitude": 39.5955, "longitude": 27.0220, "description": "Primary school in Edremit center", "type": "school"},
    "altınoluk ilköğretim okulu": {"latitude": 39.5704, "longitude": 26.7370, "description": "Primary and middle school in Altınoluk", "type": "school"},
    
    # Restaurants and dining spots
    "zeytinyağlı restoran": {"latitude": 39.5937, "longitude": 27.0235, "description": "Restaurant specializing in olive oil dishes", "type": "restaurant"},
    "akçay kahvaltı salonu": {"latitude": 39.5742, "longitude": 26.9152, "description": "Popular breakfast spot near Akçay beach", "type": "restaurant"},
    "deniz restoran": {"latitude": 39.5725, "longitude": 26.9142, "description": "Seafood restaurant with beach view in Akçay", "type": "restaurant"},
    "körfez balık": {"latitude": 39.5687, "longitude": 26.7363, "description": "Fish restaurant in Altınoluk", "type": "restaurant"},
    "zeytinli köy kahvaltısı": {"latitude": 39.5832, "longitude": 26.9837, "description": "Traditional village breakfast place", "type": "restaurant"},
    
    # Shopping and markets
    "novada avm": {"latitude": 39.6018, "longitude": 27.0299, "description": "Shopping mall in Edremit", "type": "shopping"},
    "körfez avm": {"latitude": 39.5977, "longitude": 27.0256, "description": "Shopping center with various stores", "type": "shopping"},
    "edremit pazaryeri": {"latitude": 39.5953, "longitude": 27.0249, "description": "Traditional market open on Tuesdays", "type": "shopping"},
    "akçay çarşısı": {"latitude": 39.5763, "longitude": 26.9193, "description": "Shopping area with local products", "type": "shopping"},
    
    # Ice cream shops (for the specific example given)
    "emirhan dondurma": {"latitude": 39.5961, "longitude": 27.0212, "description": "Popular ice cream shop in Edremit center", "type": "icecream"},
    "altınoluk dondurma": {"latitude": 39.5689, "longitude": 26.7361, "description": "Ice cream shop in Altınoluk", "type": "icecream"},
    "akçay dondurma": {"latitude": 39.5753, "longitude": 26.9178, "description": "Ice cream shop in Akçay", "type": "icecream"},
    
    # Hotels and accommodation
    "akçay sahil oteli": {"latitude": 39.5788, "longitude": 26.9401, "description": "Beachfront hotel in Akçay with sea view", "type": "hotel"},
    "altınoluk hotel": {"latitude": 39.5688, "longitude": 26.7355, "description": "Centrally located hotel in Altınoluk", "type": "hotel"},
    "güre termal resort": {"latitude": 39.5871, "longitude": 26.8828, "description": "Luxury thermal spa hotel in Güre", "type": "hotel"},
    "edremit park hotel": {"latitude": 39.5944, "longitude": 27.0239, "description": "Central hotel in Edremit city", "type": "hotel"},
    "zeytinli butik otel": {"latitude": 39.5836, "longitude": 26.9815, "description": "Boutique hotel among olive groves in Zeytinli", "type": "hotel"},
    "akçay pansiyon": {"latitude": 39.5788, "longitude": 26.9401, "description": "Family-run pension near Akçay beach", "type": "hotel"},
    "otel": {"latitude": 39.5942, "longitude": 27.0246, "description": "Hotels in Edremit area", "type": "hotel"},
    "hotel": {"latitude": 39.5942, "longitude": 27.0246, "description": "Hotels in Edremit area", "type": "hotel"},
    "konaklama": {"latitude": 39.5942, "longitude": 27.0246, "description": "Accommodation options in Edremit", "type": "hotel"},
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
        
    # For incomplete queries without location context, default to Edremit
    # This handles cases like "sahil kenarı" or "eczane" without specific location
    if lower_place in ["otel", "hotel", "oteller", "konaklama", "eczane", "market", "sahil", "plaj", "restoran", "market"] and "edremit" not in lower_place and "akçay" not in lower_place and "altinoluk" not in lower_place:
        print(f"Incomplete query '{lower_place}' without location context, defaulting to Edremit region")
        
        # Check if we have a default entry for this incomplete query
        if lower_place in EDREMIT_LOCATIONS:
            data = EDREMIT_LOCATIONS[lower_place]
            return {
                "place": lower_place.title(),
                "latitude": data["latitude"],
                "longitude": data["longitude"],
                "description": data["description"],
                "type": data.get("type", "location"),
                "note": "Default location in Edremit for incomplete query"
            }
        
        # For hotel queries without location, default to Akçay hotels
        if lower_place in ["otel", "hotel", "oteller", "konaklama"]:
            hotel_data = EDREMIT_LOCATIONS["otel"]
            return {
                "place": "Akçay Otelleri",
                "latitude": hotel_data["latitude"],
                "longitude": hotel_data["longitude"],
                "description": hotel_data["description"],
                "type": "hotel",
                "note": "Default hotel location in Akçay for incomplete query"
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
