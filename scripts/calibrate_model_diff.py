# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §5
# [MODULE] scripts.calibrate_model_diff
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES]
# [CONSUMERS] CI回归校准;人工模型对比
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 校准目标1.2-1.4x;只读护照数据;非范围退出码1
# [MODIFY-GUARD] docs/03_modules/_cross_layer/model_profiler/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 护照不存在→exit 2;分母为0→exit 3
# [TESTS] tests/test_calibrate_model_diff.py
# [TTL] permanent
"""
模型能力差异校准脚本（P1-3 治本）。

校准目标: 强模型 vs 弱模型 = 1.2-1.4x 总分比率
    示例: deepseek-v4-pro-thinking vs qwen2.5-coder:14b
    期望比率: 1.3 (±0.1 容差 → 合法区间 [1.2, 1.4])

用途:
    - 考试系统区分度回归校准 (CI 集成)
    - 检测题库膨胀导致的能力趋同 (Goodhart's Law 防御)
    - 发现校准失败时, 定位是哪些能力的判别力退化

退出码:
    0 = 在范围内 (PASS)
    1 = 超出范围 (FAIL — 校准漂移, 需复核题库)
    2 = 护照文件不存在
    3 = 分母为 0 (无法计算比率)

运行示例:
    python scripts/calibrate_model_diff.py \\
        --model-a deepseek-v4-pro-thinking \\
        --model-b qwen2.5-coder_14b \\
        --target-ratio 1.3 \\
        --tolerance 0.1
    python scripts/calibrate_model_diff.py --list
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 包外 bootstrap: 一次性极简 sys.path 注入（仅此一次, 后续路径常量必须用 REPO_ROOT）
_SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(_SRC))

from zephyr.intelligence.model_profiling.capability_passport import (  # noqa: E402
    CapabilityPassport,
)
# 注: REPO_ROOT 真源由 capability_passport.PASSPORTS_DIR 内部使用（zephyr.shared.io.paths）
# 本脚本不直接推算仓库根, 避免违反 REPO_ROOT SSoT 约束


# ══════════════════════════════════════════════════════════════
# 默认校准目标（v3.0.5 设定, 见架构审查报告 P1-3）
# ══════════════════════════════════════════════════════════════
DEFAULT_MODEL_A = "deepseek-v4-pro-thinking"  # 强模型 (期望高分)
DEFAULT_MODEL_B = "qwen2.5-coder_14b"  # 弱模型 (期望低分)
DEFAULT_TARGET_RATIO = 1.3  # 期望比率
DEFAULT_TOLERANCE = 0.1  # 容差 → 合法区间 [1.2, 1.4]

# 单能力判别力退化阈值: 若 |ratio_cap - target| > 0.3, 视为该能力缺乏区分度
CAP_DISCRIMINATION_DRIFT = 0.3


def _load_passport_or_exit(model_id: str) -> CapabilityPassport:
    """加载护照; 失败时 exit(2)。"""
    passport = CapabilityPassport.load(model_id, verify=False)
    if passport is None:
        print(f"[ERROR] 护照不存在: {model_id}", file=sys.stderr)
        print(
            f"        文件路径期望: data/brain/passports/{model_id.replace(':', '_').replace('/', '_')}.json",
            file=sys.stderr,
        )
        sys.exit(2)
    return passport


def _compute_per_capability_ratio(
    a: CapabilityPassport,
    b: CapabilityPassport,
) -> list[dict]:
    """计算各能力的 f1 比率 (model_a / model_b)。

    返回字典列表, 每项包含:
        capability, f1_a, f1_b, ratio, drift (是否判别力退化)
    """
    caps_a = a.depth.capabilities
    caps_b = b.depth.capabilities
    all_caps = sorted(set(caps_a.keys()) | set(caps_b.keys()))
    rows: list[dict] = []
    for cap in all_caps:
        f1_a = caps_a.get(cap).f1 if caps_a.get(cap) else 0.0
        f1_b = caps_b.get(cap).f1 if caps_b.get(cap) else 0.0
        # 避免除零: 若 f1_b 为 0, 用 None 占位
        ratio = (f1_a / f1_b) if f1_b > 0 else None
        drift = (
            abs(ratio - DEFAULT_TARGET_RATIO) > CAP_DISCRIMINATION_DRIFT
            if ratio is not None
            else True
        )
        rows.append(
            {
                "capability": cap,
                "f1_a": f1_a,
                "f1_b": f1_b,
                "ratio": ratio,
                "drift": drift,
            }
        )
    return rows


def _print_report(
    a: CapabilityPassport,
    b: CapabilityPassport,
    target: float,
    tolerance: float,
    verbose: bool,
) -> bool | None:
    """打印校准报告, 返回是否通过。

    返回 None 表示分母为 0 (由调用方决定退出码)。
    """
    if abs(b.overall_score) < 1e-9:  # 5.167.8 修复: 浮点==0比较改 < epsilon
        print(
            f"[ERROR] 分母模型 {b.model_id} 的 overall_score = 0, 无法计算比率",
            file=sys.stderr,
        )
        return None

    ratio = a.overall_score / b.overall_score
    lo = target - tolerance
    hi = target + tolerance
    passed = lo <= ratio <= hi

    # 头部摘要
    print("=" * 80)
    print("  模型能力差异校准报告 (P1-3)")
    print("=" * 80)
    print(f"  强模型 A: {a.model_id}")
    print(f"    overall_score = {a.overall_score:.4f}  grade = {a.overall_grade}")
    print(f"  弱模型 B: {b.model_id}")
    print(f"    overall_score = {b.overall_score:.4f}  grade = {b.overall_grade}")
    print("-" * 80)
    print(
        f"  实际比率  A/B = {ratio:.4f}"
        f"  (目标 {target:.2f} ± {tolerance:.2f} → 区间 [{lo:.2f}, {hi:.2f}])"
    )
    print(f"  校准结果: {'PASS ✓' if passed else 'FAIL ✗'}")
    print("=" * 80)

    if not passed:
        # 失败诊断
        if ratio < lo:
            print(
                f"\n  [诊断] 比率偏低 ({ratio:.4f} < {lo:.2f}): "
                f"题库对强弱模型的区分度不足 (Goodhart 风险)"
            )
            print("         建议:")
            print("           1. 复核 breadth 35% 权重是否过重 (仅检 JSON 键存在)")
            print("           2. 增加 depth 难题占比 (HARD/EXTREME)")
            print("           3. 启用三轨 judge 强制 (P1-4)")
        else:
            print(
                f"\n  [诊断] 比率偏高 ({ratio:.4f} > {hi:.2f}): "
                f"题库过度偏向强模型 (不公平风险)"
            )
            print("         建议:")
            print("           1. 增加 EASY/MEDIUM 基础题, 确保弱模型有底线分")
            print("           2. 复核 depth 多次采样是否引入随机噪声 (P1-2)")

    if verbose:
        # 各能力详细对比
        rows = _compute_per_capability_ratio(a, b)
        drifted = [r for r in rows if r["drift"]]
        print("\n  各能力 f1 对比 (drift = |ratio - 1.3| > 0.3):")
        print(f"  {'capability':<32}{'f1_A':>10}{'f1_B':>10}{'ratio':>10}  drift")
        print("  " + "-" * 76)
        for r in rows:
            ratio_str = f"{r['ratio']:.4f}" if r["ratio"] is not None else "N/A"
            mark = "✗" if r["drift"] else " "
            print(
                f"  {r['capability']:<32}{r['f1_a']:>10.4f}{r['f1_b']:>10.4f}"
                f"{ratio_str:>10}  {mark}"
            )
        if drifted:
            print(f"\n  判别力退化能力 {len(drifted)}/{len(rows)} 个:")
            for r in drifted:
                ratio_str = f"{r['ratio']:.4f}" if r["ratio"] is not None else "N/A"
                print(f"    - {r['capability']}  (ratio={ratio_str})")

    # 速度/幻觉/漂移次要指标
    print("\n  次要指标对比:")
    print(
        f"    speed.avg_latency_ms:    A={a.speed.avg_latency_ms:>10.0f}ms  "
        f"B={b.speed.avg_latency_ms:>10.0f}ms"
    )
    print(
        f"    hallucination.rate:      A={a.hallucination.overall_rate:>10.4f}  "
        f"B={b.hallucination.overall_rate:>10.4f}"
    )
    print(
        f"    drift.stable:            A={a.drift.stable!s:>10}  "
        f"B={b.drift.stable!s:>10}"
    )

    print("\n" + "=" * 80)
    return passed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="模型能力差异校准 (P1-3: 1.2-1.4x 比率回归)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--model-a",
        default=DEFAULT_MODEL_A,
        help=f"强模型 ID (默认: {DEFAULT_MODEL_A})",
    )
    parser.add_argument(
        "--model-b",
        default=DEFAULT_MODEL_B,
        help=f"弱模型 ID (默认: {DEFAULT_MODEL_B})",
    )
    parser.add_argument(
        "--target-ratio",
        type=float,
        default=DEFAULT_TARGET_RATIO,
        help=f"目标比率 (默认: {DEFAULT_TARGET_RATIO})",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=DEFAULT_TOLERANCE,
        help=f"容差 (默认: {DEFAULT_TOLERANCE})",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="输出各能力详细对比",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="列出所有可用护照后退出",
    )
    args = parser.parse_args(argv)

    if args.list:
        passports = CapabilityPassport.list_all()
        print(f"可用护照 ({len(passports)} 个):")
        for pid in sorted(passports):
            p = CapabilityPassport.load(pid)
            if p:
                print(
                    f"  {pid:<35} score={p.overall_score:.4f}  "
                    f"grade={p.overall_grade}"
                )
        return 0

    a = _load_passport_or_exit(args.model_a)
    b = _load_passport_or_exit(args.model_b)

    passed = _print_report(a, b, args.target_ratio, args.tolerance, args.verbose)
    if passed is None:
        return 3  # 分母为 0
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
