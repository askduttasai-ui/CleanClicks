<div align="center">

# 🤖 CleanClicks
### Your PC's Best Friend — Free Forever

![Version](https://img.shields.io/badge/version-3.3-orange?style=flat-square)
![Platform](https://img.shields.io/badge/platform-Windows-blue?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![Publisher](https://img.shields.io/badge/publisher-AK%20CleanClicks-orange?style=flat-square)
![Price](https://img.shields.io/badge/price-FREE-brightgreen?style=flat-square)

**More powerful than CCleaner Professional — completely free, no ads, no telemetry.**

[⬇️ Download Latest Release](#installation) · [🐛 Report Bug](../../issues) · [💡 Request Feature](../../issues)

</div>

---

## 🤖 Meet BoBo

BoBo is CleanClicks' friendly robot mascot. He walks around your screen in the background, vacuuming up digital dust and trash — then says **"Done with cleaning!"** when finished. Runs on a loop so your PC always looks (and feels) fresh.

---

## ✨ Features

| Feature | CleanClicks | CCleaner Free | Glary Free |
|---|---|---|---|
| Temp & Cache Cleaner | ✅ | ✅ | ✅ |
| Duplicate File Finder | ✅ | ❌ | ✅ |
| Startup Manager | ✅ | ✅ | ✅ |
| Large File Finder | ✅ | ❌ | ✅ |
| Privacy Cleaner | ✅ | ✅ | ✅ |
| **RAM Optimizer** | ✅ New v3.3 | ❌ paid | ✅ |
| **Auto-Clean every 5 min** | ✅ | ❌ paid | ❌ |
| **PC Health Score A–F** | ✅ | ❌ | ❌ |
| **Disk Space Trend Chart** | ✅ | ❌ | ❌ |
| **Runs as Windows Service** | ✅ | ❌ | ❌ |
| **Secure File Shredder** | ✅ | ❌ paid | ✅ |
| **Registry Cleaner** | ✅ | ✅ | ✅ |
| **Live CPU/RAM Monitor** | ✅ | ✅ | ✅ |
| **Zero ads / telemetry** | ✅ | ❌ | ❌ |
| **Standalone EXE** | ✅ | ✅ | ✅ |

---

## 🚀 Installation

### Option A — Installer (Recommended)
1. Download `CleanClicks_Setup.exe` from [Releases](../../releases)
2. Double-click it
3. Click **Next → I Agree → Install → Finish**
4. Check **"Launch CleanClicks now"** — browser opens automatically ✅

> **Windows SmartScreen warning?** Click **"More info"** → **"Run anyway"**
> This is safe — CleanClicks is open source and contains no malware.

### Option B — Portable (No Install)
1. Download `CleanClicks.exe` from [Releases](../../releases)
2. Double-click it
3. Browser opens automatically at http://localhost:5050 ✅

---

## 🔐 Security

CleanClicks is built with security at its core:

- 🔒 **Localhost-only API** — blocks ALL external requests (HTTP 403)
- 🛡 **Security headers** — XSS, clickjacking, MIME sniffing protection
- 🔑 **Session tokens** — 256-bit random token, fresh every startup
- 🔍 **File integrity check** — SHA-256 hash, warns if tampered
- 🚫 **Zero internet connections** — no telemetry, no analytics, no cloud
- 📖 **Fully open source** — every line of code is auditable

See [SECURITY.md](SECURITY.md) for full details.

---

## 🏗 Build From Source

### Requirements
- Windows 10/11
- Python 3.11
- pip

### Steps
```bash
# Clone the repository
git clone https://github.com/askduttasai-ui/CleanClicks.git
cd CleanClicks

# Install dependencies
pip install flask flask-cors waitress pywin32 psutil

# Run directly
python cleaner_backend.py

# Open in browser
start http://localhost:5050
```

### Build the EXE
```bash
# Build EXE (auto-detects Python 3.11)
build_exe.bat

# Build installer
build_installer.bat
```

---

## 📁 Project Structure

```
CleanClicks/
├── cleanclicks.html          # Frontend UI (10 tabs)
├── cleaner_backend.py        # Flask API backend
├── cleanclicks_launcher.py   # EXE launcher
├── cleanclicks_service.py    # Windows Service wrapper
├── build_exe.bat             # Builds CleanClicks.exe
├── build_installer.bat       # Builds CleanClicks_Setup.exe
├── CleanClicks_Installer.nsi # NSIS installer script
├── create_icon.py            # Generates app icon
├── create_banner.py          # Generates installer banner
├── install.bat               # One-click service installer
├── uninstall.bat             # Clean removal
├── service_manager.bat       # Start/Stop/Restart service
├── LICENSE.txt               # MIT License
├── SECURITY.md               # Security documentation
└── README.md                 # This file
```

---

## 🛣 Roadmap

- [x] Temp & Cache Cleaner
- [x] Duplicate Finder
- [x] Startup Manager
- [x] Large File Finder
- [x] Privacy Cleaner
- [x] Auto-Clean (Windows Service)
- [x] PC Health Score
- [x] Disk Trend Chart
- [x] Secure File Shredder (DoD/Gutmann)
- [x] Registry Cleaner
- [x] Live System Monitor
- [x] RAM Optimizer ✅ New in v3.3
- [x] BoBo robot mascot animation
- [x] Security hardening (7 layers)
- [ ] RAM high usage notifications
- [ ] Auto-updater
- [ ] Code signing certificate (SignPath Foundation)
- [ ] CleanClicks Mobile (Android)

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE.txt](LICENSE.txt) for details.

© 2026 AK CleanClicks — Free forever.

---

## 💬 Support

- 🐛 **Bug reports:** [Open an issue](../../issues)
- 💡 **Feature requests:** [Open an issue](../../issues)
- 🌐 **Website:** [cleanclicks.netlify.app](https://cleanclicks.netlify.app)

<div align="center">

**If CleanClicks helped you, please ⭐ star this repository!**

Made with ❤️ by AK CleanClicks

</div>
