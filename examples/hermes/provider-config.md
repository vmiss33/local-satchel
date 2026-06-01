# Hermes Provider Configuration Example

Local Satchel v1 should first provide copy-paste settings for any OpenAI-compatible client.

## Generic OpenAI-compatible settings

```text
Base URL: http://localhost:8080/v1
API Key: local-satchel
Model: local-satchel
```

## Hermes integration intent

V1:

- Show these values in the Local Satchel UI.
- Provide exact Hermes setup guidance once the current Hermes provider config format is validated.

V1.1:

- Detect Hermes config location.
- Back up the config.
- Add a Local Satchel provider entry.
- Verify Hermes can call the local endpoint.

## Safety

Local Satchel should never overwrite Hermes config without:

1. showing the user what will change,
2. creating a backup, and
3. offering a rollback path.
```
