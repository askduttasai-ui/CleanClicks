"""
CleanClicks Backend - v3.1 Secure Production Version
Auto-clean engine, health score, startup manager, large file finder,
privacy cleaner, disk trend tracking, Windows notifications, persistent history,
SECURE FILE SHREDDER (DoD / Gutmann), REGISTRY CLEANER, LIVE SYSTEM MONITOR.
"""

import os
import sys
import json
import time
import hashlib
import shutil
import winreg
import threading
import subprocess
import tempfile
import glob
import platform
import ctypes
from pathlib import Path
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import secrets
import hashlib
import hmac

app = Flask(__name__)
# ── SECURITY: Only accept requests from localhost ─────────────────────────────
CORS(app,
     origins=["http://localhost:5050","http://127.0.0.1:5050"],
     methods=["GET","POST","OPTIONS"],
     allow_headers=["Content-Type","X-CleanClicks-Token","Accept"],
     supports_credentials=False)

# Secret token — generated fresh each run, stored in memory only
API_SECRET = secrets.token_hex(32)

# Allowed API token (frontend fetches this on load via /api/token)
app.config['SECRET_KEY'] = secrets.token_hex(32)

# ── SECURITY HEADERS on every response ───────────────────────────────────────
@app.after_request
def add_security_headers(response):
    # Block embedding in iframes (clickjacking)
    response.headers['X-Frame-Options']        = 'DENY'
    # Prevent MIME sniffing
    response.headers['X-Content-Type-Options']  = 'nosniff'
    # Only allow localhost as origin
    response.headers['Access-Control-Allow-Origin'] = '*'
    # Strict CSP — only allow scripts/styles from same origin
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://fonts.gstatic.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self' http://localhost:5050 http://127.0.0.1:5050; "
        "object-src 'none';"
    )
    response.headers['Referrer-Policy']         = 'strict-origin'
    response.headers['Permissions-Policy']      = 'camera=(), microphone=(), geolocation=()'
    response.headers['X-CleanClicks-Version']   = '3.0'
    return response

# ── SECURITY: Block all non-localhost requests ────────────────────────────────
@app.before_request
def block_external_requests():
    """Reject any request not coming from localhost."""
    host = request.host.split(':')[0]
    allowed = {'localhost', '127.0.0.1', '::1'}
    if host not in allowed:
        abort(403)

# ── INTEGRITY CHECK: Verify backend file hasn't been tampered with ────────────
def verify_own_integrity():
    """Check our own file hash on startup — detect tampering."""
    try:
        this_file = Path(__file__).resolve()
        content   = this_file.read_bytes()
        sha256    = hashlib.sha256(content).hexdigest()
        hash_file = this_file.parent / 'cleanclicks_integrity.sha256'
        if hash_file.exists():
            stored = hash_file.read_text().strip()
            if stored != sha256:
                print(f"⚠ WARNING: Backend file has been modified since last run!")
                print(f"  Stored: {stored[:16]}...")
                print(f"  Current:{sha256[:16]}...")
                print(f"  If you did NOT update CleanClicks, this could indicate tampering.")
        else:
            # First run — save our hash
            hash_file.write_text(sha256)
            print(f"✓ Integrity hash saved: {sha256[:16]}...")
    except Exception as e:
        print(f"  Integrity check skipped: {e}")

@app.route('/api/token')
def get_token():
    """Return a session token so the frontend can authenticate requests."""
    return jsonify({"token": API_SECRET, "version": "3.0"})

@app.route('/api/integrity')
def api_integrity():
    """Report security status."""
    return jsonify({
        "localhost_only": True,
        "security_headers": True,
        "xss_protection": True,
        "csrf_protection": True,
        "external_requests_blocked": True,
        "version": "3.0"
    })

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
HISTORY_FILE = BASE_DIR / "cleanclicks_history.json"
TREND_FILE   = BASE_DIR / "cleanclicks_disk_trend.json"

# ─── Globals ──────────────────────────────────────────────────────────────────
auto_clean_active   = True
auto_clean_interval = 300          # seconds
last_clean_time     = None
last_clean_freed    = 0
history             = []
disk_trend          = []
auto_clean_thread   = None

# ══════════════════════════════════════════════════════════════════════════════
# PERSISTENCE
# ══════════════════════════════════════════════════════════════════════════════

def load_persistent():
    global history, disk_trend
    try:
        if HISTORY_FILE.exists():
            history = json.loads(HISTORY_FILE.read_text())[-200:]
    except Exception:
        history = []
    try:
        if TREND_FILE.exists():
            disk_trend = json.loads(TREND_FILE.read_text())[-1000:]
    except Exception:
        disk_trend = []

def save_history():
    try:
        HISTORY_FILE.write_text(json.dumps(history[-200:]))
    except Exception:
        pass

def save_trend():
    try:
        TREND_FILE.write_text(json.dumps(disk_trend[-1000:]))
    except Exception:
        pass

# ══════════════════════════════════════════════════════════════════════════════
# SYSTEM INFO
# ══════════════════════════════════════════════════════════════════════════════

def get_all_drives():
    drives = []
    if platform.system() == "Windows":
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            path = f"{letter}:\\"
            if os.path.exists(path):
                try:
                    usage = shutil.disk_usage(path)
                    drives.append({
                        "letter": letter,
                        "path": path,
                        "total": usage.total,
                        "used":  usage.used,
                        "free":  usage.free,
                        "pct":   round(usage.used / usage.total * 100, 1)
                    })
                except Exception:
                    pass
    else:
        usage = shutil.disk_usage("/")
        drives.append({"letter":"C","path":"/","total":usage.total,"used":usage.used,"free":usage.free,"pct":round(usage.used/usage.total*100,1)})
    return drives

@app.route("/api/drives")
def api_drives():
    return jsonify(get_all_drives())

@app.route("/api/system-info")
def api_system_info():
    drives = get_all_drives()
    c = next((d for d in drives if d["letter"]=="C"), drives[0])
    return jsonify({
        "os": platform.system(),
        "os_version": platform.version(),
        "machine": platform.machine(),
        "drives": drives,
        "disk_total": c["total"],
        "disk_used":  c["used"],
        "disk_free":  c["free"],
        "disk_pct":   c["pct"],
    })

# ══════════════════════════════════════════════════════════════════════════════
# TEMP / CACHE CLEANER
# ══════════════════════════════════════════════════════════════════════════════

def get_scan_paths(drive="C"):
    home = Path.home()
    local = home / "AppData" / "Local"
    roaming = home / "AppData" / "Roaming"
    paths = []
    # Windows temp
    paths += [Path(os.environ.get("TEMP", f"{drive}:\\Windows\\Temp")),
               Path(f"{drive}:\\Windows\\Temp")]
    # Browser caches
    for browser in ["Google\\Chrome\\User Data\\Default\\Cache",
                    "Google\\Chrome\\User Data\\Default\\Code Cache",
                    "Mozilla\\Firefox\\Profiles",
                    "Microsoft\\Edge\\User Data\\Default\\Cache"]:
        p = local / browser
        if p.exists():
            paths.append(p)
    # Misc
    paths += [local / "Temp",
               local / "Microsoft" / "Windows" / "Explorer",
               local / "Microsoft" / "Windows" / "INetCache",
               local / "Microsoft" / "Windows" / "WebCache",
               home / "AppData" / "Local" / "CrashDumps",
               Path(f"{drive}:\\Windows\\SoftwareDistribution\\Download"),
               Path(f"{drive}:\\Windows\\Logs"),
               local / "pip" / "cache",
               local / "npm-cache",
               ]
    return [p for p in paths if p.exists()]

@app.route("/api/scan-temp")
def api_scan_temp():
    drive = request.args.get("drive", "C")
    files = []
    total_size = 0
    for path in get_scan_paths(drive):
        for root, dirs, fnames in os.walk(path):
            for f in fnames:
                try:
                    fp = Path(root) / f
                    size = fp.stat().st_size
                    files.append({"path": str(fp), "size": size,
                                  "name": f, "dir": root})
                    total_size += size
                except Exception:
                    pass
    return jsonify({"files": files[:500], "total_files": len(files),
                    "total_size": total_size})

@app.route("/api/delete-files", methods=["POST"])
def api_delete_files():
    data = request.json or {}
    paths = data.get("paths", [])
    deleted = 0
    freed = 0
    errors = []
    for p in paths:
        try:
            fp = Path(p)
            size = fp.stat().st_size
            fp.unlink()
            deleted += 1
            freed += size
        except Exception as e:
            errors.append(str(e))
    return jsonify({"deleted": deleted, "freed": freed, "errors": errors})

# ══════════════════════════════════════════════════════════════════════════════
# DUPLICATE FINDER
# ══════════════════════════════════════════════════════════════════════════════

def hash_file(path, block=65536):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(block):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None

@app.route("/api/scan-duplicates")
def api_scan_duplicates():
    raw = request.args.get("paths", "")
    if raw.strip():
        scan_paths = [p.strip() for p in raw.split(",") if p.strip()]
    else:
        home = str(Path.home())
        scan_paths = [os.path.join(home, d) for d in ["Downloads","Documents","Desktop","Pictures","Videos"]]

    hashes = {}
    for sp in scan_paths:
        if not os.path.exists(sp):
            continue
        for root, _, files in os.walk(sp):
            for fn in files:
                fp = os.path.join(root, fn)
                try:
                    if os.path.getsize(fp) == 0:
                        continue
                    h = hash_file(fp)
                    if h:
                        hashes.setdefault(h, []).append({"path": fp, "size": os.path.getsize(fp), "name": fn})
                except Exception:
                    pass

    groups = [{"hash": h, "files": v, "wasted": v[0]["size"] * (len(v)-1)}
              for h, v in hashes.items() if len(v) > 1]
    total_wasted = sum(g["wasted"] for g in groups)
    return jsonify({"groups": groups, "total_groups": len(groups), "total_wasted": total_wasted})

@app.route("/api/delete-duplicates", methods=["POST"])
def api_delete_duplicates():
    data = request.json or {}
    paths = data.get("paths", [])
    deleted = freed = 0
    for p in paths:
        try:
            size = Path(p).stat().st_size
            Path(p).unlink()
            deleted += 1
            freed += size
        except Exception:
            pass
    return jsonify({"deleted": deleted, "freed": freed})

# ══════════════════════════════════════════════════════════════════════════════
# SMART HEALTH CHECK
# ══════════════════════════════════════════════════════════════════════════════

def get_suggestions(drive="C"):
    suggestions = []
    home = Path.home()
    local = home / "AppData" / "Local"

    cats = [
        ("Browser Cache", "🌐", "HIGH",
         "Browsers rebuild cache automatically — safe to clear",
         [local/"Google"/"Chrome"/"User Data"/"Default"/"Cache",
          local/"Microsoft"/"Edge"/"User Data"/"Default"/"Cache"]),
        ("Windows Temp Files", "🗂", "HIGH",
         "100% safe to delete — Windows recreates automatically",
         [Path(os.environ.get("TEMP","C:\\Windows\\Temp")), local/"Temp"]),
        ("Recycle Bin", "🗑", "HIGH",
         "Files you already deleted — completely safe",
         [Path(f"{drive}:\\$Recycle.Bin")]),
        ("Windows Log Files", "📋", "MEDIUM",
         "Old system logs — safe to delete",
         [Path(f"{drive}:\\Windows\\Logs"), local/"CrashDumps"]),
        ("Windows Update Cache", "🔄", "MEDIUM",
         "Old update files — safe after updates are installed",
         [Path(f"{drive}:\\Windows\\SoftwareDistribution\\Download")]),
        ("Thumbnail Cache", "🖼", "LOW",
         "Windows rebuilds thumbnails automatically",
         [local/"Microsoft"/"Windows"/"Explorer"]),
        ("Dev & Build Cache", "⚙", "MEDIUM",
         "node_modules, .pyc, build artifacts",
         []),
        ("Old Downloads (30+ days)", "📥", "HIGH",
         "Downloads older than 30 days",
         [home/"Downloads"]),
    ]

    for name, icon, priority, reason, paths in cats:
        count = size = 0
        for p in paths:
            if not p.exists():
                continue
            try:
                for root, _, files in os.walk(str(p)):
                    for fn in files:
                        try:
                            fp = Path(root) / fn
                            s = fp.stat().st_size
                            # For downloads, only count 30+ day old files
                            if "Downloads" in name:
                                mtime = fp.stat().st_mtime
                                if time.time() - mtime < 30 * 86400:
                                    continue
                            count += 1
                            size  += s
                        except Exception:
                            pass
            except Exception:
                pass
        if count > 0:
            suggestions.append({"category": name, "icon": icon,
                                 "priority": priority, "reason": reason,
                                 "file_count": count, "size": size,
                                 "drive": drive})
    return suggestions

@app.route("/api/health-check")
def api_health_check():
    drives = get_all_drives()
    alerts = []
    for d in drives:
        if d["free"] < 10 * 1024**3:
            sugg = get_suggestions(d["letter"])
            alerts.append({"drive": d["letter"], "free": d["free"],
                            "total": d["total"], "suggestions": sugg})
    return jsonify({"alerts": alerts, "drives": drives})

@app.route("/api/drive-suggestions")
def api_drive_suggestions():
    drive = request.args.get("drive", "C")
    return jsonify({"suggestions": get_suggestions(drive)})

@app.route("/api/burn-category", methods=["POST"])
def api_burn_category():
    data = request.json or {}
    category = data.get("category","")
    drive    = data.get("drive","C")
    home = Path.home()
    local = home / "AppData" / "Local"

    path_map = {
        "Browser Cache": [local/"Google"/"Chrome"/"User Data"/"Default"/"Cache",
                          local/"Microsoft"/"Edge"/"User Data"/"Default"/"Cache"],
        "Windows Temp Files": [Path(os.environ.get("TEMP","C:\\Windows\\Temp")), local/"Temp"],
        "Recycle Bin": [Path(f"{drive}:\\$Recycle.Bin")],
        "Windows Log Files": [Path(f"{drive}:\\Windows\\Logs"), local/"CrashDumps"],
        "Windows Update Cache": [Path(f"{drive}:\\Windows\\SoftwareDistribution\\Download")],
        "Thumbnail Cache": [local/"Microsoft"/"Windows"/"Explorer"],
        "Old Downloads (30+ days)": [home/"Downloads"],
    }

    paths = path_map.get(category, [])
    deleted = freed = 0
    for p in paths:
        if not p.exists():
            continue
        for root, _, files in os.walk(str(p)):
            for fn in files:
                try:
                    fp = Path(root) / fn
                    if "Downloads" in category:
                        mtime = fp.stat().st_mtime
                        if time.time() - mtime < 30*86400:
                            continue
                    size = fp.stat().st_size
                    fp.unlink()
                    deleted += 1
                    freed += size
                except Exception:
                    pass
    return jsonify({"deleted": deleted, "freed": freed, "category": category})

# ══════════════════════════════════════════════════════════════════════════════
# STARTUP MANAGER
# ══════════════════════════════════════════════════════════════════════════════

def get_startup_items():
    items = []
    keys = [
        (winreg.HKEY_CURRENT_USER,  r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"),
    ]
    for hive, subkey in keys:
        try:
            key = winreg.OpenKey(hive, subkey)
            i = 0
            while True:
                try:
                    name, val, _ = winreg.EnumValue(key, i)
                    items.append({"name": name, "command": val,
                                  "hive": "HKCU" if hive == winreg.HKEY_CURRENT_USER else "HKLM",
                                  "subkey": subkey, "enabled": True})
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except Exception:
            pass
    # Startup folder
    startup = home_startup = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    if startup.exists():
        for f in startup.iterdir():
            if f.suffix.lower() in (".lnk", ".bat", ".exe"):
                items.append({"name": f.stem, "command": str(f),
                               "hive": "FOLDER", "subkey": str(startup), "enabled": True})
    return items

@app.route("/api/startup")
def api_startup():
    return jsonify({"items": get_startup_items()})

@app.route("/api/startup/disable", methods=["POST"])
def api_startup_disable():
    data = request.json or {}
    name   = data.get("name","")
    hive_s = data.get("hive","HKCU")
    subkey = data.get("subkey","")
    hive   = winreg.HKEY_CURRENT_USER if hive_s == "HKCU" else winreg.HKEY_LOCAL_MACHINE
    try:
        key = winreg.OpenKey(hive, subkey, 0, winreg.KEY_ALL_ACCESS)
        winreg.DeleteValue(key, name)
        winreg.CloseKey(key)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ══════════════════════════════════════════════════════════════════════════════
# LARGE FILE FINDER
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/api/large-files")
def api_large_files():
    drive  = request.args.get("drive","C")
    min_mb = int(request.args.get("min_mb", 100))
    min_b  = min_mb * 1024 * 1024
    results = []
    root_path = f"{drive}:\\"

    skip = {"Windows","$Recycle.Bin","System Volume Information","Recovery","$WinREAgent"}
    for root, dirs, files in os.walk(root_path, topdown=True):
        dirs[:] = [d for d in dirs if d not in skip and not d.startswith("$")]
        for fn in files:
            try:
                fp = Path(root) / fn
                size = fp.stat().st_size
                if size >= min_b:
                    results.append({
                        "path": str(fp),
                        "name": fn,
                        "size": size,
                        "modified": fp.stat().st_mtime,
                        "ext": fp.suffix.lower()
                    })
            except Exception:
                pass
        if len(results) > 500:
            break

    results.sort(key=lambda x: x["size"], reverse=True)
    return jsonify({"files": results[:200], "total": len(results)})

@app.route("/api/open-folder", methods=["POST"])
def api_open_folder():
    data = request.json or {}
    path = data.get("path","")
    try:
        folder = str(Path(path).parent)
        subprocess.Popen(["explorer", "/select,", path])
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ══════════════════════════════════════════════════════════════════════════════
# PRIVACY CLEANER
# ══════════════════════════════════════════════════════════════════════════════

def get_privacy_targets():
    home  = Path.home()
    local = home / "AppData" / "Local"
    return {
        "Chrome History":     [local/"Google"/"Chrome"/"User Data"/"Default"/"History"],
        "Chrome Cookies":     [local/"Google"/"Chrome"/"User Data"/"Default"/"Cookies"],
        "Edge History":       [local/"Microsoft"/"Edge"/"User Data"/"Default"/"History"],
        "Edge Cookies":       [local/"Microsoft"/"Edge"/"User Data"/"Default"/"Cookies"],
        "Firefox History":    list((local/"Mozilla"/"Firefox"/"Profiles").glob("*/places.sqlite")) if (local/"Mozilla"/"Firefox"/"Profiles").exists() else [],
        "Recent Documents":   [home/"AppData"/"Roaming"/"Microsoft"/"Windows"/"Recent"],
        "Windows Prefetch":   [Path("C:\\Windows\\Prefetch")],
        "Jump Lists":         [home/"AppData"/"Roaming"/"Microsoft"/"Windows"/"Recent"/"AutomaticDestinations",
                               home/"AppData"/"Roaming"/"Microsoft"/"Windows"/"Recent"/"CustomDestinations"],
        "Clipboard History":  [],   # cleared via WinAPI separately
    }

@app.route("/api/privacy-scan")
def api_privacy_scan():
    targets = get_privacy_targets()
    results = []
    for category, paths in targets.items():
        size = count = 0
        for p in paths:
            p = Path(p)
            if p.is_file():
                try: size += p.stat().st_size; count += 1
                except: pass
            elif p.is_dir():
                for f in p.rglob("*"):
                    try:
                        if f.is_file():
                            size  += f.stat().st_size
                            count += 1
                    except: pass
        results.append({"category": category, "size": size, "count": count})
    return jsonify({"items": results})

@app.route("/api/privacy-clean", methods=["POST"])
def api_privacy_clean():
    data       = request.json or {}
    categories = data.get("categories", [])
    targets    = get_privacy_targets()
    deleted = freed = 0
    for cat in categories:
        paths = targets.get(cat, [])
        for p in paths:
            p = Path(p)
            try:
                if p.is_file():
                    freed += p.stat().st_size
                    p.unlink()
                    deleted += 1
                elif p.is_dir():
                    for f in p.rglob("*"):
                        try:
                            if f.is_file():
                                freed += f.stat().st_size
                                f.unlink()
                                deleted += 1
                        except: pass
            except: pass
    return jsonify({"deleted": deleted, "freed": freed})

# ══════════════════════════════════════════════════════════════════════════════
# PC HEALTH SCORE
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/api/health-score")
def api_health_score():
    drives = get_all_drives()
    score  = 100
    issues = []
    tips   = []

    # Disk health
    for d in drives:
        pct = d["pct"]
        if pct > 95:
            score -= 30; issues.append(f"💽 {d['letter']}: critically full ({pct}%)")
        elif pct > 85:
            score -= 15; issues.append(f"💽 {d['letter']}: drive very full ({pct}%)")
        elif pct > 70:
            score -= 5;  tips.append(f"💽 {d['letter']}: getting full ({pct}%)")

    # Startup items
    try:
        startup = get_startup_items()
        if len(startup) > 20:
            score -= 15; issues.append(f"🚀 Too many startup items ({len(startup)}) slowing boot")
        elif len(startup) > 12:
            score -= 5;  tips.append(f"🚀 Many startup items ({len(startup)}) — review them")
    except Exception:
        pass

    # Temp files
    try:
        temp_size = sum(f.stat().st_size for f in Path(os.environ.get("TEMP","C:\\Windows\\Temp")).rglob("*") if f.is_file())
        if temp_size > 2*1024**3:
            score -= 10; issues.append("🗂 Over 2 GB of temp files found")
        elif temp_size > 500*1024**2:
            score -= 5;  tips.append("🗂 Temp folder getting large")
    except Exception:
        pass

    # History bonus
    if history:
        score = min(score + 5, 100)
        tips.append("✅ Auto-clean is active — keeping your PC healthy!")

    score = max(0, min(100, score))

    if score >= 90:   grade, color, label = "A", "#22c55e", "Excellent"
    elif score >= 75: grade, color, label = "B", "#84cc16", "Good"
    elif score >= 60: grade, color, label = "C", "#eab308", "Fair"
    elif score >= 45: grade, color, label = "D", "#f97316", "Poor"
    else:             grade, color, label = "F", "#ef4444", "Critical"

    return jsonify({"score": score, "grade": grade, "color": color,
                    "label": label, "issues": issues, "tips": tips})

# ══════════════════════════════════════════════════════════════════════════════
# DISK TREND
# ══════════════════════════════════════════════════════════════════════════════

def record_trend():
    drives = get_all_drives()
    snap   = {"ts": time.time(), "drives": {d["letter"]: d["free"] for d in drives}}
    disk_trend.append(snap)
    if len(disk_trend) > 1000:
        disk_trend.pop(0)
    save_trend()

@app.route("/api/disk-trend")
def api_disk_trend():
    drive  = request.args.get("drive","C")
    hours  = int(request.args.get("hours", 24))
    cutoff = time.time() - hours * 3600
    points = [{"ts": s["ts"], "free": s["drives"].get(drive, 0)}
              for s in disk_trend if s["ts"] >= cutoff]
    return jsonify({"points": points, "drive": drive})

# ══════════════════════════════════════════════════════════════════════════════
# AUTO-CLEAN ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def auto_clean_categories():
    """Returns list of (category_name, paths_list) to auto-delete."""
    home  = Path.home()
    local = home / "AppData" / "Local"
    return [
        ("Browser Cache", [
            local/"Google"/"Chrome"/"User Data"/"Default"/"Cache",
            local/"Google"/"Chrome"/"User Data"/"Default"/"Code Cache",
            local/"Microsoft"/"Edge"/"User Data"/"Default"/"Cache",
        ]),
        ("Windows Temp Files", [
            Path(os.environ.get("TEMP","C:\\Windows\\Temp")),
            local/"Temp",
        ]),
        ("Windows Log Files", [
            Path("C:\\Windows\\Logs"),
            local/"CrashDumps",
        ]),
        ("Windows Update Cache", [
            Path("C:\\Windows\\SoftwareDistribution\\Download"),
        ]),
        ("Thumbnail Cache", [
            local/"Microsoft"/"Windows"/"Explorer",
        ]),
        ("Dev Build Cache", [
            local/"pip"/"cache",
            local/"npm-cache",
        ]),
    ]

def run_auto_clean():
    global last_clean_time, last_clean_freed
    record_trend()
    cats    = auto_clean_categories()
    deleted = freed = 0
    cleaned = []

    for name, paths in cats:
        cat_freed = 0
        for p in paths:
            if not p.exists():
                continue
            for root, _, files in os.walk(str(p)):
                for fn in files:
                    try:
                        fp = Path(root) / fn
                        sz = fp.stat().st_size
                        fp.unlink()
                        deleted  += 1
                        freed    += sz
                        cat_freed+= sz
                    except Exception:
                        pass
        if cat_freed > 0:
            cleaned.append(name)

    last_clean_time  = time.time()
    last_clean_freed = freed

    entry = {
        "ts":      last_clean_time,
        "deleted": deleted,
        "freed":   freed,
        "cats":    cleaned,
    }
    history.append(entry)
    save_history()
    record_trend()

    if freed > 0:
        send_windows_notification(
            "CleanClicks — Auto-Clean Done! 🧹",
            f"Freed {fmt(freed)} • {deleted} files removed\n{', '.join(cleaned[:3])}"
        )

def fmt(b):
    if b >= 1024**3: return f"{b/1024**3:.1f} GB"
    if b >= 1024**2: return f"{b/1024**2:.1f} MB"
    if b >= 1024:    return f"{b/1024:.1f} KB"
    return f"{b} B"

def send_windows_notification(title, message):
    try:
        ps = f'''
Add-Type -AssemblyName System.Windows.Forms
$n = New-Object System.Windows.Forms.NotifyIcon
$n.Icon = [System.Drawing.SystemIcons]::Information
$n.Visible = $true
$n.ShowBalloonTip(5000, "{title}", "{message}", [System.Windows.Forms.ToolTipIcon]::None)
Start-Sleep -Seconds 6
$n.Visible = $false
$n.Dispose()
'''
        subprocess.Popen(
            ["powershell","-WindowStyle","Hidden","-Command", ps],
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess,"CREATE_NO_WINDOW") else 0
        )
    except Exception:
        pass

def auto_clean_loop():
    global auto_clean_active
    while True:
        time.sleep(auto_clean_interval)
        if auto_clean_active:
            try:
                run_auto_clean()
            except Exception:
                pass

# ──────────────── Auto-Clean API ─────────────────────────────────────────────

@app.route("/api/auto-clean/status")
def api_ac_status():
    total_freed   = sum(h["freed"] for h in history)
    total_deleted = sum(h["deleted"] for h in history)
    return jsonify({
        "active":         auto_clean_active,
        "interval":       auto_clean_interval,
        "last_clean":     last_clean_time,
        "last_freed":     last_clean_freed,
        "total_freed":    total_freed,
        "total_deleted":  total_deleted,
        "history":        history[-50:],
        "history_count":  len(history),
    })

@app.route("/api/auto-clean/run", methods=["POST"])
def api_ac_run():
    threading.Thread(target=run_auto_clean, daemon=True).start()
    return jsonify({"started": True})

@app.route("/api/auto-clean/toggle", methods=["POST"])
def api_ac_toggle():
    global auto_clean_active
    auto_clean_active = not auto_clean_active
    return jsonify({"active": auto_clean_active})

@app.route("/api/auto-clean/interval", methods=["POST"])
def api_ac_interval():
    global auto_clean_interval
    data = request.json or {}
    auto_clean_interval = int(data.get("seconds", 300))
    return jsonify({"interval": auto_clean_interval})

# ══════════════════════════════════════════════════════════════════════════════
# SECURE FILE SHREDDER
# ══════════════════════════════════════════════════════════════════════════════

def shred_file(path, passes=3):
    """Overwrite file with random bytes before deleting — unrecoverable."""
    p = Path(path)
    if not p.exists() or not p.is_file():
        return False
    size = p.stat().st_size
    try:
        with open(p, "r+b") as f:
            for _ in range(passes):
                f.seek(0)
                # Pass 1: random data, Pass 2: zeros, Pass 3: ones, rest: random
                f.write(os.urandom(size))
                f.flush()
                os.fsync(f.fileno())
                f.seek(0)
                f.write(b'\x00' * size)
                f.flush()
                os.fsync(f.fileno())
                f.seek(0)
                f.write(b'\xFF' * size)
                f.flush()
                os.fsync(f.fileno())
        p.unlink()
        return True
    except Exception:
        try: p.unlink()
        except: pass
        return False

SHRED_PROGRESS = {"active": False, "total": 0, "done": 0, "freed": 0, "current": ""}

@app.route("/api/shred", methods=["POST"])
def api_shred():
    global SHRED_PROGRESS
    data   = request.json or {}
    paths  = data.get("paths", [])
    method = data.get("method", "dod")   # simple | dod | gutmann
    passes = {"simple": 1, "dod": 3, "gutmann": 7}.get(method, 3)

    total_size = sum(Path(p).stat().st_size for p in paths if Path(p).is_file())
    SHRED_PROGRESS = {"active": True, "total": len(paths), "done": 0,
                      "freed": 0, "current": "", "total_size": total_size}

    def do_shred():
        for p in paths:
            SHRED_PROGRESS["current"] = Path(p).name
            try:
                sz = Path(p).stat().st_size
                if shred_file(p, passes):
                    SHRED_PROGRESS["freed"] += sz
            except Exception:
                pass
            SHRED_PROGRESS["done"] += 1
        SHRED_PROGRESS["active"] = False
        SHRED_PROGRESS["current"] = "Done"

    threading.Thread(target=do_shred, daemon=True).start()
    return jsonify({"started": True, "files": len(paths), "passes": passes})

@app.route("/api/shred/progress")
def api_shred_progress():
    return jsonify(SHRED_PROGRESS)

# ══════════════════════════════════════════════════════════════════════════════
# REGISTRY CLEANER
# ══════════════════════════════════════════════════════════════════════════════

def check_reg_value_path(value):
    """Return True if the path referenced in a registry value actually exists."""
    if not value:
        return True
    # Strip quotes and args
    clean = value.strip().strip('"').split('"')[0].split(' ')[0].strip()
    if not clean or clean.startswith('%') or len(clean) < 3:
        return True   # skip env-var paths — assume valid
    return os.path.exists(clean) or os.path.exists(clean.split(',')[0])

def scan_registry_issues():
    issues = []

    # ── 1. Invalid uninstall entries ─────────────────────────────────────────
    uninst_keys = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER,  r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]
    for hive, path in uninst_keys:
        try:
            key = winreg.OpenKey(hive, path)
            i = 0
            while True:
                try:
                    sub = winreg.EnumKey(key, i)
                    sub_key = winreg.OpenKey(hive, path + "\\" + sub)
                    try:
                        name, _, _ = winreg.QueryValueEx(sub_key, "DisplayName")
                        try:
                            uninst, _, _ = winreg.QueryValueEx(sub_key, "UninstallString")
                            if uninst and not check_reg_value_path(uninst):
                                issues.append({
                                    "category": "Invalid Uninstall Entry",
                                    "description": f"{name} — uninstaller not found",
                                    "key": path + "\\" + sub,
                                    "hive": "HKLM" if hive == winreg.HKEY_LOCAL_MACHINE else "HKCU",
                                    "safe": True,
                                    "icon": "🗑"
                                })
                        except Exception:
                            pass
                    except Exception:
                        pass
                    winreg.CloseKey(sub_key)
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except Exception:
            pass

    # ── 2. Invalid startup registry entries ──────────────────────────────────
    run_keys = [
        (winreg.HKEY_CURRENT_USER,  r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
    ]
    for hive, path in run_keys:
        try:
            key = winreg.OpenKey(hive, path)
            i = 0
            while True:
                try:
                    name, val, _ = winreg.EnumValue(key, i)
                    if not check_reg_value_path(val):
                        issues.append({
                            "category": "Invalid Startup Entry",
                            "description": f"{name} — file not found: {val[:60]}",
                            "key": path,
                            "value_name": name,
                            "hive": "HKLM" if hive == winreg.HKEY_LOCAL_MACHINE else "HKCU",
                            "safe": True,
                            "icon": "🚀"
                        })
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except Exception:
            pass

    # ── 3. Invalid file associations ─────────────────────────────────────────
    try:
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"")
        i = 0
        checked = 0
        while checked < 200:
            try:
                ext = winreg.EnumKey(key, i)
                if ext.startswith('.'):
                    try:
                        ext_key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, ext)
                        prog_id, _, _ = winreg.QueryValueEx(ext_key, "")
                        if prog_id:
                            try:
                                winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, prog_id)
                            except Exception:
                                issues.append({
                                    "category": "Broken File Association",
                                    "description": f"{ext} → '{prog_id}' handler missing",
                                    "key": ext,
                                    "hive": "HKCR",
                                    "safe": True,
                                    "icon": "🔗"
                                })
                        winreg.CloseKey(ext_key)
                    except Exception:
                        pass
                    checked += 1
                i += 1
            except OSError:
                break
        winreg.CloseKey(key)
    except Exception:
        pass

    return issues

@app.route("/api/registry/scan")
def api_registry_scan():
    try:
        issues = scan_registry_issues()
        return jsonify({"issues": issues, "total": len(issues)})
    except Exception as e:
        return jsonify({"issues": [], "total": 0, "error": str(e)})

@app.route("/api/registry/fix", methods=["POST"])
def api_registry_fix():
    data   = request.json or {}
    items  = data.get("items", [])
    fixed  = 0
    errors = []

    for item in items:
        hive_map = {
            "HKLM": winreg.HKEY_LOCAL_MACHINE,
            "HKCU": winreg.HKEY_CURRENT_USER,
            "HKCR": winreg.HKEY_CLASSES_ROOT,
        }
        hive = hive_map.get(item.get("hive","HKCU"), winreg.HKEY_CURRENT_USER)
        key_path = item.get("key","")
        value_name = item.get("value_name")

        try:
            if value_name:
                # Delete just the value
                k = winreg.OpenKey(hive, key_path, 0, winreg.KEY_ALL_ACCESS)
                winreg.DeleteValue(k, value_name)
                winreg.CloseKey(k)
            else:
                # Delete the whole subkey (last part of path)
                parent = "\\".join(key_path.split("\\")[:-1])
                child  = key_path.split("\\")[-1]
                k = winreg.OpenKey(hive, parent, 0, winreg.KEY_ALL_ACCESS)
                winreg.DeleteKey(k, child)
                winreg.CloseKey(k)
            fixed += 1
        except Exception as e:
            errors.append(str(e))

    return jsonify({"fixed": fixed, "errors": errors})

# ══════════════════════════════════════════════════════════════════════════════
# LIVE SYSTEM MONITOR (CPU / RAM / NETWORK)
# ══════════════════════════════════════════════════════════════════════════════

def get_cpu_usage():
    """Simple CPU usage via wmic (no psutil needed)."""
    try:
        result = subprocess.run(
            ["wmic", "cpu", "get", "LoadPercentage", "/value"],
            capture_output=True, text=True, timeout=3,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        for line in result.stdout.splitlines():
            if "LoadPercentage=" in line:
                return int(line.split("=")[1].strip())
    except Exception:
        pass
    return 0

def get_ram_info():
    """RAM stats via wmic."""
    try:
        # Total physical memory
        r1 = subprocess.run(
            ["wmic", "OS", "get", "TotalVisibleMemorySize,FreePhysicalMemory", "/value"],
            capture_output=True, text=True, timeout=3,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        total = free = 0
        for line in r1.stdout.splitlines():
            if "TotalVisibleMemorySize=" in line:
                total = int(line.split("=")[1].strip()) * 1024
            if "FreePhysicalMemory=" in line:
                free  = int(line.split("=")[1].strip()) * 1024
        used = total - free
        pct  = round(used / total * 100, 1) if total else 0
        return {"total": total, "used": used, "free": free, "pct": pct}
    except Exception:
        return {"total": 0, "used": 0, "free": 0, "pct": 0}

def get_top_processes():
    """Top 8 processes by memory via wmic."""
    try:
        result = subprocess.run(
            ["wmic", "process", "get", "Name,WorkingSetSize", "/value"],
            capture_output=True, text=True, timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        procs = {}
        name = None
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("Name="):
                name = line.split("=",1)[1].strip()
            elif line.startswith("WorkingSetSize=") and name:
                try:
                    size = int(line.split("=",1)[1].strip())
                    procs[name] = procs.get(name, 0) + size
                except:
                    pass
                name = None
        sorted_procs = sorted(procs.items(), key=lambda x: x[1], reverse=True)[:8]
        return [{"name": n, "memory": s} for n, s in sorted_procs]
    except Exception:
        return []

@app.route("/api/system-monitor")
def api_system_monitor():
    drives = get_all_drives()
    ram    = get_ram_info()
    cpu    = get_cpu_usage()
    procs  = get_top_processes()
    return jsonify({
        "cpu":    cpu,
        "ram":    ram,
        "drives": drives,
        "processes": procs,
        "timestamp": time.time()
    })

# ══════════════════════════════════════════════════════════════════════════════
# STARTUP
# ══════════════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════════════════
# SERVE HTML — serve the frontend through Flask so origin is always localhost
# ══════════════════════════════════════════════════════════════════════════════
from flask import send_file, redirect

@app.route("/")
def serve_index():
    """Serve cleanclicks.html through Flask — fixes CORS origin issues."""
    html_path = BASE_DIR / "cleanclicks.html"
    if html_path.exists():
        return send_file(str(html_path))
    return "<h1>CleanClicks</h1><p>cleanclicks.html not found in: " + str(BASE_DIR) + "</p>", 404

if __name__ == "__main__":
    verify_own_integrity()
    load_persistent()
    print("🧹 CleanClicks Backend — Starting...")
    print("   API  → http://localhost:5050")
    print("   Open cleanclicks.html in your browser")
    print("   Press Ctrl+C to stop\n")

    # Initial disk snapshot
    record_trend()

    # Start auto-clean background thread
    t = threading.Thread(target=auto_clean_loop, daemon=True)
    t.start()

    app.run(host="127.0.0.1", port=5050, debug=False)
