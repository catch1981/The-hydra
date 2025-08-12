
import os, sys, subprocess, threading, time, signal, webbrowser, psutil

if getattr(sys, 'frozen', False):
    ROOT = os.path.abspath(getattr(sys, '_MEIPASS', os.path.dirname(sys.executable)))
else:
    ROOT = os.path.abspath(os.path.dirname(__file__))
PY   = sys.executable

def envfile():
    return os.path.join(ROOT, ".env")

def load_env():
    # naive .env loader
    if not os.path.exists(envfile()):
        raise SystemExit("Missing .env; configure your suite first.")
    with open(envfile(), "r", encoding="ascii") as f:
        for line in f:
            line=line.strip()
            if not line or line.startswith("#") or "=" not in line: continue
            k,v = line.split("=",1)
            os.environ[k]=v

def run_proc(args, name):
    return subprocess.Popen(args, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=0x00000008)

procs = []

def start_stack():
    # relay
    p1 = run_proc([PY, os.path.join(ROOT,"relay_py","relay.py")], "relay")
    procs.append(p1)
    # daemon (uvicorn)
    p2 = run_proc([PY, "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8765"], "daemon")
    procs.append(p2)

def stop_stack():
    for p in procs:
        try:
            if p and p.poll() is None:
                p.terminate()
                try: p.wait(timeout=5)
                except: p.kill()
        except Exception: pass

def tail(proc, tag):
    for line in iter(proc.stdout.readline, ""):
        print(f"[{tag}] {line}", end="")
    proc.stdout.close()

def console_mode():
    print("== Virendir Launcher / console mode ==")
    print("Starting relay + daemon ...")
    start_stack()
    t1 = threading.Thread(target=tail, args=(procs[0],"relay"), daemon=True); t1.start()
    t2 = threading.Thread(target=tail, args=(procs[1],"daemon"), daemon=True); t2.start()
    print("Open http://127.0.0.1:8765/healthz")
    print("Press Ctrl+C to stop.")
    try:
        while any(p.poll() is None for p in procs):
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping ...")
    finally:
        stop_stack()

def tray_mode():
    import pystray
    from PIL import Image
    icon_path = os.path.join(ROOT,"assets","icon.ico")
    image = Image.open(icon_path)

    start_stack()

    def on_open_health(icon, item):
        webbrowser.open("http://127.0.0.1:8765/healthz")

    def on_logs(icon, item):
        webbrowser.open("file:///C:/virendir-assistant/var/virendir.log")

    def on_quit(icon, item):
        stop_stack()
        icon.stop()

    menu = (pystray.MenuItem("Open Health", on_open_health),
            pystray.MenuItem("Open Logs", on_logs),
            pystray.MenuItem("Quit", on_quit))
    ic = pystray.Icon("Virendir", image, "Virendir", pystray.Menu(*menu))
    ic.run()

def ensure_venv_deps():
    # basic check for core deps
    try:
        import fastapi, uvicorn, websockets, psutil
    except Exception:
        print("Installing dependencies ...")
        subprocess.check_call([PY, "-m", "pip", "install", "-r", os.path.join(ROOT,"requirements_exe.txt")])

if __name__ == "__main__":
    os.chdir(ROOT)
    load_env()
    ensure_venv_deps()
    mode = "tray" if (len(sys.argv)>1 and sys.argv[1]=="tray") else "console"
    if mode == "tray":
        tray_mode()
    else:
        console_mode()
