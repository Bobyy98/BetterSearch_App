[Setup]
AppName=Better Search
AppVersion=1.0
DefaultDirName={pf}\Better Search
DefaultGroupName=Better Search
OutputDir=installer
OutputBaseFilename=BetterSearchInstaller
Compression=lzma
SolidCompression=yes
SetupIconFile=dist\main\_internal\assets\your_icon.ico
DisableDirPage=no
DisableProgramGroupPage=no

[Files]
Source: "dist\main\BetterSearchApp.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\_internal\*"; DestDir: "{app}\_internal"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Better Search"; Filename: "{app}\BetterSearchApp.exe"
Name: "{commondesktop}\Better Search"; Filename: "{app}\BetterSearchApp.exe"; Tasks: desktopicon
Name: "{group}\Uninstall Better Search"; Filename: "{uninstallexe}"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional icons:"
