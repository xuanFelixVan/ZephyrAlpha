# [BLUEPRINT] MOD-RESOURCE_OPTIMIZATION_ENGINE | docs/03_modules/_cross_layer/resource_optimization_engine/blueprint.md | §new-GPU
# [MODULE] zephyr.trading.gpu_monitor
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.__init__
# [CONSUMERS] zephyr.trading.resource_optimization; zephyr.shared.lifecycle.daemon_registry
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] collect_gpu_stats 必须在 nvidia-smi 不可用时优雅降级返回 available=False
# [MODIFY-GUARD] MOD-RESOURCE_OPTIMIZATION_ENGINE §new-GPU
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] collect_gpu_stats 返回 dict，异常时返回 {"available": False, "error": str}
# [TESTS]
# [A_module] module_id=MOD-RESOURCE_OPTIMIZATION_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


gpu_monitor.py — NVIDIA GPU 状态采集器
======================================
通过 nvidia-smi 采集 GPU 使用率/显存，纳入 ResourceOptimizationEngine 压力分级。
nvidia-smi 不可用时优雅降级（available=False）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: nvidia-smi 命令行 CSV 输出（外部进程）
#   fields: utilization.gpu(%) + memory.used(MB) + memory.total(MB)，每行一张卡
#   code: nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits L41
# 层: 算法
# - id: A1
#   name_zh: ① 调用 nvidia-smi 子进程
#   name_en: _parse_nvidia_smi (subprocess call)
#   intro: 隐藏窗口跑 nvidia-smi 查询 GPU 利用率与显存，超时 10 秒
#   desc: run_subprocess_hidden 执行查询；returncode≠0 或空输出 → available=False
#   inputs: I1
#   outputs: 原始 CSV 文本或不可用标记
# - id: A2
#   name_zh: ② CSV 解析与多卡聚合
#   name_en: _parse_nvidia_smi (parse+aggregate)
#   intro: 逐行解析浮点，跨卡求平均利用率、显存加总并 MB→GB
#   desc: 每行 split(",") 取3列 float；坏行跳过；gpu_percent=Σpct/count 保留1位；memory_*_gb=ΣMB/1024 保留2位；count=0→available=False
#   inputs: A1
#   outputs: available/gpu_count/gpu_percent/memory_used_gb/memory_total_gb
# - id: A3
#   name_zh: ③ 优雅降级包装
#   name_en: collect_gpu_stats
#   intro: 无显卡/超时/任何异常都返回 available=False 的兜底字典
#   desc: FileNotFoundError→available=False；TimeoutExpired→+error=timeout；其他异常告警→+error=str(exc)
#   inputs: A2 A1
#   outputs: GPU 状态字典（含降级）
#   invariant: nvidia-smi 不可用时必须返回 available=False 不抛异常
# 层: 输出
# - id: O1
#   name_zh: GPU 状态字典 gpu_stats
#   name_en: collect_gpu_stats 返回 dict
#   intro: 供资源优化引擎做压力分级的 GPU 利用率/显存快照
#   invariant: 异常时返回 {"available": False, "error": str}
#   downstream: resource_optimization（ResourceOptimizationEngine 压力分级）；daemon_registry
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A1 --> A3
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import logging
import subprocess
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["collect_gpu_stats"]


def _parse_nvidia_smi() -> dict[str, Any]:
    from zephyr.shared.infra.process_pool import run_subprocess_hidden

    result = run_subprocess_hidden(
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
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("gpu_monitor: collect failed: %s", exc, exc_info=True)
        return {"available": False, "error": str(exc)}
