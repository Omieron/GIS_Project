#!/bin/bash

# Docker imajını oluştur
echo "📦 Docker imajı oluşturuluyor..."
docker build -t my-fastapi-backend .

# Daha önce varsa container'ı durdur ve sil
if [ "$(docker ps -aq -f name=fastapi-container)" ]; then
  echo "🛑 Eski container siliniyor..."
  docker rm -f fastapi-container
fi

# Yeni container'ı başlat
echo "🚀 Backend başlatılıyor..."
docker run -d -p 8001:8001 --name fastapi-container my-fastapi-backend

echo "✅ Backend hazır: http://localhost:8001"