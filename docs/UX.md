# Local Satchel User Experience

## UX goal

A normal user should only need to make three decisions:

1. Do I want to check my PC?
2. Do I want the recommended model?
3. Do I want to start it?

Everything else should be automatic, explained in plain English, or hidden under **Advanced**.

## UX vocabulary

Use outcome language:

- Check
- Pack
- Run
- Connect
- Test
- Stop

Avoid exposing implementation language in the primary flow:

- CUDA flags
- GGUF quantization codes
- n-gpu-layers
- inference server
- localhost ports
- model context length
- server process

Technical details can exist, but behind an expandable section.

## First-run flow

### 1. Welcome

Title:

```text
Welcome to Local Satchel
```

Body:

```text
Run local AI models on your NVIDIA GPU.

Local Satchel checks your PC, recommends a model, starts a local AI server, and helps connect your apps.
```

Primary button:

```text
Check my PC
```

Secondary link:

```text
Advanced setup
```

### 2. Compatibility check

Title:

```text
Checking your PC
```

Checklist:

```text
✓ Windows version
✓ NVIDIA GPU
✓ NVIDIA driver
✓ Available memory
✓ Disk space
✓ Internet connection
✓ Local server port
```

### 3. Ready result

Example:

```text
Your PC is ready.

NVIDIA GeForce RTX 4070
12 GB VRAM

Recommended: 7B/8B local models
```

Primary button:

```text
Choose recommended model
```

Secondary:

```text
Show details
```

### 4. Almost ready result

Example:

```text
Almost ready.

Your NVIDIA GPU was detected, but your driver may need an update before Local Satchel can use GPU acceleration.
```

Primary button:

```text
Open NVIDIA driver download
```

Secondary:

```text
Check again
```

### 5. Model recommendation

Title:

```text
Choose a model
```

Default card:

```text
Best choice
Fast local assistant
Recommended for your GPU

Good for chat, coding help, summaries, and everyday local AI tasks.
```

Technical details collapsed:

```text
Model: <model id>
File: <filename>.gguf
Quantization: Q4_K_M
Download size: <size>
Estimated memory: <range>
```

Primary button:

```text
Use this model
```

### 6. Pack

Title:

```text
Packing your satchel
```

Progress steps:

```text
Downloading local AI runtime
Downloading model
Verifying files
Preparing local server
```

Rule:
Show realistic progress, but do not spam logs unless the user opens details.

### 7. Run

Title:

```text
Starting your local model
```

Progress steps:

```text
Loading model
Using NVIDIA GPU acceleration
Starting local endpoint
Testing response
```

### 8. Success

Title:

```text
Your local AI model is running
```

Show:

```text
Endpoint: http://localhost:8080/v1
Model: local-satchel
Status: Running
```

Actions:

```text
Test chat
Copy settings
Connect to Hermes
Stop model
Open logs
```

### 9. Test chat

Title:

```text
Ask your local model something
```

Prompt placeholder:

```text
Write a short poem about local AI.
```

Success copy:

```text
It works. Your response came from the model running on this computer.
```

### 10. Connect apps

Title:

```text
Connect your apps
```

Cards:

- Hermes Agent
- OpenAI-compatible app
- Continue
- Open WebUI

V1 can provide copy-paste settings. Later versions can configure apps directly.

## Error copy rules

Every error must include:

1. Plain-English summary
2. Why it matters
3. Recommended next action
4. Technical details only if expanded

### Example: no NVIDIA GPU

```text
Local Satchel could not find an NVIDIA GPU.

V1 needs an NVIDIA GPU to run models with GPU acceleration. If this PC has an NVIDIA GPU, try updating your NVIDIA driver and checking again.
```

### Example: not enough VRAM

```text
This model is too large for your GPU.

Your GPU has 8 GB of VRAM. This model is expected to need more than that. Try the smaller recommended model.
```

### Example: port in use

```text
Another app is already using Local Satchel's server port.

Local Satchel can use a different local port.
```

Button:

```text
Use another port
```

### Example: runtime failed

```text
Local Satchel could not start GPU acceleration.

This usually means the NVIDIA driver is missing, outdated, or not visible to the local runtime.
```

Buttons:

```text
Check driver
Show details
```

## Tone

Use:

- Clear
- Calm
- Helpful
- Slightly warm

Avoid:

- Cute error messages
- Overuse of satchel metaphors
- Raw stack traces
- Blaming the user

## Satchel metaphor

Use sparingly:

Good:

- Packing your satchel
- Your satchel is ready

Too much:

- Your straps are tangled
- Your model fell out of the bag
- The satchel goblin failed

## Accessibility considerations

- Do not rely on color alone for pass/fail.
- Use large readable text for status.
- Make copy buttons keyboard accessible.
- Preserve logs in selectable text.
- Do not hide critical errors behind animations.
