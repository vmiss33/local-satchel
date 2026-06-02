# Local Satchel

Pack, run, and connect local AI models.

Carry your models. Run them anywhere.

Local Satchel turns your NVIDIA GPU into a local AI endpoint. It checks your PC, chooses a compatible model, downloads the runtime and model files, starts a private local server, and configures apps that support OpenAI-compatible APIs.

V1 is aimed at Windows 11 PCs with NVIDIA GPUs. The point is to hide the hard parts: CUDA builds, GGUF filenames, quantization, server flags, ports, and endpoint URLs.

## The simple version

Local Satchel should feel like this:

```text
Check  ->  Pack  ->  Run  ->  Test  ->  Connect  ->  Stop
```

What those words mean:

- **Check**: Look at your PC and decide whether local AI can run well here.
- **Pack**: Download the recommended local runtime and model for this machine.
- **Run**: Start the model server privately on this PC.
- **Test**: Send a real chat request and confirm the local endpoint works.
- **Connect**: Configure another app to use the local model.
- **Stop**: Turn the local model server off.

The user should not need to know what `llama.cpp`, CUDA, GGUF, quantization, or an inference server is.

## Current status

Local Satchel is currently a working CLI prototype, not a finished consumer app.

Already working in the prototype:

- Windows NVIDIA hardware check
- VRAM-aware model recommendation
- curated model catalog
- llama.cpp CUDA runtime preparation
- model download/preparation
- local server start/stop
- OpenAI-compatible test request
- Hermes Agent configuration

The current validated path is Windows 11 + NVIDIA GeForce RTX 4070 Laptop GPU + NVIDIA Nemotron 3 Nano 4B Q4_K_M through llama.cpp CUDA.

## Install on Windows

Open PowerShell and run:

```powershell
powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/vmiss33/local-satchel/main/scripts/install-local-satchel.ps1 | iex"
```

The installer creates Local Satchel under:

```text
C:\Users\<you>\AppData\Local\LocalSatchel
```

It also creates a `satchel` command.

After install, open a new PowerShell window. If `satchel` is not found yet, close and reopen PowerShell once more.

## First run

Run these commands in PowerShell:

```powershell
satchel check
satchel pack recommended
satchel run
satchel test
satchel connect hermes
```

Expected flow:

1. `satchel check` reports whether your PC is ready and which model tier it recommends.
2. `satchel pack recommended` downloads/prepares the runtime and model files.
3. `satchel run` starts the local server at `http://127.0.0.1:8080/v1`.
4. `satchel test` sends a chat request to the local server.
5. `satchel connect hermes` configures Hermes Agent to use the Local Satchel endpoint.

Then start a new Hermes session:

```powershell
hermes
```

When finished:

```powershell
satchel stop
```

## How this is meant to work

Local Satchel is a local AI launcher and connection helper.

It does four jobs:

1. **Inspect the computer**
   - Finds the NVIDIA GPU.
   - Reads VRAM and driver information.
   - Checks available disk space.

2. **Choose a safe default**
   - Uses a curated model catalog.
   - Picks the best validated model for the detected VRAM tier.
   - Avoids asking normal users to choose quantization levels or model files.

3. **Prepare the local AI bundle**
   - Downloads a Windows CUDA build of llama.cpp.
   - Downloads the selected GGUF model.
   - Stores app-managed files under `C:\Users\<you>\AppData\Local\LocalSatchel`.

4. **Run and connect**
   - Starts `llama-server.exe` bound to `127.0.0.1` only.
   - Exposes an OpenAI-compatible endpoint at `http://127.0.0.1:8080/v1`.
   - Configures Hermes Agent with a named `Local Satchel` provider.
   - Prints raw endpoint settings for other compatible clients.

The important product idea: users should operate Local Satchel with product verbs, not infrastructure vocabulary.

They should say:

```text
Check my PC.
Pack the model.
Run it.
Test it.
Connect my app.
Stop it.
```

They should not have to say:

```text
Download a CUDA artifact, pick a GGUF quant, choose llama-server flags, bind a host, pick a port, and configure an OpenAI-compatible base URL.
```

## Connect Hermes Agent

With Local Satchel running, configure Hermes Agent to use the local model:

```powershell
satchel connect hermes
```

That command writes a named `Local Satchel` provider into the Hermes config and sets it as the active model provider.

It sets:

```text
Provider: Local Satchel
Base URL: http://127.0.0.1:8080/v1
API key: local-satchel
Model: NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf
```

The API key is only a placeholder for clients that require one. The V1 prototype binds to `127.0.0.1`, so the server is private to this PC.

Start a new Hermes session after connecting so Hermes loads the updated config:

```powershell
hermes
```

## Connect another OpenAI-compatible app

For apps other than Hermes, print the raw settings:

```powershell
satchel connect hermes --show
```

Copy the printed Base URL, API key, and Model into the app's OpenAI-compatible/custom endpoint settings.

## Developer commands

From a cloned repo:

```powershell
git clone https://github.com/vmiss33/local-satchel.git C:\Users\<you>\repos\local-satchel
cd C:\Users\<you>\repos\local-satchel
powershell -ExecutionPolicy Bypass -File .\scripts\install-local-satchel.ps1
```

Useful debug commands:

```powershell
satchel check --json
satchel models --json
satchel recommend --vram-gb 8 --json
satchel status --json
satchel connect hermes --show
```

Run tests from the repo:

```powershell
$env:PYTHONPATH = "src"
python -m pytest tests -q
```

## Repository layout

```text
local-satchel/
  src/local_satchel/          CLI and runtime code
  tests/                      CLI and packaging tests
  scripts/                    Windows installer and helper scripts
  docs/                       PRD, UX, roadmap, architecture, research
  examples/hermes/            Hermes provider notes
  model-catalog/models.json   source model catalog
```

## Design constraints for V1

- Windows 11 is the first implementation target.
- NVIDIA GPU required for the first path.
- Use a direct Windows install path for V1 instead of requiring container tooling.
- Do not require manual CUDA installation unless research proves it unavoidable.
- Use llama.cpp CUDA builds, GGUF models, and OpenAI-compatible localhost endpoints.
- Bind to `127.0.0.1` by default; do not expose the server to the LAN by accident.
- Prefer safe defaults over asking users technical questions.
