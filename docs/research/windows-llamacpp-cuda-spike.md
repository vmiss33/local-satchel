# Windows llama.cpp CUDA Research Spike

## Purpose

Validate the simplest Windows path for Local Satchel v1:

Windows 11 + NVIDIA GPU + llama.cpp CUDA build + GGUF model + OpenAI-compatible localhost endpoint.

This spike must be run on a real Windows NVIDIA machine. The current planning environment is Linux and cannot validate Windows GPU behavior.

## Research questions

1. Which llama.cpp Windows CUDA release should Local Satchel download?
2. Does the release include `llama-server.exe`?
3. Which flags are required for a reliable OpenAI-compatible endpoint?
4. How does `llama-server.exe` behave when VRAM is insufficient?
5. What error messages appear for missing/outdated NVIDIA drivers?
6. Can Local Satchel use the runtime without requiring a separate CUDA toolkit install?
7. What model sizes/quantizations work well for common NVIDIA VRAM levels?
8. What health endpoint or test request should Local Satchel use?

## Manual test plan

### Step 1: Record machine info

Capture:

- Windows version
- GPU model
- VRAM
- NVIDIA driver version
- free disk space

Suggested commands:

```powershell
nvidia-smi
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsHardwareAbstractionLayer
```

### Step 2: Download llama.cpp CUDA release

Find the current official llama.cpp release artifact for Windows CUDA.

Record:

- release URL
- artifact name
- included binaries
- whether `llama-server.exe` is present
- whether extra DLLs are required

### Step 3: Download a small GGUF model

Use a small model first to validate the server path before trying larger models.

Record:

- model name
- source URL
- license
- file size
- quantization

### Step 4: Start server manually

Candidate command:

```powershell
.\llama-server.exe --model C:\Path\To\model.gguf --host 127.0.0.1 --port 8080 --ctx-size 4096 --n-gpu-layers -1
```

Record:

- startup logs
- time to first ready state
- GPU memory usage
- CPU memory usage
- final endpoint

### Step 5: Test OpenAI-compatible chat

Candidate request:

```powershell
$body = @{
  model = "local-satchel"
  messages = @(@{ role = "user"; content = "Write one sentence about local AI." })
} | ConvertTo-Json -Depth 4

Invoke-RestMethod -Uri "http://localhost:8080/v1/chat/completions" -Method Post -ContentType "application/json" -Body $body
```

Record:

- response shape
- latency
- any required model name behavior

### Step 6: Failure tests

Test or simulate:

- port already in use
- missing model file
- invalid model file
- insufficient VRAM
- interrupted download
- server process killed

For each failure, capture:

- raw error text
- user-friendly translation
- recommended fix

## Candidate output

After this spike, update:

- `model-catalog/models.json`
- `docs/ARCHITECTURE.md`
- `docs/PRD.md` if runtime assumptions changed

## Exit criteria

The spike is complete when a Windows NVIDIA machine can:

1. Start `llama-server.exe` with GPU acceleration.
2. Serve an OpenAI-compatible chat completion request.
3. Produce documented commands and failure notes that the CLI MVP can automate.
