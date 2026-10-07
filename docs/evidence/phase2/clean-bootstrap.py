"""Reproduce documented setup in a disposable source copy with fresh dependencies."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import tempfile
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "docs/evidence/phase2"
results = []

def run(args, cwd, env, name):
    log = EVIDENCE / ("bootstrap-" + name + ".log")
    with log.open("w") as output:
        result = subprocess.run(args, cwd=cwd, env=env, stdout=output, stderr=subprocess.STDOUT)
    results.append({"step": name, "exit_code": result.returncode, "log": log.name})
    if result.returncode:
        raise RuntimeError(f"{name} failed; see {log.name}")

with tempfile.TemporaryDirectory(prefix="public-agent-store-bootstrap-") as directory:
    checkout = Path(directory) / "source"
    shutil.copytree(ROOT, checkout, ignore=shutil.ignore_patterns(".git", "node_modules", "dist", "web-dist", ".venv", "venv", "__pycache__", ".env*", ".DS_Store"))
    env = {key: value for key, value in os.environ.items()
           if not re.search(r"TOKEN|SECRET|PASSWORD|API_KEY|DATABASE|CREDENTIAL|AUTH", key, re.I)}
    run(["python3", "-m", "venv", ".venv"], checkout, env, "venv")
    python = checkout / ".venv/bin/python"
    env["PATH"] = str(python.parent) + os.pathsep + env["PATH"]
    env["PYTHON"] = str(python)
    run([str(python), "-m", "pip", "install", "-r", "requirements.txt"], checkout, env, "python-install")
    for name, args in [
        ("npm-ci", ["npm", "ci"]),
        ("generate", ["npm", "run", "generate"]),
        ("python-tests", [str(python), "-m", "unittest", "discover", "-s", "tests", "-v"]),
        ("node-tests", ["npm", "test"]),
        ("typecheck", ["npm", "run", "typecheck"]),
        ("build", ["npm", "run", "build"]),
        ("host", ["npm", "run", "check:host"]),
    ]:
        run(args, checkout, env, name)
    compare = {}
    for file in ["README.md", "site/catalog.json", "site/data.js", "src/generated/enums.ts", "web-dist/index.html"]:
        compare[file] = (checkout / file).read_bytes() == (ROOT / file).read_bytes()
    assert all(compare.values()), compare
    server_log = EVIDENCE / "bootstrap-start.log"
    with server_log.open("w") as output:
        server = subprocess.Popen(["npm", "run", "start", "--", "--port", "3001"], cwd=checkout, env=env, stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            html = None
            for _ in range(60):
                if server.poll() is not None:
                    raise RuntimeError("fresh server exited before readiness")
                try:
                    html = urllib.request.urlopen("http://localhost:3001", timeout=2).read().decode()
                    break
                except OSError:
                    time.sleep(0.1)
            assert html and "Agent" in html
            refs = re.findall(r'(?:src|href)="([^" ]+)"', html)
            assets = {}
            for ref in refs:
                if ref.startswith("./assets/"):
                    assets[ref] = len(urllib.request.urlopen("http://localhost:3001/" + ref[2:], timeout=3).read())
            assert any(ref.endswith(".js") for ref in assets) and any(ref.endswith(".css") for ref in assets)
            catalog_name = next((checkout / "web-dist/assets").glob("catalog-*.json")).name
            public = json.loads(urllib.request.urlopen("http://localhost:3001/assets/" + catalog_name, timeout=3).read())
            assert len(public["resources"]["resources"]) == 20
            results.append({"step": "start", "exit_code": 0, "http_status": 200, "resource_count": 20, "assets": assets})
        finally:
            if server.poll() is None:
                os.killpg(server.pid, signal.SIGTERM)
            server.wait(timeout=10)
    report = {"steps": results, "source_generated_and_entry_equal": compare, "fresh_dependencies": True, "private_source_required": False, "temporary_source_copy_cleaned": True}
(EVIDENCE / "clean-bootstrap.json").write_text(json.dumps(report, indent=2) + "\n")
print("PASS: fresh dependencies, documented commands, host package and production startup; temporary source copy removed")
