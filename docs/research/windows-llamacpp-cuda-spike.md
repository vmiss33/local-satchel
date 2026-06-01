# Windows llama.cpp CUDA Research Spike

## Purpose

Validate the simplest Windows path for Local Satchel v1:

Windows 11 + NVIDIA GPU + llama.cpp CUDA build + GGUF model + OpenAI-compatible localhost endpoint.

This spike was run on a real Windows NVIDIA machine on 2026-06-01.

## Result

Verdict: VALIDATED for a small GGUF model on Windows NVIDIA.

A downloaded official llama.cpp Windows CUDA build successfully started `llama-server.exe` on `127.0.0.1:8080`, loaded a GGUF model with CUDA visible, and answered an OpenAI-compatible `/v1/chat/completions` request from PowerShell.

Important packaging finding: the llama.cpp release has both CUDA runtime DLL packages and actual binary packages. The `cudart-llama-bin-win-cuda-*.zip` artifact only contained CUDA DLLs. The runnable server was in `llama-b9453-bin-win-cuda-12.4-x64.zip`.

## Machine info captured

### Host / shell

Command:

```bash
uname -a
```

Output:

```text
MINGW64_NT-10.0-26200 horcrux 3.6.6-1cdd4371.x86_64 2026-01-15 22:20 UTC x86_64 Msys
```

PowerShell command:

```powershell
$PSVersionTable.PSVersion.ToString()
```

Output:

```text
5.1.26100.8457
```

### Windows version

Command:

```powershell
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsHardwareAbstractionLayer, OsBuildNumber | Format-List
```

Output:

```text
WindowsProductName         : Windows 10 Home
WindowsVersion             : 2009
OsHardwareAbstractionLayer : 10.0.26100.1
OsBuildNumber              : 26200
```

Registry command:

```powershell
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion" | Select-Object ProductName, DisplayVersion, CurrentBuild, UBR | Format-List
```

Output:

```text
ProductName    : Windows 10 Home
DisplayVersion : 25H2
CurrentBuild   : 26200
UBR            : 8457
```

Finding: Windows compatibility detection should not rely only on `ProductName`, because this machine reports `Windows 10 Home` in legacy fields while using build `26200` / display version `25H2`, which is Windows 11-generation.

### NVIDIA GPU / driver

Command:

```bash
command -v nvidia-smi
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader,nounits
nvidia-smi
```

Output:

```text
/c/WINDOWS/system32/nvidia-smi
NVIDIA GeForce RTX 4070 Laptop GPU, 8188, 581.04
```

Relevant `nvidia-smi` header:

```text
NVIDIA-SMI 581.04                 Driver Version: 581.04         CUDA Version: 13.0
GPU: NVIDIA GeForce RTX 4070 Laptop GPU
Memory: 0MiB / 8188MiB before server start
```

### Disk space

Command:

```powershell
Get-PSDrive C | Select-Object Name, @{Name="UsedGB";Expression={[math]::Round($_.Used/1GB,2)}}, @{Name="FreeGB";Expression={[math]::Round($_.Free/1GB,2)}} | Format-List
```

Output:

```text
Name   : C
UsedGB : 497.66
FreeGB : 453.98
```

### PowerShell internet reachability

Initial `Invoke-WebRequest -Method Head` checks produced `Object reference not set to an instance of an object.` on this Windows PowerShell 5.1 environment, so the spike used GET requests with `-UseBasicParsing` and a User-Agent.

Commands:

```powershell
Invoke-WebRequest -Uri "https://github.com" -UseBasicParsing -TimeoutSec 20 -Headers @{"User-Agent"="LocalSatchelSpike"}
Invoke-WebRequest -Uri "https://huggingface.co" -UseBasicParsing -TimeoutSec 20 -Headers @{"User-Agent"="LocalSatchelSpike"}
```

Observed output:

```text
GitHub status: 200; bytes: 571189
HuggingFace status: 200; bytes: 177130
```

Finding: Local Satchel should prefer a robust GET/short download probe over relying only on `Invoke-WebRequest -Method Head` in Windows PowerShell 5.1.

## llama.cpp release tested

Latest release was discovered through:

```text
https://api.github.com/repos/ggml-org/llama.cpp/releases/latest
```

Output:

```text
tag: b9453
name: b9453
published_at: 2026-06-01T14:56:10Z
```

Relevant release assets:

```text
cudart-llama-bin-win-cuda-12.4-x64.zip       391443627 bytes
cudart-llama-bin-win-cuda-13.3-x64.zip       390970417 bytes
llama-b9453-bin-win-cuda-12.4-x64.zip        260242093 bytes
llama-b9453-bin-win-cuda-13.3-x64.zip        158379272 bytes
```

Downloaded temporary files under:

```text
C:\Users\melis\LocalSatchelSpike\runtime
```

### CUDA runtime DLL package test

Downloaded:

```text
C:\Users\melis\LocalSatchelSpike\runtime\cudart-llama-bin-win-cuda-12.4-x64.zip
```

Result:

```text
zip entries: 3
cublas64_12.dll
cublasLt64_12.dll
cudart64_12.dll
llama-server entries: []
```

Finding: this package is not enough by itself. It provides CUDA DLLs only.

### llama.cpp Windows CUDA binary package test

Downloaded:

```text
C:\Users\melis\LocalSatchelSpike\runtime\llama-b9453-bin-win-cuda-12.4-x64.zip
```

Extracted to:

```text
C:\Users\melis\LocalSatchelSpike\runtime\llama-b9453-bin-win-cuda-12.4-x64
```

Result:

```text
zip entries: 52
llama-server entries: ['llama-server.exe']
```

Included relevant files:

```text
ggml-cuda.dll
llama-server-impl.dll
llama-server.exe
llama.dll
llama-common.dll
```

Version command:

```powershell
.\llama-server.exe --version
```

Output:

```text
version: 9453 (48b88c3b0)
built with Clang 19.1.5 for Windows x86_64
```

## Model tested

Selected a small model to validate the runtime path before larger model recommendations.

Model:

```text
Qwen2.5-0.5B-Instruct GGUF Q4_K_M
```

Source:

```text
https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf
```

License from Hugging Face model API:

```text
apache-2.0
```

Downloaded to:

```text
C:\Users\melis\LocalSatchelSpike\models\qwen2.5-0.5b-instruct-q4_k_m.gguf
```

Size observed:

```text
491400032 bytes
469 MiB displayed by ls -lh
```

Hugging Face HEAD/redirect headers included:

```text
X-Linked-Size: 491400032
Content-Length: 491400032
```

## Server run

Port pre-check:

```powershell
Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,State,OwningProcess | Format-Table -AutoSize
```

Initial output was empty, so port 8080 was available.

Exact server command used from Git Bash/MSYS:

```bash
cd /c/Users/melis/LocalSatchelSpike/runtime/llama-b9453-bin-win-cuda-12.4-x64
export PATH="/c/Users/melis/LocalSatchelSpike/runtime/extracted:$(pwd):$PATH"
./llama-server.exe \
  --model /c/Users/melis/LocalSatchelSpike/models/qwen2.5-0.5b-instruct-q4_k_m.gguf \
  --host 127.0.0.1 \
  --port 8080 \
  --ctx-size 4096 \
  --n-gpu-layers -1 \
  --jinja
```

Copy-pasteable PowerShell equivalent for Local Satchel docs/testing:

```powershell
$Runtime = "C:\Users\melis\LocalSatchelSpike\runtime\llama-b9453-bin-win-cuda-12.4-x64"
$CudaDlls = "C:\Users\melis\LocalSatchelSpike\runtime\extracted"
$Model = "C:\Users\melis\LocalSatchelSpike\models\qwen2.5-0.5b-instruct-q4_k_m.gguf"
$env:Path = "$CudaDlls;$Runtime;$env:Path"
Set-Location $Runtime
.\llama-server.exe --model $Model --host 127.0.0.1 --port 8080 --ctx-size 4096 --n-gpu-layers -1 --jinja
```

Startup log excerpt:

```text
CUDA0   : NVIDIA GeForce RTX 4070 Laptop GPU (8187 MiB, 7054 MiB free)
CPU     : AMD Ryzen 7 7735HS with Radeon Graphics (31940 MiB, 16522 MiB free)
loading model 'C:/Users/melis/LocalSatchelSpike/models/qwen2.5-0.5b-instruct-q4_k_m.gguf'
n_ctx_seq (4096) < n_ctx_train (32768) -- the full capacity of the model will not be utilized
chat template, thinking = 0
model loaded
server is listening on http://127.0.0.1:8080
```

Health checks:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8080/health" -TimeoutSec 5 | ConvertTo-Json -Depth 5
Invoke-RestMethod -Uri "http://127.0.0.1:8080/v1/models" -TimeoutSec 5 | ConvertTo-Json -Depth 5
```

Output:

```json
{
  "status": "ok"
}
```

`/v1/models` returned the model id:

```text
qwen2.5-0.5b-instruct-q4_k_m.gguf
```

GPU memory while the server was running:

```bash
nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits
```

Output:

```text
NVIDIA GeForce RTX 4070 Laptop GPU, 1702, 8188, 0
```

## OpenAI-compatible chat test

Exact PowerShell request:

```powershell
$body = @{
  model = "local-satchel"
  messages = @(@{ role = "user"; content = "Write one sentence about local AI." })
  max_tokens = 40
  temperature = 0.2
} | ConvertTo-Json -Depth 5

$start = Get-Date
$r = Invoke-RestMethod -Uri "http://127.0.0.1:8080/v1/chat/completions" -Method Post -ContentType "application/json" -Body $body -TimeoutSec 120
$elapsed = ((Get-Date) - $start).TotalSeconds
"elapsed_seconds=$elapsed"
$r | ConvertTo-Json -Depth 10
```

Observed output:

```json
{
  "elapsed_seconds": 0.5424689,
  "choices": [
    {
      "finish_reason": "length",
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Local AI refers to the application of artificial intelligence technologies in specific local contexts, such as healthcare, education, and transportation, where local knowledge and resources are integrated with AI to deliver personalized and efficient solutions."
      }
    }
  ],
  "created": 1780327241,
  "model": "qwen2.5-0.5b-instruct-q4_k_m.gguf",
  "system_fingerprint": "b9453-48b88c3b0",
  "object": "chat.completion",
  "usage": {
    "completion_tokens": 40,
    "prompt_tokens": 36,
    "total_tokens": 76
  },
  "timings": {
    "prompt_n": 36,
    "prompt_ms": 132.736,
    "prompt_per_second": 271.21504339440696,
    "predicted_n": 40,
    "predicted_ms": 372.694,
    "predicted_per_second": 107.32665403789703
  }
}
```

Finding: the request body used `model = "local-satchel"`, but llama.cpp returned the loaded GGUF filename as the response `model`. Local Satchel should probably display/copy the actual `/v1/models` id unless later testing confirms aliases can be configured reliably.

## Nemotron-first V1 follow-up

The original smoke test used Qwen2.5 0.5B only to validate the Windows + llama.cpp CUDA path quickly. The product direction for Local Satchel v1 is Nemotron-first, so the next step was to find and run a Nemotron GGUF that fits this Windows NVIDIA platform.

### Nemotron candidate search

Hugging Face API searches for `nemotron GGUF`, `Llama-3.1-Nemotron-Nano GGUF`, and `Nemotron-Nano-8B GGUF` found these relevant candidates:

```text
nvidia/NVIDIA-Nemotron-3-Nano-4B-GGUF
unsloth/NVIDIA-Nemotron-3-Nano-4B-GGUF
unsloth/Llama-3.1-Nemotron-Nano-8B-v1-GGUF
bartowski/nvidia_Llama-3.1-Nemotron-Nano-8B-v1-GGUF
```

Candidate sizes from the Hugging Face tree API:

```text
nvidia/NVIDIA-Nemotron-3-Nano-4B-GGUF
  NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf              2.64 GiB

unsloth/NVIDIA-Nemotron-3-Nano-4B-GGUF
  NVIDIA-Nemotron-3-Nano-4B-Q4_K_M.gguf             2.70 GiB
  NVIDIA-Nemotron-3-Nano-4B-Q5_K_M.gguf             2.94 GiB
  NVIDIA-Nemotron-3-Nano-4B-Q6_K.gguf               3.78 GiB

unsloth/Llama-3.1-Nemotron-Nano-8B-v1-GGUF
  Llama-3.1-Nemotron-Nano-8B-v1-Q3_K_M.gguf         3.74 GiB
  Llama-3.1-Nemotron-Nano-8B-v1-Q4_K_M.gguf         4.58 GiB
  Llama-3.1-Nemotron-Nano-8B-v1-Q5_K_M.gguf         5.34 GiB

bartowski/nvidia_Llama-3.1-Nemotron-Nano-8B-v1-GGUF
  nvidia_Llama-3.1-Nemotron-Nano-8B-v1-Q3_K_M.gguf  3.74 GiB
  nvidia_Llama-3.1-Nemotron-Nano-8B-v1-Q4_K_M.gguf  4.58 GiB
  nvidia_Llama-3.1-Nemotron-Nano-8B-v1-Q5_K_M.gguf  5.34 GiB
```

Selection for the first Nemotron V1 candidate: `nvidia/NVIDIA-Nemotron-3-Nano-4B-GGUF`, because it is an official NVIDIA GGUF repo, small enough for this 8 GB VRAM laptop GPU, and closer to the V1 product thesis than the temporary Qwen smoke-test model.

### Nemotron model tested

Model:

```text
NVIDIA Nemotron 3 Nano 4B Q4_K_M
```

Source:

```text
https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-4B-GGUF/resolve/main/NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf
```

Hugging Face metadata:

```text
modelId: nvidia/NVIDIA-Nemotron-3-Nano-4B-GGUF
license: other
```

Downloaded to:

```text
C:\Users\melis\LocalSatchelSpike\models\NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf
```

Size observed:

```text
X-Linked-Size: 2837072864
Content-Length: 2837072864
ls -lh: 2.7G
model gib: 2.642
```

### Nemotron server command

Port pre-check:

```powershell
Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue
```

Output:

```text
No listener on port 8080
```

First command tested:

```bash
cd /c/Users/melis/LocalSatchelSpike/runtime/llama-b9453-bin-win-cuda-12.4-x64
export PATH="/c/Users/melis/LocalSatchelSpike/runtime/extracted:$(pwd):$PATH"
./llama-server.exe \
  --model /c/Users/melis/LocalSatchelSpike/models/NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf \
  --host 127.0.0.1 \
  --port 8080 \
  --ctx-size 4096 \
  --n-gpu-layers -1 \
  --jinja
```

This loaded and served successfully, but the first chat response returned an empty `message.content` with text in `message.reasoning_content` instead. For normal Local Satchel Test chat behavior, restart with reasoning disabled.

Recommended Nemotron command for Local Satchel v1:

```bash
cd /c/Users/melis/LocalSatchelSpike/runtime/llama-b9453-bin-win-cuda-12.4-x64
export PATH="/c/Users/melis/LocalSatchelSpike/runtime/extracted:$(pwd):$PATH"
./llama-server.exe \
  --model /c/Users/melis/LocalSatchelSpike/models/NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf \
  --host 127.0.0.1 \
  --port 8080 \
  --ctx-size 4096 \
  --n-gpu-layers -1 \
  --jinja \
  --reasoning off
```

Copy-pasteable PowerShell equivalent:

```powershell
$Runtime = "C:/Users/melis/LocalSatchelSpike/runtime/llama-b9453-bin-win-cuda-12.4-x64"
$CudaDlls = "C:/Users/melis/LocalSatchelSpike/runtime/extracted"
$Model = "C:/Users/melis/LocalSatchelSpike/models/NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf"
$env:Path = "$CudaDlls;$Runtime;$env:Path"
Set-Location $Runtime
.\llama-server.exe --model $Model --host 127.0.0.1 --port 8080 --ctx-size 4096 --n-gpu-layers -1 --jinja --reasoning off
```

Startup log excerpt with `--reasoning off`:

```text
CUDA0   : NVIDIA GeForce RTX 4070 Laptop GPU (8187 MiB, 7054 MiB free)
loading model 'C:/Users/melis/LocalSatchelSpike/models/NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf'
n_ctx_seq (4096) < n_ctx_train (1048576) -- the full capacity of the model will not be utilized
chat template, thinking = 0
model loaded
server is listening on http://127.0.0.1:8080
```

Health check:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8080/health" -TimeoutSec 5 | ConvertTo-Json -Compress
```

Output:

```json
{"status":"ok"}
```

Model endpoint returned:

```text
NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf
```

GPU memory while loaded:

```text
NVIDIA GeForce RTX 4070 Laptop GPU, 3247 MiB used, 8188 MiB total, 0% util
```

GPU memory during/after chat:

```text
NVIDIA GeForce RTX 4070 Laptop GPU, 3249 MiB used, 8188 MiB total, 96% util
```

### Nemotron OpenAI-compatible chat test

Exact PowerShell request:

```powershell
$body = @{
  model = "NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf"
  messages = @(
    @{ role = "system"; content = "You are Local Satchel test assistant. Answer concisely without showing reasoning." },
    @{ role = "user"; content = "In one sentence, explain what Local Satchel does for someone with an NVIDIA GPU." }
  )
  max_tokens = 80
  temperature = 0.2
} | ConvertTo-Json -Depth 5

$start = Get-Date
$r = Invoke-RestMethod -Uri "http://127.0.0.1:8080/v1/chat/completions" -Method Post -ContentType "application/json" -Body $body -TimeoutSec 180
$elapsed = ((Get-Date) - $start).TotalSeconds
"elapsed_seconds=$elapsed"
$r | ConvertTo-Json -Depth 10
```

Observed output:

```json
{
  "elapsed_seconds": 0.4362976,
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Local Satchel optimizes NVIDIA GPU performance for local AI tasks by efficiently managing resources and accelerating inference."
      }
    }
  ],
  "created": 1780328359,
  "model": "NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf",
  "system_fingerprint": "b9453-48b88c3b0",
  "object": "chat.completion",
  "usage": {
    "completion_tokens": 23,
    "prompt_tokens": 52,
    "total_tokens": 75
  },
  "timings": {
    "prompt_n": 52,
    "prompt_ms": 74.626,
    "prompt_per_second": 696.8080829737625,
    "predicted_n": 23,
    "predicted_ms": 292.622,
    "predicted_per_second": 78.59969516987786
  }
}
```

Nemotron result: VALIDATED as the V1 starting model candidate on this platform.

### Nemotron-specific findings

- The official NVIDIA 4B Q4_K_M GGUF fits comfortably on the 8 GB RTX 4070 Laptop GPU.
- `--reasoning off` should be included for the normal Local Satchel Test flow; otherwise OpenAI-compatible responses may put generated text in `reasoning_content` and leave `content` empty.
- The model id exposed by `/v1/models` is the GGUF filename, so Local Satchel should use/copy `NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf` unless a reliable alias layer is added later.
- The 4B Nemotron should replace the Qwen smoke-test model as the initial catalog entry. The 8B Nemotron Nano Q4_K_M remains a next quality/fit test, not the first default.

## Failure tests

### Missing model file

Command:

```bash
./llama-server.exe --model /c/Users/melis/LocalSatchelSpike/models/does-not-exist.gguf --host 127.0.0.1 --port 8081 --ctx-size 1024 --n-gpu-layers -1 --jinja --no-warmup
```

Exit code:

```text
1
```

Error excerpt:

```text
gguf_init_from_file: failed to open GGUF file 'C:/Users/melis/LocalSatchelSpike/models/does-not-exist.gguf' (No such file or directory)
llama_model_load: error loading model: llama_model_loader: failed to load model from C:/Users/melis/LocalSatchelSpike/models/does-not-exist.gguf
common_init_from_params: failed to load model 'C:/Users/melis/LocalSatchelSpike/models/does-not-exist.gguf'
load_model: failed to load model, 'C:/Users/melis/LocalSatchelSpike/models/does-not-exist.gguf'
llama_server: exiting due to model loading error
```

User-friendly translation:

```text
Local Satchel could not find the model file. The download may have been moved, deleted, or interrupted. Try packing the model again.
```

### Invalid model file

Command:

```bash
printf 'not a gguf model\n' > /c/Users/melis/LocalSatchelSpike/models/invalid-model.gguf
./llama-server.exe --model /c/Users/melis/LocalSatchelSpike/models/invalid-model.gguf --host 127.0.0.1 --port 8081 --ctx-size 1024 --n-gpu-layers -1 --jinja --no-warmup
```

Exit code:

```text
1
```

Error excerpt:

```text
gguf_init_from_reader: invalid magic characters: 'not ', expected 'GGUF'
llama_model_load: error loading model: llama_model_loader: failed to load model from C:/Users/melis/LocalSatchelSpike/models/invalid-model.gguf
common_init_from_params: failed to load model 'C:/Users/melis/LocalSatchelSpike/models/invalid-model.gguf'
load_model: failed to load model, 'C:/Users/melis/LocalSatchelSpike/models/invalid-model.gguf'
llama_server: exiting due to model loading error
```

User-friendly translation:

```text
This file is not a valid GGUF model. The download may be corrupt or the wrong file was selected. Try downloading the model again.
```

### Port already in use

A second `llama-server.exe` was launched against the same host/port while the first server was listening on `127.0.0.1:8080`. It did not fail quickly; it loaded the model and logged `server is listening on http://127.0.0.1:8080`, then remained running until the test command timeout killed it.

Finding: Local Satchel should not rely only on llama.cpp to produce a clear port conflict error. It should pre-check the port before launch with `Get-NetTCPConnection` and choose another local port or show a friendly message.

Suggested user-friendly translation:

```text
Another Local Satchel server or app may already be using this local port. Local Satchel can use another local port.
```

### Insufficient VRAM

Not reproduced in this run. The small Qwen2.5 0.5B Q4_K_M model fit comfortably on the RTX 4070 Laptop GPU. Server startup reported about 7054 MiB free before loading and `nvidia-smi` reported 1702 MiB used while running.

## Answers to research questions

1. Which llama.cpp Windows CUDA release should Local Satchel download?

   Candidate for this machine: `llama-b9453-bin-win-cuda-12.4-x64.zip` plus the `cudart-llama-bin-win-cuda-12.4-x64.zip` DLL package on PATH. The binary package contains `llama-server.exe`; the cudart package contains CUDA DLLs.

2. Does the release include `llama-server.exe`?

   Yes, in `llama-b9453-bin-win-cuda-12.4-x64.zip`. No, not in `cudart-llama-bin-win-cuda-12.4-x64.zip`.

3. Which flags are required for a reliable OpenAI-compatible endpoint?

   Tested flags:

   ```text
   --model <model.gguf> --host 127.0.0.1 --port 8080 --ctx-size 4096 --n-gpu-layers -1 --jinja
   ```

4. How does `llama-server.exe` behave when VRAM is insufficient?

   Not tested yet. This model fit.

5. What error messages appear for missing/outdated NVIDIA drivers?

   Not tested yet. NVIDIA driver 581.04 was installed and working.

6. Can Local Satchel use the runtime without requiring a separate CUDA toolkit install?

   On this machine, yes for this test path: the downloaded release artifacts plus NVIDIA driver were enough. The CUDA Toolkit was already present on the machine, but the server was run using the downloaded CUDA DLL package on PATH. A clean machine without CUDA Toolkit should still be tested before treating this as final.

7. What model sizes/quantizations work well for common NVIDIA VRAM levels?

   Validated two models on this 8 GB VRAM machine:

   - Qwen2.5-0.5B-Instruct Q4_K_M as an initial smoke test. It used about 1.7 GB GPU memory while serving.
   - NVIDIA Nemotron 3 Nano 4B Q4_K_M as the V1-aligned starting model. It used about 3.25 GB GPU memory while serving/chatting and answered `/v1/chat/completions` successfully when `--reasoning off` was set.

   The larger Llama 3.1 Nemotron Nano 8B family still needs quality/fit testing on this 8 GB VRAM GPU before becoming a default recommendation.

8. What health endpoint or test request should Local Satchel use?

   Health endpoint:

   ```text
   GET http://127.0.0.1:8080/health
   ```

   Expected output:

   ```json
   { "status": "ok" }
   ```

   Functional endpoint test:

   ```text
   POST http://127.0.0.1:8080/v1/chat/completions
   ```

## Implications for Local Satchel UX

- The product copy should continue to hide runtime details from normal users.
- Internally, the Pack step needs to download both the server binary package and any required CUDA DLL package.
- The Check step should detect `nvidia-smi`, GPU name, VRAM, driver version, disk space, internet access, and port availability before Run.
- The Run step should bind to `127.0.0.1` by default.
- The Test step can use `/health`, `/v1/models`, then `/v1/chat/completions`.
- Technical output should be captured under Show details / Open logs.

## Recommended next step

Treat `nvidia/NVIDIA-Nemotron-3-Nano-4B-GGUF` / `NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf` as the initial V1 catalog default for 8 GB NVIDIA Windows machines, with `--reasoning off` in the Run command. Next, test Llama 3.1 Nemotron Nano 8B Q4_K_M and Q3_K_M on this same machine to decide whether 8B can be offered as a higher-quality option or should require 12 GB+ VRAM.
