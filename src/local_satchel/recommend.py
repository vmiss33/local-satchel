from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .catalog import models_by_id

VALIDATED_STATUS = "validated-windows-llamacpp-cuda"


@dataclass(frozen=True)
class Recommendation:
    tier_id: str
    tier_label: str
    model_id: str | None
    model: dict[str, Any] | None
    candidate_model_ids: list[str]
    user_message: str
    is_exact_tier_recommendation: bool
    is_fallback: bool
    can_auto_download: bool

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["model_name"] = self.model.get("display_name") if self.model else None
        data["filename"] = self.model.get("filename") if self.model else None
        return data


def recommend_for_vram(catalog: dict[str, Any], detected_vram_gb: int | float) -> Recommendation:
    tier = find_tier(catalog, detected_vram_gb)
    model_lookup = models_by_id(catalog)

    recommended_id = tier.get("recommended_model_id")
    recommended_model = model_lookup.get(recommended_id) if recommended_id else None
    if _is_auto_recommendable(recommended_model):
        return _make_recommendation(
            tier=tier,
            model=recommended_model,
            exact=True,
            fallback=False,
            can_auto_download=True,
        )

    fallback_id = tier.get("fallback_model_id")
    fallback_model = model_lookup.get(fallback_id) if fallback_id else None
    if _is_auto_recommendable(fallback_model):
        return _make_recommendation(
            tier=tier,
            model=fallback_model,
            exact=False,
            fallback=True,
            can_auto_download=True,
        )

    lower_model = _best_lower_validated_model(catalog, detected_vram_gb)
    if lower_model is not None:
        return _make_recommendation(
            tier=tier,
            model=lower_model,
            exact=False,
            fallback=True,
            can_auto_download=True,
        )

    return _make_recommendation(
        tier=tier,
        model=None,
        exact=False,
        fallback=False,
        can_auto_download=False,
    )


def find_tier(catalog: dict[str, Any], detected_vram_gb: int | float) -> dict[str, Any]:
    for tier in catalog["vram_tiers"]:
        minimum = tier["detected_vram_gb_min"]
        maximum = tier["detected_vram_gb_max"]
        if detected_vram_gb >= minimum and (maximum is None or detected_vram_gb <= maximum):
            return tier
    raise ValueError(f"No VRAM tier covers {detected_vram_gb} GB")


def _is_auto_recommendable(model: dict[str, Any] | None) -> bool:
    return bool(
        model
        and model.get("status") == VALIDATED_STATUS
        and model.get("automatic_recommendation_eligible") is True
    )


def _best_lower_validated_model(catalog: dict[str, Any], detected_vram_gb: int | float) -> dict[str, Any] | None:
    candidates = [
        model
        for model in catalog["models"]
        if _is_auto_recommendable(model)
        and model.get("recommended_vram_gb", 10**9) <= detected_vram_gb
    ]
    if not candidates:
        return None
    return sorted(candidates, key=lambda model: model.get("quality_rank", 0), reverse=True)[0]


def _make_recommendation(
    *,
    tier: dict[str, Any],
    model: dict[str, Any] | None,
    exact: bool,
    fallback: bool,
    can_auto_download: bool,
) -> Recommendation:
    message = f"{tier['label']}: {tier.get('user_message', '')}"
    if fallback and model:
        message = f"{message} Using {model['display_name']} as a temporary safe fallback."
    return Recommendation(
        tier_id=tier["tier_id"],
        tier_label=tier["label"],
        model_id=model.get("id") if model else None,
        model=model,
        candidate_model_ids=list(tier.get("candidate_model_ids", [])),
        user_message=message,
        is_exact_tier_recommendation=exact,
        is_fallback=fallback,
        can_auto_download=can_auto_download,
    )
