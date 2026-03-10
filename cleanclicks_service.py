"""
CleanClicks Windows Service Wrapper
Runs cleaner_backend.py as a proper Windows background service.
"""

import sys
import os
import time
import subprocess
import threading
import servicemanager
import win32event
import win32service
import win32serviceutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND  = os.path.join(BASE_DIR, "cleaner_backend.py")
PYTHON   = sys.executable
LOG_FILE = os.path.join(BASE_DIR, "cleanclicks_service.log")


class CleanClicksService(win32serviceutil.ServiceFramework):
    _svc_name_        = "CleanClicksService"
    _svc_display_name_= "CleanClicks PC Cleaner"
    _svc_description_ = "Automatically cleans temp files, cache and logs every 5 minutes."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event  = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive    = True
        self.process     = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.is_alive = False
        if self.process:
            try:
                self.process.terminate()
            except Exception:
                pass

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.main()

    def main(self):
        while self.is_alive:
            try:
                self.process = subprocess.Popen(
                    [PYTHON, BACKEND],
                    cwd=BASE_DIR,
                    stdout=open(LOG_FILE, "a"),
                    stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                self.process.wait()
            except Exception as e:
                with open(LOG_FILE, "a") as f:
                    f.write(f"[ERROR] {e}\n")
            if self.is_alive:
                time.sleep(5)   # brief pause before restart


if __name__ == "__main__":
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(CleanClicksService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(CleanClicksService)
