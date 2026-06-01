# Local Satchel Architecture

## Architecture goal

Separate the product experience from the runtime plumbing.

The GUI should be a friendly wizard. The core should be a testable engine that can run as a CLI. Platform-specific checks should be isolated so Windows can be implemented first without blocking future Linux support.

## High-level architecture

```text
Local Satchel Desktop App
        |
        v
Local Satchel Core CLI / Engine
        |
        +-- System checker
        +-- Model recommender
        +-- Runtime manager
        +-- Model cache manager
        +-- Server process manager
        +-- Connection profile generator
        |
        v
llama.cpp CUDA server
        |
        v
OpenAI-compatible localhost endpoint
        |
        v
Hermes / Continue / Open WebUI / other apps
```

## Core components

### 1. System checker

Responsible for readiness detection.

Windows checks:

- OS version
- NVIDIA GPU presence
- GPU name
- VRAM
- NVIDIA driver availability
- disk space
- internet connectivity
- local port availability

Implementation notes:

- Prefer `nvidia-smi` when available.
- Fall back to PowerShell/CIM/WMI only if needed.
- Return structured JSON, not prose.
- Convert structured results into friendly copy in the UI layer.

### 2. Model catalog

A curated metadata file that maps model options to hardware recommendations.

Initial file:

```text
model-catalog/models.json
```

Fields:

- id
- display_name
- family
- source_url
- license
- filename
- quantization
- download_size_gb
- min_vram_gb
- recommended_vram_gb
- context_size_default
- notes

### 3. Model recommender

Input:

- GPU VRAM
- system RAM
- free disk
- model catalog

Output:

- best choice
- smaller/faster option
- higher-quality option if available
- incompatible models with reasons

Rule:

The normal user sees one recommended model. Advanced users can inspect alternatives.

### 4. Runtime manager

Responsible for preparing llama.cpp CUDA.

Responsibilities:

- determine correct runtime package
- download runtime
- verify binary exists
- verify launchability
- store runtime version metadata

V1 should avoid requiring users to install CUDA manually.

### 5. Model cache manager

Responsibilities:

- create Local Satchel model directory
- download selected GGUF
- verify file size/checksum when available
- resume or skip existing downloads when safe
- delete downloaded models at user request

### 6. Server process manager

Responsibilities:

- start llama.cpp server
- capture logs
- detect readiness
- stop/restart server
- recover from failed starts
- keep server bound to localhost by default

Default endpoint:

```text
http://localhost:8080/v1
```

### 7. Connection profile generator

Produces copy-paste settings for apps.

Generic OpenAI-compatible profile:

```text
Base URL: http://localhost:8080/v1
API Key: local-satchel
Model: local-satchel
```

Hermes profile:

See `examples/hermes/provider-config.md`.

## CLI-first design

Even if the primary UX is graphical, the core should expose a CLI:

```bash
satchel doctor --json
satchel models --json
satchel pack recommended
satchel run
satchel status --json
satchel stop
satchel connect hermes
```

Benefits:

- easier testing
- easier automation
- easier debugging
- easier portfolio demonstration
- GUI can call stable commands/APIs

## Suggested implementation stack

This is intentionally not locked yet.

Strong option:

- Go core CLI for single-binary distribution
- Tauri desktop app for lightweight Windows GUI
- JSON boundary between GUI and CLI

Alternative faster prototype:

- Python core CLI
- Textual or simple web UI for prototype
- Later port core to Go/Rust if needed

Decision criteria:

- Windows distribution simplicity
- ability to manage child processes reliably
- easy testing of command execution
- minimal dependency burden for nontechnical users

## Security and safety

- Bind to `127.0.0.1` by default.
- Do not expose LAN access without explicit user consent.
- Do not run privileged commands silently.
- Do not collect prompts or model outputs.
- Do not auto-delete user files.
- Store downloaded models in app-owned directories.
- Keep logs local.

## Observability

Local Satchel should keep:

- user-friendly status events
- technical log file
- latest startup command with sensitive values redacted
- runtime version
- model version/file metadata

Logs should be available through **Open logs**.

## Testing strategy

### Unit tests

- Parse sample `nvidia-smi` output.
- Recommend models for VRAM levels.
- Generate server commands.
- Parse health check responses.
- Map technical errors to friendly messages.

### Integration tests

- Start a mocked server and verify status detection.
- Exercise download/cache logic with small fixture files.
- Validate model catalog schema.

### Manual hardware tests

Required because this assistant is not running on Windows and cannot validate NVIDIA GPU behavior here.

- Windows 11 + 8 GB NVIDIA GPU
- Windows 11 + 12 GB NVIDIA GPU
- Windows 11 + 16/24 GB NVIDIA GPU if available
- Driver missing/outdated scenario if possible
- Port conflict scenario
- interrupted download scenario

## Known architecture risk

The development environment for this planning package is Linux, not Windows. Windows-specific detection and llama.cpp CUDA behavior must be validated on a real Windows NVIDIA system before implementation decisions are treated as final.
