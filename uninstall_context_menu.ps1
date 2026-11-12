# Syed's Image Convertor - Context Menu Uninstaller
$ErrorActionPreference = "SilentlyContinue"

Write-Host "Removing Syed's Image Convertor context menu..." -ForegroundColor Cyan

$hkcu = [Microsoft.Win32.Registry]::CurrentUser

try { $hkcu.DeleteSubKeyTree("Software\Classes\SystemFileAssociations\image\shell\SyedsImageConvertor", $false) } catch {}
try { $hkcu.DeleteSubKeyTree("Software\Classes\*\shell\SyedsImageConvertor", $false) } catch {}
try { $hkcu.DeleteSubKeyTree("Software\Classes\SystemFileAssociations\image\shell\ImageConverter", $false) } catch {}
try { $hkcu.DeleteSubKeyTree("Software\Classes\*\shell\ImageConverter", $false) } catch {}
try { $hkcu.DeleteSubKeyTree("Software\Classes\SystemFileAssociations\image\shell\AnyWebP", $false) } catch {}
try { $hkcu.DeleteSubKeyTree("Software\Classes\*\shell\AnyWebP", $false) } catch {}

# Remove SendTo shortcuts
foreach ($oldLnk in @("Syed's Image Convertor.lnk", "Image Converter.lnk", "AnyWebP Converter.lnk")) {
    $sendTo = [System.IO.Path]::Combine($env:APPDATA, "Microsoft\Windows\SendTo\$oldLnk")
    if (Test-Path $sendTo) { Remove-Item -Path $sendTo -Force }
}

Write-Host "Syed's Image Convertor context menu removed cleanly." -ForegroundColor Green
