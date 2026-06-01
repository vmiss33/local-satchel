# Local Satchel

Pack, run, and connect local AI models.

Local Satchel turns your NVIDIA GPU into a local AI endpoint. It checks your PC, recommends a compatible model, downloads the right local runtime, starts an OpenAI-compatible server, and gives you connection settings for apps and agents like Hermes.

No manual CUDA setup. No model-server guesswork.

## What Local Satchel is

Local Satchel is a cross-platform local AI setup assistant. The first implementation target is Windows 11 with NVIDIA GPUs using llama.cpp CUDA builds and curated GGUF models.

The product is not Windows-only and not tied to one model host. Windows is the first beachhead because it is a high-friction environment for nontechnical local AI users.

## V1 promise

A normal user should be able to:

1. Open Local Satchel.
2. Click **Check my PC**.
3. Accept the recommended model.
4. Click **Pack**.
5. Click **Run**.
6. Test a local chat response.
7. Copy connection settings into Hermes or another OpenAI-compatible app.

## V1 scope

- Windows 11 initial target
- NVIDIA GPU required
- llama.cpp CUDA runtime
- Curated GGUF model catalog
- OpenAI-compatible local endpoint
- Built-in test chat
- Copy-paste Hermes/OpenAI-compatible connection settings

## Repository layout

```text
local-satchel/
  src/
    local_satchel/
      assets.py
      catalog.py
      cli.py
      doctor.py
      recommend.py
      model_catalog/
        models.json

  docs/
    PRD.md
    UX.md
    ROADMAP.md
    ARCHITECTURE.md
    research/
      windows-llamacpp-cuda-spike.md
  examples/
    hermes/
      provider-config.md
  model-catalog/
    models.json
```

## How this is meant to work

Local Satchel is the bridge between Hermes Agent and your NVIDIA GPU.

The intended first-run flow is:

1. Install Hermes Agent, but do not configure a cloud model yet.
2. Install Local Satchel.
3. Run Local Satchel's local model server on `127.0.0.1`.
4. Point Hermes Agent at the Local Satchel OpenAI-compatible endpoint.
5. Use Hermes Agent normally, backed by the model running on your own PC.

In other words: Hermes Agent is the assistant interface. Local Satchel is the local model pack, runner, and connection helper.

## Step 1: Install Hermes Agent first

Install Hermes Agent before Local Satchel so there is already an assistant app ready to connect.

Follow the Hermes Agent install instructions:

```text
https://hermes-agent.nousresearch.com/docs
```

Stop after installing Hermes Agent. Do not run the model/provider setup wizard yet, and do not configure a cloud provider unless you want one separately.

## Step 2: Install Local Satchel on Windows

Open PowerShell and paste this one command:

```powershell
powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/vmiss33/local-satchel/main/scripts/install-local-satchel.ps1 | iex"
```

The installer:

- installs Python for you with Windows Package Manager if Python is missing
- creates Local Satchel's app environment under `C:\Users\<you>\AppData\Local\LocalSatchel`
- installs the `satchel` command
- checks your PC when installation finishes

After Local Satchel is installed, open a new terminal and run:

```powershell
satchel check
satchel pack recommended
satchel run
satchel test
```

What those commands do:

- `satchel check` checks your NVIDIA GPU, VRAM, driver, and free disk space.
- `satchel pack recommended` downloads/prepares the recommended local runtime and model.
- `satchel run` starts the local OpenAI-compatible server on `127.0.0.1:8080`.
- `satchel test` sends a real chat request to make sure the endpoint works.

## Step 3: Connect Hermes Agent to Local Satchel

With Local Satchel still running, print the Hermes connection settings:

```powershell
satchel connect hermes
```

Local Satchel currently provides these OpenAI-compatible settings:

```text
Base URL: http://127.0.0.1:8080/v1
API key: local-satchel
Model: NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf
```

Use those values when Hermes asks for a provider/model. Choose the OpenAI-compatible/custom endpoint option, then enter the Local Satchel base URL, API key, and model name.

After Hermes is configured, use it normally:

```powershell
hermes
```

Keep Local Satchel running while Hermes is using the local model. When you are done, stop the local model server:

```powershell
satchel stop
```

## Developer/debug commands

These are useful while building or troubleshooting Local Satchel:

```powershell
satchel check --json
satchel models --json
satchel recommend --vram-gb 12 --json
satchel status --json
```

If you are testing from a cloned repo before a public release, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-local-satchel.ps1
```

The CLI currently stores app-managed assets under:

```text
C:\Users\<you>\AppData\Local\LocalSatchel
```

It binds llama.cpp to `127.0.0.1:8080` only.

## Current status

Phase 0 validated the Windows NVIDIA llama.cpp CUDA path with NVIDIA Nemotron 3 Nano 4B Q4_K_M. Phase 1 CLI core is in progress: Check, model-tier recommendation, Pack, Run, Test, Connect, and Stop now exist as an installable Python CLI prototype backed by tests.
