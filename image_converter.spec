# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_all

block_cipher = None

datas = []
binaries = []
hiddenimports = [
    'PIL',
    'PIL.Image',
    'PIL.ImageOps',
    'PIL.ImageSequence',
    'PIL.WebPImagePlugin',
    'PIL.PngImagePlugin',
    'PIL.JpegImagePlugin',
    'PIL.BmpImagePlugin',
    'PIL.GifImagePlugin',
    'PIL.IcoImagePlugin',
    'PIL.TiffImagePlugin',
    'PIL.PdfImagePlugin',
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'converter',
    'toast',
]

for pkg in ['pillow_heif', 'pillow_avif', 'tkinterdnd2']:
    try:
        d, b, h = collect_all(pkg)
        datas += d
        binaries += b
        hiddenimports += h
    except Exception as e:
        print(f"Hook warning for {pkg}: {e}")

# Include app icons in data
datas.append(('app_icon.ico', '.'))
datas.append(('app_icon.png', '.'))

a_gui = Analysis(
    ['gui.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'numpy', 'pandas', 'IPython', 'pytest'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

a_cli = Analysis(
    ['quick_convert.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'numpy', 'pandas', 'IPython', 'pytest'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz_gui = PYZ(a_gui.pure, a_gui.zipped_data, cipher=block_cipher)
pyz_cli = PYZ(a_cli.pure, a_cli.zipped_data, cipher=block_cipher)

exe_gui = EXE(
    pyz_gui,
    a_gui.scripts,
    [],
    exclude_binaries=True,
    name='ImageConverter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico'
)

exe_cli = EXE(
    pyz_cli,
    a_cli.scripts,
    [],
    exclude_binaries=True,
    name='quick_convert',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico'
)

coll = COLLECT(
    exe_gui,
    a_gui.binaries,
    a_gui.zipfiles,
    a_gui.datas,
    exe_cli,
    a_cli.binaries,
    a_cli.zipfiles,
    a_cli.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ImageConverter'
)
