import subprocess
import signal
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent
processes = []


def start_services():
    global processes

    internal = subprocess.Popen(
        [sys.executable, "internal_service.py"],
        cwd=BASE_DIR,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )
    processes.append(internal)

    public = subprocess.Popen(
        [sys.executable, "public_app.py"],
        cwd=BASE_DIR,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )
    processes.append(public)

    print("[✓] SSRF services started.")


def stop_services():
    print("[*] Stopping SSRF services...")

    for p in processes:
        try:
            p.terminate()
            p.wait(timeout=5)
            print(f"[+] Stopped PID {p.pid}")
        except Exception:
            pass

    print("[✓] All services stopped.")


def handle_exit(signum=None, frame=None):
    stop_services()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    start_services()

    while True:
        time.sleep(1)
