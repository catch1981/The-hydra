
import subprocess, shlex
def run_shell(cmd: str):
    proc = subprocess.run(shlex.split(cmd), capture_output=True, text=True, timeout=90)
    return {"code": proc.returncode, "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-4000:]}
