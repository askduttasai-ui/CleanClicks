# 🔐 CleanClicks v3.1 — Security Guide

## Protection Against Hackers

CleanClicks runs 100% locally on your PC.
Here is every security measure built in:

---

## 🛡 What's Protected

### 1. Localhost-Only API
The backend ONLY accepts requests from your own PC.
Any request from an external IP is blocked with HTTP 403.
→ Hackers on the internet CANNOT reach your CleanClicks API.

### 2. Security Headers (every response)
| Header | What it prevents |
|---|---|
| X-Frame-Options: DENY | Clickjacking attacks |
| X-Content-Type-Options: nosniff | MIME sniffing / drive-by downloads |
| Content-Security-Policy | XSS (Cross-Site Scripting) |
| Referrer-Policy: strict-origin | Data leakage via referrer |
| Permissions-Policy | Camera/mic/location abuse |
| Access-Control-Allow-Origin | Unauthorized cross-origin requests |

### 3. CORS Locked to Localhost
Only these origins can call the API:
- http://localhost:5050
- http://127.0.0.1:5050
All other origins are blocked.

### 4. File Integrity Check
On every startup, CleanClicks computes a SHA-256 hash of its own
backend file and compares it to the stored hash.
If someone modified cleaner_backend.py (e.g. injected malware),
CleanClicks will warn you immediately on startup.

### 5. Session Token
The frontend gets a random 256-bit secret token on load.
This token must match for all API calls.
Regenerated fresh every time CleanClicks starts.

### 6. No Internet Connections
CleanClicks makes ZERO outbound internet connections.
No telemetry, no analytics, no update checks, no cloud sync.
Everything stays 100% on your PC.

### 7. No Data Storage of Personal Files
CleanClicks never reads the CONTENT of your files.
It only reads file paths, sizes, and dates.
Your documents, photos, and data are never accessed.

---

## 🔍 For Open Source Verification

CleanClicks is open source. You can verify every line of code:
- cleaner_backend.py   — The complete Python backend
- cleanclicks.html     — The complete frontend
- No obfuscation, no minification, no hidden code

Anyone can audit, verify, and trust CleanClicks.

---

## 📋 Security Checklist for Distribution

Before sharing CleanClicks_Setup.exe:
- [ ] Run build_exe.bat to build fresh EXE
- [ ] Run build_installer.bat to wrap in installer
- [ ] Check cleanclicks_integrity.sha256 matches your build
- [ ] Apply for SignPath Foundation certificate (free, see README)
- [ ] Upload source to GitHub for public audit

---

CleanClicks v3.1 — Secure, Free, Open Source
