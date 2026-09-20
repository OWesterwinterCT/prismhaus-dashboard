"""Start an isolated local server, check HTTP readiness, then stop it."""
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen

root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryFile(mode="w+") as log:
    process=subprocess.Popen([
        sys.executable,"-m","streamlit","run","app.py",
        "--server.address=127.0.0.1","--server.port=8765",
        "--browser.serverAddress=localhost","--server.headless=true",
    ],cwd=root,stdout=log,stderr=subprocess.STDOUT)
    try:
        ready=False
        for _ in range(40):
            if process.poll() is not None:
                break
            try:
                with urlopen("http://127.0.0.1:8765/_stcore/health",timeout=1) as response:
                    ready=response.status==200 and response.read()==b"ok"
                if ready:
                    break
            except OSError:
                time.sleep(.25)
        if not ready:
            log.seek(0)
            raise RuntimeError("Streamlit did not become ready.\n"+log.read())
        with urlopen("http://127.0.0.1:8765",timeout=5) as response:
            assert response.status==200
            assert b"Streamlit" in response.read()
        print("PASS: local Streamlit health endpoint and application shell returned HTTP 200.")
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
