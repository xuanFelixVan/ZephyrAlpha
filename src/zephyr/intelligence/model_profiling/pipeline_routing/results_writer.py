# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md
# [MODULE] zephyr.intelligence.model_profiling.pipeline_routing.results_writer
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.intelligence.model_profiling.pipeline_routing.profiler
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RSC_results_writer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Results Writer — 持久化 benchmark 结果，支持历史对比（漂移检测）
=================================================================
将 ModelProfile 结果写入 JSONL 文件，支持：
  - 历史结果查询（同模型多次测试对比 → 漂移检测）
  - 与 Pipeline ModelBenchmarkResult 数据模型对接
  - 增量写入（每次 benchmark 追加一行）
  - 历史趋势分析

用法
----
    write_benchmark_results(profiles, "data/model_profiles/")
    history = load_benchmark_history("qwen3:8b")
    drift_report = detect_drift(history)
"""

from __future__ import annotations

from typing import Final
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from zephyr.intelligence.model_profiling.pipeline_routing.profiler import ModelProfile
from zephyr.shared.utils.time_utils import now_utc

_log = logging.getLogger(__name__)

DEFAULT_OUTPUT_DIR: Final[str] = "data/model_profiles"


def write_benchmark_results(
    profiles: list[ModelProfile],
    output_dir: str = DEFAULT_OUTPUT_DIR,
) -> str:
    """将 benchmark 结果写入 JSONL 文件（每行一个模型的结果）。"""
    base = Path(output_dir)
    base.mkdir(parents=True, exist_ok=True)
    timestamp = now_utc().strftime("%Y%m%d_%H%M%S")
    filepath = base / f"benchmark_{timestamp}.jsonl"

    # 5.74.3 修复：原子写入——tmp 文件 + flush + fsync + os.replace，
    # 防止写入中途崩溃产生截断的 JSONL 文件导致 load_benchmark_history 解析失败。
    tmp_path = str(filepath) + ".tmp"
    lines_written = 0
    with open(tmp_path, "w", encoding="utf-8") as f:
        for p in profiles:
            record = _profile_to_dict(p)
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            lines_written += 1
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, str(filepath))

    _log.info("ResultsWriter: wrote %d profiles → %s", lines_written, filepath)
    return str(filepath)


def load_benchmark_history(
    model_name: str,
    results_dir: str = DEFAULT_OUTPUT_DIR,
) -> list[dict[str, Any]]:
    """加载某个模型的所有历史 benchmark 结果（按时间排序）。"""
    base = Path(results_dir)
    if not base.exists():
        return []

    history: list[dict[str, Any]] = []
    for f in sorted(base.glob("benchmark_*.jsonl")):
        try:
            for line in f.read_text(encoding="utf-8").strip().split("\n"):
                if not line.strip():
                    continue
                record = json.loads(line)
                if record.get("model_name") == model_name:
                    history.append(record)
        except Exception as exc:
            _log.debug("ResultsWriter: skip %s: %s", f.name, exc, exc_info=True)

    history.sort(key=lambda r: r.get("benchmark_date", ""))
    return history


def detect_drift(
    history: list[dict[str, Any]],
    threshold_score_decline: float = 0.10,
    threshold_latency_increase_pct: float = 0.50,
) -> dict[str, Any]:
    """检测模型性能漂移——对比最新与历史的分数/延迟变化。"""
    if len(history) < 2:
        return {"drift_detected": False, "reason": "insufficient_history", "details": {}}

    latest = history[-1]
    prev = history[-2]

    score_delta = latest.get("average_score", 0.0) - prev.get("average_score", 0.0)
    latency_delta = latest.get("latency_p50_ms", 0.0) - prev.get("latency_p50_ms", 0.0)
    prev_latency = prev.get("latency_p50_ms", 1.0)
    latency_pct = (latency_delta / prev_latency) if prev_latency > 0 else 0.0

    drift_detected = abs(score_delta) > threshold_score_decline or latency_pct > threshold_latency_increase_pct

    category_drift: dict[str, float] = {}
    for cat in set(list(latest.get("category_scores", {}).keys())):
        prev_cat = prev.get("category_scores", {}).get(cat, 0.0)
        latest_cat = latest.get("category_scores", {}).get(cat, 0.0)
        if prev_cat > 0:
            category_drift[cat] = round(latest_cat - prev_cat, 4)

    return {
        "drift_detected": drift_detected,
        "model_name": latest.get("model_name", ""),
        "latest_date": latest.get("benchmark_date", ""),
        "previous_date": prev.get("benchmark_date", ""),
        "details": {
            "score_delta": round(score_delta, 4),
            "latency_delta_ms": round(latency_delta, 1),
            "latency_increase_pct": round(latency_pct * 100, 1),
            "throughput_delta_tok_per_sec": round(
                latest.get("throughput_tokens_per_sec", 0.0) - prev.get("throughput_tokens_per_sec", 0.0), 1
            ),
            "category_drift": category_drift,
            "hallucination_rate_delta": round(
                latest.get("hallucination_rate", 0.0) - prev.get("hallucination_rate", 0.0), 4
            ),
        },
    }


def to_model_benchmark_result(profile: ModelProfile) -> dict[str, Any]:
    """将 ModelProfile 转换为 Pipeline 中 ModelBenchmarkResult 格式。"""
    return {
        "model_name": profile.model_name,
        "model_version": profile.model_name.split(":")[-1] if ":" in profile.model_name else "",
        "benchmark_date": profile.benchmark_date,
        "task_scores": {
            "composite_score": profile.average_score,
            "latency_p50_ms": profile.latency_p50_ms,
            "latency_p95_ms": profile.latency_p95_ms,
            "throughput_tok_per_sec": profile.throughput_tokens_per_sec,
            "hallucination_rate": profile.hallucination_rate,
            "code_validity_rate": profile.code_validity_rate,
            "json_validity_rate": profile.json_validity_rate,
            **profile.category_scores,
        },
        "vs_previous_version": None,
        "recommendation": profile.recommendation,
        "regression_detected": profile.average_score < 0.3,
        "regression_tasks": [r.case_id for r in profile.case_results if r.passed is False and r.error == ""],
    }


def _profile_to_dict(p: ModelProfile) -> dict[str, Any]:
    return {
        "model_name": p.model_name,
        "source": p.source,
        "benchmark_date": p.benchmark_date,
        "total_tests": p.total_tests,
        "passed_tests": p.passed_tests,
        "average_score": p.average_score,
        "latency_p50_ms": p.latency_p50_ms,
        "latency_p95_ms": p.latency_p95_ms,
        "latency_p99_ms": p.latency_p99_ms,
        "throughput_tokens_per_sec": p.throughput_tokens_per_sec,
        "total_tokens": p.total_tokens,
        "total_time_ms": p.total_time_ms,
        "category_scores": p.category_scores,
        "hallucination_rate": p.hallucination_rate,
        "refusal_rate": p.refusal_rate,
        "json_validity_rate": p.json_validity_rate,
        "code_validity_rate": p.code_validity_rate,
        "recommendation": p.recommendation,
        "rank": p.rank,
        "available": p.available,
        "error": p.error,
    }
