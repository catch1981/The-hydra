
import asyncio, json, os, time, uuid, threading, websockets

def setup_from_cfg(cfg, secret, on_tool):
    return MeshClient(cfg["mesh"].get("relays",["ws://127.0.0.1:8787"]), cfg["mesh"]["room"], cfg["mesh"]["node_id"], on_tool)

class MeshClient:
    def __init__(self, relays, room, node_id, on_tool):
        self.relays=relays; self.room=room; self.node_id=node_id; self.on_tool=on_tool; self.ws=None; self.stop=False

    async def _loop(self):
        while not self.stop:
            for url in self.relays:
                try:
                    async with websockets.connect(url, max_size=10_000_000) as ws:
                        self.ws=ws
                        await ws.send(json.dumps({"type":"AUTH","node_id":self.node_id,"room":self.room,"ts":int(time.time()*1000),"nonce":str(uuid.uuid4()),"sig":"DEV"}))
                        await ws.send(json.dumps({"type":"CHAT","text":f"[{self.node_id}] online"}))
                        async for raw in ws:
                            msg=json.loads(raw)
                            if msg.get("type")=="TOOL":
                                asyncio.create_task(self.on_tool(msg))
                except Exception:
                    await asyncio.sleep(3)

    def start_bg(self):
        def runner(): asyncio.run(self._loop())
        threading.Thread(target=runner, daemon=True).start()

    async def send_chat(self, text):
        try:
            if self.ws: await self.ws.send(json.dumps({"type":"CHAT","text":text[:8000]}))
        except Exception: pass
