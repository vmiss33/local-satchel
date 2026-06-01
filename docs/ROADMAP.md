# Local Satchel Roadmap

## Phase 0: Windows llama.cpp CUDA research spike

Goal: prove the simplest working path on a real Windows NVIDIA machine.

Questions:

- Which llama.cpp Windows CUDA release is easiest to download and run?
- Does `llama-server` expose the OpenAI-compatible endpoints Local Satchel needs?
- Which command-line flags produce reliable defaults on NVIDIA GPUs?
- What happens when VRAM is insufficient?
- What driver versions are needed in practice?
- Which model families and quantizations work well for all cataloged NVIDIA VRAM tiers: 4 GB, 6 GB, 8 GB, 10 GB, 12 GB, 16 GB, 24 GB, 32 GB, and 48 GB+?
- How should Local Satchel detect and recover from common startup failures?

Deliverables:

- `docs/research/windows-llamacpp-cuda-spike.md`
- Manual runbook
- Candidate model catalog with explicit entries for every supported NVIDIA VRAM tier, including research-needed gaps
- Working curl request against local endpoint
- Notes on failure modes

Exit criteria:

A real Windows NVIDIA machine can run a GGUF model through llama.cpp CUDA and answer an OpenAI-compatible chat request.

## Phase 1: CLI MVP

Goal: build the core engine before the GUI.

Commands:

```bash
satchel doctor
satchel models
satchel pack recommended
satchel run
satchel status
satchel stop
satchel connect hermes
```

Capabilities:

- Detect NVIDIA GPU
- Detect VRAM
- Recommend the best validated model for the detected GPU/VRAM tier
- Download runtime
- Download the selected model, not a hardcoded default
- Start local server
- Verify endpoint
- Print connection settings
- Stop server

Exit criteria:

A technical user can reach a working local endpoint from CLI commands without manually downloading llama.cpp or a model.

## Phase 2: Desktop wizard

Goal: make the CLI flow usable by a nontechnical user.

Screens:

- Welcome
- Check my PC
- Readiness result
- Choose recommended model
- Pack
- Run
- Test chat
- Connect apps
- Troubleshooting/logs

Exit criteria:

A nontechnical tester can get a working local model response without using a terminal.

## Phase 3: Hermes integration

Goal: make the original agent use case smooth.

V1 integration:

- Copy-paste Hermes provider settings
- Example config docs
- Verification prompt

V1.1 integration:

- Detect Hermes config location
- Backup config before writing
- Add Local Satchel provider automatically
- Verify Hermes can call the endpoint

Exit criteria:

A user can select/use the Local Satchel endpoint from Hermes Agent.

## Phase 4: Linux support

Goal: bring the same Local Satchel flow to Linux.

Linux-specific work:

- Detect NVIDIA GPU through `nvidia-smi`
- Download Linux llama.cpp CUDA binary or document build path
- Use XDG cache/config directories
- Optional systemd user service for background server
- Same model catalog and recommendation logic

Exit criteria:

The same conceptual flow works on Linux:

```bash
satchel doctor
satchel pack recommended
satchel run
satchel connect hermes
```

## Phase 5: Model management

Goal: make Local Satchel useful after first run.

Features:

- Multiple downloaded models
- Delete model
- Update model metadata
- Benchmark this model on this GPU
- Quality vs speed presets
- Context length presets
- Custom port selection
- Import existing GGUF

Exit criteria:

Users can manage local models without file-system spelunking.

## Phase 6: Runtime expansion

Goal: support additional local AI runtimes without losing simplicity.

Candidates:

- NVIDIA NIM as an enterprise/container runtime option
- Ollama
- LM Studio detection
- vLLM
- TensorRT-LLM

Rule:

Do not add runtime choices until the default llama.cpp path is excellent. Runtime expansion must not turn Local Satchel into a confusing control panel.

## Phase 7: Portfolio polish

Goal: make the project legible to hiring managers, AI infrastructure teams, and developer relations audiences.

Deliverables:

- README screenshots
- 90-second demo video
- Architecture diagram
- Troubleshooting matrix
- Design decision record: why no Docker in v1
- Design decision record: product identity vs Windows initial target
- Blog post: turning an NVIDIA GPU into a local AI endpoint

Exit criteria:

The repository tells a complete product, UX, and infrastructure story even before someone reads the code.
