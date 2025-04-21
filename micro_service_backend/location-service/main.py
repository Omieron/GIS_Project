from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.location_router import router as location_router  # Import yolunu düzelttim

app = FastAPI(
    title="Konum Servisi",
    description="Konum tabanlı işlemler için API",
    version="0.1.0",
    docs_url="/documentation",
    root_path="/location-service"  # root_path ekleyin
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Location router'ını include et
app.include_router(location_router)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "location-service"}

@app.get("/")
def read_root():
    return {
        "service": "Konum Servisi",
        "status": "running",
        "endpoints": [
            {
                "path": "/api/location/",
                "description": "Konum tabanlı doğal dil sorgulaması için API"
            },
            {
                "path": "/api/osm/amenities/",
                "description": "OpenStreetMap'te yakın belirli tesis türlerini bulma"
            },
            {
                "path": "/api/osm/poi/",
                "description": "Edremit bölgesinde ilgi noktalarının bulunması"
            },
            {
                "path": "/api/enhanced-location/",
                "description": "Geliştirilmiş konum sorguları için API"
            }
        ]
    }