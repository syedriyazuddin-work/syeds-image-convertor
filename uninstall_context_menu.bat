@echo off
title Removing AnyWebP Context Menu...
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0uninstall_context_menu.ps1"
echo.
pause
