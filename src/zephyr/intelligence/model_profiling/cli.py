# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] zephyr.intelligence.model_profiling.cli
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.intelligence.model_profiling.__init__; zephyr.intelligence.model_profiling.results_writer
# [CONSUMERS] MOD-INF-034
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] CLI入口;discover/quick/benchmark/drift/best/history六命令
# [MODIFY-GUARD] docs/03_modules/_cross_layer/model_profiler/blueprint.md;src/zephyr/intelligence/model_profiling/__init__.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CLIError
# [TESTS] tests/test_model_profiler/
# [A_module] module_id=MOD-RSC_cli | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
model-profiler.cli — 模型性能检测命令行入口
==============================================
用法
----
    python -m zephyr.intelligence.model_profiling.cli discover     # 列出所有可用模型
    python -m zephyr.intelligence.model_profiling.cli quick qwen3:8b  # 快速测试单个模型
    python -m zephyr.intelligence.model_profiling.cli benchmark    # 全量 benchmark
    python -m zephyr.intelligence.model_profiling.cli drift qwen3:8b   # 漂移检测
    python -m zephyr.intelligence.model_profiling.cli best         # 显示最佳模型
    python -m zephyr.intelligence.model_profiling.cli history      # 查看历史 benchmark 记录
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import sys


def cmd_discover() -> None:
    from zephyr.intelligence.model_profiling import ModelDiscovery

    d = ModelDiscovery()
    if not d.ollama_available():
        print("Ollama 服务未运行，请先启动 Ollama。")
        return

    models = d.discover_ollama()
    if not models:
        print("未找到任何 Ollama 模型。")
        return

    print(f"\n共发现 {len(models)} 个 Ollama 模型:\n")
    print(f"  {'模型名':<30} {'大小':>8} {'参数量':>12} {'量化':>10}")
    print(f"  {'-' * 30} {'-' * 8} {'-' * 12} {'-' * 10}")
    for m in sorted(models, key=lambda x: x.size_bytes, reverse=True):
        print(f"  {m.name:<30} {m.size_gb:>7.1f}GB {m.parameter_size:>12} {m.quantization_level:>10}")


def cmd_quick(model_name: str) -> None:
    from zephyr.intelligence.model_profiling import ModelProfiler

    profiler = ModelProfiler()
    profile = profiler.quick_profile(model_name)

    if profile is None or profile.total_tests == 0:
        print(f"无法测试模型: {model_name}")
        return

    print(f"\n  {model_name} — 快速评测")
    print(f"  {'─' * 50}")
    print(f"  综合评分: {profile.average_score:.3f}")
    print(f"  通过率:   {profile.passed_tests}/{profile.total_tests}")
    print(f"  延迟 P50: {profile.latency_p50_ms:.0f}ms")
    print(f"  吞吐量:   {profile.throughput_tokens_per_sec:.0f} tok/s")
    print()
    for r in profile.case_results:
        status = "PASS" if r.passed else "FAIL"
        print(f"  [{status}] {r.case_id:<8} score={r.score:.2f}  {r.latency_ms:.0f}ms  {r.tokens_per_second:.0f}tok/s")
    print()


def cmd_benchmark() -> None:
    from zephyr.intelligence.model_profiling import ModelProfiler

    profiler = ModelProfiler()
    print("\n正在运行全量 model benchmark...\n")
    results = profiler.profile_ollama_only()
    profiler.print_ranking(results)


def cmd_best() -> None:
    from zephyr.intelligence.model_profiling import ModelProfiler

    profiler = ModelProfiler()
    results = profiler.profile_ollama_only()

    scored = sorted(
        [p for p in results if p.average_score > 0 and p.available],
        key=lambda p: p.average_score,
        reverse=True,
    )
    if not scored:
        print("没有可用的 benchmark 结果（可能需要先运行 benchmark）。")
        return

    best = scored[0]
    print(f"\n  最佳模型: {best.model_name}")
    print(f"  综合评分: {best.average_score:.3f}")
    print(f"  延迟 P50: {best.latency_p50_ms:.0f}ms")
    print(f"  延迟 P95: {best.latency_p95_ms:.0f}ms")
    print(f"  吞吐量:   {best.throughput_tokens_per_sec:.0f} tok/s")
    print(f"  幻觉率:   {best.hallucination_rate:.1%}")
    print(f"  代码质量: {best.code_validity_rate:.3f}")
    print(f"  推荐:     {best.recommendation}")
    if len(scored) > 1:
        second = scored[1]
        gap = best.average_score - second.average_score
        print(f"\n  第二名: {second.model_name} (差距 {gap:.3f})")
    print()


def cmd_drift(model_name: str) -> None:
    from zephyr.intelligence.model_profiling.results_writer import (
        detect_drift,
        load_benchmark_history,
    )

    history = load_benchmark_history(model_name)
    if len(history) < 2:
        print(f"\n  {model_name}: 历史数据不足（仅 {len(history)} 条记录），无法检测漂移。")
        print("  请至少运行两次 benchmark 后再检测。\n")
        return

    report = detect_drift(history)
    print(f"\n  {model_name} — 漂移检测")
    print(f"  {'─' * 50}")
    print(f"  最新: {report.get('latest_date', '?')}")
    print(f"  上次: {report.get('previous_date', '?')}")
    print(f"  漂移: {'⚠  检测到漂移!' if report.get('drift_detected') else '✓ 无显著漂移'}")
    details = report.get("details", {})
    if details:
        print(f"  分数变化: {details.get('score_delta', 0):+.4f}")
        print(
            f"  延迟变化: {details.get('latency_delta_ms', 0):+.1f}ms ({details.get('latency_increase_pct', 0):+.1f}%)"
        )
        print(f"  吞吐变化: {details.get('throughput_delta_tok_per_sec', 0):+.1f} tok/s")
        print(f"  幻觉变化: {details.get('hallucination_rate_delta', 0):+.4f}")
        cat_drift = details.get("category_drift", {})
        if cat_drift:
            print("  分维度:")
            for cat, delta in cat_drift.items():
                print(f"    {cat}: {delta:+.4f}")
    print()


def cmd_history() -> None:
    base = Path("data/model_profiles")
    if not base.exists():
        print("暂无 benchmark 历史记录。")
        return

    files = sorted(base.glob("benchmark_*.jsonl"))
    if not files:
        print("暂无 benchmark 历史记录。")
        return

    print(f"\n  Benchmark 历史记录 ({len(files)} 次)\n")
    for f in files:
        ts = f.stem.replace("benchmark_", "")
        record_count = 0
        try:
            for line in f.read_text(encoding="utf-8").strip().split("\n"):
                if line.strip():
                    record_count += 1
        except Exception as e:
            logger.warning("suppressed error in cli", exc_info=True)
        size_kb = f.stat().st_size / 1024
        print(f"  {ts}  ->  {record_count} models, {size_kb:.1f}KB")
    print()


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return

    cmd = args[0].lower()

    if cmd == "discover":
        cmd_discover()
    elif cmd == "quick":
        if len(args) < 2:
            print("用法: python -m zephyr.intelligence.model_profiling.cli quick <model_name>")
            return
        cmd_quick(args[1])
    elif cmd == "benchmark":
        cmd_benchmark()
    elif cmd == "best":
        cmd_best()
    elif cmd == "drift":
        if len(args) < 2:
            print("用法: python -m zephyr.intelligence.model_profiling.cli drift <model_name>")
            return
        cmd_drift(args[1])
    elif cmd == "history":
        cmd_history()
    else:
        print(f"未知命令: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
