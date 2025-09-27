; ----------------------------------------------------------------------------
; Script Inno Setup para instalar o Monitor de Impressão
; ----------------------------------------------------------------------------

#define AppName "Monitor de Impressão"
#define AppVersion "1.0"
#define AppPublisher "SeuNome ou Empresa"
#define AppExeName "monitor_impressao.exe"
#define AppIconFile "icone.ico"  ; se você tiver um ícone opcional
#define ConfigIniFile "config.ini"

[Setup]
; Identificação única (gere um GUID novo usando o Inno Setup IDE)
AppId={{01234567-89AB-CDEF-0123-456789ABCDEF}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
UninstallDisplayIcon={app}\{#AppExeName}
OutputDir=installer_output
OutputBaseFilename=MonitorImpressaoSetup
Compression=lzma
SolidCompression=yes
; Se você não quiser que o instalador peça privilégios elevados, pode usar:
; PrivilegesRequired=lowest

[Languages]
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"

[Files]
; Copiar o executável
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Copiar o arquivo config.ini (se existir)
Source: "{#ConfigIniFile}"; DestDir: "{app}"; Flags: ignoreversion
; Se houver outros arquivos necessários, copie aqui:
; Source: "outra_pasta\*.dll"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\Desinstalar {#AppName}"; Filename: "{uninstallexe}"

[Run]
; Executar após instalação (opcional)
Filename: "{app}\{#AppExeName}"; Description: "Executar {#AppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Se quiser deletar configs ou outros arquivos extras no desinstalar
Type: files; Name: "{app}\{#ConfigIniFile}"


#instalar o Inno Setup : https://jrsoftware.org/isinfo.php