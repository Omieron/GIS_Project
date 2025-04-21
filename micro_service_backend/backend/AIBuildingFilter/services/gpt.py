"""
GPT integration for natural language building filter queries
"""
import json
import logging
from typing import Dict, Any, List, Optional

from openai import OpenAI
from pydantic import BaseModel

from AIBuildingFilter.config import (
    OPENAI_API_KEY, 
    DEFAULT_GPT_MODEL, 
    BUILDING_FILTER_SYSTEM_PROMPT,
    BUILDING_FILTER_FUNCTIONS
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

class BuildingFilterResponse(BaseModel):
    zeminustu: Optional[int] = None
    zeminalti: Optional[int] = None
    durum: Optional[str] = None
    tip: Optional[str] = None
    seragazi: Optional[str] = None
    deprem_riski: Optional[str] = None
    deprem_toggle: bool = False
    raw_query: str
    processed_query: Optional[str] = None
    sql_query: Optional[str] = None
    is_update_request: bool = False
    
async def process_building_filter_query(query: str) -> Dict[str, Any]:
    """
    Process a natural language query about building filters and extract parameters.
    
    Args:
        query: The natural language query from the user
        
    Returns:
        Dictionary containing the extracted filter parameters
    """
    try:
        logger.info(f"Processing building filter query: {query}")
        
        # Create chat completion with function calling
        response = client.chat.completions.create(
            model=DEFAULT_GPT_MODEL,
            messages=[
                {"role": "system", "content": BUILDING_FILTER_SYSTEM_PROMPT},
                {"role": "user", "content": query}
            ],
            tools=BUILDING_FILTER_FUNCTIONS,
            tool_choice="auto"
        )
        
        # Extract the function call
        if not response.choices or not response.choices[0].message.tool_calls:
            logger.warning("No function call found in response")
            return {"error": "Failed to process query"}
        
        # Get the function call arguments
        tool_call = response.choices[0].message.tool_calls[0]
        if tool_call.function.name != "extract_building_filter_parameters":
            logger.warning(f"Unexpected function call: {tool_call.function.name}")
            return {"error": "Unexpected function call"}
        
        # Parse the function arguments as JSON
        try:
            filter_params = json.loads(tool_call.function.arguments)
            logger.info(f"Extracted filter parameters: {filter_params}")
            
            # Ensure the deprem_toggle is set if deprem_riski is present
            if "deprem_riski" in filter_params and filter_params["deprem_riski"]:
                filter_params["deprem_toggle"] = True
            else:
                filter_params.setdefault("deprem_toggle", False)
            
            # Handle processed query if available
            if "processed_query" not in filter_params or not filter_params["processed_query"]:
                filter_params["processed_query"] = query
                
            # Handle update request flag if missing
            filter_params.setdefault("is_update_request", False)
            
            # PROBLEM ÇÖZÜMÜ - deprem_toggle değerini her zaman boolean olarak ayarla
            filter_params.setdefault("deprem_toggle", False)  # Varsayılan değer boolean olarak False
                
            # Include the original query
            filter_params["raw_query"] = query
            
            # Log SQL query if present
            if "sql_query" in filter_params and filter_params["sql_query"]:
                logger.info(f"Generated SQL query: {filter_params['sql_query']}")
                
            logger.info(f"Final filter params: {filter_params}")  # Son parametreleri logla
            
            return filter_params
            
        except json.JSONDecodeError:
            logger.error(f"Failed to parse function arguments: {tool_call.function.arguments}")
            return {"error": "Failed to parse function arguments", "raw_query": query}
        
    except Exception as e:
        logger.error(f"Error processing building filter query: {str(e)}")
        return {"error": str(e), "raw_query": query}
