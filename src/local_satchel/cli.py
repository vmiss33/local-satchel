from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from .assets import pack_recommended, start_server, status as server_status, stop_server
from .catalog import DEFAULT_CATALOG_PATH, load_catalog
from .doctor import disk_free_gb, query_nvidia_gpu, summarize_readiness
from .recommend import recommend_for_vram

DEFAULT_TEST_PROMPT = "Reply with exactly: satchel works"
LOCAL_SATCHEL_BASE_URL = "http://127.0.0.1:8080/v1"
LOCAL_SATCHEL_API_KEY = "local-satchel"
HERMES_PROVIDER_KEY = "local-satchel"
HERMES_PROVIDER_NAME = "Local Satchel"
HERMES_API_MODE = "chat_completions"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:  # pragma: no cover - safety net for CLI users
        print(f"Local Satchel error: {exc}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="satchel", description="Pack, run, and connect local AI models.")
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG_PATH), help="Path to model catalog JSON")
    sub = parser.add_subparsers(dest="command", required=True)

    models = sub.add_parser("models", help="Show curated model catalog")
    models.add_argument("--json", action="store_true", help="Output JSON")
    models.set_defaults(func=cmd_models)

    recommend = sub.add_parser("recommend", help="Recommend a model for a detected VRAM size")
    recommend.add_argument("--vram-gb", type=float, required=True, help="Detected GPU VRAM in GB")
    recommend.add_argument("--json", action="store_true", help="Output JSON")
    recommend.set_defaults(func=cmd_recommend)

    doctor = sub.add_parser("doctor", help="Developer alias for check")
    doctor.add_argument("--json", action="store_true", help="Output JSON")
    doctor.set_defaults(func=cmd_doctor)

    check = sub.add_parser("check", help="Check this PC and recommend the right catalog tier")
    check.add_argument("--json", action="store_true", help="Output JSON")
    check.set_defaults(func=cmd_doctor)

    connect = sub.add_parser("connect", help="Configure another app to use Local Satchel")
    connect_sub = connect.add_subparsers(dest="target", required=True)
    hermes = connect_sub.add_parser("hermes", help="Configure Hermes Agent to use Local Satchel")
    hermes.add_argument("--show", action="store_true", help="Print settings without changing Hermes config")
    hermes.set_defaults(func=cmd_connect_hermes)

    status = sub.add_parser("status", help="Show local endpoint status")
    status.add_argument("--json", action="store_true", help="Output JSON")
    status.set_defaults(func=cmd_status)

    pack = sub.add_parser("pack", help="Prepare runtime/model assets")
    pack.add_argument("selection", choices=["recommended"], help="Pack the recommended model")
    pack.set_defaults(func=cmd_pack)

    run = sub.add_parser("run", help="Start the local model server")
    run.set_defaults(func=cmd_run)

    test = sub.add_parser("test", help="Send a test chat request to the local endpoint")
    test.add_argument("--json", action="store_true", help="Output JSON")
    test.add_argument("--prompt", default=DEFAULT_TEST_PROMPT, help="Prompt to send to the local endpoint")
    test.set_defaults(func=cmd_test)

    stop = sub.add_parser("stop", help="Stop the local model server")
    stop.set_defaults(func=cmd_stop)
    return parser


def cmd_models(args: argparse.Namespace) -> int:
    catalog = load_catalog(args.catalog)
    if args.json:
        print(json.dumps(catalog, indent=2))
    else:
        print("Local Satchel model catalog")
        for tier in catalog["vram_tiers"]:
            print(f"- {tier['label']}: {tier.get('recommended_model_id') or 'needs validation'}")
    return 0


def cmd_recommend(args: argparse.Namespace) -> int:
    catalog = load_catalog(args.catalog)
    recommendation = recommend_for_vram(catalog, args.vram_gb)
    if args.json:
        print(json.dumps(recommendation.to_dict(), indent=2))
    else:
        _print_recommendation(recommendation.to_dict())
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    catalog = load_catalog(args.catalog)
    gpu = query_nvidia_gpu()
    if gpu is None:
        payload = {
            "status": "blocked",
            "message": "Local Satchel could not find nvidia-smi or an NVIDIA GPU.",
        }
    else:
        recommendation = recommend_for_vram(catalog, gpu.vram_gb)
        summary = summarize_readiness(
            gpu_name=gpu.name,
            detected_vram_gb=gpu.vram_gb,
            driver_version=gpu.driver_version,
            disk_free_gb=disk_free_gb(),
            recommendation_model_name=recommendation.model.get("display_name") if recommendation.model else None,
            tier_label=recommendation.tier_label,
            is_fallback=recommendation.is_fallback,
        )
        payload = {
            "status": summary.status,
            "message": summary.message,
            "gpu": {
                "name": gpu.name,
                "vram_mb": gpu.vram_mb,
                "vram_gb": gpu.vram_gb,
                "driver_version": gpu.driver_version,
            },
            "recommendation": recommendation.to_dict(),
        }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(payload["message"])
    return 0 if payload["status"] != "blocked" else 2


def cmd_connect_hermes(args: argparse.Namespace) -> int:
    model_name = hermes_model_name(args.catalog)
    if args.show:
        print_hermes_settings(model_name)
        return 0
    try:
        configure_hermes(model_name)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print("Hermes configured to use Local Satchel.")
    print(f"Provider: {HERMES_PROVIDER_NAME}")
    print(f"Base URL: {LOCAL_SATCHEL_BASE_URL}")
    print(f"Model: {model_name}")
    print("Start a new Hermes session for the config change to take effect.")
    print("Keep Local Satchel running while Hermes uses this local model.")
    return 0


def hermes_model_name(catalog_path: str) -> str:
    catalog = load_catalog(catalog_path)
    recommendation = recommend_for_vram(catalog, 8)
    return recommendation.model["filename"] if recommendation.model else "local-satchel"


def print_hermes_settings(model_name: str) -> None:
    print("Local Satchel Hermes/OpenAI-compatible settings")
    print(f"Base URL: {LOCAL_SATCHEL_BASE_URL}")
    print(f"API key: {LOCAL_SATCHEL_API_KEY}")
    print(f"Model: {model_name}")
    print("Keep the server bound to 127.0.0.1 unless you explicitly enable LAN access later.")


def configure_hermes(model_name: str, hermes_command: str = "hermes") -> None:
    if shutil.which(hermes_command) is None:
        raise RuntimeError(
            "Hermes Agent was not found on PATH. Install Hermes first, or run "
            "`satchel connect hermes --show` and paste the settings manually."
        )

    settings = [
        (f"providers.{HERMES_PROVIDER_KEY}.name", HERMES_PROVIDER_NAME),
        (f"providers.{HERMES_PROVIDER_KEY}.base_url", LOCAL_SATCHEL_BASE_URL),
        (f"providers.{HERMES_PROVIDER_KEY}.api_key", LOCAL_SATCHEL_API_KEY),
        (f"providers.{HERMES_PROVIDER_KEY}.default_model", model_name),
        (f"providers.{HERMES_PROVIDER_KEY}.api_mode", HERMES_API_MODE),
        ("model.provider", HERMES_PROVIDER_KEY),
        ("model.default", model_name),
    ]
    for key, value in settings:
        command = [hermes_command, "config", "set", key, value]
        result = subprocess.run(command, text=True, capture_output=True, check=False)
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "unknown error").strip()
            raise RuntimeError(f"Hermes config update failed for {key}: {detail}")


def cmd_status(args: argparse.Namespace) -> int:
    payload = server_status()
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        if payload["status"] == "running":
            print(f"Local Satchel is running at {payload['base_url']} (PID {payload['pid']}).")
        elif payload["status"] == "stale":
            print("Local Satchel has a recorded PID, but the health check is not responding.")
        else:
            print("Local Satchel is not running.")
    return 0


def cmd_pack(args: argparse.Namespace) -> int:
    catalog = load_catalog(args.catalog)
    gpu = query_nvidia_gpu()
    if gpu is None:
        print("Local Satchel could not find an NVIDIA GPU. Pack stopped before downloading.", file=sys.stderr)
        return 2
    recommendation = recommend_for_vram(catalog, gpu.vram_gb)
    assets = pack_recommended(recommendation)
    print("Packing complete.")
    print(f"Runtime: {assets.runtime_dir}")
    print(f"CUDA DLLs: {assets.cuda_dll_dir}")
    print(f"Model: {assets.model_path}")
    print(f"Selected: {assets.model['display_name']}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    result = start_server(host="127.0.0.1", port=8080)
    print("Local Satchel is running.")
    print("Endpoint: http://127.0.0.1:8080/v1")
    print(f"Health: {result['health']}")
    return 0


def cmd_test(args: argparse.Namespace) -> int:
    result = test_endpoint(prompt=args.prompt)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("Local Satchel test passed.")
        print(f"Endpoint: {result['base_url']}")
        print(f"Model: {result['model']}")
        print(f"Response: {result['content']}")
        if result.get("completion_tokens") is not None:
            print(f"Completion tokens: {result['completion_tokens']}")
    return 0


def cmd_stop(args: argparse.Namespace) -> int:
    result = stop_server()
    print(json.dumps(result, indent=2))
    return 0


def _print_recommendation(data: dict[str, Any]) -> None:
    print(f"Tier: {data['tier_label']}")
    if data["model_name"]:
        label = "Temporary safe fallback" if data["is_fallback"] else "Recommended"
        print(f"{label}: {data['model_name']}")
        print(f"File: {data['filename']}")
    else:
        print("No validated automatic model for this tier yet.")
    if data["candidate_model_ids"]:
        print("Advanced/research candidates:")
        for model_id in data["candidate_model_ids"]:
            print(f"- {model_id}")
    print(data["user_message"])


def test_endpoint(host: str = "127.0.0.1", port: int = 8080, prompt: str = DEFAULT_TEST_PROMPT) -> dict[str, Any]:
    base_url = f"http://{host}:{port}/v1"
    payload = {
        "model": "local-satchel",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 32,
        "temperature": 0,
    }
    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8", errors="replace"))
    except urllib.error.URLError as exc:
        raise RuntimeError("Local endpoint is not responding. Run: satchel run") from exc

    choice = data.get("choices", [{}])[0]
    message = choice.get("message", {})
    content = message.get("content") or ""
    if not content.strip():
        raise RuntimeError("Local endpoint responded, but the chat content was empty")
    return {
        "status": "ok",
        "base_url": base_url,
        "model": data.get("model"),
        "content": content.strip(),
        "completion_tokens": data.get("usage", {}).get("completion_tokens"),
    }


if __name__ == "__main__":
    raise SystemExit(main())
