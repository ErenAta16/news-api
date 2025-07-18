@echo off
chcp 65001 >nul
title Haber Analizi - Tüm Sistem Kontrol
color 0B

:menu
cls
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                        📰 HABER ANALİZİ - ANA KONTROL                      ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo [1] 📊 Tam Analiz Çalıştır
echo [2] 🌐 Dashboard Başlat
echo [3] ⏰ Otomatik Zamanlayıcı
echo [4] 📊 Ham Veri Görüntüle
echo [5] 📋 Sistem Durumu
echo [6] 📁 Proje Klasörünü Aç
echo [7] 📖 README Görüntüle
echo [8] ❌ Çıkış
echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo.
set /p choice="Seçiminizi yapın (1-8): "

if "%choice%"=="1" goto analysis
if "%choice%"=="2" goto dashboard
if "%choice%"=="3" goto scheduler
if "%choice%"=="4" goto view_data
if "%choice%"=="5" goto status
if "%choice%"=="6" goto open_folder
if "%choice%"=="7" goto readme
if "%choice%"=="8" goto exit
goto menu

:analysis
cls
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                        🚀 TAM ANALİZ BAŞLATILIYOR                          ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
cd src
python main.py
cd ..
pause
goto menu

dashboard
cls
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                        🌐 DASHBOARD BAŞLATILIYOR                           ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
cd src
streamlit run dashboard.py
cd ..
pause
goto menu

:scheduler
cls
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                        ⏰ OTOMATİK ZAMANLAYICI BAŞLATILIYOR                ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
cd src
python scheduler.py
cd ..
pause
goto menu

:view_data
cls
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                        📊 HAM VERİ GÖRÜNTÜLEME SİSTEMİ                     ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
cd src
python view_raw_data.py
cd ..
pause
goto menu

:status
cls
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                        📋 SİSTEM DURUMU                                     ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo 📊 PROJE DURUMU:
echo   ✅ RSS Toplayıcı: Aktif
echo   ✅ Metin İşleme: Aktif
echo   ✅ Analiz Sistemi: Aktif
echo   ✅ Dashboard: Hazır
echo   ✅ Zamanlayıcı: Hazır
echo   ✅ Veritabanı: Aktif
echo.
echo 📁 DOSYA YAPISI:
echo   📄 main.py - Ana analiz sistemi
echo   📄 dashboard.py - Streamlit dashboard
echo   📄 rss_collector.py - RSS veri toplayıcı
echo   📄 database.py - Veritabanı yönetimi
echo   📄 text_processor.py - Metin işleme
echo   📄 scheduler.py - Otomatik zamanlayıcı
echo   📄 view_raw_data.py - Ham veri görüntüleme
echo.
echo 🎯 KULLANIM:
echo   1. Tam analiz için: python src\main.py
echo   2. Dashboard için: streamlit run src\dashboard.py
echo   3. Zamanlayıcı için: python src\scheduler.py
echo   4. Ham veri için: python src\view_raw_data.py
echo.
pause
goto menu

:open_folder
cls
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                        📁 PROJE KLASÖRÜ AÇILIYOR                           ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
explorer .
pause
goto menu

:readme
cls
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                        📖 README DOSYASI                                    ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
type README.md
echo.
pause
goto menu

:exit
cls
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                        👋 GÜLE GÜLE!                                        ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo Haber Analizi sisteminden çıkılıyor...
timeout /t 2 >nul
exit 