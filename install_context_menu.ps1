# Syed's Image Convertor - Context Menu Installer
# Created by Syed Riyazuddin
# Supports both standalone compiled executables and source python script mode

$ErrorActionPreference = "Stop"

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host " Installing Syed's Image Convertor Context Menu      " -ForegroundColor Cyan
Write-Host " Created by Syed Riyazuddin                          " -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan

$scriptDir = $PSScriptRoot
if (-not $scriptDir) {
    $scriptDir = (Get-Location).Path
}

$isStandalone = (Test-Path (Join-Path $scriptDir "quick_convert.exe")) -and (Test-Path (Join-Path $scriptDir "ImageConverter.exe"))

if ($isStandalone) {
    $quickConvertExe = Join-Path $scriptDir "quick_convert.exe"
    $guiExe = Join-Path $scriptDir "ImageConverter.exe"
    Write-Host "Mode:   Standalone Executables" -ForegroundColor Green
    Write-Host "Folder: $scriptDir" -ForegroundColor Gray
} else {
    # Locate Python executables
    $pythonDir = "$env:LOCALAPPDATA\Programs\Python\Python312"
    $pythonw = "$pythonDir\pythonw.exe"
    if (-not (Test-Path $pythonw)) {
        $pyCmd = Get-Command pythonw.exe -ErrorAction SilentlyContinue
        if ($pyCmd) {
            $pythonw = $pyCmd.Source
        } else {
            $pyCmd2 = Get-Command python.exe -ErrorAction SilentlyContinue
            if ($pyCmd2) {
                $pythonw = Join-Path (Split-Path $pyCmd2.Source) "pythonw.exe"
            }
        }
    }

    if (-not (Test-Path $pythonw)) {
        Write-Error "Could not find pythonw.exe or standalone executables. Please ensure Python 3 is installed."
        exit 1
    }

    $quickConvertScript = Join-Path $scriptDir "quick_convert.py"
    $guiScript = Join-Path $scriptDir "gui.py"
    Write-Host "Mode:   Python Script" -ForegroundColor Cyan
    Write-Host "Python: $pythonw" -ForegroundColor Gray
    Write-Host "Folder: $scriptDir" -ForegroundColor Gray
}

# Icon path: use app_icon.ico if present, otherwise imageres.dll,67
$iconPath = Join-Path $scriptDir "app_icon.ico"
if (-not (Test-Path $iconPath)) {
    $iconPath = "imageres.dll,67"
}

# Clean up any previous keys
$hkcu = [Microsoft.Win32.Registry]::CurrentUser
try { $hkcu.DeleteSubKeyTree("Software\Classes\SystemFileAssociations\image\shell\SyedsImageConvertor", $false) } catch {}
try { $hkcu.DeleteSubKeyTree("Software\Classes\*\shell\SyedsImageConvertor", $false) } catch {}
try { $hkcu.DeleteSubKeyTree("Software\Classes\SystemFileAssociations\image\shell\ImageConverter", $false) } catch {}
try { $hkcu.DeleteSubKeyTree("Software\Classes\*\shell\ImageConverter", $false) } catch {}
try { $hkcu.DeleteSubKeyTree("Software\Classes\SystemFileAssociations\image\shell\AnyWebP", $false) } catch {}
try { $hkcu.DeleteSubKeyTree("Software\Classes\*\shell\AnyWebP", $false) } catch {}

# Clean up old SendTo shortcuts
foreach ($oldLnk in @("AnyWebP Converter.lnk", "Image Converter.lnk", "Syed's Image Convertor.lnk")) {
    $p = [System.IO.Path]::Combine($env:APPDATA, "Microsoft\Windows\SendTo\$oldLnk")
    if (Test-Path $p) { Remove-Item -Path $p -Force -ErrorAction SilentlyContinue }
}

# File types filter for AppliesTo
$extensions = @('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif', '.tiff', '.tif', '.avif', '.heic', '.heif', '.ico', '.jfif')
$appliesFilter = ($extensions | ForEach-Object { "System.FileName:`"$_`"" }) -join " OR "

function Create-SyedImageConverterMenu([string]$relativeRootKey) {
    $hkcu = [Microsoft.Win32.Registry]::CurrentUser

    # Main cascading menu key
    $menuKey = $hkcu.CreateSubKey($relativeRootKey)
    $menuKey.SetValue("MUIVerb", "Syed's Image Convertor")
    $menuKey.SetValue("Icon", $iconPath)
    $menuKey.SetValue("SubCommands", "")
    $menuKey.SetValue("AppliesTo", $appliesFilter)
    $menuKey.Close()

    # Determine command strings based on mode
    if ($isStandalone) {
        $cmdWebp = "`"$quickConvertExe`" webp `"%1`""
        $cmdPng  = "`"$quickConvertExe`" png `"%1`""
        $cmdJpg  = "`"$quickConvertExe`" jpg `"%1`""
        $cmdAvif = "`"$quickConvertExe`" avif `"%1`""
        $cmdGui  = "`"$guiExe`" `"%1`""
    } else {
        $cmdWebp = "`"$pythonw`" `"$quickConvertScript`" webp `"%1`""
        $cmdPng  = "`"$pythonw`" `"$quickConvertScript`" png `"%1`""
        $cmdJpg  = "`"$pythonw`" `"$quickConvertScript`" jpg `"%1`""
        $cmdAvif = "`"$pythonw`" `"$quickConvertScript`" avif `"%1`""
        $cmdGui  = "`"$pythonw`" `"$guiScript`" `"%1`""
    }

    # 1. Quick Convert to WebP
    $k1 = $hkcu.CreateSubKey("$relativeRootKey\shell\01_webp")
    $k1.SetValue("MUIVerb", "Convert to WebP (Instant)")
    $k1.SetValue("Icon", $iconPath)
    $k1Cmd = $hkcu.CreateSubKey("$relativeRootKey\shell\01_webp\command")
    $k1Cmd.SetValue("", $cmdWebp)
    $k1.Close()
    $k1Cmd.Close()

    # 2. Quick Convert to PNG
    $k2 = $hkcu.CreateSubKey("$relativeRootKey\shell\02_png")
    $k2.SetValue("MUIVerb", "Convert to PNG (Instant)")
    $k2Cmd = $hkcu.CreateSubKey("$relativeRootKey\shell\02_png\command")
    $k2Cmd.SetValue("", $cmdPng)
    $k2.Close()
    $k2Cmd.Close()

    # 3. Quick Convert to JPG
    $k3 = $hkcu.CreateSubKey("$relativeRootKey\shell\03_jpg")
    $k3.SetValue("MUIVerb", "Convert to JPG (Instant)")
    $k3Cmd = $hkcu.CreateSubKey("$relativeRootKey\shell\03_jpg\command")
    $k3Cmd.SetValue("", $cmdJpg)
    $k3.Close()
    $k3Cmd.Close()

    # 4. Quick Convert to AVIF
    $k4 = $hkcu.CreateSubKey("$relativeRootKey\shell\04_avif")
    $k4.SetValue("MUIVerb", "Convert to AVIF (Instant)")
    $k4Cmd = $hkcu.CreateSubKey("$relativeRootKey\shell\04_avif\command")
    $k4Cmd.SetValue("", $cmdAvif)
    $k4.Close()
    $k4Cmd.Close()

    # 5. Open in Desktop GUI
    $k5 = $hkcu.CreateSubKey("$relativeRootKey\shell\05_gui")
    $k5.SetValue("MUIVerb", "Customize & Convert (GUI)...")
    $k5.SetValue("Icon", "imageres.dll,114")
    $k5Cmd = $hkcu.CreateSubKey("$relativeRootKey\shell\05_gui\command")
    $k5Cmd.SetValue("", $cmdGui)
    $k5.Close()
    $k5Cmd.Close()
}

# 1. Register under SystemFileAssociations\image\shell\SyedsImageConvertor
Create-SyedImageConverterMenu "Software\Classes\SystemFileAssociations\image\shell\SyedsImageConvertor"

# 2. Register under *\shell\SyedsImageConvertor
Create-SyedImageConverterMenu "Software\Classes\*\shell\SyedsImageConvertor"

# 3. Ensure PerceivedType is set to 'image' for modern formats
$hkcu = [Microsoft.Win32.Registry]::CurrentUser
foreach ($ext in @('.avif', '.heic', '.webp')) {
    $eKey = $hkcu.CreateSubKey("Software\Classes\$ext")
    $eKey.SetValue("PerceivedType", "image")
    $eKey.Close()
}

# 4. Create SendTo shortcut
$sendToDir = [System.IO.Path]::Combine($env:APPDATA, "Microsoft\Windows\SendTo")
if (Test-Path $sendToDir) {
    try {
        $shortcutPath = Join-Path $sendToDir "Syed's Image Convertor.lnk"
        $wsh = New-Object -ComObject WScript.Shell
        $shortcut = $wsh.CreateShortcut($shortcutPath)
        if ($isStandalone) {
            $shortcut.TargetPath = $guiExe
            $shortcut.Arguments = ""
        } else {
            $shortcut.TargetPath = $pythonw
            $shortcut.Arguments = "`"$guiScript`""
        }
        $shortcut.WorkingDirectory = $scriptDir
        $shortcut.Description = "Syed's Image Convertor - Created by Syed Riyazuddin"
        $shortcut.IconLocation = $iconPath
        $shortcut.Save()
        Write-Host "Created 'Send to' shortcut: Syed's Image Convertor" -ForegroundColor Green
    } catch {
        Write-Host "Note: Could not create SendTo shortcut ($($_.Exception.Message))" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Syed's Image Convertor Context Menu installed successfully!" -ForegroundColor Green
Write-Host "You can now right-click any image in Windows Explorer!" -ForegroundColor Yellow
