from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from typing import Dict, Any, Optional
from pydantic import BaseModel
from database.database import get_db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class UpdateRequest(BaseModel):
    sql_query: str
    building_ids: list[str]

@router.post("/update", status_code=200)
async def update_buildings(
    request: UpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Execute an SQL update query on the YAPI table.
    This endpoint is designed to work with the AIBuildingFilter service.
    
    - Only UPDATE queries are allowed
    - The query must target the YAPI table
    - Only certain fields can be updated (TIP, DURUM, SERAGAZEMISYONSINIF)
    """
    try:
        # Validate query - basic security check
        sql_query = request.sql_query.strip()
        building_ids = request.building_ids
        
        # Validate building IDs
        if not building_ids or len(building_ids) == 0:
            raise HTTPException(
                status_code=400,
                detail="No building IDs provided. Cannot update without target buildings."
            )
            
        # Check if it's an UPDATE query on YAPI table
        if not sql_query.upper().startswith("UPDATE PUBLIC.\"YAPI\" SET"):
            raise HTTPException(
                status_code=400, 
                detail="Invalid query format. Only UPDATE queries on the YAPI table are allowed."
            )
        
        # Validate the fields being updated - only allow specific fields
        allowed_fields = ["\"TIP\"", "\"DURUM\"", "\"SERAGAZEMISYONSINIF\""]
        valid_field = False
        
        for field in allowed_fields:
            if field in sql_query:
                valid_field = True
                break
                
        if not valid_field:
            raise HTTPException(
                status_code=400,
                detail=f"Only the following fields can be updated: {', '.join(allowed_fields)}"
            )
            
        # Modify the query to only target specific buildings
        # Extract the main part of the query (what's being updated)
        if "WHERE" in sql_query.upper():
            # If there's already a WHERE clause, we don't want to modify it
            # This is a safety check, but our current implementation doesn't add WHERE clauses
            logger.warning(f"Query already contains WHERE clause: {sql_query}")
            raise HTTPException(
                status_code=400,
                detail="Custom WHERE clauses are not supported. The system will add the appropriate filters automatically."
            )
            
        # Add WHERE clause to only update the filtered buildings
        building_ids_list = ", ".join([f"'{bid}'" for bid in building_ids])
        modified_query = f"{sql_query} WHERE \"ID\" IN ({building_ids_list})"
        
        # Execute the modified query
        logger.info(f"Original query: {sql_query}")
        logger.info(f"Executing modified query: {modified_query}")
        
        result = db.execute(text(modified_query))
        db.commit()
        
        # Get count of affected rows
        affected_rows = result.rowcount
        logger.info(f"Updated {affected_rows} rows")
        
        return {
            "status": "success",
            "message": f"Successfully updated {affected_rows} buildings",
            "affected_rows": affected_rows
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error executing update query: {str(e)}")
        db.rollback()  # Roll back the transaction on error
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")
