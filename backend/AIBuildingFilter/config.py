"""
Configuration for AIBuildingFilter service
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI API Key
OPENAI_API_FILTER_KEY = os.getenv("OPENAI_API_FILTER_KEY")

# Fine-tuned model to use for filtering
DEFAULT_GPT_MODEL = "ft:gpt-4o-mini-2024-07-18:personal:filter-ai:BPv4KrqP"

# Fallback model in case fine-tuned model fails
FALLBACK_GPT_MODEL = "gpt-4o-mini"

# Function definition for building filter (minimal version for fine-tuned model)
BUILDING_FILTER_FUNCTION = {
  "name": "extract_building_filter_parameters",
  "description": "Extracts building filter parameters from the natural language query and generates SQL update queries when needed",
  "strict": True,
  "parameters": {
    "type": "object",
    "properties": {
      "zeminustu": {
        "type": ["integer", "null"],
        "description": "Minimum number of floors above ground"
      },
      "zeminalti": {
        "type": ["integer", "null"],
        "description": "Minimum number of floors below ground"
      },
      "durum": {
        "type": ["string", "null"],
        "enum": ["1", "2"],
        "description": "Building status: 1=Mevcut, 2=Yıkılmış"
      },
      "tip": {
        "type": ["string", "null"],
        "enum": ["1", "2", "3", "4"],
        "description": "Building type: 1=Konut, 2=Ticari, 3=Karma, 4=Diğer"
      },
      "seragazi": {
        "type": ["string", "null"],
        "enum": ["A", "B", "C", "D", "E", "F", "G"],
        "description": "Greenhouse gas emission class"
      },
      "deprem_riski": {
        "type": ["string", "null"],
        "enum": ["1", "2", "3", "4", "5"],
        "description": "Earthquake risk scale: 1=Çok Düşük, 2=Düşük, 3=Orta, 4=Yüksek, 5=Çok Yüksek"
      },
      "deprem_toggle": {
        "type": "boolean",
        "description": "Whether to filter by earthquake risk"
      },
      "processed_query": {
        "type": "string",
        "description": "A processed, cleaned version of the query in Turkish"
      },
      "sql_query": {
        "type": ["string", "null"],
        "description": "SQL UPDATE query to update filtered buildings based on user request"
      },
      "is_update_request": {
        "type": "boolean",
        "description": "Whether this request is asking to update buildings"
      }
    },
    "required": ["processed_query", "is_update_request"],
    "additionalProperties": False
  }
}