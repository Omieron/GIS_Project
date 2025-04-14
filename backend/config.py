"""
Application configuration settings
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Information
API_TITLE = "GIS Project with Smart Location AI"
API_VERSION = "1.0.0"
API_DESCRIPTION = """
A GIS service that integrates MAKS data with natural language location queries using OpenAI's GPT models
and provides location services through Foursquare integration.

Features:
- GIS data visualization and querying
- Natural language processing for location queries
- Restaurant and place search
- Multi-language support (English/Turkish)
"""

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FOURSQUARE_API_KEY = os.getenv("FOURSQUARE_API_KEY")

# Default settings
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "tr")  # Default language (Turkish)
DEFAULT_SEARCH_RADIUS = int(os.getenv("DEFAULT_SEARCH_RADIUS", 2000))  # Default search radius in meters
DEFAULT_RESULTS_LIMIT = int(os.getenv("DEFAULT_RESULTS_LIMIT", 5))  # Default number of results to return

# Conversation settings
CONVERSATION_EXPIRY = 30 * 60  # 30 minutes in seconds
