
import os, time, socket, threading
import firebase_admin
from firebase_admin import credentials, firestore, db

_app=_fs=_db=None

def init_firebase():
    global _app,_fs,_db
    if _app: return _fs,_db
    cred_path=os.getenv("FIREBASE_CRED"); db_url=os.getenv("FIREBASE_DB_URL"); project=os.getenv("FIREBASE_PROJECT")
    if not (cred_path and db_url and project):
        raise RuntimeError("Firebase env missing: set FIREBASE_CRED, FIREBASE_DB_URL, FIREBASE_PROJECT")
    cred=credentials.Certificate(cred_path)
    _app=firebase_admin.initialize_app(cred, {"databaseURL":db_url, "projectId":project})
    _fs=firestore.client(); _db=db.reference("/"); return _fs,_db

def _ip():
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.connect(("8.8.8.8",80))
        ip=s.getsockname()[0]; s.close(); return ip
    except: return "0.0.0.0"

def start_presence(node_id:str, room:str, ver:str="virendir-win-1"):
    fs,_=init_firebase()
    def loop():
        while True:
            try:
                fs.collection("presence").document("nodes").collection("items").document(node_id).set({
                    "node_id":node_id,"room":room,"host":socket.gethostname(),"ip":_ip(),"version":ver,
                    "ts":int(time.time()*1000),"state":"online"
                }, merge=True)
            except Exception as e:
                # hard error: stop thread
                raise
            time.sleep(20)
    t=threading.Thread(target=loop, daemon=True); t.start()

def log_scroll(entry: dict):
    fs,_=init_firebase()
    fs.collection("scrolls").document("log").collection("entries").add(entry)
