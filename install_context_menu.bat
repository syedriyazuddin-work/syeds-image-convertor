@echo off
title Installing AnyWebP Context Menu...
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_context_menu.ps1"
echo.
pause
