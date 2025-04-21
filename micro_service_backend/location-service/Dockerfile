# Temel Python imajı
FROM python:3.10-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Gereksinim dosyasını kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# .env dosyasını kopyala (eğer varsa)
COPY .env .env

# Uvicorn ile başlat
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]