from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from database.database import get_db
from maks.deprem_risk import hesapla_deprem_riski  # doğru import
import json  # GEOJSON dönüşümü için gerekli

router = APIRouter()

@router.get("/bina")
async def get_buildings_within_radius(
    lon: float = Query(..., description="Merkez boylam"),
    lat: float = Query(..., description="Merkez enlem"),
    radius: int = Query(..., description="Metre cinsinden yarıçap"),
    db: Session = Depends(get_db)
):
    try:
        # SQL sorgusu (veri + geojson string + properties)
        query = text("""
            SELECT
                ST_AsGeoJSON(ST_Transform(geom, 4326)) AS geometry,
                to_jsonb("YAPI") - 'geom' AS properties
            FROM "YAPI"
            WHERE ST_DWithin(
                ST_Transform(geom, 4326)::geography,
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
                :radius
            )
        """)

        print(f"📍 Sorgu başlatıldı: lon={lon}, lat={lat}, radius={radius}")
        rows = db.execute(query, {"lon": lon, "lat": lat, "radius": radius}).fetchall()
        print(f"📄 Toplam satır sayısı: {len(rows)}")

        features = []

        for row in rows:
            try:
                geometry_str = row[0]  # Tuple olduğu için indeksle erişiyoruz
                raw_props = row[1]

                if not geometry_str or not raw_props:
                    print("⚠️ Boş satır atlandı.")
                    continue

                geometry = json.loads(geometry_str)
                properties = dict(raw_props)

                # Risk skoru ekle
                try:
                    properties["RISKSKORU"] = hesapla_deprem_riski(properties)
                except Exception as e:
                    print("⚠️ Risk hesaplama hatası:", e)
                    properties["RISKSKORU"] = None

                features.append({
                    "type": "Feature",
                    "geometry": geometry,
                    "properties": properties
                })

            except Exception as row_err:
                print("❌ Satır işleme hatası:", row_err)
                continue

        return {
            "type": "FeatureCollection",
            "features": features
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"🔥 Genel hata: {str(e)}")
