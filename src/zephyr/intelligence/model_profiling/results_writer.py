# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] zephyr.intelligence.model_profiling.results_writer
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.intelligence.model_profiling.profiler
# [CONSUMERS] MOD-INF-009;MOD-INF-036
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] benchmark结果持久化;JSONL格式;漂移检测
# [MODIFY-GUARD] docs/03_modules/_cross_layer/model_profiler/blueprint.md;src/zephyr/intelligence/model_profiling/__init__.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] WriteError;DriftDetectionError
# [TESTS] tests/test_model_profiler/
# [A_module] module_id=MOD-INF-034 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Results Writer — 持久化 benchmark 结果，支持历史对比（漂移检测）
=================================================================
将 ModelProfile 结果写入 JSONL 文件，支持：
  - 历史结果查询（同模型多次测试对比 -> 漂移检测）
  - 与 Pipeline ModelBenchmarkResult 数据模型对接
  - 增量写入（每次 benchmark 追加一行）
  - 历史趋势分析

用法
----
    write_benchmark_results(profiles, "data/model_profiles/")
    history = load_benchmark_history("qwen3:8b")
    drift_report = detect_drift(history)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: profiles 参数
#   fields: 参数 profiles，类型注解 list[ModelProfile]
#   code: results_writer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: output_dir 参数
#   fields: 参数 output_dir，类型注解 str
#   code: results_writer.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: model_name 参数
#   fields: 参数 model_name，类型注解 str
#   code: results_writer.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: results_dir 参数
#   fields: 参数 results_dir，类型注解 str
#   code: results_writer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① write_benchmark_results
#   name_en: write_benchmark_results
#   intro: 将 benchmark 结果写入 JSONL 文件（每行一个模型的结果）。
#   desc: 将 benchmark 结果写入 JSONL 文件（每行一个模型的结果）。 ARCH-BENCH-LEAK-001：profiles 为空时跳过写入并返回 ""——空文件无消费价…；源码 L133-L170
#   inputs: profiles output_dir
#   outputs: str
# - id: A2
#   name_zh: ② load_benchmark_history
#   name_en: load_benchmark_history
#   intro: 加载某个模型的所有历史 benchmark 结果（按时间排序）。
#   desc: 加载某个模型的所有历史 benchmark 结果（按时间排序）。；源码 L173-L195
#   inputs: model_name results_dir
#   outputs: list[dict[str, Any]]
# - id: A3
#   name_zh: ③ load_latest_benchmark_results
#   name_en: load_latest_benchmark_results
#   intro: 读取最近一次落盘的 benchmark 结果——供 boot 健康判断，不触发跑分（ ）。
#   desc: 读取最近一次落盘的 benchmark 结果——供 boot 健康判断，不触发跑分（ ）。 返回 (results, meta)： - results: to_model_ben…；源码 L198-L242
#   inputs: results_dir max_age_hours
#   outputs: tuple[list[dict[str, Any]], dict[str, A…
# - id: A4
#   name_zh: ④ detect_drift
#   name_en: detect_drift
#   intro: 检测模型性能漂移——对比最新与历史的分数/延迟变化。
#   desc: 检测模型性能漂移——对比最新与历史的分数/延迟变化。；源码 L272-L315
#   inputs: history threshold_score_decline threshold_latency_increase_pct
#   outputs: dict[str, Any]
# - id: A5
#   name_zh: ⑤ to_model_benchmark_result
#   name_en: to_model_benchmark_result
#   intro: 将 ModelProfile 转换为 Pipeline 中 ModelBenchmarkResult 格式。
#   desc: 将 ModelProfile 转换为 Pipeline 中 ModelBenchmarkResult 格式。；源码 L318-L338
#   inputs: profile
#   outputs: dict[str, Any]
# 层: 输出
# - id: O1
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-INF-009;MOD-INF-036
# - id: O2
#   name_zh: list[dict[str, Any]]
#   name_en: list[dict[str, Any]]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-INF-009;MOD-INF-036
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
"""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

from zephyr.intelligence.model_profiling.profiler import ModelProfile
from zephyr.shared.utils.time_utils import now_utc

_log = logging.getLogger(__name__)

DEFAULT_OUTPUT_DIR: Final[str] = "data/model_profiles"

# ARCH-208：boot 启动路径读取上次落盘 benchmark 结果的新鲜度上限（7 天）。
# 超过即视为过期——启动降级"未知"不阻断，跑分由独立 CLI 异步执行刷新。
BENCHMARK_CACHE_MAX_AGE_HOURS: Final[float] = 168.0


def write_benchmark_results(
    profiles: list[ModelProfile],
    output_dir: str = DEFAULT_OUTPUT_DIR,
) -> str:
    """将 benchmark 结果写入 JSONL 文件（每行一个模型的结果）。

    ARCH-BENCH-LEAK-001：profiles 为空时跳过写入并返回 ""——空文件无消费价值
    （漂移检测需 ≥2 条记录，router 读空文件返回 0），且会遮蔽最新有效结果。
    """
    if not profiles:
        _log.info("ResultsWriter: empty profiles, skip writing (ARCH-BENCH-LEAK-001)")
        return ""
    base = Path(output_dir)
    base.mkdir(parents=True, exist_ok=True)
    timestamp = now_utc().strftime("%Y%m%d_%H%M%S")
    filepath = base / f"benchmark_{timestamp}.jsonl"

    # 5.74.3 修复：原子写入——tmp 文件 + flush + fsync + os.replace，
    # 防止写入中途崩溃产生截断的 JSONL 文件导致 load_benchmark_history 解析失败。
    # 裁定4 加固：异常时清理 tmp 残留（存在才删）再原样抛出，防止留下 0 字节 .tmp。
    tmp_path = str(filepath) + ".tmp"
    lines_written = 0
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            for p in profiles:
                record = _profile_to_dict(p)
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                lines_written += 1
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, str(filepath))
    except BaseException:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise

    _log.info("ResultsWriter: wrote %d profiles -> %s", lines_written, filepath)
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
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            _log.debug("ResultsWriter: skip %s: %s", f.name, exc, exc_info=True)

    history.sort(key=lambda r: r.get("benchmark_date", ""))
    return history


def load_latest_benchmark_results(
    results_dir: str = DEFAULT_OUTPUT_DIR,
    max_age_hours: float = BENCHMARK_CACHE_MAX_AGE_HOURS,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """读取最近一次落盘的 benchmark 结果——供 boot 健康判断，不触发跑分（#ARCH-208）。

    返回 (results, meta)：
      - results: to_model_benchmark_result 兼容字典列表（仅 available 模型），
        可直接传给 ModelTaskMatrix.load_benchmark_baseline / ModelRouter.load_benchmark_profiles。
      - meta: {"state": "fresh"|"stale"|"missing", "path": str, "age_hours": float|None}
    新鲜度以文件名时间戳（benchmark_%Y%m%d_%H%M%S.jsonl，UTC）判定。
    """
    base = Path(results_dir)
    if not base.exists():
        return [], {"state": "missing", "path": "", "age_hours": None}

    files = sorted(base.glob("benchmark_*.jsonl"))
    if not files:
        return [], {"state": "missing", "path": "", "age_hours": None}

    latest = files[-1]
    age_hours: float | None = None
    try:
        ts = datetime.strptime(latest.stem.replace("benchmark_", ""), "%Y%m%d_%H%M%S").replace(tzinfo=UTC)
        age_hours = (now_utc() - ts).total_seconds() / 3600.0
    except ValueError:
        _log.debug("ResultsWriter: unparsable timestamp in %s, treat as stale", latest.name)
        return [], {"state": "stale", "path": str(latest), "age_hours": None}

    if age_hours > max_age_hours:
        return [], {"state": "stale", "path": str(latest), "age_hours": age_hours}

    results: list[dict[str, Any]] = []
    try:
        for line in latest.read_text(encoding="utf-8").strip().split("\n"):
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("available"):
                results.append(_stored_record_to_benchmark_result(record))
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        _log.warning("ResultsWriter: failed to parse %s: %s", latest.name, exc, exc_info=True)
        return [], {"state": "stale", "path": str(latest), "age_hours": age_hours}

    return results, {"state": "fresh", "path": str(latest), "age_hours": age_hours}


def _stored_record_to_benchmark_result(record: dict[str, Any]) -> dict[str, Any]:
    """将落盘 JSONL 记录（_profile_to_dict 格式）转换为 to_model_benchmark_result 兼容格式。

    落盘记录不含 case 级明细（case_results 未持久化），regression_tasks 恒为空列表。
    """
    model_name = record.get("model_name", "")
    return {
        "model_name": model_name,
        "model_version": model_name.split(":")[-1] if ":" in model_name else "",
        "benchmark_date": record.get("benchmark_date", ""),
        "task_scores": {
            "composite_score": record.get("average_score", 0.0),
            "latency_p50_ms": record.get("latency_p50_ms", 0.0),
            "latency_p95_ms": record.get("latency_p95_ms", 0.0),
            "throughput_tok_per_sec": record.get("throughput_tokens_per_sec", 0.0),
            "hallucination_rate": record.get("hallucination_rate", 0.0),
            "code_validity_rate": record.get("code_validity_rate", 0.0),
            "json_validity_rate": record.get("json_validity_rate", 0.0),
            **record.get("category_scores", {}),
        },
        "vs_previous_version": None,
        "recommendation": record.get("recommendation", ""),
        "regression_detected": record.get("average_score", 0.0) < 0.3,
        "regression_tasks": [],
    }


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
