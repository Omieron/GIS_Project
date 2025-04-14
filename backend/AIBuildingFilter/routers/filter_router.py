"""
FastAPI router for the Building Filter AI service
"""
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from AIBuildingFilter.services.gpt import process_building_filter_query

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

class FilterQuery(BaseModel):
    prompt: str
    
class FilterResponse(BaseModel):
    zeminustu: Optional[int] = None
    zeminalti: Optional[int] = None
    durum: Optional[str] = None
    tip: Optional[str] = None
    seragazi: Optional[str] = None
    deprem_riski: Optional[str] = None
    deprem_toggle: bool = False
    raw_query: str
    processed_query: str = ""
    error: Optional[str] = None

@router.post("/filter/", response_model=FilterResponse)
async def process_filter_query(query: FilterQuery) -> Dict[str, Any]:
    """
    Process a natural language building filter query
    
    Example queries:
    - "Show me all buildings with at least 3 floors above ground"
    - "I want to see apartment buildings with a low earthquake risk"
    - "Filter for buildings with high greenhouse gas emissions in class F or G"
    """
    try:
        logger.info(f"Received filter query: {query.prompt}")
        
        # Process the query through GPT
        result = await process_building_filter_query(query.prompt)
        
        # Add processed description in Turkish
        filters_applied = []
        
        if result.get("zeminustu"):
            filters_applied.append(f"zemin üstü en az {result['zeminustu']} kat")
            
        if result.get("zeminalti"):
            filters_applied.append(f"zemin altı en az {result['zeminalti']} kat")
            
        if result.get("durum"):
            durum_map = {
                "1": "mevcut", 
                "2": "yıkılmış"
            }
            filters_applied.append(f"durumu: {durum_map.get(result['durum'], result['durum'])}")
            
        if result.get("tip"):
            tip_map = {
                "1": "konut", 
                "2": "ticari", 
                "3": "karma", 
                "4": "diğer"
            }
            filters_applied.append(f"bina tipi: {tip_map.get(result['tip'], result['tip'])}")
            
        if result.get("seragazi"):
            filters_applied.append(f"seragazı emisyon sınıfı: {result['seragazi']}")
            
        if result.get("deprem_riski") and result.get("deprem_toggle", False):
            risk_map = {
                "1": "çok düşük", 
                "2": "düşük", 
                "3": "orta", 
                "4": "yüksek", 
                "5": "çok yüksek"
            }
            filters_applied.append(f"deprem riski: {risk_map.get(result['deprem_riski'], result['deprem_riski'])}")
        
        # Create a human-readable summary of the filters applied in Turkish
        if filters_applied:
            result["processed_query"] = f"Şu özelliklere sahip binalar filtreleniyor: {', '.join(filters_applied)}"
        else:
            result["processed_query"] = "Belirli bir filtre tespit edilemedi"
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing filter query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
