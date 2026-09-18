# [BLUEPRINT] MOD-SOWNER-002 | docs/03_modules/_domain_ashare_signal/blueprint.md
# [MODULE] zephyr.strategy_factory.owner_regime_switcher.exam
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] numpy; pandas; typing; zephyr.strategy_factory.owner_regime_switcher.switcher; zephyr.strategy_factory.owner_regime_switcher.packages; zephyr.strategy_factory.owner_regime_switcher.engine; zephyr.strategy_factory.owner_regime_switcher.data_loader
# [CONSUMERS] scripts/strategy_factory/run_s_owner_002_exam.py; tests/strategy_factory/test_s_owner_002_redblue.py
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 双跑对照=同池同实现，仅调度表不同（on=切换器/off=全时全包）；OOS 单次通过；bootstrap=moving block（块 20/1 万次/seed 20260916，冻结 §5）；敞口匹配对照 k=切换腿均敞口/基线腿均敞口；IS/OOS 分别报告禁只报好段
# [MODIFY-GUARD] 考试冻结文档 §5/§6——冻结后语义变更=第二真源作弊
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)； ValueError(窗口非法)
# [TESTS] tests/strategy_factory/test_s_owner_002_redblue.py
# [A_module] module_id=MOD-SOWNER-002 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""E4 考试器——切换器 on/off 双跑对照 + 敞口匹配对照 + block bootstrap CI。

冻结验收线（§6）: H = OOS 年化 Sharpe 差 95% CI 不含 0（正）且切换腿 OOS MaxDD ≤
基线腿 OOS MaxDD；两腿敞口/交易次数必报；对敞口匹配基线的差值做归因（降敞口 vs 择时）。
检测器质量描述表（§5）: 各 dominant 态占比 + 000300 前向 20 日收益按态均值（描述性，无验收线）。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

import numpy as np
import pandas as pd

from zephyr.strategy_factory.owner_regime_switcher.data_loader import (
    WARMUP_START,
    load_basket_daily,
    load_index_daily,
    load_regime_snapshots,
)
from zephyr.strategy_factory.owner_regime_switcher.engine import EngineConfig, LegResult, run_leg
from zephyr.strategy_factory.owner_regime_switcher.packages import (
    PACKAGE_A_SYMBOL,
    PACKAGE_B_BASKET,
    package_a_targets,
    package_b_targets,
)
from zephyr.strategy_factory.owner_regime_switcher.switcher import (
    SwitcherConfig,
    baseline_schedule,
    build_schedule,
    scaled_schedule,
)

IS_START, IS_END = "2019-04-01", "2023-12-31"
OOS_START, OOS_END = "2024-01-01", "2026-09-15"
BOOT_BLOCK = 20
BOOT_DRAWS = 10_000
BOOT_SEED = 20260916

__all__: Final = ["run_exam", "bootstrap_sharpe_diff", "detector_quality_table"]


@dataclass
class WindowResult:
    """单窗口双跑产出。"""

    window: str
    switcher: LegResult
    baseline: LegResult
    matched_scalar: float
    matched: LegResult
    sharpe_diff_ci: tuple[float, float]
    mean_diff_ci: tuple[float, float]
    matched_sharpe_diff_ci: tuple[float, float]


def bootstrap_sharpe_diff(
    ret_a: pd.Series,
    ret_b: pd.Series,
    block: int = BOOT_BLOCK,
    draws: int = BOOT_DRAWS,
    seed: int = BOOT_SEED,
) -> tuple[tuple[float, float], tuple[float, float]]:
    """两腿逐日收益差的 moving block bootstrap（冻结 §5）。

    :return: ((sharpe_diff CI 低, 高), (日均收益差 CI 低, 高))——95% 分位。
    """
    joined = pd.concat([ret_a.rename("a"), ret_b.rename("b")], axis=1).dropna()
    diff = (joined["a"] - joined["b"]).to_numpy()
    n = len(diff)
    if n < block + 10:
        raise ValueError(f"bootstrap 样本过短: {n}")
    n_blocks = int(np.ceil(n / block))
    rng = np.random.default_rng(seed)
    max_start = n - block
    sharpes = np.empty(draws)
    means = np.empty(draws)
    sqrt_t = float(np.sqrt(244.0))
    for k in range(draws):
        starts = rng.integers(0, max_start + 1, size=n_blocks)
        sample = np.concatenate([diff[s : s + block] for s in starts])[:n]
        sd = float(sample.std(ddof=1))
        sharpes[k] = 0.0 if sd == 0.0 else float(sample.mean() / sd * sqrt_t)
        means[k] = float(sample.mean())
    lo_s, hi_s = float(np.percentile(sharpes, 2.5)), float(np.percentile(sharpes, 97.5))
    lo_m, hi_m = float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))
    return ((lo_s, hi_s), (lo_m, hi_m))


def detector_quality_table(
    snapshots: pd.DataFrame,
    idx_close: pd.Series,
    forward_days: int = 20,
) -> pd.DataFrame:
    """检测器质量描述表（冻结 §5：描述性产出，无验收线）。

    各 dominant 态: 天数/占比 + 000300 前向 forward_days 日收益按态均值
    （态序经济学方向检查: 进攻态应为正、危机态应为负）。
    """
    snap = snapshots.copy()
    snap["trade_date"] = pd.to_datetime(snap["trade_date"])
    fwd = idx_close.shift(-forward_days) / idx_close - 1.0
    snap["fwd_ret"] = snap["trade_date"].map(fwd)
    grp = snap.dropna(subset=["dominant"]).groupby("dominant")
    total = max(len(snap), 1)
    rows = []
    for dom, g in grp:
        rows.append(
            {
                "dominant": dom,
                "days": int(len(g)),
                "share": float(len(g) / total),
                "fwd20_mean": float(g["fwd_ret"].mean()) if g["fwd_ret"].notna().any() else float("nan"),
            }
        )
    return pd.DataFrame(rows).sort_values("dominant").reset_index(drop=True)


def _run_window(  # noqa: long-param-list  冻结考试器窗口对照签名，契约绑定方=本文件 run_exam 2 处+tests/strategy_factory/test_s_owner_002_redblue.py 1 处；参数对象重构按 R-037 改裁属独立批
    window: str,
    start: str,
    end: str,
    snapshots: pd.DataFrame,
    daily: dict[str, pd.DataFrame],
    a_t: pd.Series,
    b_t: pd.DataFrame,
    exec_symbols: list[str],
    switcher_cfg: SwitcherConfig | None = None,
    engine_cfg: EngineConfig | None = None,
) -> WindowResult:
    """单窗口双跑（切换 on/off + 敞口匹配对照；bootstrap 同窗收益差）。"""
    trade_days = pd.DatetimeIndex(daily[PACKAGE_A_SYMBOL].index)
    trade_days = trade_days[(trade_days >= pd.Timestamp(start)) & (trade_days <= pd.Timestamp(end))]
    sched_on = build_schedule(trade_days, snapshots, switcher_cfg or SwitcherConfig())
    sched_off = baseline_schedule(trade_days)
    leg_on = run_leg(sched_on, a_t, b_t, daily, exec_symbols, start, end, engine_cfg, config_tag=f"{window}-switcher")
    leg_off = run_leg(sched_off, a_t, b_t, daily, exec_symbols, start, end, engine_cfg, config_tag=f"{window}-baseline")
    avg_on = float(leg_on.exposure.mean())
    avg_off = float(leg_off.exposure.mean())
    k = 1.0 if avg_off <= 0 else min(avg_on / avg_off, 1.0)
    leg_matched = run_leg(
        scaled_schedule(sched_off, k), a_t, b_t, daily, exec_symbols, start, end, engine_cfg, config_tag=f"{window}-matched"
    )
    ret_on = leg_on.nav.pct_change().dropna()
    ret_off = leg_off.nav.pct_change().dropna()
    ret_m = leg_matched.nav.pct_change().dropna()
    (s_lo, s_hi), (m_lo, m_hi) = bootstrap_sharpe_diff(ret_on, ret_off)
    (ms_lo, ms_hi), _ = bootstrap_sharpe_diff(ret_on, ret_m)
    return WindowResult(
        window=window,
        switcher=leg_on,
        baseline=leg_off,
        matched_scalar=float(k),
        matched=leg_matched,
        sharpe_diff_ci=(s_lo, s_hi),
        mean_diff_ci=(m_lo, m_hi),
        matched_sharpe_diff_ci=(ms_lo, ms_hi),
    )


def run_exam(
    warmup_start: str = WARMUP_START,
    switcher_cfg: SwitcherConfig | None = None,
    engine_cfg: EngineConfig | None = None,
    snapshots_override: pd.DataFrame | None = None,
    daily_override: dict[str, pd.DataFrame] | None = None,
) -> dict[str, Any]:
    """E4 主入口：IS/OOS 各跑一次（OOS 单次纪律由调用序保证）。

    :param snapshots_override/daily_override: 测试注入用（红蓝对抗/单测），正式跑数不传。
    """
    snapshots = snapshots_override if snapshots_override is not None else load_regime_snapshots()
    daily = daily_override if daily_override is not None else load_basket_daily(
        sorted(set(PACKAGE_B_BASKET) | {PACKAGE_A_SYMBOL}), warmup_start
    )
    exec_symbols = sorted(set(PACKAGE_B_BASKET) | {PACKAGE_A_SYMBOL})
    # 包目标（全历史 t 收盘判定；引擎统一 shift）
    a_t = package_a_targets(daily[PACKAGE_A_SYMBOL]["close"])
    close_panel = pd.DataFrame({s: daily[s]["close"] for s in PACKAGE_B_BASKET})
    b_t = package_b_targets(close_panel)
    is_res = _run_window("IS", IS_START, IS_END, snapshots, daily, a_t, b_t, exec_symbols, switcher_cfg, engine_cfg)
    oos_res = _run_window("OOS", OOS_START, OOS_END, snapshots, daily, a_t, b_t, exec_symbols, switcher_cfg, engine_cfg)
    out: dict[str, Any] = {"IS": is_res, "OOS": oos_res}
    if snapshots_override is None and daily_override is None:
        idx = load_index_daily(warmup_start)
        out["detector_quality"] = detector_quality_table(snapshots, idx["close"])
    return out
