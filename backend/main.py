from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from maks.bina import router as bina_router

# Import AILocationService router
from AILocationService.routers.location_router import router as location_router

# Import AIBuildingFilter router
from AIBuildingFilter.routers.filter_router import router as filter_router

app = FastAPI(
    title="Benim API'm",
    description="Bu API hakkında açıklama",
    version="0.1.0",
    docs_url="/documentation"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(bina_router, prefix="/maks")

# Include AILocationService router - note that location_router already has prefix='/api'
app.include_router(location_router)

# Include AIBuildingFilter router
app.include_router(filter_router, prefix="/ai-filter")

@app.get("/")
def read_root():
    return {
        "message": "Edremit MAKS Veri Servisi",
        "status": "running",
        "endpoints": [
            {
                "path": "/geojson/yapi",
                "query_params": {
                    "bbox": "İsteğe bağlı, görünüm alanı sınırları (minx,miny,maxx,maxy)"
                },
                "description": "Ham YAPI verilerini döndürür (offset frontend tarafında uygulanır)"
            },
            {
                "path": "/api/location/",
                "description": "Konum tabanlı doğal dil sorgulaması için API (POST)"
            },
            {
                "path": "/api/osm/amenities/",
                "description": "OpenStreetMap'te yakın belirli tesis türlerinin (restaurant, cafe, vb.) bulunması (GET)"
            },
            {
                "path": "/api/osm/poi/",
                "description": "Edremit bölgesinde ilgi noktalarının bulunması (GET)"
            },
            {
                "path": "/api/enhanced-location/",
                "description": "Geliştirilmiş konum sorguları için API (POST)"
            },
            {
                "path": "/ai-filter/filter/",
                "description": "Doğal dil ile bina filtresi için API (POST)"
            }
        ]
    }