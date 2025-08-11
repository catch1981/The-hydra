
import os, pathlib, time
def _resolve(path):
    return str(pathlib.Path(path).expanduser().resolve())
def tool_listdir(policy, args):
    base = _resolve(args.get("path","C:\\"))
    items = []
    for entry in os.scandir(base):
        try: items.append({"name": entry.name, "is_dir": entry.is_dir(), "size": entry.stat().st_size})
        except Exception: pass
    return {"path": base, "items": items}
def tool_write_text(policy, args):
    base = _resolve(args["path"]); data = args["text"].encode("utf-8")
    os.makedirs(os.path.dirname(base), exist_ok=True)
    with open(base, "wb") as f: f.write(data)
    return {"wrote": len(data), "path": base, "ts": time.time()}
