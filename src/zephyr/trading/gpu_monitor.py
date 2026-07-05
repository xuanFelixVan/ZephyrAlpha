# [BLUEPRINT] MOD-RESOURCE_OPTIMIZATION_ENGINE | docs/03_modules/_cross_layer/resource_optimization_engine/blueprint.md | §new-GPU
# [MODULE] zephyr.trading.gpu_monitor
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.__init__
# [CONSUMERS] zephyr.trading.resource_optimization; zephyr.shared.lifecycle.daemon_registry
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] collect_gpu_stats 必须在 nvidia-smi 不可用时优雅降级返回 available=False
# [MODIFY-GUARD] MOD-RESOURCE_OPTIMIZATION_ENGINE §new-GPU
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] collect_gpu_stats 返回 dict，异常时返回 {"available": False, "error": str}
# [TESTS]
# [A_module] module_id=MOD-ORC_gpu_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
gpu_monitor.py — NVIDIA GPU 状态采集器
======================================
通过 nvidia-smi 采集 GPU 使用率/显存，纳入 ResourceOptimizationEngine 压力分级。
nvidia-smi 不可用时优雅降级（available=False）。
"""

from __future__ import annotations

import logging
import subprocess
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["collect_gpu_stats"]


def _parse_nvidia_smi() -> dict[str, Any]:
    result = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=utilization.gpu,memory.used,memory.total",
            "--format=csv,noheader,nounits",
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return {"available": False}

    lines = result.stdout.strip().split("\n")
    total_gpu_pct = 0.0
    total_mem_used_mb = 0.0
    total_mem_total_mb = 0.0
    gpu_count = 0

    for line in lines:
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 3:
            continue
        try:
            gpu_pct = float(parts[0])
            mem_used = float(parts[1])
            mem_total = float(parts[2])
        except (ValueError, IndexError):
            continue
        total_gpu_pct += gpu_pct
        total_mem_used_mb += mem_used
        total_mem_total_mb += mem_total
        gpu_count += 1

    if gpu_count == 0:
        return {"available": False}

    return {
        "available": True,
        "gpu_count": gpu_count,
        "gpu_percent": round(total_gpu_pct / gpu_count, 1),
        "memory_used_gb": round(total_mem_used_mb / 1024.0, 2),
        "memory_total_gb": round(total_mem_total_mb / 1024.0, 2),
    }


def collect_gpu_stats() -> dict[str, Any]:
    try:
        return _parse_nvidia_smi()
    except FileNotFoundError:
        return {"available": False}
    except subprocess.TimeoutExpired:
        logger.warning("gpu_monitor: nvidia-smi timed out")
        return {"available": False, "error": "timeout"}
    except Exception as exc:
        logger.warning("gpu_monitor: collect failed: %s", exc)
        return {"available": False, "error": str(exc)}
