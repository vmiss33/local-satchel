# Local Satchel Product Requirements Document

## Product name

Local Satchel

## Tagline

Pack, run, and connect local AI models.

## Secondary line

Carry your models. Run them anywhere.

## Product thesis

Local Satchel turns your NVIDIA GPU into a local AI endpoint.

## Product vision

Local Satchel makes local AI usable by normal people. It hides the complexity of GPU detection, model selection, runtime setup, server launch, and app connection behind a simple guided experience.

Local Satchel is cross-platform by design. The first implementation target is Windows 11 with NVIDIA GPUs.

## V1 goal

Let a Windows user with an NVIDIA GPU run a local model through an OpenAI-compatible endpoint without installing Docker, manually installing CUDA, choosing quantization settings, or typing terminal commands.

## V1 implementation target

- Operating system: Windows 11
- Hardware: NVIDIA GPU
- Runtime: llama.cpp CUDA build
- Model format: GGUF
- Model source: curated downloadable model catalog, initially likely Hugging Face-hosted GGUF files
- API surface: OpenAI-compatible local HTTP endpoint

## Target users

### Primary user

A nontechnical or semi-technical Windows user with an NVIDIA GPU who wants local AI but does not know Docker, CUDA, GGUF, quantization, ports, or inference servers.

### Secondary user

A technical evaluator, hiring manager, or AI infrastructure practitioner who wants to see a polished, thoughtful local inference bootstrapper.

### Tertiary user

Hermes Agent users who want a local OpenAI-compatible model endpoint.

## Core user promise

If your PC has an NVIDIA GPU, Local Satchel can help you run a local AI model.

## V1 success criteria

1. User can install/open Local Satchel on Windows 11.
2. User can click **Check my PC** and get a plain-English readiness result.
3. Local Satchel detects GPU name, VRAM, driver availability, disk space, internet connectivity, and port availability.
4. Local Satchel recommends the best compatible curated model for the detected GPU/VRAM tier, not a single hardcoded default.
5. User can accept the recommendation without understanding model size, quantization, runtime flags, or VRAM tiers.
6. Local Satchel downloads the required llama.cpp CUDA runtime and GGUF model.
7. Local Satchel starts a local OpenAI-compatible server.
8. Local Satchel sends a test prompt and displays a response.
9. User can copy connection settings for Hermes or another OpenAI-compatible client.
10. User can stop and restart the local model.

## Non-goals for v1

- Docker
- NVIDIA NIM as the default path
- Linux implementation, though Linux must remain in the architecture roadmap
- macOS support
- AMD GPU support
- CPU-only mode as a primary path
- Custom model import
- Advanced quantization selection
- Fine-tuning
- Multi-node or distributed inference
- Kubernetes
- Runtime marketplace
- One-click modification of every supported app

## Product principles

### 1. Hide plumbing

Normal users should not need to learn Docker, CUDA flags, GGUF internals, quantization names, ports, or server commands.

### 2. Recommend, do not overwhelm

The default path should choose a safe model for the user. Advanced choices may exist, but the primary UX should not be a model wall.

### 3. Prove it works inside the app

A local API endpoint is abstract. A visible chat response is concrete. V1 must include a built-in test chat.

### 4. Be honest about hardware limits

If the GPU cannot run a supported model well, say so plainly and recommend a smaller option or explain the limitation.

### 5. Keep the product cross-platform

Windows is the first implementation target, not the product identity.

## Functional requirements

### FR1: PC readiness check

Local Satchel must detect:

- Windows version
- NVIDIA GPU presence
- GPU name
- GPU VRAM
- NVIDIA driver availability
- Available system RAM
- Available disk space
- Internet connectivity
- Whether the local server port is free

### FR2: Friendly readiness result

The readiness check must produce user-friendly messages:

- Ready
- Almost ready, with specific fixes
- Blocked, with a clear reason

Raw command output must be hidden behind **Show technical details**.

### FR3: Model recommendation

Local Satchel must recommend a model based on detected VRAM and a curated model catalog. The recommendation engine must choose the highest-quality validated model that fits the current machine, rather than always choosing the smallest/8 GB-safe model.

Initial Nemotron-first recommendation tiers must be explicit in the catalog for all common NVIDIA card-size tiers, not implied in code:

- 4 GB VRAM: cataloged as below the current V1 validated floor unless a smaller Nemotron model is validated.
- 6 GB VRAM: cataloged with the smallest validated Nemotron recommendation.
- 8 GB VRAM: cataloged with the validated small Nemotron tier, currently NVIDIA Nemotron 3 Nano 4B Q4_K_M.
- 10 GB VRAM: cataloged separately; use the best validated fit, not an implicit 8 GB assumption.
- 12 GB VRAM: cataloged separately; should recommend a validated larger Nemotron tier once testing proves it fits reliably.
- 16 GB VRAM: cataloged separately; should recommend a higher-quality validated Nemotron tier when available.
- 24 GB VRAM: cataloged separately for high-end consumer/workstation GPUs.
- 32 GB VRAM: cataloged separately for workstation-class GPUs.
- 48 GB+ VRAM: cataloged separately for high-VRAM workstation/datacenter-class GPUs.
- If a tier has no validated model yet, Local Satchel may temporarily fall back to the best lower validated tier, but the catalog must show the gap explicitly and the UX must not pretend the lower-tier model is the final optimized answer for that card size.

The recommendation should include:

- Friendly label, such as **Best choice**
- Model display name
- Estimated download size
- Estimated VRAM/RAM fit
- Quality/speed expectation
- Why this model was chosen for this GPU
- Advanced technical details hidden by default

### FR4: Runtime preparation

Local Satchel must download or locate a compatible llama.cpp CUDA server binary and verify that it can be launched.

### FR5: Model packing

Local Satchel must download the selected GGUF model, store it in a predictable app-managed directory, and preserve it between runs.

### FR6: Run local server

Local Satchel must start the local llama.cpp server with safe defaults:

- localhost binding only by default
- OpenAI-compatible API enabled
- auto-selected GPU layer behavior where supported
- conservative context size based on model/GPU defaults

### FR7: Health check

Local Satchel must wait for the server to become ready and then send a test prompt.

### FR8: Connection settings

Local Satchel must configure Hermes Agent automatically and display copyable settings for other OpenAI-compatible clients:

- Base URL
- API key placeholder if a client requires one
- Model name
- Example curl request
- Hermes config update summary

### FR9: Start/stop/status

Local Satchel must support:

- Start model
- Stop model
- Restart model
- Show running status
- Show logs
- Remove downloaded model later, at user request

### FR10: Troubleshooting

Every common failure must answer:

1. What happened?
2. Why does it matter?
3. What should I do next?

## Nonfunctional requirements

### NFR1: Beginner-friendly

The primary flow must not require the terminal.

### NFR2: Safe by default

Bind local servers to `127.0.0.1` unless the user explicitly enables LAN access.

### NFR3: Transparent downloads

Show model/runtime download size before downloading.

### NFR4: Reversible

User can stop the model and remove downloaded assets.

### NFR5: Testable core

Detection, recommendation, and command execution logic must be testable without a real NVIDIA GPU by using mocked command outputs.

### NFR6: Portfolio-grade documentation

The repo must explain product decisions, architecture, roadmap, troubleshooting, and implementation tradeoffs.

## Key product decision: no Docker in v1

V1 intentionally avoids Docker because the primary goal is nontechnical usability. Docker adds concepts like containers, images, volumes, ports, registry login, daemon state, and GPU passthrough. Those are valid infrastructure concepts, but they are not acceptable as required user knowledge for Local Satchel v1.

NVIDIA NIM can become a later enterprise/runtime option. It is not the default v1 path.
