from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from maks.bina import router as bina_router

app = FastAPI(
    title="Benim API'm",
    description="Bu API hakkında açıklama",
    version="0.1.0",
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
            }
        ]
    }