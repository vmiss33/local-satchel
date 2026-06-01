from __future__ import annotations

import math
import shutil
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class GpuInfo:
    name: str
    vram_mb: int
    driver_version: str

    @property
    def vram_gb(self) -> int:
        return max(1, math.ceil(self.vram_mb / 1024))


@dataclass(frozen=True)
class ReadinessSummary:
    status: str
    message: str


def parse_nvidia_smi_csv(output: str) -> GpuInfo:
    first_line = next((line.strip() for line in output.splitlines() if line.strip()), "")
    if not first_line:
        raise ValueError("nvidia-smi returned no GPU rows")
    parts = [part.strip() for part in first_line.split(",")]
    if len(parts) < 3:
        raise ValueError(f"Unexpected nvidia-smi CSV row: {first_line}")
    return GpuInfo(name=parts[0], vram_mb=int(parts[1]), driver_version=parts[2])


def query_nvidia_gpu() -> GpuInfo | None:
    if shutil.which("nvidia-smi") is None:
        return None
    result = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=name,memory.total,driver_version",
            "--format=csv,noheader,nounits",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return parse_nvidia_smi_csv(result.stdout)


def disk_free_gb(path: str = ".") -> int:
    usage = shutil.disk_usage(path)
    return math.floor(usage.free / (1024**3))


def summarize_readiness(
    *,
    gpu_name: str,
    detected_vram_gb: int,
    driver_version: str,
    disk_free_gb: int,
    recommendation_model_name: str | None,
    tier_label: str,
    is_fallback: bool,
) -> ReadinessSummary:
    if recommendation_model_name is None:
        return ReadinessSummary(
            status="blocked",
            message=(
                f"Local Satchel found {gpu_name} with {detected_vram_gb} GB VRAM, "
                f"but no validated Nemotron model is ready for {tier_label}."
            ),
        )
    if is_fallback:
        status = "ready-with-fallback"
        fallback_text = " Local Satchel will use a temporary safe fallback until this card-size tier has its own validated model."
    else:
        status = "ready"
        fallback_text = ""
    return ReadinessSummary(
        status=status,
        message=(
            f"Your PC is ready. {gpu_name} has {detected_vram_gb} GB VRAM "
            f"and NVIDIA driver {driver_version}. Tier: {tier_label}. "
            f"Recommended: {recommendation_model_name}. "
            f"Free disk: {disk_free_gb} GB."
            f"{fallback_text}"
        ),
    )
