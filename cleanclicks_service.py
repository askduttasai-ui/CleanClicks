"""
CleanClicks Windows Service Wrapper v2
Runs cleaner_backend.py as a Windows background service.
Compatible with Python 3.11 + pywin32.
"""

import sys
import os
import time
import subprocess
import win32event
import win32service
import win32serviceutil
import servicemanager

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND  = os.path.join(BASE_DIR, "cleaner_backend.py")
PYTHON   = r"C:\Users\DELL\AppData\Local\Programs\Python\Python311\python.exe"
LOG_FILE = os.path.join(BASE_DIR, "cleanclicks_service.log")


def log(msg):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass


class CleanClicksService(win32serviceutil.ServiceFramework):
    _svc_name_         = "CleanClicksService"
    _svc_display_name_ = "CleanClicks PC Cleaner"
    _svc_description_  = "Automatically cleans temp files, cache and logs. Runs CleanClicks backend."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive   = True
        self.process    = None

    def SvcStop(self):
        log("Service stopping...")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.is_alive = False
        if self.process:
            try:
                self.process.terminate()
                log("Backend process terminated.")
            except Exception as e:
                log(f"Error terminating process: {e}")

    def SvcDoRun(self):
        log("Service starting...")
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.main()

    def main(self):
        log(f"Python: {PYTHON}")
        log(f"Backend: {BACKEND}")

        while self.is_alive:
            try:
                log("Launching cleaner_backend.py...")
                with open(LOG_FILE, "a", encoding="utf-8") as logf:
                    env = os.environ.copy()
                    env["PYTHONIOENCODING"] = "utf-8"
                    env["PYTHONUTF8"] = "1"
                    self.process = subprocess.Popen(
                        [PYTHON, "-X", "utf8", BACKEND],
                        env=env,
                        cwd=BASE_DIR,
                        stdout=logf,
                        stderr=logf,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                log(f"Backend started. PID: {self.process.pid}")
                self.process.wait()
                log(f"Backend exited with code: {self.process.returncode}")
            except Exception as e:
                log(f"[ERROR] {e}")

            if self.is_alive:
                log("Restarting backend in 5 seconds...")
                time.sleep(5)

        log("Service stopped.")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(CleanClicksService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(CleanClicksService)
