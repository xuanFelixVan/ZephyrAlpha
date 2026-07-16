# [BLUEPRINT] MOD-INF-005 | scripts/run_ollama_exam.py | §
# [MODULE] scripts.run_ollama_exam
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.integration.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
Ollama 入职考试运行脚本
======================
对本地 Ollama 模型运行五轴入职考试（33项能力109题）。
零费用，网络仅 localhost。

支持模型:
  - qwen3:8b
  - deepseek-r1:8b
  - deepseek-r1:14b
  - qwen2.5-coder:14b
  - qwen3-coder:30b

用法:
    python scripts/run_ollama_exam.py
    python scripts/run_ollama_exam.py --model qwen3:8b
    python scripts/run_ollama_exam.py --model qwen3:8b --timeout 120
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
_log = logging.getLogger("ollama_exam")

DEFAULT_MODELS = ["qwen3:8b", "deepseek-r1:8b", "deepseek-r1:14b", "qwen2.5-coder:14b"]


def run_exam(model: str, timeout_s: float = 120.0) -> dict[str, Any]:
    from zephyr.integration.local_model.ollama_chat import OllamaChat
    from zephyr.intelligence.model_profiling.exam_orchestrator import ExamOrchestrator

    model_id = model.replace(":", "_").replace("/", "_")
    _log.info("=" * 60)
    _log.info("Starting exam: %s", model)
    _log.info("=" * 60)

    chat = OllamaChat(
        model=model,
        timeout_s=timeout_s,
        max_tokens=4096,
    )

    orch = ExamOrchestrator(chat, model_id=model_id)
    t0 = time.time()
    passport = orch.run_full_exam(skip_drift=True)
    passport.save()

    elapsed = time.time() - t0

    result = {
        "variant": model,
        "model": model,
        "exam_timestamp": passport.exam_timestamp,
        "exam_duration_seconds": round(elapsed, 1),
        "overall_grade": passport.overall_grade,
        "overall_score": passport.overall_score,
        "breadth_score": passport.breadth.score,
        "breadth_passed": passport.breadth.passed,
        "breadth_total": passport.breadth.total,
        "breadth_failed": passport.breadth.failed_capabilities,
        "depth_score": passport.depth.overall_score,
        "hallucination_rate": passport.hallucination.overall_rate,
        "fabrication_rate": passport.hallucination.fabrication_rate,
        "inconsistency_rate": passport.hallucination.inconsistency_rate,
        "refusal_rate": passport.hallucination.refusal_rate,
        "speed_avg_latency_ms": passport.speed.avg_latency_ms,
        "speed_p50_ms": passport.speed.latency_p50_ms,
        "speed_p95_ms": passport.speed.latency_p95_ms,
        "safe_capabilities": passport.recommendations.safe_capabilities,
        "unsafe_capabilities": passport.recommendations.unsafe_capabilities,
        "recommendations_note": passport.recommendations.note,
    }

    _log.info(
        "Result: grade=%s score=%.3f breadth=%d/%d safe=%d unsafe=%d",
        passport.overall_grade,
        passport.overall_score,
        passport.breadth.passed,
        passport.breadth.total,
        len(passport.recommendations.safe_capabilities),
        len(passport.recommendations.unsafe_capabilities),
    )
    return result


def print_summary(results: list[dict[str, Any]]) -> None:
    print("\n" + "=" * 80)
    print("  Ollama 入职考试汇总报告")
    print("=" * 80)

    print(f"\n{'模型':<30} {'等级':<5} {'总分':<8} {'breadth':<10} {'safe':<6} {'耗时'}")
    print("-" * 80)

    for r in results:
        print(
            f"{r['variant']:<30} "
            f"{r['overall_grade']:<5} "
            f"{r['overall_score']:<8.3f} "
            f"{r['breadth_passed']}/{r['breadth_total']:<8} "
            f"{len(r['safe_capabilities']):<6} "
            f"{r['exam_duration_seconds']:.1f}s"
        )
    print()

    capability_comparison: dict[str, dict[str, str]] = {}
    for r in results:
        for cap in r["safe_capabilities"]:
            capability_comparison.setdefault(cap, {})[r["variant"]] = "safe"
        for cap in r["unsafe_capabilities"]:
            capability_comparison.setdefault(cap, {})[r["variant"]] = "unsafe"

    print("能力对比矩阵 (safe=✓, unsafe=✗):")
    variants = [r["variant"] for r in results]
    header = f"{'能力':<35}" + "".join(f"{v[:20]:<22}" for v in variants)
    print(header)
    print("-" * len(header))
    for cap, statuses in sorted(capability_comparison.items()):
        row = f"{cap:<35}"
        for v in variants:
            s = statuses.get(v, "-")
            row += f"{'✓' if s == 'safe' else '✗':<22}"
        print(row)

    results_path = PROJECT_ROOT / "data" / "brain" / "ollama_exam_results.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n完整结果已保存: {results_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ollama 入职考试")
    parser.add_argument(
        "--model",
        help="仅测试指定模型（默认测试全部）",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=120.0,
        help="单次 API 调用超时秒数（默认 120）",
    )
    args = parser.parse_args()

    models = [args.model] if args.model else DEFAULT_MODELS

    print(f"\n将运行 {len(models)} 个考试变体:")
    for m in models:
        print(f"  - {m}")
    print()

    results: list[dict[str, Any]] = []
    for model in models:
        try:
            result = run_exam(model, timeout_s=args.timeout)
            results.append(result)
        except Exception as exc:
            _log.error("Exam failed for %s: %s", model, exc)
            results.append(
                {
                    "variant": model,
                    "model": model,
                    "overall_grade": "F",
                    "overall_score": 0.0,
                    "error": str(exc),
                }
            )

    if results:
        print_summary(results)


if __name__ == "__main__":
    main()
