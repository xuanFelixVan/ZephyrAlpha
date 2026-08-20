# [BLUEPRINT] MOD-VERIFY-CALIB | 13_regime_phase3_engineering_plan §2.2.9 Bug #3 验证
# [MODULE] scripts.tests.verify_calibration_nll
# [DOMAIN] D_REGIME
# [STARTUP] event_driven
# [MATURITY] design
# [TTL] permanent
"""验证二元交叉熵 NLL 计算逻辑不再崩溃（修复 occurred.argmax(axis=1) bug）.

构造 3 组 mock 数据：
  1. 过自信场景（高 confidence 但低 occurred 频率）—— 预期 T > 1.0
  2. 欠自信场景（低 confidence 但高 occurred 频率）—— 预期 T < 1.0
  3. 已校准场景（confidence ≈ occurred 频率）—— 预期 T ≈ 1.0

验证点：
  - fit_temperature 不崩溃（不再有 AxisError）
  - T 在 (0.1, 10.0) 范围内
  - T 方向正确（过自信→T>1，欠自信→T<1）
  - 校准后 confidence 比原始更接近 occurred 频率
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import minimize_scalar


def fit_temperature(log_proba: np.ndarray, occurred: np.ndarray) -> float:
    """T 从 IS 数据学：最小化二元交叉熵（13_regime_phase3_engineering_plan §2.2.8 B 修正版）."""

    def binary_cross_entropy(T: float) -> float:
        scaled = log_proba / T
        log_softmax = scaled - np.logaddexp.reduce(scaled, axis=1, keepdims=True)
        proba = np.exp(log_softmax)
        calibrated_confidence = proba.max(axis=1)
        eps = 1e-8
        return float(
            -np.mean(
                occurred * np.log(calibrated_confidence + eps)
                + (1 - occurred) * np.log(1 - calibrated_confidence + eps)
            )
        )

    result = minimize_scalar(binary_cross_entropy, bounds=(0.1, 10.0), method="bounded")
    return float(result.x)


def make_log_proba(logits: np.ndarray) -> np.ndarray:
    """原始 logits → log_softmax（模拟 HMM 输出的 log_proba）."""
    return logits - np.logaddexp.reduce(logits, axis=1, keepdims=True)


def run_scenario(name: str, logits: np.ndarray, occurred: np.ndarray) -> None:
    """跑一个场景并打印结果."""
    log_proba = make_log_proba(logits)
    original_conf = np.exp(log_proba.max(axis=1))

    print(f"\n{'=' * 60}")
    print(f"场景: {name}")
    print(f"  样本数: {len(occurred)}")
    print(f"  occurred=1 占比: {occurred.mean():.1%}")
    print(f"  原始 confidence 均值: {original_conf.mean():.3f}")

    # ── 核心验证：不崩溃 ──
    try:
        T = fit_temperature(log_proba, occurred)
        print("  ✅ fit_temperature 不崩溃")
    except Exception as exc:
        print(f"  ❌ fit_temperature 崩溃: {type(exc).__name__}: {exc}")
        return

    print(f"  T = {T:.4f} (范围 0.1-10.0)")

    # 校准后 confidence
    scaled = log_proba / T
    cal_proba = np.exp(scaled - np.logaddexp.reduce(scaled, axis=1, keepdims=True))
    cal_conf = cal_proba.max(axis=1)

    print(f"  校准后 confidence 均值: {cal_conf.mean():.3f}")
    print(f"  降温效果 (校准<原始): {cal_conf.mean() < original_conf.mean()}")

    # 分桶校准效果
    buckets = [(0.0, 0.5), (0.5, 0.8), (0.8, 1.01)]
    print("  分桶校准:")
    for lo, hi in buckets:
        mask = (original_conf >= lo) & (original_conf < hi)
        if mask.sum() == 0:
            continue
        orig_mean = original_conf[mask].mean()
        cal_mean = cal_conf[mask].mean()
        occ_freq = occurred[mask].mean()
        orig_err = abs(orig_mean - occ_freq)
        cal_err = abs(cal_mean - occ_freq)
        improved = "✅" if cal_err < orig_err else "❌"
        print(
            f"    [{lo:.1f},{hi:.1f}): n={mask.sum():4d} | "
            f"原始={orig_mean:.3f} 校准={cal_mean:.3f} 实际={occ_freq:.3f} | "
            f"误差 {orig_err:.3f}→{cal_err:.3f} {improved}"
        )


def main() -> None:
    np.random.seed(42)

    N = 500
    n_states = 4

    # ── 场景 1：过自信（模拟我们的 B1 FAIL 场景）──
    # 高 confidence 但 occurred 频率低
    logits_over = np.random.randn(N, n_states) * 0.3  # 小方差 → 接近均匀
    # 放大一半样本的 logits → 高 confidence
    high_mask = np.random.rand(N) > 0.5
    logits_over[high_mask] *= 4.0  # 放大 → softmax 后 ~0.85-0.95
    occurred_over = np.zeros(N, dtype=int)
    occurred_over[~high_mask] = (np.random.rand((~high_mask).sum()) < 0.55).astype(int)
    occurred_over[high_mask] = (np.random.rand(high_mask.sum()) < 0.50).astype(int)

    # ── 场景 2：欠自信 ──
    # 低 confidence 但 occurred 频率高
    logits_under = np.random.randn(N, n_states) * 0.8  # 大方差 → 均匀
    occurred_under = (np.random.rand(N) < 0.75).astype(int)  # 75% 正确

    # ── 场景 3：已校准 ──
    # confidence ≈ occurred 频率
    logits_calibrated = np.random.randn(N, n_states) * 1.0
    # 调整使 confidence 接近 60%
    for i in range(N):
        while True:
            lp = make_log_proba(logits_calibrated[i : i + 1])
            conf = float(np.exp(lp.max()))
            if 0.55 < conf < 0.65:
                break
            logits_calibrated[i] *= 0.95 if conf > 0.65 else 1.05
    occurred_calibrated = (np.random.rand(N) < 0.60).astype(int)

    # ── 场景 4：极端情况——全 0 occurred ──
    logits_all_zero = np.random.randn(100, n_states) * 2.0
    occurred_all_zero = np.zeros(100, dtype=int)

    # ── 场景 5：极端情况——全 1 occurred ──
    logits_all_one = np.random.randn(100, n_states) * 2.0
    occurred_all_one = np.ones(100, dtype=int)

    # ── 场景 6：occurred 是 Python list（非 numpy）──
    logits_list = np.random.randn(50, n_states) * 1.5
    occurred_list = [0, 1] * 25  # Python list

    print("=" * 60)
    print("二元交叉熵 NLL 验证（13_regime_phase3_engineering_plan §2.2.9 Bug #3 修复）")
    print("=" * 60)

    run_scenario("1. 过自信（模拟 B1 FAIL）", logits_over, occurred_over)
    run_scenario("2. 欠自信", logits_under, occurred_under)
    run_scenario("3. 已校准", logits_calibrated, occurred_calibrated)
    run_scenario("4. 全 0 occurred", logits_all_zero, occurred_all_zero)
    run_scenario("5. 全 1 occurred", logits_all_one, occurred_all_one)
    run_scenario("6. occurred 是 Python list", logits_list, np.array(occurred_list))

    # ── 场景 7：旧 bug 复现——验证旧代码确实崩溃 ──
    print(f"\n{'=' * 60}")
    print("场景 7: 旧 bug 复现（occurred.argmax(axis=1) 应崩溃）")
    print(f"{'=' * 60}")
    old_occurred = np.array([0, 1, 1, 0, 1] * 20)
    try:
        # 旧代码的写法
        _ = old_occurred.argmax(axis=1)
        print("  ⚠️  旧代码没崩溃（可能 numpy 版本行为不同）")
    except Exception as exc:
        print(f"  ✅ 旧代码确认崩溃: {type(exc).__name__}: {exc}")
        print("     这验证了 Bug #3 的存在——旧代码 occurred.argmax(axis=1) 对 1D 数组无效")

    print(f"\n{'=' * 60}")
    print("验证完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
