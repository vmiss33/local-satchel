# Hermes Provider Configuration Example

Local Satchel configures Hermes Agent through:

```powershell
satchel connect hermes
```

That command writes a named `Local Satchel` provider into the base Hermes config and sets it as the active model provider.

To configure an additional Hermes profile instead, create that profile in Hermes first, then point Local Satchel at it:

```powershell
hermes profile create myprofile
satchel connect hermes --profile myprofile
```

Local Satchel does not create Hermes profiles for you. Use `--profile default` or `--profile base` when you want to be explicit about configuring the base Hermes profile.

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

## Hermes profile behavior

Local Satchel configures the base Hermes profile by default:

```powershell
satchel connect hermes
```

For a named Hermes profile, Local Satchel runs Hermes config commands with Hermes' profile flag:

```powershell
hermes --profile myprofile config set providers.local-satchel.base_url http://127.0.0.1:8080/v1
```

Use:

```powershell
satchel connect hermes --profile myprofile
```

`--profile base` and `--profile default` both mean the base Hermes config.

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

Start a new Hermes session after connecting so Hermes reloads its config. For a named profile, start that same profile:

```powershell
hermes --profile myprofile
```
