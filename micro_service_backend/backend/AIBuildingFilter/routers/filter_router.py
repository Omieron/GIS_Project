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
    sql_query: Optional[str] = None
    is_update_request: bool = False
    error: Optional[str] = None
    
    class Config:
        # Bu, None değerlerinin dönüşte dışarıda bırakılmasını sağlar
        exclude_none = True
        # Bu, istenen türlere dönüşümü otomatik yapar
        validate_assignment = True

@router.post("/filter/")
async def process_filter_query(query: FilterQuery):
    """
    Process a natural language building filter query
    
    Example queries:
    - "Show me all buildings with at least 3 floors above ground"
    - "I want to see apartment buildings with a low earthquake risk"
    - "Filter for buildings with high greenhouse gas emissions in class F or G"
    """
    try:
        logger.info(f"Received filter query: {query.prompt}")
        
        # Önce sözcük tabanlı basit bir analiz yapalım
        prompt_lower = query.prompt.lower()
        
        # Güncelleme sorgusu olup olmadığını tespit et
        update_keywords = ["güncelle", "değiştir", "yap", "olsun", "ayarla"]
        is_update_query = any(keyword in prompt_lower for keyword in update_keywords)
        
        # SQL sorgusu oluştur (eğer güncelleme sorgusuysa)
        sql_query = None
        if is_update_query:
            # Tip güncelleme
            if "tipini ticari" in prompt_lower or "ticari yap" in prompt_lower:
                sql_query = "UPDATE public.\"YAPI\" SET \"TIP\" = 2"
            elif "tipini konut" in prompt_lower or "konut yap" in prompt_lower:
                sql_query = "UPDATE public.\"YAPI\" SET \"TIP\" = 1"
            elif "tipini karma" in prompt_lower or "karma yap" in prompt_lower:
                sql_query = "UPDATE public.\"YAPI\" SET \"TIP\" = 3"
            elif "tipini diğer" in prompt_lower or "diğer yap" in prompt_lower:
                sql_query = "UPDATE public.\"YAPI\" SET \"TIP\" = 4"
            
            # Durum güncelleme
            elif "durumunu yıkılmış" in prompt_lower or "yıkılmış olarak" in prompt_lower:
                sql_query = "UPDATE public.\"YAPI\" SET \"DURUM\" = 2"
            elif "durumunu mevcut" in prompt_lower or "mevcut olarak" in prompt_lower:
                sql_query = "UPDATE public.\"YAPI\" SET \"DURUM\" = 1"
            
            # Deprem riski güncelleme
            elif "riskini yüksek" in prompt_lower or "yüksek risk" in prompt_lower:
                sql_query = "UPDATE public.\"YAPI\" SET \"DEPREM_RISKI\" = 4"
            elif "riskini düşük" in prompt_lower or "düşük risk" in prompt_lower:
                sql_query = "UPDATE public.\"YAPI\" SET \"DEPREM_RISKI\" = 2"
            elif "riskini orta" in prompt_lower or "orta risk" in prompt_lower:
                sql_query = "UPDATE public.\"YAPI\" SET \"DEPREM_RISKI\" = 3"
        
        # Şimdi normal GPT işlemini devam ettir
        result = await process_building_filter_query(query.prompt)
        
        # Eğer basit analizimiz bir güncelleme sorgusu tespit ettiyse, GPT'den dönen çıktıyı override et
        if is_update_query and sql_query:
            result["is_update_request"] = True
            result["sql_query"] = sql_query
            result["filter_params"] = {}
        
        # Manuel olarak gerekli alanları kontrol et ve varsayılan değerleri ayarla
        if "deprem_toggle" not in result or result["deprem_toggle"] is None:
            result["deprem_toggle"] = False
            
        if "is_update_request" not in result or result["is_update_request"] is None:
            result["is_update_request"] = False
        
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
        if is_update_query and sql_query:
            # Güncelleme sorgusu için özel açıklama
            if "tip" in sql_query.lower():
                if "2" in sql_query:
                    result["processed_query"] = "Filtrelenmiş binaların tipi ticari olarak güncelleniyor"
                elif "1" in sql_query:
                    result["processed_query"] = "Filtrelenmiş binaların tipi konut olarak güncelleniyor"
                elif "3" in sql_query:
                    result["processed_query"] = "Filtrelenmiş binaların tipi karma olarak güncelleniyor"
                else:
                    result["processed_query"] = "Filtrelenmiş binaların tipi diğer olarak güncelleniyor"
            elif "durum" in sql_query.lower():
                if "2" in sql_query:
                    result["processed_query"] = "Filtrelenmiş binaların durumu yıkılmış olarak güncelleniyor"
                else:
                    result["processed_query"] = "Filtrelenmiş binaların durumu mevcut olarak güncelleniyor"
            elif "deprem_riski" in sql_query.lower():
                if "4" in sql_query:
                    result["processed_query"] = "Filtrelenmiş binaların deprem riski yüksek olarak güncelleniyor"
                elif "2" in sql_query:
                    result["processed_query"] = "Filtrelenmiş binaların deprem riski düşük olarak güncelleniyor"
                else:
                    result["processed_query"] = "Filtrelenmiş binaların deprem riski güncelleniyor"
            else:
                result["processed_query"] = "Filtrelenmiş binalar güncelleniyor"
        elif filters_applied:
            if result.get("is_update_request", False) and result.get("sql_query"):
                result["processed_query"] = f"Şu özelliklere sahip binalar güncelleniyor: {', '.join(filters_applied)}"
            else:
                result["processed_query"] = f"Şu özelliklere sahip binalar filtreleniyor: {', '.join(filters_applied)}"
        else:
            result["processed_query"] = "Belirli bir filtre tespit edilemedi"
            
        # Log SQL query if present
        if result.get("sql_query"):
            logger.info(f"SQL sorgusu oluşturuldu: {result['sql_query']}")
        
        # Son kontrol: Boş string değerlerini None'a çevir ve tüm gereklileri kontrol et
        for key in ["zeminustu", "zeminalti", "durum", "tip", "seragazi", "deprem_riski"]:
            if key in result and result[key] == "":
                result[key] = None
                
        # dictionary şeklinde doğrudan döndür, response_model kullanmadan
        return {k: v for k, v in result.items() if v is not None or k in ["deprem_toggle", "is_update_request", "processed_query", "raw_query"]}
        
    except Exception as e:
        logger.error(f"Error processing filter query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
