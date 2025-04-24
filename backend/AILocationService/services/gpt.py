"""
GPT integration for natural language location query processing
"""
import os
import json
import logging
import traceback
from typing import Dict, Any, Optional

from openai import OpenAI
from pydantic import BaseModel

from ..config import (
    OPENAI_API_LOCATION_KEY,
    LOCATION_GPT_MODEL,
    FALLBACK_GPT_MODEL,
    LOCATION_FUNCTION,
    DEFAULT_LANGUAGE
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_LOCATION_KEY)

# Minimal system prompt to guide the model
MINIMAL_SYSTEM_PROMPT = "Sen bir konum çözümleme ve yorumlama uzmanısın. Öncelikli olarak Edremit, Balıkesir bölgesinde uzmanlaşmış bir sistemsin."

class LocationQueryResponse(BaseModel):
    action: str
    service_type: str
    location_name: Optional[str] = None
    context: Optional[str] = None
    location_type: Optional[str] = None
    food: Optional[str] = None
    landmark_name: Optional[str] = None
    query: Optional[str] = None
    location: Optional[str] = None
    raw_query: str

async def interpret_location(prompt: str, language: str = DEFAULT_LANGUAGE) -> Dict[str, Any]:
    """
    Interpret a location query using our fine-tuned model
    
    Args:
        prompt: The user's location query
        language: Language code (default: tr for Turkish)
        
    Returns:
        Dictionary with interpreted action and parameters
    """
    # For logging purposes
    logger.info(f"Processing location query: {prompt} (language: {language})")

    try:
        # Only use function calling for Turkish
        if language.lower() == "tr":
            # Make the API call with function calling
            response = client.chat.completions.create(
                model=LOCATION_GPT_MODEL,
                messages=[
                    {"role": "system", "content": MINIMAL_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                tools=[{"type": "function", "function": LOCATION_FUNCTION}],
                tool_choice={"type": "function", "function": {"name": "process_location_query"}}
            )
            
            # Extract the function call parameters
            if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
                tool_call = response.choices[0].message.tool_calls[0]
                interpretation = json.loads(tool_call.function.arguments)
                logger.info(f"Model interpretation: {interpretation}")
            else:
                # Try fallback model
                logger.warning("No function call in response, trying fallback model")
                response = client.chat.completions.create(
                    model=FALLBACK_GPT_MODEL,
                    messages=[
                        {"role": "system", "content": MINIMAL_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    tools=[{"type": "function", "function": LOCATION_FUNCTION}],
                    tool_choice={"type": "function", "function": {"name": "process_location_query"}}
                )
                
                if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
                    tool_call = response.choices[0].message.tool_calls[0]
                    interpretation = json.loads(tool_call.function.arguments)
                else:
                    interpretation = {"action": "defined-location", "location_name": "edremit", "service_type": "default_service"}
        else:
            # For non-Turkish languages, use default GPT behavior (not fine-tuned)
            response = client.chat.completions.create(
                model=FALLBACK_GPT_MODEL,
                messages=[
                    {"role": "system", "content": MINIMAL_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
            )
            
            # Parse the response content
            content = response.choices[0].message.content
            try:
                interpretation = json.loads(content)
            except json.JSONDecodeError:
                interpretation = {"action": "defined-location", "location_name": "edremit", "service_type": "default_service"}
        
        # Add raw query to response
        interpretation["raw_query"] = prompt
        
        # Ensure proper action values
        if interpretation.get('action') not in ["user-location", "defined-location", "contextual-location", 
                                              "food-location", "landmark-search", "expanded-query"]:
            interpretation['action'] = "defined-location"
            
        # Ensure service_type is present
        if 'service_type' not in interpretation:
            interpretation['service_type'] = 'default_service'
            
        return interpretation
    
    except Exception as e:
        logger.error(f"Error interpreting location: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Return a safe default response
        return {
            "action": "defined-location", 
            "location_name": "edremit",
            "service_type": "default_service",
            "raw_query": prompt,
            "error": str(e)
        }