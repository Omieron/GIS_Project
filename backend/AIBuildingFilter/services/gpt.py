"""
GPT integration for natural language building filter queries
"""
import json
import logging
from typing import Dict, Any, Optional

from openai import OpenAI
from pydantic import BaseModel

from ..config import (
    OPENAI_API_FILTER_KEY, 
    DEFAULT_GPT_MODEL,
    FALLBACK_GPT_MODEL,
    BUILDING_FILTER_FUNCTION
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_FILTER_KEY)

# Minimal system prompt to guide the model
MINIMAL_SYSTEM_PROMPT = "Sen bir bina filtreleme ve güncelleme aracısın. Türkçe bina sorgularını analiz ederek parametrelere dönüştür."

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
    Uses a fine-tuned model to understand Turkish queries about building filters.
    
    Args:
        query: The natural language query from the user
        
    Returns:
        Dictionary containing the extracted filter parameters
    """
    try:
        logger.info(f"Processing building filter query: {query}")
        
        # Create chat completion with function calling using fine-tuned model
        response = client.chat.completions.create(
            model=DEFAULT_GPT_MODEL,
            messages=[
                {"role": "system", "content": MINIMAL_SYSTEM_PROMPT},
                {"role": "user", "content": query}
            ],
            tools=[{"type": "function", "function": BUILDING_FILTER_FUNCTION}],
            tool_choice={"type": "function", "function": {"name": "extract_building_filter_parameters"}}
        )
        
        # Extract the function call
        if not response.choices or not response.choices[0].message.tool_calls:
            logger.warning("No function call found in response, trying fallback model")
            
            # Try fallback model
            response = client.chat.completions.create(
                model=FALLBACK_GPT_MODEL,
                messages=[
                    {"role": "system", "content": MINIMAL_SYSTEM_PROMPT},
                    {"role": "user", "content": query}
                ],
                tools=[{"type": "function", "function": BUILDING_FILTER_FUNCTION}],
                tool_choice={"type": "function", "function": {"name": "extract_building_filter_parameters"}}
            )
            
            if not response.choices or not response.choices[0].message.tool_calls:
                logger.error("Fallback model also failed to provide function call")
                return {"error": "Failed to process query", "raw_query": query}
        
        # Get the function call arguments
        tool_call = response.choices[0].message.tool_calls[0]
        if tool_call.function.name != "extract_building_filter_parameters":
            logger.warning(f"Unexpected function call: {tool_call.function.name}")
            return {"error": "Unexpected function call", "raw_query": query}
        
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
                
            # Include the original query
            filter_params["raw_query"] = query
            
            # Log SQL query if present
            if "sql_query" in filter_params and filter_params["sql_query"]:
                logger.info(f"Generated SQL query: {filter_params['sql_query']}")
                
            return filter_params
            
        except json.JSONDecodeError:
            logger.error(f"Failed to parse function arguments: {tool_call.function.arguments}")
            return {"error": "Failed to parse function arguments", "raw_query": query}
        
    except Exception as e:
        logger.error(f"Error processing building filter query: {str(e)}")
        return {"error": str(e), "raw_query": query}