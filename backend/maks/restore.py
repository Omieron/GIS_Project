from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database.database import get_db  # varsa kendi db bağlantı fonksiyonun

router = APIRouter()

@router.post("/yapi/restore")
async def restore_yapi_from_clone(db: Session = Depends(get_db)):
    try:
        # 1. Orijinal tabloyu boşalt
        db.execute(text('TRUNCATE TABLE "YAPI" RESTART IDENTITY CASCADE;'))

        # 2. Klon tablodan veri kopyala
        db.execute(text('INSERT INTO "YAPI" SELECT * FROM "YAPI_KLON";'))

        # 3. (Opsiyonel) Commit işlemi
        db.commit()

        return {"message": "✅ YAPI tablosu başarıyla geri yüklendi."}

    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"🔥 Restore işlemi başarısız: {str(e)}")
