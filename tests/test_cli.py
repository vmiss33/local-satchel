import json
import subprocess
import sys
from pathlib import Path

import local_satchel.cli as cli
from local_satchel.catalog import DEFAULT_CATALOG_PATH


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "local_satchel.cli", *args],
        text=True,
        capture_output=True,
        check=False,
    )


def test_models_command_outputs_catalog_tiers_as_json():
    result = run_cli("models", "--json")

    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["version"] == 1
    assert any(tier["tier_id"] == "vram-12gb" for tier in data["vram_tiers"])


def test_recommend_command_for_12gb_reports_explicit_tier_and_fallback():
    result = run_cli("recommend", "--vram-gb", "12", "--json")

    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["tier_id"] == "vram-12gb"
    assert data["model_id"] == "nvidia-nemotron-3-nano-4b-q4-k-m"
    assert data["is_fallback"] is True
    assert data["can_auto_download"] is True
    assert data["candidate_model_ids"] == ["llama-3-1-nemotron-nano-8b-q4-k-m"]


def test_connect_hermes_show_prints_localhost_openai_settings():
    result = run_cli("connect", "hermes", "--show")

    assert result.returncode == 0, result.stderr
    assert "http://127.0.0.1:8080/v1" in result.stdout
    assert "NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf" in result.stdout


def test_connect_hermes_configures_hermes_with_named_local_satchel_provider(monkeypatch, capsys):
    calls = []

    def fake_which(command):
        assert command == "hermes"
        return "C:/Users/melis/AppData/Local/hermes/bin/hermes.exe"

    def fake_run(command, text, capture_output, check):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    monkeypatch.setattr(cli.shutil, "which", fake_which)
    monkeypatch.setattr(cli.subprocess, "run", fake_run)

    result = cli.main(["connect", "hermes"])

    assert result == 0
    assert calls == [
        ["hermes", "config", "set", "providers.local-satchel.name", "Local Satchel"],
        ["hermes", "config", "set", "providers.local-satchel.base_url", "http://127.0.0.1:8080/v1"],
        ["hermes", "config", "set", "providers.local-satchel.api_key", "local-satchel"],
        ["hermes", "config", "set", "providers.local-satchel.default_model", "NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf"],
        ["hermes", "config", "set", "providers.local-satchel.api_mode", "chat_completions"],
        ["hermes", "config", "set", "model.provider", "local-satchel"],
        ["hermes", "config", "set", "model.default", "NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf"],
    ]
    out = capsys.readouterr().out
    assert "Hermes configured to use Local Satchel." in out
    assert "Start a new Hermes session" in out


def test_connect_hermes_configures_named_hermes_profile(monkeypatch, capsys):
    calls = []

    monkeypatch.setattr(cli.shutil, "which", lambda command: "hermes")

    def fake_run(command, text, capture_output, check):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    monkeypatch.setattr(cli.subprocess, "run", fake_run)

    result = cli.main(["connect", "hermes", "--profile", "ambrosia"])

    assert result == 0
    assert calls[0] == [
        "hermes",
        "--profile",
        "ambrosia",
        "config",
        "set",
        "providers.local-satchel.name",
        "Local Satchel",
    ]
    assert calls[-1] == [
        "hermes",
        "--profile",
        "ambrosia",
        "config",
        "set",
        "model.default",
        "NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf",
    ]
    out = capsys.readouterr().out
    assert "Hermes profile: ambrosia" in out
    assert "hermes --profile ambrosia" in out


def test_connect_hermes_profile_base_alias_configures_default_profile(monkeypatch, capsys):
    calls = []

    monkeypatch.setattr(cli.shutil, "which", lambda command: "hermes")
    monkeypatch.setattr(
        cli.subprocess,
        "run",
        lambda command, text, capture_output, check: calls.append(command)
        or subprocess.CompletedProcess(command, 0, stdout="ok", stderr=""),
    )

    result = cli.main(["connect", "hermes", "--profile", "base"])

    assert result == 0
    assert all("--profile" not in command for command in calls)
    assert "Hermes profile: default" in capsys.readouterr().out


def test_connect_hermes_reports_missing_hermes_without_touching_config(monkeypatch, capsys):
    monkeypatch.setattr(cli.shutil, "which", lambda command: None)

    result = cli.main(["connect", "hermes"])

    assert result == 2
    err = capsys.readouterr().err
    assert "Hermes Agent was not found" in err


def test_default_catalog_path_is_package_data_for_installed_satchel_command():
    path = Path(DEFAULT_CATALOG_PATH)

    assert path.exists()
    assert path.name == "models.json"
    assert path.parts[-3:] == ("local_satchel", "model_catalog", "models.json")


def test_packaged_catalog_matches_repository_catalog():
    repo_catalog_path = Path(__file__).resolve().parents[1] / "model-catalog" / "models.json"

    assert json.loads(Path(DEFAULT_CATALOG_PATH).read_text()) == json.loads(repo_catalog_path.read_text())


def test_check_command_is_normal_user_alias_for_doctor():
    result = run_cli("check", "--json")

    assert result.returncode in (0, 2), result.stderr
    data = json.loads(result.stdout)
    assert data["status"] in {"ready", "blocked"}


def test_test_command_reports_endpoint_response(monkeypatch, capsys):
    def fake_test_endpoint(host="127.0.0.1", port=8080, prompt=cli.DEFAULT_TEST_PROMPT):
        return {
            "status": "ok",
            "base_url": "http://127.0.0.1:8080/v1",
            "model": "NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf",
            "content": "satchel works",
            "completion_tokens": 4,
        }

    monkeypatch.setattr(cli, "test_endpoint", fake_test_endpoint)

    result = cli.main(["test"])

    assert result == 0
    assert "Local Satchel test passed." in capsys.readouterr().out


def test_build_parser_exposes_normal_user_commands():
    parser = cli.build_parser()
    commands_action = next(action for action in parser._actions if action.dest == "command")

    assert {"check", "pack", "run", "connect", "test", "stop"}.issubset(commands_action.choices)
