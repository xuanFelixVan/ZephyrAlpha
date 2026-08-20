# [BLUEPRINT] MOD-SIM-026 | docs/03_modules/_domain_simulation/blueprint.md
# [MODULE] zephyr.simulation.divergence_attributor
# [DOMAIN] D_SIMULATION
# [DEPENDENCIES]
# [CONSUMERS] 预留(paper_live_transition SHADOW/GRAY_RAMP 阶段实盘数据累积后接线, 53号§3.5)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 四因子输入注入式(None=未观测跳过);overall_passed=全观测因子通过;阈值默认值与paper_live_transition key_gates一致
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DivergenceAttributionError(ZA-SIM-0026)
# [TESTS] tests/simulation/test_divergence_attributor.py
# [TTL] permanent
# [A_module] module_id=MOD-SIM-026 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [ALGO_FLOW]
# I1: DivergenceObservation(signal_match/slippage_diff_bps/data_lag_ms/latency_ms/pnl_correlation, None=未观测)
# I2: DivergenceThresholds(默认对齐paper_live_transition key_gates: 99.9%/1bp/0.95/100ms)
# A1: 四因子逐项门禁判定(滑点A/数据滞后B/前瞻残留C/执行时延D + PnL相关总值)
# A2: dominant_factor(未通过因子中偏差幅度最大者)
# O1: DivergenceReport(逐因子verdict + overall_passed + dominant_factor)
# [/ALGO_FLOW]
"""回测-实盘偏差四因子归因模块(BM-BT-05-H)

职责(53号 memo §3.5, v2.0 候选——待实盘数据累积后启用):
  - 将回测-实盘总偏差分解为四因子逐项门禁判定:
      A 滑点偏差(slippage_diff_bps < 1bp, 复用 ex_sor/slippage_analyzer 口径)
      B 数据滞后(data_lag_ms, arrived_at−timestamp 插桩值, 默认无门禁仅记录)
      C 前瞻残留(signal_match >= 99.9%, 复用 look_ahead_bias_detector 数据层金标准)
      D 执行时延(latency_ms < 100ms, 复用 execution_quality_scorer 口径)
    另附 PnL 相关总值门禁(shadow_pnl_correlation >= 0.95)
  - 输出逐因子判定 + 主导因子(未通过因子中偏差幅度最大者), 供偏差调查定位

约束:
  - 输入注入式: 全部观测量由调用方供给(实盘成交/对账数据), 本模块不采集数据
  - None = 该因子未观测, 跳过判定不记失败(与 53 号"待实盘数据"状态兼容)
  - 阈值默认值与 paper_live_transition key_gates 机制初始值一致, 校准走配置注入

SSoT: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/53_simulation_live_path.md §3.5
"""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = [
    "DivergenceAttributionError",
    "DivergenceThresholds",
    "DivergenceObservation",
    "FactorVerdict",
    "DivergenceReport",
    "attribute_divergence",
]


class DivergenceAttributionError(Exception):
    """偏差归因错误(输入非法)"""

    error_code = "ZA-SIM-0026"

    def __init__(self, *args, error_code: str | None = None) -> None:
        super().__init__(*args)
        if error_code is not None:
            self.error_code = error_code


@dataclass(frozen=True)
class DivergenceThresholds:
    """四因子门禁阈值(不可变; 默认值=paper_live_transition key_gates 机制初始值)

    Attributes:
        signal_match_min: 信号一致性下限(因子C, 默认0.999)
        slippage_diff_max_bps: 滑点偏差上限(因子A, 默认1.0bp)
        data_lag_max_ms: 数据滞后上限(因子B, 默认None=无门禁仅记录,
            arrived_at−timestamp 插桩阈值待实盘数据校准)
        latency_max_ms: 执行时延上限(因子D, 默认100ms)
        pnl_correlation_min: PnL相关下限(总值门禁, 默认0.95)
    """

    signal_match_min: float = 0.999
    slippage_diff_max_bps: float = 1.0
    data_lag_max_ms: float | None = None
    latency_max_ms: float = 100.0
    pnl_correlation_min: float = 0.95

    def __post_init__(self) -> None:
        if not 0 < self.signal_match_min <= 1:
            raise DivergenceAttributionError(f"signal_match_min必须在(0,1], got {self.signal_match_min}")
        if self.slippage_diff_max_bps <= 0:
            raise DivergenceAttributionError(f"slippage_diff_max_bps必须>0, got {self.slippage_diff_max_bps}")
        if self.data_lag_max_ms is not None and self.data_lag_max_ms <= 0:
            raise DivergenceAttributionError(f"data_lag_max_ms必须>0或None, got {self.data_lag_max_ms}")
        if self.latency_max_ms <= 0:
            raise DivergenceAttributionError(f"latency_max_ms必须>0, got {self.latency_max_ms}")
        if not 0 < self.pnl_correlation_min <= 1:
            raise DivergenceAttributionError(f"pnl_correlation_min必须在(0,1], got {self.pnl_correlation_min}")


@dataclass(frozen=True)
class DivergenceObservation:
    """回测-实盘偏差观测量(输入注入式; None=该因子未观测)

    Attributes:
        signal_match_pct: 信号一致率(因子C, ∈[0,1])
        slippage_diff_bps: 滑点偏差绝对值(因子A, bp, >=0)
        data_lag_ms: 数据滞后(因子B, ms, >=0)
        latency_ms: 执行时延(因子D, ms, >=0)
        pnl_correlation: 模拟/实盘PnL相关系数(总值, ∈[-1,1])
    """

    signal_match_pct: float | None = None
    slippage_diff_bps: float | None = None
    data_lag_ms: float | None = None
    latency_ms: float | None = None
    pnl_correlation: float | None = None


@dataclass(frozen=True)
class FactorVerdict:
    """单因子判定结果(不可变)

    Attributes:
        factor: 因子标识(A_SLIPPAGE/B_DATA_LAG/C_LOOKAHEAD/D_LATENCY/TOTAL_PNL)
        observed: 是否有观测输入
        value: 观测值(未观测为None)
        threshold: 判定阈值(无门禁为None)
        passed: 是否通过(未观测/无门禁为True)
        excess_ratio: 偏差幅度(超出阈值的比例, 通过/无门禁为0)——dominant_factor 依据
        reason: 判定理由
    """

    factor: str
    observed: bool
    value: float | None
    threshold: float | None
    passed: bool
    excess_ratio: float = 0.0
    reason: str = ""


@dataclass(frozen=True)
class DivergenceReport:
    """四因子归因报告(不可变)

    Attributes:
        factors: 逐因子判定(固定5项: A/B/C/D/TOTAL_PNL)
        overall_passed: 全部已观测因子通过
        dominant_factor: 主导偏差因子(未通过因子中 excess_ratio 最大者; 全通过/无未通过为None)
        n_observed: 有观测输入的因子数
        n_failed: 未通过因子数
    """

    factors: tuple[FactorVerdict, ...] = field(default_factory=tuple)
    overall_passed: bool = True
    dominant_factor: str | None = None
    n_observed: int = 0
    n_failed: int = 0


def _verdict_below(factor: str, value: float | None, threshold: float | None, name_zh: str) -> FactorVerdict:
    """ "值<=阈值"型因子判定(滑点A/数据滞后B/执行时延D)"""
    if value is None:
        return FactorVerdict(
            factor=factor,
            observed=False,
            value=None,
            threshold=threshold,
            passed=True,
            reason=f"{name_zh}未观测,跳过判定",
        )
    v = float(value)
    if v < 0:
        raise DivergenceAttributionError(f"{name_zh}观测值必须>=0, got {value}")
    if threshold is None:
        return FactorVerdict(
            factor=factor,
            observed=True,
            value=v,
            threshold=None,
            passed=True,
            reason=f"{name_zh}={v}已记录(无门禁阈值,待实盘校准)",
        )
    passed = v <= threshold
    excess = 0.0 if passed else (v - threshold) / threshold
    return FactorVerdict(
        factor=factor,
        observed=True,
        value=v,
        threshold=threshold,
        passed=passed,
        excess_ratio=excess,
        reason=(
            f"{name_zh}={v} <= {threshold} 通过" if passed else f"{name_zh}={v} > {threshold} 未通过(超出{excess:.2%})"
        ),
    )


def _verdict_above(
    factor: str, value: float | None, threshold: float, name_zh: str, lo: float, hi: float
) -> FactorVerdict:
    """ "值>=阈值"型因子判定(前瞻残留C/PnL相关总值)"""
    if value is None:
        return FactorVerdict(
            factor=factor,
            observed=False,
            value=None,
            threshold=threshold,
            passed=True,
            reason=f"{name_zh}未观测,跳过判定",
        )
    v = float(value)
    if not lo <= v <= hi:
        raise DivergenceAttributionError(f"{name_zh}观测值必须在[{lo},{hi}], got {value}")
    passed = v >= threshold
    excess = 0.0 if passed else (threshold - v) / threshold
    return FactorVerdict(
        factor=factor,
        observed=True,
        value=v,
        threshold=threshold,
        passed=passed,
        excess_ratio=excess,
        reason=(
            f"{name_zh}={v} >= {threshold} 通过" if passed else f"{name_zh}={v} < {threshold} 未通过(缺口{excess:.2%})"
        ),
    )


def attribute_divergence(
    observation: DivergenceObservation,
    thresholds: DivergenceThresholds | None = None,
) -> DivergenceReport:
    """回测-实盘偏差四因子归因(输入注入式)

    Args:
        observation: 观测量(None=该因子未观测, 跳过判定)
        thresholds: 门禁阈值(None=默认, 对齐 paper_live_transition key_gates)

    Returns:
        DivergenceReport: 逐因子判定 + overall_passed + dominant_factor

    Raises:
        DivergenceAttributionError: observation 非法或观测值越界
    """
    if not isinstance(observation, DivergenceObservation):
        raise DivergenceAttributionError(f"observation必须是DivergenceObservation: {type(observation).__name__}")
    th = thresholds if thresholds is not None else DivergenceThresholds()

    factors = (
        _verdict_below("A_SLIPPAGE", observation.slippage_diff_bps, th.slippage_diff_max_bps, "滑点偏差(bps)"),
        _verdict_below("B_DATA_LAG", observation.data_lag_ms, th.data_lag_max_ms, "数据滞后(ms)"),
        _verdict_above("C_LOOKAHEAD", observation.signal_match_pct, th.signal_match_min, "信号一致率", 0.0, 1.0),
        _verdict_below("D_LATENCY", observation.latency_ms, th.latency_max_ms, "执行时延(ms)"),
        _verdict_above("TOTAL_PNL", observation.pnl_correlation, th.pnl_correlation_min, "PnL相关", -1.0, 1.0),
    )

    failed = [f for f in factors if f.observed and not f.passed]
    dominant = max(failed, key=lambda f: f.excess_ratio).factor if failed else None
    return DivergenceReport(
        factors=factors,
        overall_passed=len(failed) == 0,
        dominant_factor=dominant,
        n_observed=sum(1 for f in factors if f.observed),
        n_failed=len(failed),
    )
