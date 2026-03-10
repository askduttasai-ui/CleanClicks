"""
CleanClicks Silent Launcher v3.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Double-click EXE → browser opens automatically
- No CMD window, no splash, no tray icon
- Runs Flask backend silently in background
- Single instance guard (double-click again = just opens browser)
- Keeps running until user closes browser or kills process
"""

import sys
import os
import time
import socket
import threading
import webbrowser
from pathlib import Path

# ── Base directory (works both as .exe and .py) ───────────────────────────────
if getattr(sys, 'frozen', False):
    BASE_DIR   = Path(sys.executable).parent
    BUNDLE_DIR = Path(sys._MEIPASS) if hasattr(sys, '_MEIPASS') else BASE_DIR
else:
    BASE_DIR   = Path(__file__).parent
    BUNDLE_DIR = BASE_DIR

os.chdir(str(BASE_DIR))
sys.path.insert(0, str(BUNDLE_DIR))

# ── Single instance guard ─────────────────────────────────────────────────────
# If CleanClicks is already running, just open the browser and exit cleanly
def already_running():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
        s.bind(('127.0.0.1', 5051))
        s.listen(1)
        return False, s
    except OSError:
        return True, None

is_running, guard_sock = already_running()

if is_running:
    # Already running — just bring up the browser
    webbrowser.open(str(BASE_DIR / 'cleanclicks.html'))
    sys.exit(0)

# ── Wait for backend to be ready ─────────────────────────────────────────────
def wait_for_backend(timeout=20):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            s = socket.create_connection(('127.0.0.1', 5050), timeout=0.5)
            s.close()
            return True
        except OSError:
            time.sleep(0.3)
    return False

# ── Start Flask backend silently ──────────────────────────────────────────────
def start_backend():
    import cleaner_backend as backend
    backend.BASE_DIR     = BASE_DIR
    backend.HISTORY_FILE = BASE_DIR / 'cleanclicks_history.json'
    backend.TREND_FILE   = BASE_DIR / 'cleanclicks_disk_trend.json'
    backend.load_persistent()
    backend.record_trend()

    # Start auto-clean background thread
    t = threading.Thread(target=backend.auto_clean_loop, daemon=True)
    t.start()

    # Use waitress (production server) if available, else Flask dev server
    try:
        from waitress import serve
        serve(backend.app, host='127.0.0.1', port=5050, threads=4)
    except ImportError:
        backend.app.run(host='127.0.0.1', port=5050, debug=False, use_reloader=False)

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':

    # Start backend silently in background
    t = threading.Thread(target=start_backend, daemon=True)
    t.start()

    # Wait until backend is accepting connections
    wait_for_backend(timeout=20)

    # Open browser — user sees the app immediately
    webbrowser.open(str(BASE_DIR / 'cleanclicks.html'))

    # Keep process alive (backend runs as daemon thread)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        if guard_sock:
            try: guard_sock.close()
            except: pass
