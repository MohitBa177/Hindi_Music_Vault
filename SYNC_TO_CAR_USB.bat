@echo off
chcp 65001 >nul
title Car USB Sync - Hindi Music Vault
color 0B
cls
python "%~dp0Scripts\usb_car_sync.py"
pause
