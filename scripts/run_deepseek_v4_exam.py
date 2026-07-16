# [BLUEPRINT] MOD-INF-005 | scripts/run_deepseek_v4_exam.py | §
# [MODULE] scripts.run_deepseek_v4_exam
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
DeepSeek V4 入职考试运行脚本
============================
对 deepseek-v4-flash 和 deepseek-v4-pro 两个模型，
分别在思考模式和非思考模式下运行五轴入职考试，
计算并输出详细费用报告。

定价基准 (人民币元/百万tokens，缓存未命中):
  deepseek-v4-flash: 输入 1元/M, 输出 2元/M
  deepseek-v4-pro:   输入 3元/M, 输出 6元/M (2.5折优惠价)

4 个考试变体:
  1. deepseek-v4-flash-thinking
  2. deepseek-v4-flash-non-thinking
  3. deepseek-v4-pro-thinking
  4. deepseek-v4-pro-non-thinking

用法:
    python scripts/run_deepseek_v4_exam.py
    python scripts/run_deepseek_v4_exam.py --model deepseek-v4-pro
    python scripts/run_deepseek_v4_exam.py --model deepseek-v4-flash --no-thinking
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from zephyr.shared.security.secrets import get_required_secret, get_secret_or_default

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
_log = logging.getLogger("deepseek_v4_exam")

# 通过 SSoT secret loader 读取（.env 由 zephyr/__init__.py 自动加载）；main() 校验非空
DEEPSEEK_API_KEY = get_secret_or_default("DEEPSEEK_API_KEY")


def run_exam(model: str, thinking: bool) -> dict[str, Any]:
    from zephyr.intelligence.model_profiling.deepseek_v4_chat import DeepSeekV4Chat
    from zephyr.intelligence.model_profiling.exam_orchestrator import ExamOrchestrator

    variant = f"{model}{'-thinking' if thinking else '-non-thinking'}"
    _log.info("=" * 60)
    _log.info("Starting exam: %s", variant)
    _log.info("=" * 60)

    chat = DeepSeekV4Chat(
        model=model,
        api_key=DEEPSEEK_API_KEY,
        thinking=thinking,
        max_tokens=4096,
    )

    orch = ExamOrchestrator(chat, model_id=variant)
    t0 = time.time()
    passport = orch.run_full_exam(skip_drift=True)
    passport.save()

    elapsed = time.time() - t0

    result = {
        "variant": variant,
        "model": model,
        "thinking": thinking,
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
        "cost": {
            "total_cost_rmb": round(chat.cumulative_cost_rmb, 6),
            "input_tokens": chat.cumulative_input_tokens,
            "output_tokens": chat.cumulative_output_tokens,
            "total_tokens": chat.cumulative_input_tokens + chat.cumulative_output_tokens,
            "api_calls": chat.call_count,
            "pricing_input_per_1M_rmb": chat._pricing["input_per_1M"],
            "pricing_output_per_1M_rmb": chat._pricing["output_per_1M"],
        },
    }

    _log.info(
        "Result: grade=%s score=%.3f cost=%.6f元 tokens=%d",
        passport.overall_grade,
        passport.overall_score,
        chat.cumulative_cost_rmb,
        chat.cumulative_input_tokens + chat.cumulative_output_tokens,
    )
    return result


def print_summary(results: list[dict[str, Any]]) -> None:
    print("\n" + "=" * 80)
    print("  DeepSeek V4 入职考试汇总报告")
    print("=" * 80)

    print(f"\n{'变体':<40} {'等级':<5} {'总分':<8} {'费用(元)':<12} {'Tokens':<10} {'耗时'}")
    print("-" * 80)

    total_cost = 0.0
    total_tokens = 0

    for r in results:
        c = r["cost"]
        print(
            f"{r['variant']:<40} "
            f"{r['overall_grade']:<5} "
            f"{r['overall_score']:<8.3f} "
            f"¥{c['total_cost_rmb']:<11.6f} "
            f"{c['total_tokens']:<10} "
            f"{r['exam_duration_seconds']:.1f}s"
        )
        total_cost += c["total_cost_rmb"]
        total_tokens += c["total_tokens"]

    print("-" * 80)
    print(f"{'合计':<40} {'':5} {'':8} ¥{total_cost:<11.6f} {total_tokens:<10}")
    print()

    print("费用明细:")
    for r in results:
        c = r["cost"]
        print(f"  {r['variant']}:")
        print(
            f"    输入: {c['input_tokens']:,} tokens × ¥{c['pricing_input_per_1M_rmb']}/M"
            f" = ¥{c['input_tokens'] / 1_000_000 * c['pricing_input_per_1M_rmb']:.6f}"
        )
        print(
            f"    输出: {c['output_tokens']:,} tokens × ¥{c['pricing_output_per_1M_rmb']}/M"
            f" = ¥{c['output_tokens'] / 1_000_000 * c['pricing_output_per_1M_rmb']:.6f}"
        )
        print(f"    合计: ¥{c['total_cost_rmb']:.6f}  ({c['api_calls']} 次 API 调用)")
    print(f"\n  总计费用: ¥{total_cost:.6f}  (约 ${total_cost * 0.14:.4f} USD)")

    capability_comparison = {}
    for r in results:
        for cap in r["safe_capabilities"]:
            capability_comparison.setdefault(cap, {})[r["variant"]] = "safe"
        for cap in r["unsafe_capabilities"]:
            capability_comparison.setdefault(cap, {})[r["variant"]] = "unsafe"

    print("\n能力对比矩阵 (safe=✓, unsafe=✗):")
    variants = [r["variant"] for r in results]
    header = f"{'能力':<25}" + "".join(f"{v[:20]:<22}" for v in variants)
    print(header)
    print("-" * len(header))
    for cap, statuses in sorted(capability_comparison.items()):
        row = f"{cap:<25}"
        for v in variants:
            s = statuses.get(v, "-")
            row += f"{'✓' if s == 'safe' else '✗':<22}"
        print(row)

    results_path = PROJECT_ROOT / "data" / "brain" / "deepseek_v4_exam_results.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n完整结果已保存: {results_path}")


def main():
    parser = argparse.ArgumentParser(description="DeepSeek V4 入职考试")
    parser.add_argument(
        "--model", choices=["deepseek-v4-flash", "deepseek-v4-pro"], help="仅测试指定模型（默认测试全部）"
    )
    parser.add_argument("--no-thinking", action="store_true", help="仅测试非思考模式")
    parser.add_argument("--thinking-only", action="store_true", help="仅测试思考模式")
    args = parser.parse_args()

    if not DEEPSEEK_API_KEY:
        try:
            get_required_secret("DEEPSEEK_API_KEY")
        except Exception as e:
            _log.error(str(e))
        return 2

    models = [args.model] if args.model else ["deepseek-v4-flash", "deepseek-v4-pro"]
    thinking_modes: list[bool] = []
    if args.no_thinking and not args.thinking_only:
        thinking_modes = [False]
    elif args.thinking_only and not args.no_thinking:
        thinking_modes = [True]
    else:
        thinking_modes = [True, False]

    variants = []
    for model in models:
        for thinking in thinking_modes:
            variants.append((model, thinking))

    print(f"\n将运行 {len(variants)} 个考试变体:")
    for m, t in variants:
        print(f"  - {m}{'-thinking' if t else '-non-thinking'}")
    print()

    results = []
    for model, thinking in variants:
        try:
            result = run_exam(model, thinking)
            results.append(result)
        except Exception as exc:
            variant = f"{model}{'-thinking' if thinking else '-non-thinking'}"
            _log.error("Exam failed for %s: %s", variant, exc)
            results.append(
                {
                    "variant": variant,
                    "model": model,
                    "thinking": thinking,
                    "error": str(exc),
                    "overall_grade": "F",
                    "overall_score": 0.0,
                }
            )

    if results:
        print_summary(results)

    failed = [r for r in results if r.get("error")]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
