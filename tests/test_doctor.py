from local_satchel.doctor import parse_nvidia_smi_csv, summarize_readiness


def test_parse_nvidia_smi_csv_extracts_gpu_name_vram_and_driver():
    output = "NVIDIA GeForce RTX 4070 Laptop GPU, 8188, 581.04\n"

    gpu = parse_nvidia_smi_csv(output)

    assert gpu.name == "NVIDIA GeForce RTX 4070 Laptop GPU"
    assert gpu.vram_mb == 8188
    assert gpu.vram_gb == 8
    assert gpu.driver_version == "581.04"


def test_summarize_readiness_includes_model_recommendation():
    summary = summarize_readiness(
        gpu_name="Example RTX 3080 Ti Laptop GPU",
        detected_vram_gb=12,
        driver_version="581.04",
        disk_free_gb=250,
        recommendation_model_name="NVIDIA Nemotron 3 Nano 4B",
        tier_label="12 GB NVIDIA GPUs",
        is_fallback=True,
    )

    assert summary.status == "ready-with-fallback"
    assert "Example RTX 3080 Ti Laptop GPU" in summary.message
    assert "12 GB NVIDIA GPUs" in summary.message
    assert "temporary safe fallback" in summary.message
