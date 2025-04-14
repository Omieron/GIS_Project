"""
Configuration for AIBuildingFilter service
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Default model to use for filtering
DEFAULT_GPT_MODEL = "gpt-4o-mini"

# System prompt for building filter AI
BUILDING_FILTER_SYSTEM_PROMPT = """You are an AI assistant that translates natural language queries about buildings into specific filter parameters.
Your task is to extract filter parameters from a user's natural language query about buildings in Turkish.

You must extract the following parameters (when mentioned):
- zeminustu (number of floors above ground) - Return as number
- zeminalti (number of floors below ground) - Return as number
- durum (building status) - Return numeric value matching these options: 
  * "1" for existing buildings (mevcut, yapılmış, inşa edilmiş, tamamlanmış)
  * "2" for demolished buildings (yıkılmış, yıkık)
- tip (building type) - Return numeric value matching these options:
  * "1" for residential buildings (konut, ev, apartman, müstakil ev, yaşam alanı, mesken)
  * "2" for commercial buildings (ticari, işyeri, ofis, dükkan, mağaza)
  * "3" for mixed-use buildings (karma, karma kullanım, konut+ticari)
  * "4" for other building types (diğer, farklı, başka)
- seragazi (greenhouse gas emission class) - Return exact match from options: "A", "B", "C", "D", "E", "F", "G"
- deprem_riski (earthquake risk score) - Return numeric value matching these options:
  * "1" for very low risk ("yok denecek kadar az", "çok düşük risk")
  * "2" for low risk ("düşük risk", "az riskli")
  * "3" for medium risk ("orta risk", "orta riskli")
  * "4" for high risk ("yüksek risk", "riskli")
  * "5" for very high risk ("çok yüksek risk", "tehlikeli", "çok riskli")

For example:
- If the user asks for "mevcut binalar", you should set durum: "1"
- If the user asks for "konut tipi binalar", you should set tip: "1"
- If the user asks for "apartmanlar", you should set tip: "1" as apartments are residential buildings

Only include parameters that are explicitly mentioned or clearly implied in the query.
If a parameter is not mentioned, do not include it in your response.

Output the results as a valid JSON object with parameter names and values.
Do not include any explanations before or after the JSON.
"""

# Function calling definition for building filters
BUILDING_FILTER_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "extract_building_filters",
            "description": "Extract building filter parameters from a natural language query",
            "parameters": {
                "type": "object",
                "properties": {
                    "zeminustu": {
                        "type": "integer",
                        "description": "Minimum number of floors above ground (ZEMINUSTUKATSAYISI)"
                    },
                    "zeminalti": {
                        "type": "integer",
                        "description": "Minimum number of floors below ground (ZEMINALTIKATSAYISI)"
                    },
                    "durum": {
                        "type": "string",
                        "enum": ["1", "2"],
                        "description": "Building status: 1=Mevcut (existing), 2=Yıkılmış (demolished)"
                    },
                    "tip": {
                        "type": "string",
                        "enum": ["1", "2", "3", "4"],
                        "description": "Building type: 1=Konut (residential), 2=Ticari (commercial), 3=Karma (mixed), 4=Diğer (other)"
                    },
                    "seragazi": {
                        "type": "string",
                        "enum": ["A", "B", "C", "D", "E", "F", "G"],
                        "description": "Greenhouse gas emission class (SERAGAZEMISYONSINIF)"
                    },
                    "deprem_riski": {
                        "type": "string",
                        "enum": ["1", "2", "3", "4", "5"],
                        "description": "Earthquake risk scale: 1=Çok Düşük, 2=Düşük, 3=Orta, 4=Yüksek, 5=Çok Yüksek"
                    },
                    "deprem_toggle": {
                        "type": "boolean",
                        "description": "Whether earthquake risk filter should be applied"
                    }
                },
                "required": []
            }
        }
    }
]
