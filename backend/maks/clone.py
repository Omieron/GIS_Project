from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database.database import get_db  # kendi db bağlantı fonksiyonun

router = APIRouter()

@router.post("/yapi/clone")
async def klonla_yapi_tablosu(db: Session = Depends(get_db)):
    try:
        # 1. Eğer tablo zaten varsa, DROP et (isteğe bağlı)
        db.execute(text('DROP TABLE IF EXISTS public."YAPI_KLON";'))

        # 2. Yeni klon tabloyu oluştur (şema ve tüm constraint'leriyle birlikte)
        db.execute(text('CREATE TABLE public."YAPI_KLON" (LIKE public."YAPI" INCLUDING ALL);'))

        # 3. Verileri orijinal tablodan klona kopyala
        db.execute(text('INSERT INTO public."YAPI_KLON" SELECT * FROM public."YAPI";'))

        db.commit()
        return {"message": "✅ YAPI tablosu başarıyla klonlandı -> YAPI_KLON"}

    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"🔥 Klonlama işlemi başarısız: {str(e)}")
