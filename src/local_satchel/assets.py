from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .catalog import load_catalog
from .recommend import Recommendation

APP_DIR = Path.home() / "AppData" / "Local" / "LocalSatchel"
RUNTIME_DIR = APP_DIR / "runtime"
MODEL_DIR = APP_DIR / "models"
LOG_DIR = APP_DIR / "logs"
STATE_PATH = APP_DIR / "state.json"

LLAMA_TAG = "b9453"
RUNTIME_ZIP_NAME = "llama-b9453-bin-win-cuda-12.4-x64.zip"
CUDART_ZIP_NAME = "cudart-llama-bin-win-cuda-12.4-x64.zip"
RUNTIME_URL = f"https://github.com/ggml-org/llama.cpp/releases/download/{LLAMA_TAG}/{RUNTIME_ZIP_NAME}"
CUDART_URL = f"https://github.com/ggml-org/llama.cpp/releases/download/{LLAMA_TAG}/{CUDART_ZIP_NAME}"
RUNTIME_EXTRACT_DIR = RUNTIME_DIR / "llama-b9453-bin-win-cuda-12.4-x64"
CUDART_EXTRACT_DIR = RUNTIME_DIR / "cudart-llama-bin-win-cuda-12.4-x64"
SPIKE_DIR = Path.home() / "LocalSatchelSpike"


@dataclass(frozen=True)
class PackedAssets:
    runtime_dir: Path
    cuda_dll_dir: Path
    server_path: Path
    model_path: Path
    model: dict[str, Any]


def ensure_dirs() -> None:
    for path in (APP_DIR, RUNTIME_DIR, MODEL_DIR, LOG_DIR):
        path.mkdir(parents=True, exist_ok=True)


def pack_recommended(recommendation: Recommendation) -> PackedAssets:
    if recommendation.model is None or not recommendation.can_auto_download:
        raise RuntimeError("No validated automatic model is available for this GPU tier")
    ensure_dirs()
    runtime_zip = RUNTIME_DIR / RUNTIME_ZIP_NAME
    cudart_zip = RUNTIME_DIR / CUDART_ZIP_NAME
    _obtain_file(runtime_zip, RUNTIME_URL, _spike_runtime_zip())
    _obtain_file(cudart_zip, CUDART_URL, _spike_cudart_zip())
    _extract_zip(runtime_zip, RUNTIME_EXTRACT_DIR)
    _extract_zip(cudart_zip, CUDART_EXTRACT_DIR)
    model_path = MODEL_DIR / recommendation.model["filename"]
    _obtain_file(model_path, recommendation.model["source_url"], _spike_model_path(recommendation.model["filename"]))
    server_path = RUNTIME_EXTRACT_DIR / "llama-server.exe"
    if not server_path.exists():
        raise RuntimeError(f"llama-server.exe was not found at {server_path}")
    if not model_path.exists():
        raise RuntimeError(f"Model was not found at {model_path}")
    state = _read_state()
    state["packed"] = {
        "runtime_dir": str(RUNTIME_EXTRACT_DIR),
        "cuda_dll_dir": str(CUDART_EXTRACT_DIR),
        "server_path": str(server_path),
        "model_path": str(model_path),
        "model_id": recommendation.model["id"],
        "model_filename": recommendation.model["filename"],
        "run_args": recommendation.model.get("run_args", []),
    }
    _write_state(state)
    return PackedAssets(RUNTIME_EXTRACT_DIR, CUDART_EXTRACT_DIR, server_path, model_path, recommendation.model)


def start_server(host: str = "127.0.0.1", port: int = 8080) -> dict[str, Any]:
    state = _read_state()
    packed = state.get("packed")
    if not packed:
        raise RuntimeError("Nothing is packed yet. Run: satchel pack recommended")
    if is_port_listening(port):
        raise RuntimeError(f"Port {port} is already listening. Stop the existing server or choose another port later.")
    server_path = Path(packed["server_path"])
    model_path = Path(packed["model_path"])
    runtime_dir = Path(packed["runtime_dir"])
    cuda_dll_dir = Path(packed["cuda_dll_dir"])
    log_path = LOG_DIR / "llama-server.log"
    env = os.environ.copy()
    env["PATH"] = f"{cuda_dll_dir}{os.pathsep}{runtime_dir}{os.pathsep}{env.get('PATH', '')}"
    args = [str(server_path), "--model", str(model_path), "--host", host, "--port", str(port)]
    args.extend(packed.get("run_args") or ["--ctx-size", "4096", "--n-gpu-layers", "-1", "--jinja", "--reasoning", "off"])
    log_file = log_path.open("w", encoding="utf-8", errors="replace")
    proc = subprocess.Popen(args, cwd=str(runtime_dir), env=env, stdout=log_file, stderr=subprocess.STDOUT)
    state["server"] = {
        "pid": proc.pid,
        "host": host,
        "port": port,
        "base_url": f"http://{host}:{port}/v1",
        "log_path": str(log_path),
        "model_path": str(model_path),
    }
    _write_state(state)
    return wait_for_server(port=port, timeout_seconds=60)


def wait_for_server(port: int = 8080, timeout_seconds: int = 60) -> dict[str, Any]:
    deadline = time.time() + timeout_seconds
    last_error = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2) as response:
                body = response.read().decode("utf-8", errors="replace")
                return {"status": "running", "health": body, "port": port}
        except Exception as exc:  # noqa: BLE001 - report last readiness error
            last_error = str(exc)
            time.sleep(1)
    raise RuntimeError(f"Server did not become healthy within {timeout_seconds}s: {last_error}")


def stop_server() -> dict[str, Any]:
    state = _read_state()
    server = state.get("server")
    if not server:
        return {"status": "not-running", "message": "No Local Satchel server PID is recorded."}
    pid = int(server["pid"])
    result = subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], text=True, capture_output=True, check=False)
    time.sleep(1)
    state.pop("server", None)
    _write_state(state)
    return {"status": "stopped", "pid": pid, "taskkill_returncode": result.returncode, "output": result.stdout + result.stderr}


def status() -> dict[str, Any]:
    state = _read_state()
    server = state.get("server")
    if not server:
        return {"status": "not-running"}
    port = int(server["port"])
    return {**server, "status": "running" if is_port_listening(port) else "stale"}


def is_port_listening(port: int) -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1):
            return True
    except Exception:
        return False


def _obtain_file(destination: Path, url: str, local_source: Path | None = None) -> None:
    if destination.exists() and destination.stat().st_size > 0:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    if local_source and local_source.exists():
        shutil.copy2(local_source, destination)
        return
    with urllib.request.urlopen(url) as response, destination.open("wb") as handle:
        shutil.copyfileobj(response, handle)


def _extract_zip(zip_path: Path, destination: Path) -> None:
    if destination.exists() and any(destination.iterdir()):
        return
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(destination)


def _read_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def _write_state(state: dict[str, Any]) -> None:
    ensure_dirs()
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _spike_runtime_zip() -> Path | None:
    path = SPIKE_DIR / "runtime" / RUNTIME_ZIP_NAME
    return path if path.exists() else None


def _spike_cudart_zip() -> Path | None:
    path = SPIKE_DIR / "runtime" / CUDART_ZIP_NAME
    return path if path.exists() else None


def _spike_model_path(filename: str) -> Path | None:
    path = SPIKE_DIR / "models" / filename
    return path if path.exists() else None
