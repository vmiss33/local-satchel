from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from typing import Any


DEFAULT_CATALOG_PATH = resources.files("local_satchel.model_catalog").joinpath("models.json")


def load_catalog(path: str | Path = DEFAULT_CATALOG_PATH) -> dict[str, Any]:
    catalog_path = Path(path)
    with catalog_path.open("r", encoding="utf-8") as handle:
        catalog = json.load(handle)
    validate_catalog(catalog)
    return catalog


def validate_catalog(catalog: dict[str, Any]) -> None:
    if "models" not in catalog or not isinstance(catalog["models"], list):
        raise ValueError("Catalog must contain a models list")
    if "vram_tiers" not in catalog or not isinstance(catalog["vram_tiers"], list):
        raise ValueError("Catalog must contain explicit vram_tiers")

    model_ids = {model.get("id") for model in catalog["models"]}
    for tier in catalog["vram_tiers"]:
        for field in ("recommended_model_id", "fallback_model_id"):
            model_id = tier.get(field)
            if model_id is not None and model_id not in model_ids:
                raise ValueError(f"Tier {tier.get('tier_id')} references unknown {field}: {model_id}")
        for model_id in tier.get("candidate_model_ids", []):
            if model_id not in model_ids:
                raise ValueError(f"Tier {tier.get('tier_id')} references unknown candidate: {model_id}")


def models_by_id(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {model["id"]: model for model in catalog["models"]}
