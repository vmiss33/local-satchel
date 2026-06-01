# Local Satchel

Pack, run, and connect local AI models.

Local Satchel turns your NVIDIA GPU into a local AI endpoint. It checks your PC, recommends a compatible model, downloads the right local runtime, starts an OpenAI-compatible server, and gives you connection settings for apps and agents like Hermes.

No Docker in v1. No manual CUDA setup. No model-server guesswork.

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

## Non-goals for v1

- Docker
- NVIDIA NIM as the default runtime
- macOS
- AMD GPUs
- CPU-only as the primary path
- Fine-tuning
- Kubernetes or container orchestration
- Arbitrary model marketplace

## Repository layout

```text
local-satchel/
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

## Current status

Planning package committed. Next step is the Windows research spike to validate llama.cpp CUDA server behavior on a real Windows NVIDIA machine.
