
import os, time, socket, requests, tomllib, json
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import Response, PlainTextResponse
from pydantic import BaseModel
from log import get_logger, TraceAdapter
from quarantine import in_quarantine, set_quarantine
from mesh import setup_from_cfg
from firebase_bus import start_presence

from tools.shell import run_shell
from tools.files import tool_listdir, tool_write_text
from tts import tts_elevenlabs
from stt import stt_transcribe
from router import build_task

CFG = tomllib.load(open(os.path.join(os.path.dirname(__file__), "config.toml"), "rb"))
LOG = TraceAdapter(get_logger(), {})
COUNTS={"req":0,"sudo":0,"fail":0}

app = FastAPI()
NODE_ID = CFG.get("mesh",{}).get("node_id","pan-node")
ROOM    = CFG.get("mesh",{}).get("room","coven-zero")
SUDO_TOKEN = os.getenv("VIREN_SUDO_TOKEN","")

from enum import Enum
class Risk(str, Enum):
    low="low"; med="med"; high="high"

CATASTROPHIC = [
    r"(?i)\brm\s+-rf\s+([\\/]|C:)",
    r"(?i)\bformat(\.exe)?\b",
    r"(?i)\bdiskpart\b.*\b(clean|format)\b",
    r"(?i)\bdel\s+/f\s+/s\s+/q\s+C:\\\\\*",
    r"(?i)\bmkfs\.",
    r"(?i)\bdd\s+if=",
]

def is_catastrophic(s: str) -> bool:
    import re
    return any(re.search(p, s) for p in CATASTROPHIC)

def ok_sudo(token: str|None) -> bool:
    return bool(SUDO_TOKEN) and token and token == SUDO_TOKEN

SUDO_RATE = {"window":60,"max":20,"events":[]}
def record_sudo():
    now=time.time()
    SUDO_RATE["events"]=[t for t in SUDO_RATE["events"] if now - t < SUDO_RATE["window"]]
    SUDO_RATE["events"].append(now)
    if len(SUDO_RATE["events"])>SUDO_RATE["max"]:
        raise HTTPException(429,"Too many sudo ops – slow down")

def execute_shell(cmd: str, sudo: bool, token: str|None):
    if is_catastrophic(cmd): raise HTTPException(400,"Command blocked by catastrophic guard")
    if in_quarantine(): raise HTTPException(423,"Quarantine active")
    if sudo and ok_sudo(token): record_sudo()
    return run_shell(cmd)

SYSTEM_PATHS = [r"C:\Windows", r"C:\Program Files", r"C:\Program Files (x86)"]
def is_system_path(path: str)->bool:
    p = os.path.abspath(path)
    return any(p.lower().startswith(sp.lower()) for sp in SYSTEM_PATHS)

def guarded_write(path: str, data: bytes, sudo: bool, token: str|None):
    risk = Risk.high if is_system_path(path) or len(data) > 10_000_000 else Risk.med
    if in_quarantine(): raise HTTPException(423,"Quarantine active")
    if is_system_path(path) and not (sudo and ok_sudo(token)):
        raise HTTPException(403,"System path requires Builder Sudo")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path,"wb") as f: f.write(data)
    return {"wrote": len(data), "path": path, "ts": time.time()}

MESH=None
@app.on_event("startup")
async def _boot():
    # hard error if Firebase vars set but invalid
    fb_vars = (os.getenv("FIREBASE_CRED"), os.getenv("FIREBASE_DB_URL"), os.getenv("FIREBASE_PROJECT"))
    if all(fb_vars):
        try:
            from firebase_bus import start_presence
            start_presence(NODE_ID, ROOM)
        except Exception as e:
            raise RuntimeError(f"Firebase init failed: {e}")
    # mesh (always try local relay)
    from mesh import setup_from_cfg
    global MESH
    MESH = setup_from_cfg(CFG, os.getenv("RELAY_SHARED_SECRET",""), handle_tool)
    MESH.start_bg()

async def handle_tool(msg):
    # for now only shell/write_text/listdir
    tool = msg.get("tool",""); args = msg.get("args",{}); sudo = bool(msg.get("sudo",False)); tok = os.getenv("VIREN_SUDO_TOKEN") if sudo else None
    if tool=="shell":
        res = execute_shell(args.get("cmd",""), sudo, tok)
    elif tool=="write_text":
        res = guarded_write(args.get("path",""), args.get("text","").encode(), sudo, tok)
    elif tool=="listdir":
        res = tool_listdir({}, {"path": args.get("path","C:\\")})
    else:
        res = {"error":"unknown tool"}
    # echo to mesh chat
    if MESH:
        await MESH.send_chat(f"[{NODE_ID}] {tool} -> {str(res)[:160]}")

class ShellIn(BaseModel):
    cmd: str
    sudo: bool = False
    sudo_token: str | None = None

@app.post("/tools/shell")
def api_shell(inp: ShellIn):
    return execute_shell(inp.cmd, inp.sudo, inp.sudo_token)

class WriteIn(BaseModel):
    path: str
    text: str
    sudo: bool = False
    sudo_token: str | None = None

@app.post("/tools/write_text")
def api_write(inp: WriteIn):
    return guarded_write(inp.path, inp.text.encode(), inp.sudo, inp.sudo_token)

class SpeakIn(BaseModel):
    text: str

@app.post("/tts")
def tts(s: SpeakIn):
    audio = tts_elevenlabs(s.text)
    return Response(content=audio, media_type="audio/mpeg")

@app.post("/stt")
async def stt(file: UploadFile = File(...)):
    data = await file.read()
    text = stt_transcribe(data)  # will raise if not configured
    return {"text": text}

class MeshOut(BaseModel): text: str
@app.post("/mesh/send")
async def mesh_send(m: MeshOut):
    if MESH: await MESH.send_chat(m.text)
    return {"ok": True}

@app.get("/healthz")
def healthz():
    ok={"daemon": True}
    try: s=socket.socket(); s.settimeout(2); s.connect(("127.0.0.1",8787)); s.close(); ok["relay"]=True
    except Exception: ok["relay"]=False
    ok["tts_api"]=bool(os.getenv("ELEVENLABS_API_KEY"))
    ok["sudo_enabled"]=bool(os.getenv("VIREN_SUDO_TOKEN"))
    ok["all_good"]= all(ok.values())
    return ok

@app.post("/quarantine/{state}")
def q(state:str):
    set_quarantine(state=="on"); return {"quarantine": state}

from openai_client import openai_chat, OpenAIBlocked
from pydantic import BaseModel as _BaseModel2

class CloudIn(_BaseModel2):
    prompt: str

@app.post("/cloud/chat")
def cloud_chat(inp: CloudIn):
    text, _tok = openai_chat([{"role":"user","content": inp.prompt}], temperature=0.4, max_tokens=800)
    return {"text": text}
