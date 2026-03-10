; ============================================================
;  CleanClicks v3.0 — Professional Windows Installer
;  Built with NSIS (Nullsoft Scriptable Install System)
;  Same technology used by VLC, 7-Zip, WinRAR
; ============================================================

!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "FileFunc.nsh"

; ── App Info ─────────────────────────────────────────────────
!define APPNAME        "CleanClicks"
!define VERSION        "3.0"
!define PUBLISHER      "AK CleanClicks"
!define DESCRIPTION    "Your PC's Best Friend — Free PC Cleaner"
!define WEBSITE        "https://github.com/cleanclicks"
!define INSTALLDIR     "$PROGRAMFILES\CleanClicks"
!define UNINSTKEY      "Software\Microsoft\Windows\CurrentVersion\Uninstall\CleanClicks"
!define REGKEY         "Software\CleanClicks"
!define MAINEXE        "CleanClicks.exe"
!define LAUNCHEXE      "CleanClicks.exe"

; ── Installer Settings ───────────────────────────────────────
Name              "${APPNAME} ${VERSION}"
OutFile           "CleanClicks_Setup.exe"
InstallDir        "${INSTALLDIR}"
InstallDirRegKey  HKLM "${REGKEY}" "InstallDir"
RequestExecutionLevel admin
SetCompressor     /SOLID lzma
CRCCheck          on
ShowInstDetails   show
ShowUninstDetails show

; ── Modern UI Settings ───────────────────────────────────────
!define MUI_ABORTWARNING
!define MUI_ICON                    "cleanclicks.ico"
!define MUI_UNICON                  "cleanclicks.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "installer_banner.bmp"

; Header colors (blue theme)
!define MUI_HEADERIMAGE
!define MUI_BGCOLOR                 "FFFFFF"
!define MUI_HEADER_TRANSPARENT_TEXT ""

; Welcome page
!define MUI_WELCOMEPAGE_TITLE       "Welcome to CleanClicks ${VERSION}"
!define MUI_WELCOMEPAGE_TEXT        "CleanClicks is your PC's best friend.$\r$\n$\r$\nIt automatically cleans temp files, finds duplicates, shreds sensitive files, monitors your system, and keeps your PC running fast.$\r$\n$\r$\nThis wizard will install CleanClicks ${VERSION} on your computer.$\r$\n$\r$\nClick Next to continue."

; Finish page
!define MUI_FINISHPAGE_TITLE        "CleanClicks is Ready!"
!define MUI_FINISHPAGE_TEXT         "CleanClicks has been installed successfully.$\r$\n$\r$\nClick Finish to launch CleanClicks now."
!define MUI_FINISHPAGE_RUN          "$INSTDIR\${LAUNCHEXE}"
!define MUI_FINISHPAGE_RUN_TEXT     "Launch CleanClicks now"
!define MUI_FINISHPAGE_LINK         "Visit CleanClicks website"
!define MUI_FINISHPAGE_LINK_LOCATION "${WEBSITE}"

; ── Pages ────────────────────────────────────────────────────
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE        "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; ── Language ─────────────────────────────────────────────────
!insertmacro MUI_LANGUAGE "English"

; ── Version Info (shows in file properties) ──────────────────
VIProductVersion                    "3.0.0.0"
VIAddVersionKey "ProductName"       "${APPNAME}"
VIAddVersionKey "ProductVersion"    "${VERSION}"
VIAddVersionKey "CompanyName"       "AK CleanClicks"
VIAddVersionKey "FileDescription"   "${DESCRIPTION}"
VIAddVersionKey "FileVersion"       "${VERSION}"
VIAddVersionKey "LegalCopyright"    "© 2025 AK CleanClicks"

; ============================================================
;  INSTALL SECTION
; ============================================================
Section "CleanClicks" SecMain

    SectionIn RO   ; Required — can't be deselected

    SetOutPath "$INSTDIR"
    SetOverwrite on

    ; ── Copy all application files ────────────────────────────
    File "dist\CleanClicks.exe"
    File "cleanclicks.html"
    File "cleaner_backend.py"
    File "cleanclicks_launcher.py"
    File "cleanclicks_service.py"
    File "README.txt"

    ; ── Write registry entries ────────────────────────────────
    WriteRegStr   HKLM "${REGKEY}" "InstallDir"    "$INSTDIR"
    WriteRegStr   HKLM "${REGKEY}" "Version"       "${VERSION}"

    ; ── Add to Windows Programs & Features (Add/Remove) ──────
    WriteRegStr   HKLM "${UNINSTKEY}" "DisplayName"          "${APPNAME}"
    WriteRegStr   HKLM "${UNINSTKEY}" "DisplayVersion"       "${VERSION}"
    WriteRegStr   HKLM "${UNINSTKEY}" "Publisher"            "${PUBLISHER}"
    WriteRegStr   HKLM "${UNINSTKEY}" "DisplayIcon"          "$INSTDIR\${MAINEXE}"
    WriteRegStr   HKLM "${UNINSTKEY}" "InstallLocation"      "$INSTDIR"
    WriteRegStr   HKLM "${UNINSTKEY}" "UninstallString"      "$INSTDIR\Uninstall.exe"
    WriteRegStr   HKLM "${UNINSTKEY}" "HelpLink"             "${WEBSITE}"
    WriteRegStr   HKLM "${UNINSTKEY}" "URLInfoAbout"         "${WEBSITE}"
    WriteRegDWORD HKLM "${UNINSTKEY}" "NoModify"             1
    WriteRegDWORD HKLM "${UNINSTKEY}" "NoRepair"             1

    ; Estimated size (fixed 50MB)
    WriteRegDWORD HKLM "${UNINSTKEY}" "EstimatedSize" 51200

    ; ── Create Desktop Shortcut ───────────────────────────────
    CreateShortcut "$DESKTOP\CleanClicks.lnk" \
                   "$INSTDIR\${MAINEXE}" "" \
                   "$INSTDIR\${MAINEXE}" 0 \
                   SW_SHOWNORMAL "" \
                   "${DESCRIPTION}"

    ; ── Create Start Menu Shortcut ────────────────────────────
    CreateDirectory "$SMPROGRAMS\CleanClicks"
    CreateShortcut  "$SMPROGRAMS\CleanClicks\CleanClicks.lnk" \
                    "$INSTDIR\${MAINEXE}" "" \
                    "$INSTDIR\${MAINEXE}" 0
    CreateShortcut  "$SMPROGRAMS\CleanClicks\Uninstall CleanClicks.lnk" \
                    "$INSTDIR\Uninstall.exe"

    ; ── Write uninstaller ─────────────────────────────────────
    WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd

; ── Optional: Add to Windows Startup (auto-start with Windows) ──
Section /o "Start with Windows" SecStartup
    WriteRegStr HKCU \
        "Software\Microsoft\Windows\CurrentVersion\Run" \
        "CleanClicks" \
        "$INSTDIR\${MAINEXE}"
SectionEnd

; ============================================================
;  UNINSTALL SECTION
; ============================================================
Section "Uninstall"

    ; Stop the process if running
    ExecWait 'taskkill /f /im ${MAINEXE}' $0

    ; Remove files
    Delete "$INSTDIR\CleanClicks.exe"
    Delete "$INSTDIR\cleanclicks.html"
    Delete "$INSTDIR\cleaner_backend.py"
    Delete "$INSTDIR\cleanclicks_launcher.py"
    Delete "$INSTDIR\cleanclicks_service.py"
    Delete "$INSTDIR\README.txt"
    Delete "$INSTDIR\cleanclicks_history.json"
    Delete "$INSTDIR\cleanclicks_disk_trend.json"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir  "$INSTDIR"

    ; Remove shortcuts
    Delete "$DESKTOP\CleanClicks.lnk"
    Delete "$SMPROGRAMS\CleanClicks\CleanClicks.lnk"
    Delete "$SMPROGRAMS\CleanClicks\Uninstall CleanClicks.lnk"
    RMDir  "$SMPROGRAMS\CleanClicks"

    ; Remove startup entry
    DeleteRegValue HKCU \
        "Software\Microsoft\Windows\CurrentVersion\Run" \
        "CleanClicks"

    ; Remove registry entries
    DeleteRegKey HKLM "${UNINSTKEY}"
    DeleteRegKey HKLM "${REGKEY}"

    MessageBox MB_ICONINFORMATION "CleanClicks has been uninstalled successfully.$\r$\nThank you for using CleanClicks!"

SectionEnd
