# [BLUEPRINT] none | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/11_regime_backtest_validation_plan.md §0.6.3 缺口3 / §4.3 C4
# [MODULE] zephyr.backtest.regime_validation.e2_stationary_bootstrap
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] numpy; zephyr.shared.foundation.errors
# [CONSUMERS] 人工审查; 11_regime_backtest_validation_plan Phase 4 E2 / C4 统计显著性
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 块长几何分布(均值mean_block)保平稳性,优于固定块; 开/关成对序列共用同一组重采样索引(保配对); 只读输入不改状态; 固定seed结果可复现
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] E2BootstrapError(ZA-BT-0027)
# [TESTS] tests/backtest/test_e2_stationary_bootstrap.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: returns_on/returns_off(Shrinkage 开/关两组逐期收益序列, 等长, C1 既有回测产物)
# I2: E2BootstrapConfig(n_boot=2000 / mean_block=21 / ci_level=0.90 / prob_threshold=0.75)
# F1: stationary_bootstrap_indices(Politis-Romano: 每步以 p=1/mean_block 重开新块, 否则顺移, 环形取模)
# F2: annualized_sharpe(逐期收益→年化 Sharpe, 零波动/样本<2 退化为 0)
# A1: bootstrap_sharpe_difference(B 次成对重采样→Sharpe 差值分布→percentile CI + P(diff>0))
# O1: E2BootstrapResult(observed_diff / CI / prob_positive / passed), prob_positive≥0.75 对齐 §4.3 C4 判定
# [/ALGO_FLOW]
"""
D_BACKTEST — E2 Stationary Bootstrap 重采样引擎（11 号 memo §0.6.3 缺口 3）。

替代原方案 §4.3 C4 的固定 21-day block-bootstrap：块长按几何分布随机
（Politis & Romano 1994），保留序列平稳性、避免固定块边界的人为不连续
（algovantis 2026-04 背书，memo §0.6.3）。

主入口 bootstrap_sharpe_difference：对 C1 既有回测产物（开/关两组逐期收益）
做成对 stationary bootstrap，产出 Sharpe 改善的置信区间与 P(Sharpe_开>Sharpe_关)，
后者对齐 §5 C4 判定门槛 ≥75%。

依据: 11_regime_backtest_validation_plan §0.6.3 / §4.3 C4 / §5
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: n 参数
#   fields: 参数 n，类型注解 int
#   code: e2_stationary_bootstrap.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: mean_block 参数
#   fields: 参数 mean_block，类型注解 int
#   code: e2_stationary_bootstrap.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: rng 参数
#   fields: 参数 rng，类型注解 np.random.Generator
#   code: e2_stationary_bootstrap.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: returns 参数
#   fields: 参数 returns，类型注解 Sequence[float]
#   code: e2_stationary_bootstrap.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① stationary_bootstrap_indices
#   name_en: stationary_bootstrap_indices
#   intro: 生成一组 stationary bootstrap 索引（Politis & Romano 1994）。
#   desc: 生成一组 stationary bootstrap 索引（Politis & Romano 1994）。 每步以概率 p=1/mean_block 从均匀分布重开新块，否则顺移到…；源码 L159-L185
#   inputs: n mean_block rng
#   outputs: np.ndarray
# - id: A2
#   name_zh: ② annualized_sharpe
#   name_en: annualized_sharpe
#   intro: 逐期收益 → 年化 Sharpe。
#   desc: 逐期收益 → 年化 Sharpe。样本<2 或零波动退化为 0.0。；源码 L188-L196
#   inputs: returns periods_per_year
#   outputs: float
# - id: A3
#   name_zh: ③ bootstrap_sharpe_difference
#   name_en: bootstrap_sharpe_difference
#   intro: E2 主入口：开/关两组收益序列的 stationary bootstrap Sharpe 差显著性。
#   desc: E2 主入口：开/关两组收益序列的 stationary bootstrap Sharpe 差显著性。 开/关序列成对重采样（共用同一组索引，保留逐期配对结构）， 产出 Shar…；源码 L199-L259
#   inputs: returns_on returns_off config
#   outputs: E2BootstrapResult
#   （注：A3 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: np.ndarray
#   name_en: np.ndarray
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 人工审查; 11_regime_backtest_validation_plan Phase 4 E2 / C4 统计显著性
# - id: O2
#   name_zh: float
#   name_en: float
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 人工审查; 11_regime_backtest_validation_plan Phase 4 E2 / C4 统计显著性
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Sequence

import numpy as np

try:  # 治理基类缺失时降级为 Exception，保证模块可独立 import
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # pragma: no cover  # noqa: BLE001
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

_logger = logging.getLogger(__name__)


class E2BootstrapError(ZephyrBaseError):
    """ZA-BT-0027: E2 stationary bootstrap 错误（输入非法/序列过短）。"""

    error_code = "ZA-BT-0027"


@dataclass(frozen=True)
class E2BootstrapConfig:
    """E2 bootstrap 配置——不可变。

    Attributes:
        n_boot: 重采样次数（§4.3 C4 对照 Morwane 2000×）
        mean_block: 平均块长（几何分布均值，§4.3 对照 21 交易日）
        seed: 随机种子（复现用）
        ci_level: 置信区间水平（默认 90%）
        periods_per_year: 年化频率（A 股日度=252）
        prob_threshold: P(Sharpe_开>Sharpe_关) 通过门槛（§5 C4=0.75）
    """

    n_boot: int = 2000
    mean_block: int = 21
    seed: int = 42
    ci_level: float = 0.90
    periods_per_year: int = 252
    prob_threshold: float = 0.75


@dataclass(frozen=True)
class E2BootstrapResult:
    """E2 bootstrap 显著性结果——不可变。"""

    observed_diff: float  # 实测 Sharpe 差（开−关）
    ci_lower: float  # 差值分布 CI 下界（percentile）
    ci_upper: float  # 差值分布 CI 上界
    prob_positive: float  # P(Sharpe_开 > Sharpe_关) = bootstrap 差值>0 占比
    n_boot: int
    mean_block: int
    passed: bool  # prob_positive ≥ config.prob_threshold（§5 C4）
    summary: str


def stationary_bootstrap_indices(n: int, mean_block: int, rng: np.random.Generator) -> np.ndarray:
    """生成一组 stationary bootstrap 索引（Politis & Romano 1994）。

    每步以概率 p=1/mean_block 从均匀分布重开新块，否则顺移到下一观测，
    环形取模（wrap-around）保持平稳性。

    Args:
        n: 序列长度（≥2）
        mean_block: 平均块长（≥1）
        rng: numpy 随机数生成器（调用方持有，保证整批可复现）

    Returns:
        (n,) int64 索引数组，取值 [0, n)。
    """
    if n < 2:
        raise E2BootstrapError(f"序列长度 n 需 ≥2: {n}")
    if mean_block < 1:
        raise E2BootstrapError(f"mean_block 需 ≥1: {mean_block}")
    p = 1.0 / float(mean_block)
    idx = np.empty(n, dtype=np.int64)
    idx[0] = rng.integers(0, n)
    for t in range(1, n):
        if rng.random() < p:
            idx[t] = rng.integers(0, n)
        else:
            idx[t] = (idx[t - 1] + 1) % n
    return idx


def annualized_sharpe(returns: Sequence[float], periods_per_year: int = 252) -> float:
    """逐期收益 → 年化 Sharpe。样本<2 或零波动退化为 0.0。"""
    arr = np.asarray(returns, dtype=float)
    if arr.size < 2:
        return 0.0
    std = float(arr.std(ddof=1))
    if std <= 0.0:
        return 0.0
    return float(arr.mean() / std * np.sqrt(float(periods_per_year)))


def bootstrap_sharpe_difference(
    returns_on: Sequence[float],
    returns_off: Sequence[float],
    config: E2BootstrapConfig | None = None,
) -> E2BootstrapResult:
    """E2 主入口：开/关两组收益序列的 stationary bootstrap Sharpe 差显著性。

    开/关序列成对重采样（共用同一组索引，保留逐期配对结构），
    产出 Sharpe 差值的 percentile CI 与 P(diff>0)。

    Args:
        returns_on: 实验组（Shrinkage 开）逐期收益序列（C1 回测产物）
        returns_off: 基准组（关）逐期收益序列，与 on 等长
        config: E2BootstrapConfig（None=默认 2000×/21 块/90% CI/0.75 门槛）

    Returns:
        E2BootstrapResult。passed = P(diff>0) ≥ 0.75（§5 C4 判定）。

    Raises:
        E2BootstrapError: 空序列 / 长度不一致 / 样本<2 / 含非有限值 / n_boot<1。
    """
    cfg = config or E2BootstrapConfig()
    on = np.asarray(returns_on, dtype=float)
    off = np.asarray(returns_off, dtype=float)
    if on.size == 0 or off.size == 0:
        raise E2BootstrapError("收益序列不能为空")
    if on.shape != off.shape:
        raise E2BootstrapError(f"开/关序列长度需一致: {on.size} vs {off.size}")
    if on.size < 2:
        raise E2BootstrapError(f"样本数不足: {on.size} < 2")
    if not (np.isfinite(on).all() and np.isfinite(off).all()):
        raise E2BootstrapError("收益序列含 NaN/Inf")
    if cfg.n_boot < 1:
        raise E2BootstrapError(f"n_boot 需 ≥1: {cfg.n_boot}")

    rng = np.random.default_rng(cfg.seed)
    observed = annualized_sharpe(on, cfg.periods_per_year) - annualized_sharpe(off, cfg.periods_per_year)
    diffs = np.empty(cfg.n_boot, dtype=float)
    for b in range(cfg.n_boot):
        idx = stationary_bootstrap_indices(on.size, cfg.mean_block, rng)
        diffs[b] = annualized_sharpe(on[idx], cfg.periods_per_year) - annualized_sharpe(off[idx], cfg.periods_per_year)
    alpha = 1.0 - cfg.ci_level
    ci_lower, ci_upper = (float(q) for q in np.quantile(diffs, [alpha / 2.0, 1.0 - alpha / 2.0]))
    prob_positive = float(np.mean(diffs > 0.0))
    passed = prob_positive >= cfg.prob_threshold
    summary = (
        f"E2 stationary bootstrap: B={cfg.n_boot} mean_block={cfg.mean_block} "
        f"Sharpe差(开−关)={observed:+.4f} CI{int(cfg.ci_level * 100)}%=[{ci_lower:+.4f},{ci_upper:+.4f}] "
        f"P(开>关)={prob_positive:.3f} 门槛≥{cfg.prob_threshold} → {'通过' if passed else '不显著'}"
    )
    _logger.info("E2 完成: %s", summary)
    return E2BootstrapResult(
        observed_diff=observed,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        prob_positive=prob_positive,
        n_boot=cfg.n_boot,
        mean_block=cfg.mean_block,
        passed=passed,
        summary=summary,
    )


__all__ = [
    "E2BootstrapConfig",
    "E2BootstrapError",
    "E2BootstrapResult",
    "annualized_sharpe",
    "bootstrap_sharpe_difference",
    "stationary_bootstrap_indices",
]
