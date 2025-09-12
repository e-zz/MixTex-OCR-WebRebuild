import subprocess
import sys
import time
import signal
import socket
from pathlib import Path
import threading

ROOT = Path(__file__).parent.resolve()
BACKEND_DIR = ROOT / "webapi"
FRONTEND_DIR = ROOT / "web-frontend"
OUTPUT_ENCODING = "utf-8"  # force UTF-8 decoding with replacement

processes = []

def port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0

def wait_for(port: int, timeout=20):
    start = time.time()
    while time.time() - start < timeout:
        if port_in_use(port):
            return True
        time.sleep(0.4)
    return False

def start_backend():
    if not (BACKEND_DIR / "app.py").exists():
        print("Backend app.py not found in webapi/", file=sys.stderr)
        sys.exit(1)
    cmd = [
        sys.executable, "-m", "uvicorn",
        "app:app", "--host", "127.0.0.1", "--port", "8000", "--reload"
    ]
    p = subprocess.Popen(
        cmd,
        cwd=BACKEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding=OUTPUT_ENCODING,  # specify encoding
        errors="replace"  # avoid UnicodeDecodeError
    )
    processes.append(p)
    return p

def ensure_frontend_deps():
    if not (FRONTEND_DIR / "node_modules").exists():
        print("Installing frontend dependencies (first run)...")
        subprocess.check_call(["npm", "install"], cwd=FRONTEND_DIR)

def run_diagnostics():
    print("[DIAG] Checking npm availability...")
    try:
        subprocess.check_call('npm.cmd --help')
        print("[DIAG] npm OK")
    except Exception as e:
        print("[DIAG][ERROR] npm not runnable:", e)

def start_frontend(check_npm=False):
    if check_npm:
        run_diagnostics()
    ensure_frontend_deps()
    cmd = ["npm.cmd", "run", "dev", "--", "--port", "3000"]
    p = subprocess.Popen(
        cmd,
        cwd=FRONTEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding=OUTPUT_ENCODING,  # specify encoding
        errors="replace"  # avoid UnicodeDecodeError
    )
    processes.append(p)
    return p

def stream_output(tag, proc):
    for line in proc.stdout:
        print(f"[{tag}] {line.rstrip()}")

def graceful_exit(*_):
    print("\nStopping processes...")
    for p in processes:
        if p.poll() is None:
            try:
                p.terminate()
            except Exception:
                pass
    # Give them a moment
    time.sleep(1)
    for p in processes:
        if p.poll() is None:
            try:
                p.kill()
            except Exception:
                pass
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, graceful_exit)
    signal.signal(signal.SIGTERM, graceful_exit)

    if port_in_use(8000):
        print("Port 8000 already in use. Abort.")
        return
    if port_in_use(3000):
        print("Port 3000 already in use. Abort.")
        return

    back = start_backend()
    # Simple non-blocking output readers
    threading.Thread(target=stream_output, args=("BACKEND", back), daemon=True).start()

    if not wait_for(8000, timeout=25):
        print("Backend did not start (port 8000). See logs above.")
    else:
        print("Backend ready: http://127.0.0.1:8000")

    front = start_frontend()
    threading.Thread(target=stream_output, args=("FRONTEND", front), daemon=True).start()

    print("Frontend starting (Vite)... expected at http://127.0.0.1:3000")
    print("Press Ctrl+C to stop both.")

    # Keep main thread alive
    while True:
        # If either died unexpectedly, exit
        if back.poll() is not None:
            print("Backend exited. Shutting down.")
            break
        if front.poll() is not None:
            print("Frontend exited. Shutting down.")
            break
        time.sleep(1)

    graceful_exit()

if __name__ == "__main__":
    main()