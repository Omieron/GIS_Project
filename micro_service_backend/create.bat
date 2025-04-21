@echo off
echo ========================================================
echo   Edremit Belediyesi Backend Sistemi Baslatma Betigi
echo ========================================================
echo.

echo Docker ve Docker Compose kontrol ediliyor...
where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo HATA: docker komutu bulunamadi! Docker'in kurulu oldugundan emin olun.
    exit /b 1
)

where docker-compose >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo HATA: docker-compose komutu bulunamadi! Docker Compose'un kurulu oldugundan emin olun.
    exit /b 1
)

echo Docker ve Docker Compose kontrol edildi.
echo.

echo Calisan docker konteynerlerini kontrol ediyorum...
docker ps -q > tmp_containers.txt
for /f %%i in ("tmp_containers.txt") do set size=%%~zi
if %size% gtr 0 (
    echo UYARI: Sistemde calisan konteynerler var.
    echo Devam ederseniz, cakisma olabilir. Once mevcut konteynerleri durdurmak ister misiniz?
    set /p stop_choice="Mevcut konteynerleri durdur ve devam et? (y/n): "
    
    if /i "%stop_choice%"=="y" (
        echo Mevcut konteynerler durduruluyor...
        docker-compose down 2>nul
        docker-compose -p edremit-backend down 2>nul
    )
    echo.
)
del tmp_containers.txt

echo Backend sistemi baslatiliyor...
echo.

docker-compose up -d

if %ERRORLEVEL% equ 0 (
    echo.
    echo Sistem basariyla baslatildi!
    echo.
    echo Servis durumu:
    docker-compose ps
    
    echo.
    echo API'ye su adresten erisebilirsiniz:
    echo http://localhost:8001/
    echo.
    echo Swagger dokumantasyonuna erismek icin:
    echo http://localhost:8001/documentation
    echo http://localhost:8001/location-docs
    
    echo.
    echo Log dosyalarini kontrol etmek icin:
    echo - docker logs nginx-proxy      (Nginx loglari)
    echo - docker logs backend_monolith (Backend loglari)
    echo - docker logs location_service (Konum servisi loglari)
) else (
    echo.
    echo HATA: Sistem baslatilamadi!
    echo docker-compose.yml dosyasinin dogru konumda oldugundan emin olun.
    echo Hata detaylari icin docker-compose logs komutunu calistirin.
)

echo.
echo Islem tamamlandi!
pause