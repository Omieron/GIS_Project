"""
Configuration for Location Query Processor
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Information
API_TITLE = "Smart Location AI"
API_VERSION = "1.0.0"
API_DESCRIPTION = "Natural language processing for location queries with Foursquare integration"

# API Keys
OPENAI_API_LOCATION_KEY = os.getenv("OPENAI_API_LOCATION_KEY")
FOURSQUARE_API_KEY = os.getenv("FOURSQUARE_API_KEY")

# Fine-tuned model for location queries
LOCATION_GPT_MODEL = "ft:gpt-4o-mini-2024-07-18:personal:location-ai:BPvWcY7S"
FALLBACK_GPT_MODEL = "gpt-4o-mini"

# Default settings
DEFAULT_LANGUAGE = "tr"
DEFAULT_SEARCH_RADIUS = 2000
DEFAULT_RESULTS_LIMIT = 5

# Function definition for location processing (minimal version for fine-tuned model)
LOCATION_FUNCTION = {
  "name": "process_location_query",
  "description": "Process a natural language location query about Edremit region and Turkey",
  "strict": True,
  "parameters": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["user-location", "defined-location", "contextual-location", 
                "food-location", "landmark-search", "expanded-query"],
        "description": "The type of location query being made"
      },
      "location_name": {
        "type": "string",
        "description": "Primary location being searched for"
      },
      "context": {
        "type": "string",
        "description": "Secondary location providing context"
      },
      "location_type": {
        "type": "string",
        "description": "Type of location being searched for"
      },
      "food": {
        "type": "string",
        "description": "Food type when searching for restaurants"
      },
      "landmark_name": {
        "type": "string",
        "description": "Name of landmark when searching for landmarks"
      },
      "query": {
        "type": "string",
        "description": "Full query for expanded searches"
      },
      "location": {
        "type": "string",
        "description": "Location context for expanded queries or food searches"
      },
      "service_type": {
        "type": "string",
        "enum": ["foursquare_service", "maks_service", "overpass_service", 
                "edremit_service", "default_service"],
        "description": "Which service should handle this query"
      }
    },
    "required": ["action", "service_type"],
    "additionalProperties": False
  }
}

# Conversation settings
CONVERSATION_EXPIRY = 30 * 60  # 30 minutes in seconds