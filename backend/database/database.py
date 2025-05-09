from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Eğer Docker İçinde Kullanılıyorsa
# DATABASE_URL = "postgresql://postgres:123@host.docker.internal:8086/edremit_maks"

# Eğer PC üzerinden direkt çalıştırılırsa
DATABASE_URL = "postgresql://postgres:123@localhost:8086/edremit_maks"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()