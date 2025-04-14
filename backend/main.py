from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from maks.bina import router as bina_router
from routers.location_router import router as location_router
from routers.buildings_router import router as buildings_router

# Check if required environment variables are set
required_env_vars = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "FOURSQUARE_API_KEY": os.getenv("FOURSQUARE_API_KEY")
}

missing_vars = [var for var, value in required_env_vars.items() if not value]
if missing_vars:
    print(f"⚠️ Warning: Missing environment variables: {', '.join(missing_vars)}")
    print("Some AILocationService features may not work correctly.")

app = FastAPI(
    title="Edremit GIS with Smart Location AI",
    description="GIS veri servisi ile entegre edilmiş akıllı konum hizmetleri. MAKS verileri ve doğal dil işleme özellikleri bulunmaktadır.",
    version="1.0.0",
    docs_url="/documentation"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bina_router, prefix="/maks")

# Include AILocationService routers
app.include_router(location_router)
app.include_router(buildings_router)

@app.get("/")
def read_root():
    return {
        "message": "Edremit GIS with Smart Location AI",
        "status": "running",
        "components": {
            "maks_service": "active",
            "location_service": "active",
            "buildings_service": "active"
        },
        "endpoints": [
            {
                "path": "/maks/geojson/yapi",
                "query_params": {
                    "bbox": "İsteğe bağlı, görünüm alanı sınırları (minx,miny,maxx,maxy)"
                },
                "description": "Ham YAPI verilerini döndürür (offset frontend tarafında uygulanır)"
            },
            {
                "path": "/api/location/",
                "method": "POST",
                "body": {
                    "prompt": "Doğal dil konum sorgusu (ör: 'Edremit'te kafe nerede?')"
                },
                "description": "Doğal dilde konum sorguları için AI tabanlı konum hizmeti"
            },
            {
                "path": "/api/buildings/",
                "query_params": {
                    "lon": "Merkez noktanın boylamı",
                    "lat": "Merkez noktanın enlemi",
                    "radius": "Arama yarıçapı (metre)"
                },
                "description": "Belirlenen noktanın çevresindeki binaları getirir"
            }
        ]
    }

@app.get("/health")
def health_check():
    api_keys_status = "active" if all(required_env_vars.values()) else "missing_keys"
    
    return {
        "status": "service_running",
        "components": {
            "maks_service": "active",
            "location_service": api_keys_status,
            "buildings_service": "active",
            "database": "configured"
        },
        "api_keys": {
            "openai": "configured" if required_env_vars["OPENAI_API_KEY"] else "missing",
            "foursquare": "configured" if required_env_vars["FOURSQUARE_API_KEY"] else "missing"
        }
    }