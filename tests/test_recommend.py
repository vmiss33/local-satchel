import copy
from pathlib import Path

from local_satchel.catalog import load_catalog
from local_satchel.recommend import recommend_for_vram


CATALOG_PATH = Path(__file__).resolve().parents[1] / "model-catalog" / "models.json"


def test_catalog_has_explicit_card_size_tiers():
    catalog = load_catalog(CATALOG_PATH)

    tier_ids = [tier["tier_id"] for tier in catalog["vram_tiers"]]

    assert tier_ids == [
        "vram-4gb",
        "vram-6gb",
        "vram-8gb",
        "vram-10gb",
        "vram-12gb",
        "vram-16gb",
        "vram-24gb",
        "vram-32gb",
        "vram-48gb-plus",
    ]


def test_8gb_card_recommends_validated_nemotron_4b():
    catalog = load_catalog(CATALOG_PATH)

    recommendation = recommend_for_vram(catalog, detected_vram_gb=8)

    assert recommendation.tier_id == "vram-8gb"
    assert recommendation.model_id == "nvidia-nemotron-3-nano-4b-q4-k-m"
    assert recommendation.is_exact_tier_recommendation is True
    assert recommendation.is_fallback is False
    assert recommendation.model["automatic_recommendation_eligible"] is True


def test_12gb_card_uses_explicit_tier_and_falls_back_until_8b_is_validated():
    catalog = load_catalog(CATALOG_PATH)

    recommendation = recommend_for_vram(catalog, detected_vram_gb=12)

    assert recommendation.tier_id == "vram-12gb"
    assert recommendation.model_id == "nvidia-nemotron-3-nano-4b-q4-k-m"
    assert recommendation.is_exact_tier_recommendation is False
    assert recommendation.is_fallback is True
    assert recommendation.candidate_model_ids == ["llama-3-1-nemotron-nano-8b-q4-k-m"]
    assert "12 GB" in recommendation.user_message


def test_12gb_card_recommends_8b_after_catalog_marks_it_validated():
    catalog = load_catalog(CATALOG_PATH)
    catalog = copy.deepcopy(catalog)
    model = next(m for m in catalog["models"] if m["id"] == "llama-3-1-nemotron-nano-8b-q4-k-m")
    model["status"] = "validated-windows-llamacpp-cuda"
    model["automatic_recommendation_eligible"] = True
    tier = next(t for t in catalog["vram_tiers"] if t["tier_id"] == "vram-12gb")
    tier["recommended_model_id"] = "llama-3-1-nemotron-nano-8b-q4-k-m"

    recommendation = recommend_for_vram(catalog, detected_vram_gb=12)

    assert recommendation.tier_id == "vram-12gb"
    assert recommendation.model_id == "llama-3-1-nemotron-nano-8b-q4-k-m"
    assert recommendation.is_exact_tier_recommendation is True
    assert recommendation.is_fallback is False


def test_4gb_card_does_not_auto_download_any_model():
    catalog = load_catalog(CATALOG_PATH)

    recommendation = recommend_for_vram(catalog, detected_vram_gb=4)

    assert recommendation.tier_id == "vram-4gb"
    assert recommendation.model_id is None
    assert recommendation.model is None
    assert recommendation.can_auto_download is False
    assert "below" in recommendation.user_message
