# [BLUEPRINT] MOD-BT-GDENGINE | docs/03_modules/_domain_backtest/blueprint.md（G-D 波10 逐格统计引擎；10_wave_plan 10.G-D 判据真源）
# [MODULE] scripts.backtest.grid_stats_engine
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.simulation.deflated_sharpe_calculator; zephyr.backtest.core.n_trial_ledger(compute_effective_rank); zephyr.backtest.regime_validation.e2_stationary_bootstrap(stationary_bootstrap_indices); numpy; pandas
# [CONSUMERS] 波12 正式跑消费（G-D.4 点火卡 Owner 门位）；tests/backtest/test_grid_stats_engine.py
# [STARTUP] imported
# [MATURITY] draft
# [INVARIANTS] ★READY_NOT_FIRED（10_wave_plan 10.G-D）：本件=引擎+口径实现，禁对生产数据点火/不入账本/不作策略结论，正式跑全推迟到波 12（G-D.4 Owner 门位）；夏普口径四条（⚑-2 B 案）①年化基准 244 交易日（exam_cost_gate.DEFAULT_TURNOVER_DAYS_BASIS 同源）禁 ×√252 ②ddof=0（与 PSR/DSR 同口径）③停牌/涨跌停数据面治理归调用方（喂进来的序列须已按 A 股口径治理）④Ljung-Box(q=年化基准) 显著才施加 Lo(2002) 修正因子；DSR 公式零自写——唯一真源委托 zephyr.simulation.deflated_sharpe_calculator.deflated_sharpe_from_moments；样本<30 判 INSUFFICIENT-N 单列（30 日地板先例）；c* 二分+单调校验（非单调=疑似引擎缺陷单列，禁静默吞）；负结果无论正负都保留（negative_result_promise 口径）
# [MODIFY-GUARD] tests/backtest/test_grid_stats_engine.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] GridStatsEngineError(输入非法/面板不可对齐)
# [TESTS] tests/backtest/test_grid_stats_engine.py
# [TTL] permanent
"""D_BACKTEST — G-D 逐格统计引擎（共振矩阵每格四件套：样本／夏普／c*／DSR）。

判据唯一真源=docs/_archive/_working_cleared/total_command_closeout/10_wave_plan.md 10.G-D 行
（★READY_NOT_FIRED：引擎+prereg 冻结+日频小样本冒烟通过即出口；不点火、结果
不入账本、不作策略结论，正式跑推迟到波 12）。规格细读=ext_01_revised_construction_plan.md
G-D.2/G-D.3 行。多重检验与滚动重考的学术口径采纳自案卷
docs/_archive/_working_cleared/total_command_closeout/final_review_chartlib/dossier_academic_papers.md §四。

四件套口径（每格）：
1. 样本数 n —— <30 判 INSUFFICIENT-N（单列，不作通过/拒绝判定）。
2. 夏普 —— Lo(2002) 自相关修正年化+ddof=0：SR_ann = (μ/σ₀)·√244·c，
   c=√(q/(q+2Σ(q−k)ρ̂ₖ)) 仅当 Ljung-Box(q=244) 显著（p<0.05）；
   n≤q 检验不可估→c=1 且如实标 lb_testable=False（禁把"测不了"当"无自相关"）。
   显著才施加 Lo(2002) 修正因子；自相关截断 lag=Newey-West (1994) 自动定阶
   l=floor(4·(n/100)^{2/9})（文献标准低方差截断）。
3. 盈亏平衡成本 c* —— 逐期附加成本二分：f(c_bp)=mean(r)−(c_bp/1e4)·turnover，
   c*=使 f≥0 的最大 bp；全程探针单调校验（线性成本下非单调=NaN 污染/引擎缺陷，
   单列 C_STAR_NON_MONOTONIC 禁静默）。
4. DSR —— 委托 deflated_sharpe_from_moments（全仓唯一真源），num_trials=N_eff。

C251 案卷采纳口径（§四.2/§四.4，必读）：
- **有效试验数**：DSR 分母的 num_trials 应填 N_eff=试验总数按格间平均相关折算
  （格子高度相关时 N_eff≪N；面板级估计用 n_trial_ledger.compute_effective_rank
  熵加权特征值广度，或调用方显式传入）。禁 Bonferroni 式"除以 3700"——
  格间不独立，除总格数=过度惩罚（案卷 §四.5）。
- **全试验披露**：全部尝试过的格子必须入 N 账本（n_trial_ledger）——
  "未披露试验数的回测一文不值"（Bailey-López de Prado）。
- **滚动重考**：Sullivan et al.(1999)/Hsu et al.(2010) 实证规则盈利性随市场结构
  漂移——四件套判定须分半窗+时间外推检验并按事件触发滚动重考
  （half_split_reexam；排程=返回待登记任务记录由消费方写 tasks 注册，
  禁 cron/Timer/sleep-loop——永久系统四要素红线）。

多重检验（G-D.3，同件交付）：
- spa_reality_check —— White (2000) Reality Check / Hansen (2005) SPA 简版：
  stationary bootstrap（Politis-Romano 1994，复用 e2_stationary_bootstrap）联合
  重采样（保持格间截面相关），逐格 SPA p 值=bootstrap max 统计量超过实测的比例
  （centered=recentered bootstrap，Hansen (2005) lower-bound 口径）。
- stepm —— Romano-Wolf (2005) StepM 思路简版：按 t 降序迭代：当前存活集上取
  bootstrap max 分布 95 分位，超过者入显著集并移出存活集，重复至无新增。
  简化点（如实披露）：逐步重推 max 分布而非 Romano-Wolf 的逐步 recentering；
  对"识别全部显著格"目标（而非单最优格）够用，正式波 12 跑前如需严格
  StepM-SPA 可在此接口内升级，判据不变。

Usage:
    from scripts.backtest.grid_stats_engine import GridStatsConfig, evaluate_grid

    stats = evaluate_grid({"cell_a": rets_a, "cell_b": rets_b}, n_eff=None)
    # stats["cell_a"].sharpe_annualized / .breakeven_cost_bp / .dsr / .status

"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from zephyr.backtest.core.n_trial_ledger import compute_effective_rank
from zephyr.backtest.regime_validation.e2_stationary_bootstrap import stationary_bootstrap_indices
from zephyr.backtest.regime_validation.exam_cost_gate import DEFAULT_TURNOVER_DAYS_BASIS
from zephyr.simulation.deflated_sharpe_calculator import (
    DSR_SIGNIFICANCE_THRESHOLD,
    deflated_sharpe_from_moments,
)

#: INSUFFICIENT-N 样本地板（30 日地板先例，ext_01 G-D.2 判据栏）
MIN_SAMPLES_PER_CELL: int = 30

#: Ljung-Box 显著性水平（⚑-2 B 案口径①：显著才施加 Lo(2002) 修正因子）
LJUNG_BOX_ALPHA: float = 0.05

#: c* 二分成本上界（bp，逐期附加成本扫描上限；超界=负期望格 c* 封 0）
C_STAR_MAX_BP: float = 5000.0

#: c* 二分收敛精度（bp）
C_STAR_TOL_BP: float = 0.01

#: DSR 显著判读沿用全仓阈值（本件只透传报告，不另立门槛=禁第二真源）
DSR_PASS_THRESHOLD: float = DSR_SIGNIFICANCE_THRESHOLD

#: SPA/StepM bootstrap 联合重采样次数（冒烟级默认；波 12 正式跑建议 ≥2000）
SPA_N_BOOT: int = 500

#: SPA 平均块长（Politis-Romano 几何分布均值；对齐 e2 件 21 交易日先例）
SPA_MEAN_BLOCK: int = 21

#: StepM 家族置信水平
STEPW_ALPHA: float = 0.05


class GridStatsEngineError(Exception):
    """G-D 逐格统计引擎输入非法/面板不可对齐。"""


@dataclass(frozen=True)
class GridStatsConfig:
    """引擎配置——不可变。默认值=⚑-2 B 案 A 股口径，改口径须走裁定。"""

    periods_per_year: int = DEFAULT_TURNOVER_DAYS_BASIS  # 244（禁 ×√252）
    min_samples: int = MIN_SAMPLES_PER_CELL
    ljung_box_alpha: float = LJUNG_BOX_ALPHA
    c_star_max_bp: float = C_STAR_MAX_BP
    c_star_tol_bp: float = C_STAR_TOL_BP
    dsr_threshold: float = DSR_PASS_THRESHOLD
    spa_n_boot: int = SPA_N_BOOT
    spa_mean_block: int = SPA_MEAN_BLOCK
    stepw_alpha: float = STEPW_ALPHA
    seed: int = 42


@dataclass(frozen=True)
class CellStats:
    """单格四件套回执——不可变。

    Attributes:
        cell_id: 格标识
        n_samples: 样本数
        win_rate: 胜率（逐期收益>0 占比）
        sharpe_annualized: Lo(2002) 修正年化夏普（ddof=0，√244 基准）
        lo_correction_factor: Lo(2002) 修正因子 c（1.0=未施加）
        ljung_box_p: Ljung-Box p 值（None=不可估：n≤q）
        breakeven_cost_bp: 盈亏平衡逐期附加成本 c*（bp；负期望格=0.0）
        c_star_monotonic: 二分探针单调性校验通过
        dsr: Deflated Sharpe（N_eff 折算；退化态=0.0 且 degenerate=True）
        dsr_degenerate: DSR 退化态（V[SR] 非正=不可判定，禁读作"不显著"）
        per_period_sharpe: 非年化 SR（DSR 输入口径，留痕）
        skewness: 样本偏度（DSR 输入）
        excess_kurtosis: 样本超额峰度（DSR 输入）
        n_eff: 本格 DSR 分母（有效试验数，面板级折算或调用方传入）
        status: "OK" | "INSUFFICIENT-N" | "C_STAR_NON_MONOTONIC"（可复合，分号连接）
    """

    cell_id: str
    n_samples: int
    win_rate: float
    sharpe_annualized: float
    lo_correction_factor: float
    ljung_box_p: float | None
    breakeven_cost_bp: float
    c_star_monotonic: bool
    dsr: float
    dsr_degenerate: bool
    per_period_sharpe: float
    skewness: float
    excess_kurtosis: float
    n_eff: int
    status: str = "OK"


def _to_array(returns: Sequence[float] | np.ndarray | pd.Series) -> np.ndarray:
    arr = np.asarray(returns, dtype=float)
    arr = arr[~np.isnan(arr)]
    return arr


def ljung_box_pvalue(x: np.ndarray, q: int) -> float | None:
    """Ljung-Box Q 检验 p 值（H₀=1..q 阶自相关联合为零）。n≤q 时 None（不可估）。

    Q = n(n+2)·Σ_{k=1..q} ρ̂ₖ²/(n−k)，H₀ 下 ~ χ²(q)。
    上侧 p 值经正则化上不完全 Gamma（χ² sf 闭式）stdlib 自实现，零新依赖。
    """
    n = x.size
    if n <= q + 1:
        return None
    xc = x - x.mean()
    denom = float((xc * xc).sum())
    if denom <= 0.0:
        return None
    q_stat = 0.0
    for k in range(1, q + 1):
        rho = float((xc[k:] * xc[:-k]).sum()) / denom
        q_stat += rho * rho / (n - k)
    q_stat *= n * (n + 2)
    return float(_chi2_sf(q_stat, q))


def _chi2_sf(x: float, k: int) -> float:
    """χ²(k) 上侧概率 = 正则化上不完全 Gamma P(k/2, x/2)（Lentz 连分式，stdlib 口径）。"""
    if x <= 0.0:
        return 1.0
    a, xx = k / 2.0, x / 2.0
    ln_prefactor = -xx + a * math.log(xx) - math.lgamma(a)
    if xx < a + 1.0:  # 级数展这边收敛
        term = 1.0 / a
        total = term
        n = 1
        # 有界级数（PERM-TRIGGER 友好：不用 while True——数值收敛迭代非事件循环）
        while n <= 10000:
            term *= xx / (a + n)
            total += term
            if abs(term) < abs(total) * 1e-14:
                break
            n += 1
        return max(0.0, min(1.0, 1.0 - math.exp(ln_prefactor + math.log(total))))
    # 连分式（Lentz）
    tiny = 1e-300
    b, c, d = xx + 1.0 - a, 1.0 / tiny, 1.0 / (xx + 1.0 - a)
    h = d
    for i in range(1, 10000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-14:
            break
    return max(0.0, min(1.0, math.exp(ln_prefactor + math.log(h))))


def lo2002_annualized_sharpe(
    returns: Sequence[float] | np.ndarray | pd.Series,
    *,
    periods_per_year: int,
    ljung_box_alpha: float,
) -> tuple[float, float, float | None, dict[str, Any]]:
    """⚑-2 B 案口径夏普：ddof=0 + Ljung-Box 显著才施加 Lo(2002) 修正因子。

    Returns:
        (sharpe_annualized, lo_factor, lb_pvalue, meta)
        meta: {"lb_testable": bool, "max_lag": int|None, "n": int}
    """
    x = _to_array(returns)
    n = x.size
    if n < 2:
        return float("nan"), 1.0, None, {"lb_testable": False, "max_lag": None, "n": n}
    sd0 = float(x.std(ddof=0))
    if not sd0 > 0.0:
        return float("nan"), 1.0, None, {"lb_testable": False, "max_lag": None, "n": n}
    q = int(periods_per_year)
    lb_p = ljung_box_pvalue(x, q)
    factor = 1.0
    max_lag: int | None = None
    if lb_p is not None and lb_p < ljung_box_alpha:
        # Lo(2002)：q 期聚合方差含自相关项 q+2Σ(q−k)ρ̂ₖ。自相关截断 lag 用
        # Newey-West (1994) 自动定阶 l=floor(4·(n/100)^{2/9})（文献标准，低方差——
        # 大权重尾部 ρ̂ₖ 噪声 ±0.05×~200 会淹没真信号，n//4 式长截断不稳健；
        # AR(1) 真实相关集中在低阶，NW 截断后的尾部贡献 0.38^l≈0 可忽略）。
        max_lag = int(min(q - 1, max(1, math.floor(4.0 * (n / 100.0) ** (2.0 / 9.0)))))
        xc = x - x.mean()
        denom = float((xc * xc).sum())
        s = 0.0
        for k in range(1, max_lag + 1):
            rho = float((xc[k:] * xc[:-k]).sum()) / denom
            s += (q - k) * rho
        denom_var = float(q) + 2.0 * s
        if denom_var > 0.0:
            factor = math.sqrt(float(q) / denom_var)
    sr_ann = float(x.mean() / sd0) * math.sqrt(float(q)) * factor
    return sr_ann, factor, lb_p, {"lb_testable": lb_p is not None, "max_lag": max_lag, "n": n}


def breakeven_cost_bp(
    returns: Sequence[float] | np.ndarray | pd.Series,
    *,
    turnover_per_period: float = 1.0,
    max_bp: float,
    tol_bp: float,
) -> tuple[float, bool]:
    """盈亏平衡逐期附加成本 c*（bp）：二分 + 探针单调校验。

    f(c)=mean(r)−(c/1e4)·turnover_per_period；c*=sup{c≥0: f(c)≥0}。
    线性成本下 f 严格递减——探针序列若非单调递减=NaN 污染/引擎缺陷
    （C_STAR_NON_MONOTONIC，单列禁静默，ext_01 G-D.2 判据栏）。

    Returns:
        (c_star_bp, monotonic_ok)；负期望格 c*=0.0。
    """
    x = _to_array(returns)
    mu = float(x.mean()) if x.size else float("nan")
    if not math.isfinite(mu):
        return 0.0, False
    turn = float(turnover_per_period)
    if not math.isfinite(turn) or turn < 0.0:
        return 0.0, False

    probes: list[tuple[float, float]] = []

    def f(c_bp: float) -> float:
        val = mu - (c_bp / 1e4) * turn
        probes.append((c_bp, val))
        return val

    if f(0.0) < 0.0:
        return 0.0, True  # 负期望：零成本仍亏 → c*=0
    lo, hi = 0.0, float(max_bp)
    if f(hi) >= 0.0:
        c_star = hi  # 上界内仍正期望 → 封顶（如实：≥max_bp）
    else:
        while hi - lo > tol_bp:
            mid = (lo + hi) / 2.0
            if f(mid) >= 0.0:
                lo = mid
            else:
                hi = mid
        c_star = lo
    # 单调校验：f 沿 c 严格不增（容差 1e-15 浮点）
    pts = sorted(probes)
    vals = [v for _, v in pts]
    monotonic = all(vals[i] >= vals[i + 1] - 1e-15 for i in range(len(vals) - 1))
    return float(c_star), bool(monotonic)


def evaluate_grid(
    returns_by_cell: Mapping[str, Sequence[float] | np.ndarray | pd.Series],
    *,
    n_eff: int | None = None,
    turnover_by_cell: Mapping[str, float] | None = None,
    config: GridStatsConfig | None = None,
) -> dict[str, CellStats]:
    """逐格四件套主入口（G-D.2）。

    Args:
        returns_by_cell: cell_id → 逐期净收益序列（日频；停牌/涨跌停治理归调用方）
        n_eff: 有效试验数（None=面板级 compute_effective_rank 熵广度折算，C251 口径）
        turnover_by_cell: cell_id → 逐期换手（c* 换算用；缺省 1.0）
        config: 引擎配置（默认 ⚑-2 B 案口径）

    Returns:
        {cell_id: CellStats}；样本<min_samples 判 INSUFFICIENT-N（四件套仍如实输出）。
    """
    cfg = config or GridStatsConfig()
    if not returns_by_cell:
        raise GridStatsEngineError("returns_by_cell 为空——禁空面板评估")
    panel: dict[str, np.ndarray] = {}
    for cid, rets in returns_by_cell.items():
        arr = _to_array(rets)
        if arr.size == 0:
            raise GridStatsEngineError(f"cell {cid!r} 全 NaN/空序列——禁空格进引擎")
        panel[str(cid)] = arr

    if n_eff is None:
        eff, _meta = compute_effective_rank({cid: arr.tolist() for cid, arr in panel.items()})
    else:
        eff = int(n_eff)
    if eff < 1:
        raise GridStatsEngineError(f"N_eff 非法: {eff}")

    out: dict[str, CellStats] = {}
    for cid, arr in panel.items():
        status_parts: list[str] = []
        n = int(arr.size)
        win_rate = float((arr > 0).mean())
        sr_ann, lo_factor, lb_p, _lb_meta = lo2002_annualized_sharpe(
            arr, periods_per_year=cfg.periods_per_year, ljung_box_alpha=cfg.ljung_box_alpha
        )
        turn = float((turnover_by_cell or {}).get(cid, 1.0))
        c_star, mono = breakeven_cost_bp(
            arr, turnover_per_period=turn, max_bp=cfg.c_star_max_bp, tol_bp=cfg.c_star_tol_bp
        )
        if n < cfg.min_samples:
            status_parts.append("INSUFFICIENT-N")
        if not mono:
            status_parts.append("C_STAR_NON_MONOTONIC")
        # DSR 输入矩（ddof 口径与模块 SSOT 一致：偏度/峰度按其 _skewness/_kurtosis 同式）
        xc = arr - arr.mean()
        var = float((xc * xc).sum() / n)
        sd = math.sqrt(var) if var > 0 else float("nan")
        sr_per = float(arr.mean() / sd) if sd and sd > 0 else 0.0
        m4 = float((xc**4).sum() / n)
        skew = float((xc**3).sum() / n / sd**3) if sd and sd > 0 else 0.0
        kurt_exc = (m4 / var**2 - 3.0) if var > 0 else 0.0
        _var_sr, dsr, _emax, degenerate = deflated_sharpe_from_moments(
            sharpe=sr_per, num_trials=eff, num_obs=n, skewness=skew, excess_kurtosis=kurt_exc
        )
        out[cid] = CellStats(
            cell_id=cid,
            n_samples=n,
            win_rate=win_rate,
            sharpe_annualized=sr_ann,
            lo_correction_factor=lo_factor,
            ljung_box_p=lb_p,
            breakeven_cost_bp=c_star,
            c_star_monotonic=mono,
            dsr=dsr,
            dsr_degenerate=degenerate,
            per_period_sharpe=sr_per,
            skewness=skew,
            excess_kurtosis=kurt_exc,
            n_eff=eff,
            status=";".join(status_parts) if status_parts else "OK",
        )
    return out


def spa_reality_check(
    returns_by_cell: Mapping[str, Sequence[float] | np.ndarray | pd.Series],
    *,
    config: GridStatsConfig | None = None,
) -> dict[str, Any]:
    """White (2000) Reality Check / Hansen (2005) SPA 简版（G-D.3）。

    口径（文献注释）：每格统计量=标准化均值 t；stationary bootstrap（复用
    e2_stationary_bootstrap.stationary_bootstrap_indices）按行联合重采样——
    同一索引向量作用于全部格，保持格间截面相关（Reality Check 的 H₀=
    "最优格无超额"对全体格同时成立）。逐格 p 值=重采样 max 统计量 ≥ 实测 t 的
    频率（Hansen (2005) recentered/lower-bound SPA 口径：bootstrap 统计量按
    实测均值 recenter，欠中心格不拖累他格 p 值）。

    Returns:
        {"cells": {cid: {"t_stat": x, "spa_p": p}}, "n_boot": B, "n_common": n}
        p 值下限=1/(B+1)（禁报 0——bootstrap p=0 是采样不足非零概率）。
    """
    cfg = config or GridStatsConfig()
    panel = {str(cid): _to_array(r) for cid, r in returns_by_cell.items()}
    if len(panel) < 2:
        raise GridStatsEngineError("SPA 需 ≥2 格（单格无'最优'多重问题）")
    n = {cid: arr.size for cid, arr in panel.items()}
    n_common = min(n.values())
    if n_common < 2:
        raise GridStatsEngineError(f"共同窗过短: {n_common}")
    ids = sorted(panel)
    mat = np.column_stack([panel[cid][:n_common] for cid in ids])

    def _t(x: np.ndarray) -> float:
        sd = x.std(ddof=1)
        return float(x.mean() / sd * math.sqrt(x.size)) if sd > 0 else 0.0

    t_obs = np.array([_t(mat[:, j]) for j in range(len(ids))])
    mu_obs = np.array([mat[:, j].mean() for j in range(len(ids))])
    rng = np.random.default_rng(cfg.seed)
    max_boot = np.empty(cfg.spa_n_boot)
    for b in range(cfg.spa_n_boot):
        idx = stationary_bootstrap_indices(n_common, cfg.spa_mean_block, rng)
        centered = mat[idx] - mu_obs  # Hansen recentering
        max_boot[b] = max(_t(centered[:, j]) for j in range(len(ids)))
    floor = 1.0 / (cfg.spa_n_boot + 1.0)
    cells = {
        cid: {"t_stat": float(t_obs[j]), "spa_p": float(max(floor, float((max_boot >= t_obs[j]).mean())))}
        for j, cid in enumerate(ids)
    }
    return {"cells": cells, "n_boot": int(cfg.spa_n_boot), "n_common": int(n_common)}


def stepm(
    returns_by_cell: Mapping[str, Sequence[float] | np.ndarray | pd.Series],
    *,
    config: GridStatsConfig | None = None,
) -> dict[str, Any]:
    """StepM 简版（Romano-Wolf 2005 思路，G-D.3"识别全部显著格"）。

    迭代：存活集上 bootstrap max 分布 (1−α) 分位为临界值 → 超者入显著集并移出；
    重复至无新增。简化点见模块 docstring（逐步重推 max 分布，非逐步 recentering）。

    Returns:
        {"significant": [cid...], "steps": [{"critical": c, "rejected": [...]}...],
         "survivors": [cid...], "n_boot": B, "alpha": a}
    """
    cfg = config or GridStatsConfig()
    panel = {str(cid): _to_array(r) for cid, r in returns_by_cell.items()}
    if len(panel) < 2:
        raise GridStatsEngineError("StepM 需 ≥2 格")
    n_common = min(arr.size for arr in panel.values())
    if n_common < 2:
        raise GridStatsEngineError(f"共同窗过短: {n_common}")
    ids = sorted(panel)
    mat = np.column_stack([panel[cid][:n_common] for cid in ids])
    col = {cid: j for j, cid in enumerate(ids)}

    def _t(x: np.ndarray) -> float:
        sd = x.std(ddof=1)
        return float(x.mean() / sd * math.sqrt(x.size)) if sd > 0 else 0.0

    t_obs = {cid: _t(mat[:, col[cid]]) for cid in ids}
    mu_obs = {cid: float(mat[:, col[cid]].mean()) for cid in ids}
    rng = np.random.default_rng(cfg.seed)

    def _boot_max(alive: list[str]) -> np.ndarray:
        out = np.empty(cfg.spa_n_boot)
        for b in range(cfg.spa_n_boot):
            idx = stationary_bootstrap_indices(n_common, cfg.spa_mean_block, rng)
            worst = -math.inf
            for cid in alive:
                x = mat[idx, col[cid]] - mu_obs[cid]
                worst = max(worst, _t(x))
            out[b] = worst
        return out

    significant: list[str] = []
    survivors = list(ids)
    steps: list[dict[str, Any]] = []
    while survivors:
        crit = float(np.quantile(_boot_max(survivors), 1.0 - cfg.stepw_alpha))
        rejected = [cid for cid in sorted(survivors, key=lambda c: -t_obs[c]) if t_obs[cid] > crit]
        if not rejected:
            break
        significant.extend(rejected)
        survivors = [c for c in survivors if c not in rejected]
        steps.append({"critical": crit, "rejected": rejected})
    return {
        "significant": significant,
        "steps": steps,
        "survivors": survivors,
        "n_boot": int(cfg.spa_n_boot),
        "alpha": float(cfg.stepw_alpha),
    }


def half_split_reexam(
    returns_by_cell: Mapping[str, Sequence[float] | np.ndarray | pd.Series],
    *,
    config: GridStatsConfig | None = None,
    grid_id: str = "grid",
) -> dict[str, Any]:
    """分半窗+时间外推检验（G-D.3 滚动重考口径，Sullivan 1999/Hsu 2010）。

    前半窗冠军是否在后半窗存活（夏普符号/相对位次）；负结果无论正负都保留
    （negative_result_promise 口径）。**排程=事件触发**：返回值即"待登记重考任务
    记录"，由消费方（点火卡/日闸事件）写 tasks 注册——本件零 Timer/cron/sleep
    （永久系统四要素红线），READY_NOT_FIRED 不点火。

    Returns:
        {"grid_id", "half1": {cid: {"sharpe","n"}}, "half2": {...},
         "champion_half1", "champion_survives_half2": bool, "sign_flips": [cid...],
         "reexam_task": {"kind": "rolling_reexam", "event": "grid_evaluated", ...}}
    """
    cfg = config or GridStatsConfig()
    panel = {str(cid): _to_array(r) for cid, r in returns_by_cell.items()}
    n_common = min(arr.size for arr in panel.values())
    if n_common < 4:
        raise GridStatsEngineError(f"分半窗共同样本过短: {n_common}")
    half = n_common // 2
    h1_stats: dict[str, dict[str, float]] = {}
    h2_stats: dict[str, dict[str, float]] = {}
    sign_flips: list[str] = []
    for cid, arr in panel.items():
        s1, f1, _p, _m = lo2002_annualized_sharpe(
            arr[:half], periods_per_year=cfg.periods_per_year, ljung_box_alpha=cfg.ljung_box_alpha
        )
        s2, f2, _p2, _m2 = lo2002_annualized_sharpe(
            arr[half : 2 * half], periods_per_year=cfg.periods_per_year, ljung_box_alpha=cfg.ljung_box_alpha
        )
        h1_stats[cid] = {"sharpe": float(s1), "lo_factor": float(f1), "n": int(half)}
        h2_stats[cid] = {"sharpe": float(s2), "lo_factor": float(f2), "n": int(n_common - half)}
        if math.isfinite(s1) and math.isfinite(s2) and (s1 > 0) != (s2 > 0):
            sign_flips.append(cid)
    champ1 = max(h1_stats, key=lambda c: h1_stats[c]["sharpe"])
    champ_survives = h2_stats[champ1]["sharpe"] > 0.0
    return {
        "grid_id": grid_id,
        "half1": h1_stats,
        "half2": h2_stats,
        "champion_half1": champ1,
        "champion_survives_half2": bool(champ_survives),
        "sign_flips": sign_flips,
        "reexam_task": {
            "kind": "rolling_reexam",
            "event": "grid_evaluated",
            "grid_id": grid_id,
            "note": "事件触发重考任务记录（消费方写 tasks 注册；禁 cron/Timer——永久系统四要素）",
            "sign_flip_cells": sign_flips,
            "champion_half1": champ1,
            "champion_survives_half2": bool(champ_survives),
        },
    }


__all__ = [
    "C_STAR_MAX_BP",
    "C_STAR_TOL_BP",
    "DSR_PASS_THRESHOLD",
    "GridStatsConfig",
    "GridStatsEngineError",
    "LJUNG_BOX_ALPHA",
    "MIN_SAMPLES_PER_CELL",
    "SPA_MEAN_BLOCK",
    "SPA_N_BOOT",
    "STEPW_ALPHA",
    "CellStats",
    "breakeven_cost_bp",
    "evaluate_grid",
    "half_split_reexam",
    "lo2002_annualized_sharpe",
    "ljung_box_pvalue",
    "spa_reality_check",
    "stepm",
]
