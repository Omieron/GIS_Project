from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import uuid

from services.gpt import interpret_location
from services.geocode import get_precise_coordinates
from services.user_location import get_user_current_location
from services.places import find_place_near_location, find_relative_location
from services.conversations import get_conversation, add_message, get_last_location
from services.food import find_restaurant_for_dish
from services.foursquare import search_places

router = APIRouter()

@router.post("/location/")
async def process_location(
    prompt: str, 
    request: Request,
    conversation_id: Optional[str] = None
):
    # Get or create conversation
    conversation_id, conversation = get_conversation(conversation_id)
    last_location = get_last_location(conversation_id)
    conversation_history = conversation.get("messages", [])
    language = conversation.get("language", "tr")  # Default to Turkish
    
    print(f"Using conversation ID: {conversation_id}")
    
    # Process the prompt with conversation history for context
    interpretation = await interpret_location(
        prompt, 
        conversation_history=[{"prompt": entry["user"], "response": {"content": str(entry["system"])}} for entry in conversation_history],
        language=language
    )
    
    # Automatically enable conversation continuation if this is not the first message in a conversation
    continue_conversation = conversation_id is not None and len(conversation_history) > 0
    print(f"Interpretation: {interpretation}")
    print(f"Auto-continuing conversation: {continue_conversation}")
    
    result = None
    
    if interpretation["action"] == "user-location":
        user_ip = request.client.host
        location = get_user_current_location(user_ip)
        result = {"type": "user-location", "location": location}
        print(f"User location result: {result}")

    elif interpretation["action"] == "defined-location":
        coords = get_precise_coordinates(interpretation["location_name"])
        result = {"type": "defined-location", "location": coords}
        print(f"Defined location result: {result}")

    elif interpretation["action"] == "contextual-location":
        place_name = interpretation.get("location_name")
        context = interpretation.get("context")
        
        # Try Foursquare API first
        try:
            print(f"Using Foursquare to search for {place_name} near {context}")
            foursquare_result = search_places(query=place_name, location=context)
            
            if "error" not in foursquare_result and foursquare_result.get("latitude") and foursquare_result.get("longitude"):
                coords = {
                    "place": foursquare_result["place"],
                    "latitude": foursquare_result["latitude"],
                    "longitude": foursquare_result["longitude"],
                    "address": foursquare_result.get("address", ""),
                    "categories": foursquare_result.get("categories", []),
                    "context": context,
                    "place_type": place_name,
                    "source": "foursquare"
                }
            else:
                # Fall back to OpenStreetMap
                print(f"Foursquare search failed: {foursquare_result.get('error', 'Unknown error')}")
                print(f"Falling back to OpenStreetMap")
                coords = find_place_near_location(place_name, context)
        except Exception as e:
            print(f"Foursquare error: {str(e)}")
            # Fall back to OpenStreetMap
            coords = find_place_near_location(place_name, context)

        if not coords or "latitude" not in coords:
            result = {"error": "Could not find a place nearby"}
        else:
            # Store the place_type in the location for future reference
            coords["place_type"] = place_name
            
            result = {
                "type": "contextual-location",
                "resolved_place": coords["place"],
                "location": coords
            }
            print(f"Contextual location result: {result}")
    
    elif interpretation["action"] == "relative-location" or continue_conversation:
        print(f"Processing relative/continued location. Last location: {last_location}")
        print(f"Continue conversation: {continue_conversation}")
        
        # Auto-treat requests in an existing conversation as relative if:
        # 1. We have a previous location 
        # 2. The current interpretation isn't already a specific location type
        if continue_conversation and last_location and interpretation["action"] not in ["defined-location", "food-location"]:
            # Override the interpretation to treat as relative
            previous_action = interpretation["action"]
            print(f"Overriding action from {previous_action} to relative-location based on conversation context")
            interpretation["action"] = "relative-location"
            
            # Try to extract contextual cues from the prompt
            if "location_name" not in interpretation:
                # Try to use the previous location's place_type
                if "place_type" in last_location:
                    interpretation["location_name"] = last_location["place_type"]
            
            if "modifier" not in interpretation:
                # Try to extract modifier from prompt
                if any(word in prompt.lower() for word in ["merkez", "center", "yakın", "near"]):
                    interpretation["modifier"] = "merkeze yakın"
                elif any(word in prompt.lower() for word in ["uzak", "far"]):
                    interpretation["modifier"] = "uzak"
        
        if not last_location:
            result = {"error": "No previous location to reference. Try a specific location query first."}
        else:
            # Default to eczane (pharmacy) if type not specified 
            place_type = last_location.get("place_type", "eczane")  
            
            if "location_name" in interpretation and interpretation["location_name"]:
                place_type = interpretation["location_name"]
            
            print(f"Using place type: {place_type}")
            
            modifier = interpretation.get("modifier", "")
            print(f"Using modifier: {modifier}")
            
            # Get city context from previous search if not specified
            city_context = None
            if "context" in interpretation:
                city_context = interpretation["context"]
            elif "context" in last_location:
                city_context = last_location["context"]
                print(f"Using context from previous search: {city_context}")
            
            coords = find_relative_location(place_type, modifier, last_location, city_context)
            
            if not coords or "error" in coords:
                print(f"Error finding relative location: {coords if coords else 'No results'}")
                result = {"error": coords.get("error", "Could not find a relative location")} 
            else:
                # Store the place_type in the coords for future reference
                coords["place_type"] = place_type
                
                result = {
                    "type": "relative-location",
                    "resolved_place": coords["place"],
                    "location": coords,
                    "relative_to": coords.get("relative_to")
                }
                print(f"Relative location result: {result}")
    elif interpretation["action"] == "food-location":
        food = interpretation.get("food")
        location = interpretation.get("location")
        
        print(f"Looking for {food} in {location}")
        
        food_place = find_restaurant_for_dish(food, location)
        
        if "error" in food_place:
            result = {"error": food_place["error"]}
        else:
            result = {
                "type": "food-location",
                "resolved_place": food_place["place"],
                "food": food,
                "location": food_place
            }
            print(f"Found food location: {result}")
    
    else:
        result = {"error": "Unknown action"}
    
    # Update conversation with the interaction
    add_message(conversation_id, prompt, result)
    
    # Include conversation ID in the response
    if result is not None:  # Make sure result is not None before accessing it
        result["conversation_id"] = conversation_id
    else:
        result = {"error": "Failed to process request", "conversation_id": conversation_id}
    
    return result
