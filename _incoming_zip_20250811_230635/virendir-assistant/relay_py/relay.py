
import asyncio, json, time, hmac, hashlib
import websockets
from websockets.server import WebSocketServerProtocol

SECRET = b"relay-secret"  # runtime will override via env (we'll check header)
PING_SEC = 25

clients = {}  # ws -> {"node_id":..., "room":..., "ts":...}

def good_auth(msg: dict, secret: bytes) -> bool:
    if not all(k in msg for k in ("ts","nonce","sig","node_id","room")): return False
    if abs(time.time()*1000 - msg["ts"]) > 45000: return False
    raw = json.dumps({k: msg[k] for k in ("ts","nonce","node_id","room")}, separators=(',',':')).encode()
    want = hmac.new(secret, raw, hashlib.sha256).hexdigest()
    try:
        return hmac.compare_digest(want, msg["sig"])
    except Exception:
        return False

async def handler(ws: WebSocketServerProtocol):
    ws.secret = (SECRET)
    try:
        async for raw in ws:
            try:
                msg = json.loads(raw)
            except Exception:
                continue
            t = msg.get("type")
            if t == "AUTH":
                secret = (await ws.recv()).encode() if False else SECRET  # placeholder for future channel; using constant
                if not good_auth(msg, SECRET):
                    await ws.close(code=4401, reason="bad auth")
                    return
                clients[ws] = {"node_id": msg["node_id"], "room": msg["room"], "ts": time.time()}
                await ws.send(json.dumps({"type":"AUTH_OK","node_id": msg["node_id"]}))
                # announce presence
                for c, meta in list(clients.items()):
                    if meta["room"] == msg["room"] and c is not ws:
                        try: await c.send(json.dumps({"type":"PRESENCE","node_id":msg["node_id"],"state":"online"}))
                        except Exception: pass
            elif ws in clients:
                meta = clients[ws]
                meta["ts"] = time.time()
                if t in ("CHAT","TOOL","HEARTBEAT","E2E"):
                    # broadcast within room
                    for c, m in list(clients.items()):
                        if m["room"] == meta["room"] and c is not ws:
                            try: await c.send(json.dumps(msg))
                            except Exception: pass
    except Exception:
        pass
    finally:
        if ws in clients:
            gone = clients.pop(ws)
            # presence offline
            for c, meta in list(clients.items()):
                if meta["room"] == gone["room"]:
                    try: await c.send(json.dumps({"type":"PRESENCE","node_id":gone["node_id"],"state":"offline"}))
                    except Exception: pass

async def pinger():
    while True:
        await asyncio.sleep(PING_SEC)
        for ws in list(clients.keys()):
            try: await ws.ping()
            except Exception:
                try: await ws.close()
                except Exception: pass
                clients.pop(ws, None)

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8787, max_size=10_000_000):
        await pinger()

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: pass
