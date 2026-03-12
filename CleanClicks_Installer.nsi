; ============================================================
;  CleanClicks Professional Installer
;  Built with NSIS — https://nsis.sourceforge.io
;  Publisher: AK CleanClicks  |  Version: 3.3
;  Port: 5050
; ============================================================

!include "MUI2.nsh"
!include "FileFunc.nsh"

; ── Basic Info ──────────────────────────────────────────────
Name              "CleanClicks"
OutFile           "CleanClicks_Setup.exe"
InstallDir        "$PROGRAMFILES\CleanClicks"
InstallDirRegKey  HKLM "Software\CleanClicks" "Install_Dir"
RequestExecutionLevel admin
Unicode True

; ── Version Info (shows in EXE properties) ──────────────────
VIProductVersion  "3.3.0.0"
VIAddVersionKey   "ProductName"      "CleanClicks"
VIAddVersionKey   "CompanyName"      "AK CleanClicks"
VIAddVersionKey   "LegalCopyright"   "Copyright 2025 AK CleanClicks"
VIAddVersionKey   "FileDescription"  "CleanClicks PC Cleaner Setup"
VIAddVersionKey   "FileVersion"      "3.3.0.0"
VIAddVersionKey   "ProductVersion"   "3.3.0.0"

; ── Constants ───────────────────────────────────────────────
!define APPNAME    "CleanClicks"
!define APPVERSION "3.3"
!define PUBLISHER  "AK CleanClicks"
!define WEBSITE    "https://cleanclicks.netlify.app"
!define UNINSTKEY  "Software\Microsoft\Windows\CurrentVersion\Uninstall\CleanClicks"
!define REGKEY     "Software\CleanClicks"

; ── MUI Settings ────────────────────────────────────────────
!define MUI_ABORTWARNING

; App icon used in installer window title bar + Control Panel
!define MUI_ICON   "cleanclicks.ico"
!define MUI_UNICON "cleanclicks.ico"

; Welcome page
!define MUI_WELCOMEPAGE_TITLE "Welcome to CleanClicks v3.3"
!define MUI_WELCOMEPAGE_TEXT  "CleanClicks is your free, powerful PC cleaner.$\r$\n$\r$\nFeatures include:$\r$\n  • Temp & Cache Cleaner$\r$\n  • Duplicate File Finder$\r$\n  • Startup Manager$\r$\n  • Large File Finder$\r$\n  • Privacy Cleaner$\r$\n  • Auto-Clean Scheduler$\r$\n  • Secure File Shredder$\r$\n  • Registry Cleaner$\r$\n  • Live System Monitor$\r$\n  • RAM Optimizer$\r$\n$\r$\nClick Next to continue."

; ── Finish page with LAUNCH CHECKBOX ────────────────────────
!define MUI_FINISHPAGE_TITLE            "CleanClicks Installed Successfully!"
!define MUI_FINISHPAGE_TEXT             "CleanClicks v3.3 has been installed.$\r$\n$\r$\nClick Finish to complete setup."
!define MUI_FINISHPAGE_RUN              "$INSTDIR\CleanClicks.exe"
!define MUI_FINISHPAGE_RUN_TEXT         "Launch CleanClicks now"
!define MUI_FINISHPAGE_RUN_CHECKED                          ; ticked by default ✅
!define MUI_FINISHPAGE_LINK             "Visit CleanClicks Website"
!define MUI_FINISHPAGE_LINK_LOCATION    "${WEBSITE}"

; ── Pages ────────────────────────────────────────────────────
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE    "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

; ============================================================
;  INSTALL SECTION
; ============================================================
Section "CleanClicks" SecMain

  SectionIn RO   ; Cannot be deselected

  SetOutPath "$INSTDIR"

  ; ── Copy application files ────────────────────────────────
  File "dist\CleanClicks.exe"
  File "cleanclicks.html"
  File "cleaner_backend.py"
  File "cleanclicks_service.py"
  File "cleanclicks_launcher.py"
  File /nonfatal "README.txt"
  File /nonfatal "LICENSE.txt"

  ; ── Copy icon (required for Control Panel) ────────────────
  ; If icon missing, create a blank placeholder so installer doesn't fail
  File /nonfatal "cleanclicks.ico"

  ; ── Write uninstall registry entry ───────────────────────
  WriteRegStr   HKLM "${UNINSTKEY}" "DisplayName"          "${APPNAME}"
  WriteRegStr   HKLM "${UNINSTKEY}" "DisplayVersion"       "${APPVERSION}"
  WriteRegStr   HKLM "${UNINSTKEY}" "Publisher"            "${PUBLISHER}"
  WriteRegStr   HKLM "${UNINSTKEY}" "URLInfoAbout"         "${WEBSITE}"
  WriteRegStr   HKLM "${UNINSTKEY}" "HelpLink"             "${WEBSITE}"
  WriteRegStr   HKLM "${UNINSTKEY}" "UninstallString"      '"$INSTDIR\Uninstall.exe"'
  WriteRegStr   HKLM "${UNINSTKEY}" "QuietUninstallString" '"$INSTDIR\Uninstall.exe" /S'
  WriteRegStr   HKLM "${UNINSTKEY}" "InstallLocation"      "$INSTDIR"
  WriteRegDWORD HKLM "${UNINSTKEY}" "NoModify"             1
  WriteRegDWORD HKLM "${UNINSTKEY}" "NoRepair"             1

  ; ── THIS IS WHAT MAKES THE ICON SHOW IN CONTROL PANEL ────
  WriteRegStr   HKLM "${UNINSTKEY}" "DisplayIcon"  "$INSTDIR\cleanclicks.ico"

  ; ── Estimated install size (KB) ──────────────────────────
  WriteRegDWORD HKLM "${UNINSTKEY}" "EstimatedSize" 51200

  ; ── App install location registry ────────────────────────
  WriteRegStr HKLM "${REGKEY}" "Install_Dir" "$INSTDIR"
  WriteRegStr HKLM "${REGKEY}" "Version"     "${APPVERSION}"

  ; ── Desktop shortcut ─────────────────────────────────────
  CreateShortcut "$DESKTOP\CleanClicks.lnk" \
    "$INSTDIR\CleanClicks.exe" "" \
    "$INSTDIR\cleanclicks.ico" 0 \
    SW_SHOWNORMAL "" \
    "CleanClicks PC Cleaner"

  ; ── Start Menu shortcuts ──────────────────────────────────
  CreateDirectory "$SMPROGRAMS\CleanClicks"
  CreateShortcut  "$SMPROGRAMS\CleanClicks\CleanClicks.lnk" \
    "$INSTDIR\CleanClicks.exe" "" "$INSTDIR\cleanclicks.ico" 0
  CreateShortcut  "$SMPROGRAMS\CleanClicks\Uninstall CleanClicks.lnk" \
    "$INSTDIR\Uninstall.exe"

  ; ── Write uninstaller EXE ────────────────────────────────
  WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd

; ============================================================
;  UNINSTALL SECTION
; ============================================================
Section "Uninstall"

  ; ── Stop service if running ───────────────────────────────
  ExecWait 'net stop CleanClicksService'
  ExecWait 'taskkill /f /im CleanClicks.exe'

  ; ── Delete application files ──────────────────────────────
  Delete "$INSTDIR\CleanClicks.exe"
  Delete "$INSTDIR\cleanclicks.html"
  Delete "$INSTDIR\cleaner_backend.py"
  Delete "$INSTDIR\cleanclicks_service.py"
  Delete "$INSTDIR\cleanclicks_launcher.py"
  Delete "$INSTDIR\cleanclicks.ico"
  Delete "$INSTDIR\README.txt"
  Delete "$INSTDIR\LICENSE.txt"
  Delete "$INSTDIR\Uninstall.exe"

  ; ── Delete data/log files ─────────────────────────────────
  Delete "$INSTDIR\cleanclicks_history.json"
  Delete "$INSTDIR\cleanclicks_disk_trend.json"
  Delete "$INSTDIR\cleanclicks_autoclean.log"
  Delete "$INSTDIR\cleanclicks_integrity.sha256"
  Delete "$INSTDIR\cleanclicks_service.log"

  ; ── Remove install folder ─────────────────────────────────
  RMDir  "$INSTDIR"

  ; ── Remove shortcuts ──────────────────────────────────────
  Delete "$DESKTOP\CleanClicks.lnk"
  Delete "$SMPROGRAMS\CleanClicks\CleanClicks.lnk"
  Delete "$SMPROGRAMS\CleanClicks\Uninstall CleanClicks.lnk"
  RMDir  "$SMPROGRAMS\CleanClicks"

  ; ── Remove registry ───────────────────────────────────────
  DeleteRegKey HKLM "${UNINSTKEY}"
  DeleteRegKey HKLM "${REGKEY}"

SectionEnd
