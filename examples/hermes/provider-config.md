# Hermes Provider Configuration Example

Local Satchel configures Hermes Agent through:

```powershell
satchel connect hermes
```

That command writes a named `Local Satchel` provider into the Hermes config and sets it as the active model provider.

## Settings

```text
Provider: Local Satchel
Base URL: http://127.0.0.1:8080/v1
API Key: local-satchel
Model: NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf
API mode: chat_completions
```

The API key is a placeholder for clients that require an auth field. The Local Satchel V1 endpoint binds to `127.0.0.1`, so it is private to the local PC by default.

## Show settings without changing Hermes

```powershell
satchel connect hermes --show
```

Use this for other OpenAI-compatible clients or for manual troubleshooting.

## Hermes config shape

The command creates/updates this provider shape through `hermes config set`:

```yaml
providers:
  local-satchel:
    name: Local Satchel
    base_url: http://127.0.0.1:8080/v1
    api_key: local-satchel
    default_model: NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf
    api_mode: chat_completions
model:
  provider: local-satchel
  default: NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf
```

Start a new Hermes session after connecting so Hermes reloads its config.
