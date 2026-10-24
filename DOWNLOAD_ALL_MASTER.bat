@echo off
chcp 65001 >nul
title Hindi Car Music Vault - Ultimate Bollywood Archive (5,172 Tracks)
color 0A
cls
echo =======================================================================
echo    HINDI CAR MUSIC VAULT -- ULTIMATE BOLLYWOOD ARCHIVE (5,172 TRACKS)
echo =======================================================================
echo    Multi-Worker High Speed 320kbps CD Studio Direct Downloader:
echo    * [01] Retro Golden Classics (60s ^& 70s)  :   933 Tracks
echo    * [02] Evergreen Romance (80s ^& 90s)     : 1,143 Tracks
echo    * [03] 2000s Noughties Hits              :   903 Tracks
echo    * [04] 2010s Modern Bollywood            :   861 Tracks
echo    * [05] 2020s to 2026 Latest Blockbusters :   847 Tracks
echo    * [06] Sacred Bhajans ^& Devotional       :   322 Tracks
echo    * [07] Car Highway Roadtrip Anthems      :    55 Tracks
echo    * [08] Late Night Chill Slow Drive       :   108 Tracks
echo =======================================================================
echo    Total Archive Size: 5,172 Verified Tracks (~50 GB in 320kbps MP3)
echo    * Already downloaded tracks will be skipped automatically!
echo =======================================================================
echo.
set /p confirm="Do you want to start downloading now? (Y/N): "
if /I not "%confirm%"=="Y" (
    echo.
    echo Operation cancelled by user.
    pause
    exit /b
)

echo.
echo [*] Checking dependencies...
python "%~dp0Scripts\setup_ffmpeg.py"

echo.
echo [1/8] Downloading 60s ^& 70s Retro Classics (933 tracks)...
python "%~dp0Scripts\01_download_60s_70s.py"

echo.
echo [2/8] Downloading 80s ^& 90s Evergreen Romance (1,143 tracks)...
python "%~dp0Scripts\02_download_80s_90s.py"

echo.
echo [3/8] Downloading 2000s Bollywood Hits (903 tracks)...
python "%~dp0Scripts\03_download_2000s.py"

echo.
echo [4/8] Downloading 2010s Modern Bollywood (861 tracks)...
python "%~dp0Scripts\04_download_2010s.py"

echo.
echo [5/8] Downloading 2020s to Today Hits (847 tracks)...
python "%~dp0Scripts\05_download_2020s_today.py"

echo.
echo [6/8] Downloading Hindi Bhajans ^& Devotional (322 tracks)...
python "%~dp0Scripts\06_download_bhajans.py"

echo.
echo [7/8] Downloading Car Highway Roadtrip Anthems (55 tracks)...
python "%~dp0Scripts\07_download_car_highway.py"

echo.
echo [8/8] Downloading Late Night Chill Slow Drive (108 tracks)...
python "%~dp0Scripts\08_download_late_night_chill.py"

echo.
echo =======================================================================
echo    MASTER ARCHIVE DOWNLOAD FINISHED!
echo    Your Hindi Car Music Vault is fully updated with 5,172 tracks.
echo    Use 'SYNC_TO_CAR_USB.bat' to export to your car's USB drive!
echo =======================================================================
pause
