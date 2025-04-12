from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from database.database import get_db

router = APIRouter()

@router.get("/bina")
async def get_buildings_within_radius(
    lon: float = Query(..., description="Merkez boylam"),
    lat: float = Query(..., description="Merkez enlem"),
    radius: int = Query(..., description="Metre cinsinden yarıçap"),
    db: Session = Depends(get_db)
):
    try:
        query = text("""
        SELECT jsonb_build_object(
            'type', 'FeatureCollection',
            'features', jsonb_agg(feature)
        ) AS geojson
        FROM (
            SELECT jsonb_build_object(
                'type', 'Feature',
                'geometry', ST_AsGeoJSON(ST_Transform(geom, 4326))::jsonb,
                'properties', to_jsonb(row) - 'geom'
            ) AS feature
            FROM (
                SELECT * FROM "YAPI"
                WHERE ST_DWithin(
                    ST_Transform(geom, 4326)::geography,
                    ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
                    :radius
                )
            ) row
        ) features;
        """)
        result = db.execute(query, {"lon": lon, "lat": lat, "radius": radius}).fetchone()
        if result and result[0]:
            return result[0]
        else:
            raise HTTPException(status_code=404, detail="Bina bulunamadı.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hata: {str(e)}")