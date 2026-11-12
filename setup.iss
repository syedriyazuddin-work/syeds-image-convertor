#define MyAppName "Syed's Image Convertor"
#define MyAppPublisher "Syed Riyazuddin"
#define MyAppVersion "1.0.0"
#define MyAppExeName "ImageConverter.exe"
#define MyCliExeName "quick_convert.exe"

[Setup]
AppId={{C78F590A-5A77-448F-B285-84639908F87C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=C:\Users\Riyaz\.gemini\antigravity\scratch\anywebp-local\output
OutputBaseFilename=Syeds-Image-Convertor-Setup
SetupIconFile=C:\Users\Riyaz\.gemini\antigravity\scratch\anywebp-local\app_icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "contextmenu"; Description: "Add 'Syed''s Image Convertor' to Windows Explorer Right-Click Menu"; GroupDescription: "Explorer Integration:"; Flags: checkedonce

[Files]
Source: "C:\Users\anilM\AppData\Local\Programs\antigravity\dist\ImageConverter\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\Riyaz\.gemini\antigravity\scratch\anywebp-local\app_icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Riyaz\.gemini\antigravity\scratch\anywebp-local\app_icon.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Riyaz\.gemini\antigravity\scratch\anywebp-local\install_context_menu.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Riyaz\.gemini\antigravity\scratch\anywebp-local\uninstall_context_menu.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Riyaz\.gemini\antigravity\scratch\anywebp-local\install_context_menu.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Riyaz\.gemini\antigravity\scratch\anywebp-local\uninstall_context_menu.bat"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app_icon.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app_icon.ico"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Windows\SendTo\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app_icon.ico"

[Registry]
; Clean up previous keys on install
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\image\shell\AnyWebP"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\*\shell\AnyWebP"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\image\shell\ImageConverter"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\*\shell\ImageConverter"; Flags: uninsdeletekey; Tasks: contextmenu

; Context Menu under SystemFileAssociations\image\shell\SyedsImageConvertor
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\image\shell\SyedsImageConvertor"; ValueType: string; ValueName: "MUIVerb"; ValueData: "Syed's Image Convertor"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\image\shell\SyedsImageConvertor"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\app_icon.ico"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\image\shell\SyedsImageConvertor"; ValueType: string; ValueName: "SubCommands"; ValueData: ""; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\image\shell\SyedsImageConvertor"; ValueType: string; ValueName: "AppliesTo"; ValueData: "System.FileName:"".png"" OR System.FileName:"".jpg"" OR System.FileName:"".jpeg"" OR System.FileName:"".webp"" OR System.FileName:"".bmp"" OR System.FileName:"".gif"" OR System.FileName:"".tiff"" OR System.FileName:"".tif"" OR System.FileName:"".avif"" OR System.FileName:"".heic"" OR System.FileName:"".heif"" OR System.FileName:"".ico"" OR System.FileName:"".jfif"""; Flags: uninsdeletekey; Tasks: contextmenu

; Subcommand 1: WebP
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\image\shell\SyedsImageConvertor\shell\01_webp"; ValueType: string; ValueName: "MUIVerb"; ValueData: "Convert to WebP (Instant)"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\image\shell\SyedsImageConvertor\shell\01_webp"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\app_icon.ico"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\image\shell\SyedsImageConvertor\shell\01_webp\command"; ValueType: string; ValueData: """{app}\{#MyCliExeName}"" webp ""%1"""; Flags: uninsdeletekey; Tasks: contextmenu

; Subcommand 2: PNG
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\image\shell\SyedsImageConvertor\shell\02_png"; ValueType: string; ValueName: "MUIVerb"; ValueData: "Convert to PNG (Instant)"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\image\shell\SyedsImageConvertor\shell\02_png\command"; ValueType: string; ValueData: """{app}\{#MyCliExeName}"" png ""%1"""; Flags: uninsdeletekey; Tasks: contextmenu

; Subcommand 3: JPG
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\image\shell\SyedsImageConvertor\shell\03_jpg"; ValueType: string; ValueName: "MUIVerb"; ValueData: "Convert to JPG (Instant)"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\image\shell\SyedsImageConvertor\shell\03_jpg\command"; ValueType: string; ValueData: """{app}\{#MyCliExeName}"" jpg ""%1"""; Flags: uninsdeletekey; Tasks: contextmenu

; Subcommand 4: AVIF
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\image\shell\SyedsImageConvertor\shell\04_avif"; ValueType: string; ValueName: "MUIVerb"; ValueData: "Convert to AVIF (Instant)"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\image\shell\SyedsImageConvertor\shell\04_avif\command"; ValueType: string; ValueData: """{app}\{#MyCliExeName}"" avif ""%1"""; Flags: uninsdeletekey; Tasks: contextmenu

; Subcommand 5: GUI
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\image\shell\SyedsImageConvertor\shell\05_gui"; ValueType: string; ValueName: "MUIVerb"; ValueData: "Customize & Convert (GUI)..."; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\image\shell\SyedsImageConvertor\shell\05_gui"; ValueType: string; ValueName: "Icon"; ValueData: "imageres.dll,114"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\image\shell\SyedsImageConvertor\shell\05_gui\command"; ValueType: string; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Flags: uninsdeletekey; Tasks: contextmenu

; Context Menu under *\shell\SyedsImageConvertor with AppliesTo
Root: HKCU; Subkey: "Software\Classes\*\shell\SyedsImageConvertor"; ValueType: string; ValueName: "MUIVerb"; ValueData: "Syed's Image Convertor"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\*\shell\SyedsImageConvertor"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\app_icon.ico"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\*\shell\SyedsImageConvertor"; ValueType: string; ValueName: "SubCommands"; ValueData: ""; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\*\shell\SyedsImageConvertor"; ValueType: string; ValueName: "AppliesTo"; ValueData: "System.FileName:"".png"" OR System.FileName:"".jpg"" OR System.FileName:"".jpeg"" OR System.FileName:"".webp"" OR System.FileName:"".bmp"" OR System.FileName:"".gif"" OR System.FileName:"".tiff"" OR System.FileName:"".tif"" OR System.FileName:"".avif"" OR System.FileName:"".heic"" OR System.FileName:"".heif"" OR System.FileName:"".ico"" OR System.FileName:"".jfif"""; Flags: uninsdeletekey; Tasks: contextmenu

; Subcommand 1: WebP
Root: HKCU; Subkey: "Software\Classes\*\shell\SyedsImageConvertor\shell\01_webp"; ValueType: string; ValueName: "MUIVerb"; ValueData: "Convert to WebP (Instant)"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\*\shell\SyedsImageConvertor\shell\01_webp"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\app_icon.ico"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\*\shell\SyedsImageConvertor\shell\01_webp\command"; ValueType: string; ValueData: """{app}\{#MyCliExeName}"" webp ""%1"""; Flags: uninsdeletekey; Tasks: contextmenu

; Subcommand 2: PNG
Root: HKCU; Subkey: "Software\Classes\*\shell\SyedsImageConvertor\shell\02_png"; ValueType: string; ValueName: "MUIVerb"; ValueData: "Convert to PNG (Instant)"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\*\shell\SyedsImageConvertor\shell\02_png\command"; ValueType: string; ValueData: """{app}\{#MyCliExeName}"" png ""%1"""; Flags: uninsdeletekey; Tasks: contextmenu

; Subcommand 3: JPG
Root: HKCU; Subkey: "Software\Classes\*\shell\SyedsImageConvertor\shell\03_jpg"; ValueType: string; ValueName: "MUIVerb"; ValueData: "Convert to JPG (Instant)"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\*\shell\SyedsImageConvertor\shell\03_jpg\command"; ValueType: string; ValueData: """{app}\{#MyCliExeName}"" jpg ""%1"""; Flags: uninsdeletekey; Tasks: contextmenu

; Subcommand 4: AVIF
Root: HKCU; Subkey: "Software\Classes\*\shell\SyedsImageConvertor\shell\04_avif"; ValueType: string; ValueName: "MUIVerb"; ValueData: "Convert to AVIF (Instant)"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\*\shell\SyedsImageConvertor\shell\04_avif\command"; ValueType: string; ValueData: """{app}\{#MyCliExeName}"" avif ""%1"""; Flags: uninsdeletekey; Tasks: contextmenu

; Subcommand 5: GUI
Root: HKCU; Subkey: "Software\Classes\*\shell\SyedsImageConvertor\shell\05_gui"; ValueType: string; ValueName: "MUIVerb"; ValueData: "Customize & Convert (GUI)..."; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\*\shell\SyedsImageConvertor\shell\05_gui"; ValueType: string; ValueName: "Icon"; ValueData: "imageres.dll,114"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKCU; Subkey: "Software\Classes\*\shell\SyedsImageConvertor\shell\05_gui\command"; ValueType: string; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Flags: uninsdeletekey; Tasks: contextmenu

; Ensure PerceivedType is registered
Root: HKCU; Subkey: "Software\Classes\.avif"; ValueType: string; ValueName: "PerceivedType"; ValueData: "image"; Flags: createvalueifdoesntexist
Root: HKCU; Subkey: "Software\Classes\.heic"; ValueType: string; ValueName: "PerceivedType"; ValueData: "image"; Flags: createvalueifdoesntexist
Root: HKCU; Subkey: "Software\Classes\.webp"; ValueType: string; ValueName: "PerceivedType"; ValueData: "image"; Flags: createvalueifdoesntexist

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
