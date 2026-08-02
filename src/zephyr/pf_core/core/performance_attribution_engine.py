# [BLUEPRINT] MOD-PF-007 | docs/03_modules/_domain_portfolio_core/performance_attribution_engine/blueprint.md
# [MODULE] zephyr.pf_core.core.performance_attribution_engine
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.reporting.analytics_base(AttributionEngineBase); zephyr.risk.core.risk_decomposition(MOD-RK-16); zephyr.pf_alloc.core.strategy_correlation_gate(MOD-PA-004); zephyr.shared.contracts.performance_attribution_report(CTR-P1-009); numpy; zephyr.shared.foundation.errors
# [CONSUMERS] D_REPORTING(归因报告消费) ; D_GOV_ENFORCEMENT(降级检测审计) ; MOD-PF-001(PC-01 策略引擎消费降级/拥挤建议)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] excess_return=allocation+selection+interaction(守恒);factor_contributions之和≈selection_effect;降级检测不修改权重仅标记建议;transaction_cost_drag≥0;实现AttributionEngineBase OCP契约
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributionDataIncompleteError;RiskDecompositionUnavailable;ICDecayDetectionError
# [TESTS] tests/pf_core/test_performance_attribution_engine.py
# [A_module] module_id=MOD-PF-007 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Performance Attribution Engine — 绩效归因引擎 (MOD-PF-007 / PC-10)

D-PF-CORE §1.2 盘后归因核心模块。将组合收益分解为可归因的成分, 供 D_REPORTING
消费、D_GOV_ENFORCEMENT 审计、PC-01 策略引擎接收降级/拥挤反馈。

核心能力:
    1. Brinson 三因子分解 (Brinson-Fachler 模型):
       - allocation_effect   = Σ (w_p - w_b) × r_b    (配置效应)
       - selection_effect    = Σ w_b × (r_p - r_b)     (选择效应)
       - interaction_effect  = Σ (w_p - w_b) × (r_p - r_b)  (交互效应)
       - excess_return = allocation + selection + interaction (守恒)
    2. 因子归因: factor_contribution[i] = exposure_i × factor_return_i
    3. 风险归因: 复用 MOD-RK-16 RiskDecomposer (因子/残差 + MCR/CCR)
    4. 策略降级检测: IC 衰减 >50% → 权重归 0 建议
    5. 拥挤检测: ρ>0.8 减半 / ρ>0.9 归零建议 (复用 MOD-PA-004 阈值体系)

属 A 类基础设施 (数学归因模型, 无策略决策), 归因结果供 D_REPORTING 消费。
降级/拥挤检测结果仅标记建议, 由 PC-01 执行实际权重调整。
依据: D:\\临时工作区\\依赖图\\05-D-PF-CORE-组合核心域.md §1.2 PC-10
SSoT: depgraph MOD-PF-007
Version: 0.1.0
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

import numpy as np

from zephyr.pf_alloc.core.strategy_correlation_gate import StrategyCorrelationGate
from zephyr.reporting.analytics_base import AttributionEngineBase
from zephyr.risk.core.risk_decomposition import DecompositionResult, RiskDecomposer
from zephyr.shared.contracts.performance_attribution_report import (
    PerformanceAttributionReport,
)
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "CrowdingLevel",
    "SegmentReturn",
    "BrinsonResult",
    "DegradationDetection",
    "CrowdingDetection",
    "AttributionContext",
    "PerformanceAttributionEngine",
    "AttributionDataIncompleteError",
    "RiskDecompositionUnavailable",
    "ICDecayDetectionError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class CrowdingLevel(str, Enum):
    """策略拥挤级别。"""

    NONE = "none"  # 无拥挤
    WARN = "warn"  # ρ>0.8 → 权重减半
    SEVERE = "severe"  # ρ>0.9 → 权重归零


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class AttributionDataIncompleteError(ZephyrBaseError):
    """归因数据不完整 (如分段为空、权重与收益维度不匹配)。"""

    error_code = "ZA-PF-0071"


class RiskDecompositionUnavailable(ZephyrBaseError):
    """风险分解不可用 (MOD-RK-16 调用失败, 降级为跳过风险归因)。"""

    error_code = "ZA-PF-0072"


class ICDecayDetectionError(ZephyrBaseError):
    """IC 衰减检测数据不足 (降级为跳过降级检测)。"""

    error_code = "ZA-PF-0073"


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class SegmentReturn:
    """Brinson 分组 (行业/资产类别) 的收益数据。

    Attributes:
        segment: 分组名 (如 "科技"/"金融")
        portfolio_weight: 组合中该组权重 w_p (≥0)
        benchmark_weight: 基准中该组权重 w_b (≥0)
        portfolio_return: 组合中该组收益率 r_p
        benchmark_return: 基准中该组收益率 r_b
    """

    segment: str
    portfolio_weight: float
    benchmark_weight: float
    portfolio_return: float
    benchmark_return: float


@dataclass(frozen=True)
class BrinsonResult:
    """Brinson 三因子归因结果。

    不变量: excess_return = allocation + selection + interaction (守恒)。
    """

    allocation_effect: float
    selection_effect: float
    interaction_effect: float
    excess_return: float  # = allocation + selection + interaction
    portfolio_return: float  # Σ w_p × r_p (组合总收益)
    benchmark_return: float  # Σ w_b × r_b (基准总收益)
    segments: list[SegmentReturn] = field(default_factory=list)

    @property
    def total_attribution(self) -> float:
        """三因子之和 (= excess_return, 守恒校验)。"""
        return self.allocation_effect + self.selection_effect + self.interaction_effect

    @property
    def is_consistent(self) -> bool:
        """守恒校验: 三因子之和 == excess_return。"""
        return math.isclose(self.total_attribution, self.excess_return, abs_tol=1e-9)


@dataclass(frozen=True)
class DegradationDetection:
    """策略退化检测结果。

    IC (Information Coefficient) = 预测收益与实际收益的相关性。
    IC 衰减 >50% → 策略退化 → 建议权重归零。

    降级检测不修改组合权重, 仅标记建议, 由 PC-01 执行。
    """

    strategy_id: str
    baseline_ic: float  # 历史均值 IC
    recent_ic: float  # 近期 IC
    ic_decay_pct: float  # (baseline - recent) / baseline, ∈ [0, ∞)
    degraded: bool  # ic_decay_pct > threshold
    recommended_weight: float  # 0.0 if degraded else 1.0


@dataclass(frozen=True)
class CrowdingDetection:
    """策略拥挤检测结果。

    ρ>0.8 → WARN (权重减半); ρ>0.9 → SEVERE (权重归零)。
    拥挤检测不修改组合权重, 仅标记建议, 由 PC-01 执行。
    """

    strategy_id: str
    max_correlation: float  # 与其他策略的最大相关性 (绝对值)
    crowded_with: str  # 相关性最高的对手策略 ID
    crowding_level: CrowdingLevel
    recommended_weight_scale: float  # 1.0 / 0.5 / 0.0


@dataclass(frozen=True)
class AttributionContext:
    """OCP attribute() 方法的上下文 (通过 set_context 注入)。

    AttributionEngineBase.attribute() 签名不含业务数据,
    实现者通过 set_context 注入归因所需输入。
    """

    segments: list[SegmentReturn]
    portfolio_id: str = ""
    transaction_cost_drag: float = 0.0
    weights: dict[str, float] | None = None
    factor_exposures: dict[str, dict[str, float]] | None = None
    factor_returns: dict[str, float] | None = None
    covariance: np.ndarray | None = None
    assets: list[str] | None = None


# ──────────────────────────────────────────────────────────────────────────────
# 绩效归因引擎
# ──────────────────────────────────────────────────────────────────────────────


class PerformanceAttributionEngine(AttributionEngineBase):
    """绩效归因引擎——Brinson 三因子 + 因子/风险归因 + 降级/拥挤检测。

    实现 AttributionEngineBase OCP 契约 (D_REPORTING 可替换 DefaultAttributionEngine)。

    用法 (完整归因):
        engine = PerformanceAttributionEngine()
        segments = [
            SegmentReturn("科技", 0.40, 0.30, 0.05, 0.03),
            SegmentReturn("金融", 0.60, 0.70, 0.02, 0.01),
        ]
        report = engine.attribute_full(
            portfolio_id="PF-001",
            period_start="2026-01-01",
            period_end="2026-03-31",
            idempotency_key="attr-2026q1-001",
            segments=segments,
            transaction_cost_drag=0.002,
        )

    用法 (OCP 契约):
        engine.set_context(AttributionContext(segments=segments, portfolio_id="PF-001"))
        report = engine.attribute("PF-001", "2026-01-01", "2026-03-31", "attr-001")

    用法 (降级检测):
        deg = engine.detect_degradation("STRAT-A", baseline_ic=0.08, recent_ic=0.03)
        if deg.degraded:
            # PC-01 将 STRAT-A 权重归零

    Args:
        risk_decomposer: 风险分解器 (MOD-RK-16), None 则内部新建
        correlation_gate: 策略相关性门禁 (MOD-PA-004), None 则仅用阈值
        ic_decay_threshold: IC 衰减阈值 (默认 0.5 = 50%)
        crowding_warn_threshold: 拥挤警告阈值 (默认 0.8)
        crowding_severe_threshold: 拥挤严重阈值 (默认 0.9)
        clock: 可选时间源 (测试注入)
    """

    def __init__(
        self,
        risk_decomposer: RiskDecomposer | None = None,
        correlation_gate: StrategyCorrelationGate | None = None,
        ic_decay_threshold: float = 0.5,
        crowding_warn_threshold: float = 0.8,
        crowding_severe_threshold: float = 0.9,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if not 0 <= ic_decay_threshold <= 1:
            raise ICDecayDetectionError(f"ic_decay_threshold must be in [0,1], got {ic_decay_threshold}")
        if not (crowding_warn_threshold < crowding_severe_threshold):
            raise AttributionDataIncompleteError("crowding_warn_threshold must be < crowding_severe_threshold")
        self._risk_decomposer = risk_decomposer or RiskDecomposer()
        self._correlation_gate = correlation_gate
        self._ic_decay_threshold = ic_decay_threshold
        self._crowding_warn = crowding_warn_threshold
        self._crowding_severe = crowding_severe_threshold
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._context: AttributionContext | None = None

    @property
    def ic_decay_threshold(self) -> float:
        return self._ic_decay_threshold

    @property
    def crowding_warn_threshold(self) -> float:
        return self._crowding_warn

    @property
    def crowding_severe_threshold(self) -> float:
        return self._crowding_severe

    # ── Brinson 三因子 ──

    def brinson_attribute(
        self,
        segments: list[SegmentReturn],
        now: datetime | None = None,
    ) -> BrinsonResult:
        """Brinson-Fachler 三因子归因。

        Args:
            segments: 分组收益数据列表 (行业/资产类别)
            now: 时间戳

        Returns:
            BrinsonResult (allocation + selection + interaction = excess_return)

        Raises:
            AttributionDataIncompleteError: 分段为空或权重/收益非法
        """
        if not segments:
            raise AttributionDataIncompleteError("segments list is empty")
        for seg in segments:
            if seg.portfolio_weight < 0 or seg.benchmark_weight < 0:
                raise AttributionDataIncompleteError(f"negative weight in segment {seg.segment!r}")

        allocation = 0.0
        selection = 0.0
        interaction = 0.0
        portfolio_return = 0.0
        benchmark_return = 0.0

        for seg in segments:
            wp, wb = seg.portfolio_weight, seg.benchmark_weight
            rp, rb = seg.portfolio_return, seg.benchmark_return
            allocation += (wp - wb) * rb
            selection += wb * (rp - rb)
            interaction += (wp - wb) * (rp - rb)
            portfolio_return += wp * rp
            benchmark_return += wb * rb

        excess = allocation + selection + interaction

        logger.info(
            "Brinson attribution: allocation=%.6f selection=%.6f interaction=%.6f "
            "excess=%.6f (portfolio=%.6f benchmark=%.6f, segments=%d)",
            allocation,
            selection,
            interaction,
            excess,
            portfolio_return,
            benchmark_return,
            len(segments),
        )

        return BrinsonResult(
            allocation_effect=allocation,
            selection_effect=selection,
            interaction_effect=interaction,
            excess_return=excess,
            portfolio_return=portfolio_return,
            benchmark_return=benchmark_return,
            segments=list(segments),
        )

    # ── 因子归因 ──

    def factor_attribute(
        self,
        weights: dict[str, float],
        factor_exposures: dict[str, dict[str, float]],
        factor_returns: dict[str, float],
    ) -> dict[str, float]:
        """因子归因——分解各因子对组合收益的贡献。

        factor_contribution[k] = Σ_i (w_i × exposure_{i,k}) × factor_return_k

        Args:
            weights: 标产权重 {symbol: weight}
            factor_exposures: 标品因子暴露 {symbol: {factor_id: exposure}}
            factor_returns: 因子收益 {factor_id: return}

        Returns:
            {factor_id: contribution} (各因子对组合收益的贡献)
        """
        contributions: dict[str, float] = {}
        for factor_id, fr in factor_returns.items():
            contrib = 0.0
            for symbol, w in weights.items():
                exposure = factor_exposures.get(symbol, {}).get(factor_id, 0.0)
                contrib += w * exposure * fr
            contributions[factor_id] = contrib
        return contributions

    # ── 风险归因 (复用 MOD-RK-16) ──

    def risk_attribute(
        self,
        cov: np.ndarray,
        weights: np.ndarray | dict[str, float],
        assets: list[str] | None = None,
        now: datetime | None = None,
    ) -> DecompositionResult:
        """风险归因——复用 MOD-RK-16 RiskDecomposer。

        Args:
            cov: 协方差矩阵 (N, N)
            weights: 权重向量或字典
            assets: 资产代码列表 (可选)
            now: 时间戳

        Returns:
            DecompositionResult (MCR/CCR + 因子/残差分解)

        Raises:
            RiskDecompositionUnavailable: 风险分解调用失败
        """
        now = now or self._clock()
        if isinstance(weights, dict):
            if assets is None:
                assets = list(weights.keys())
            w_arr = np.array([weights.get(a, 0.0) for a in assets], dtype=float)
        else:
            w_arr = np.asarray(weights, dtype=float)
        try:
            return self._risk_decomposer.decompose(cov, w_arr, assets=assets, now=now)
        except Exception as exc:
            raise RiskDecompositionUnavailable(f"RiskDecomposer failed: {exc}") from exc

    # ── 策略降级检测 ──

    def detect_degradation(
        self,
        strategy_id: str,
        baseline_ic: float,
        recent_ic: float,
    ) -> DegradationDetection:
        """策略退化检测——IC 衰减 >50% → 权重归零建议。

        IC (Information Coefficient) = 预测收益与实际收益的相关性。
        IC 衰减 = (baseline - recent) / baseline。

        Args:
            strategy_id: 策略 ID
            baseline_ic: 历史均值 IC (基准)
            recent_ic: 近期 IC

        Returns:
            DegradationDetection (含 degraded 标记 + recommended_weight)

        Raises:
            ICDecayDetectionError: baseline_ic ≤ 0 (无法计算衰减百分比)
        """
        if baseline_ic <= 0:
            # baseline 已非正 → 策略本就无效, 直接标记降级
            logger.warning(
                "strategy %s baseline_ic=%.4f ≤ 0; marking as degraded",
                strategy_id,
                baseline_ic,
            )
            return DegradationDetection(
                strategy_id=strategy_id,
                baseline_ic=baseline_ic,
                recent_ic=recent_ic,
                ic_decay_pct=1.0 if recent_ic <= 0 else 0.0,
                degraded=True,
                recommended_weight=0.0,
            )

        ic_decay_pct = (baseline_ic - recent_ic) / baseline_ic
        degraded = ic_decay_pct > self._ic_decay_threshold
        recommended = 0.0 if degraded else 1.0

        if degraded:
            logger.warning(
                "strategy %s DEGRADED: ic_decay=%.1f%% (baseline=%.4f recent=%.4f threshold=%.0f%%)",
                strategy_id,
                ic_decay_pct * 100,
                baseline_ic,
                recent_ic,
                self._ic_decay_threshold * 100,
            )

        return DegradationDetection(
            strategy_id=strategy_id,
            baseline_ic=baseline_ic,
            recent_ic=recent_ic,
            ic_decay_pct=ic_decay_pct,
            degraded=degraded,
            recommended_weight=recommended,
        )

    # ── 拥挤检测 ──

    def detect_crowding(
        self,
        strategy_id: str,
        correlations: dict[str, float],
    ) -> CrowdingDetection:
        """策略拥挤检测——ρ>0.8 减半 / ρ>0.9 归零建议。

        Args:
            strategy_id: 被检测策略 ID
            correlations: 与其他策略的相关性 {other_strategy_id: correlation}

        Returns:
            CrowdingDetection (含 crowding_level + recommended_weight_scale)
        """
        if not correlations:
            return CrowdingDetection(
                strategy_id=strategy_id,
                max_correlation=0.0,
                crowded_with="",
                crowding_level=CrowdingLevel.NONE,
                recommended_weight_scale=1.0,
            )

        # 取绝对值最大者
        max_other = max(correlations.items(), key=lambda kv: abs(kv[1]))
        max_corr = abs(max_other[1])
        crowded_with = max_other[0]

        if max_corr > self._crowding_severe:
            level = CrowdingLevel.SEVERE
            scale = 0.0
        elif max_corr > self._crowding_warn:
            level = CrowdingLevel.WARN
            scale = 0.5
        else:
            level = CrowdingLevel.NONE
            scale = 1.0

        if level != CrowdingLevel.NONE:
            logger.warning(
                "strategy %s CROWDING %s: max_corr=%.4f with %s (warn>%.1f severe>%.1f)",
                strategy_id,
                level.value,
                max_corr,
                crowded_with,
                self._crowding_warn,
                self._crowding_severe,
            )

        return CrowdingDetection(
            strategy_id=strategy_id,
            max_correlation=max_corr,
            crowded_with=crowded_with,
            crowding_level=level,
            recommended_weight_scale=scale,
        )

    # ── OCP 契约实现 ──

    def set_context(self, context: AttributionContext) -> None:
        """注入归因上下文 (OCP attribute() 方法消费)。"""
        self._context = context

    def attribute(
        self,
        portfolio_id: str,
        period_start: str,
        period_end: str,
        idempotency_key: str,
    ) -> PerformanceAttributionReport:
        """OCP 契约实现——按期间归因分析。

        需先通过 set_context() 注入 AttributionContext (含 segments 等数据)。
        若未注入上下文, 抛出 AttributionDataIncompleteError。

        Args:
            portfolio_id: 组合 ID
            period_start: 期间起始 (ISO 字符串)
            period_end: 期间结束 (ISO 字符串)
            idempotency_key: 幂等键

        Returns:
            PerformanceAttributionReport (CTR-P1-009)

        Raises:
            AttributionDataIncompleteError: 上下文未注入或数据不完整
        """
        if self._context is None:
            raise AttributionDataIncompleteError("AttributionContext not set; call set_context() before attribute()")
        ctx = self._context
        return self.attribute_full(
            portfolio_id=portfolio_id,
            period_start=period_start,
            period_end=period_end,
            idempotency_key=idempotency_key,
            segments=ctx.segments,
            weights=ctx.weights,
            factor_exposures=ctx.factor_exposures,
            factor_returns=ctx.factor_returns,
            covariance=ctx.covariance,
            assets=ctx.assets,
            transaction_cost_drag=ctx.transaction_cost_drag,
        )

    def attribute_full(
        self,
        portfolio_id: str,
        period_start: str,
        period_end: str,
        idempotency_key: str,
        segments: list[SegmentReturn],
        weights: dict[str, float] | None = None,
        factor_exposures: dict[str, dict[str, float]] | None = None,
        factor_returns: dict[str, float] | None = None,
        covariance: np.ndarray | None = None,
        assets: list[str] | None = None,
        transaction_cost_drag: float = 0.0,
        now: datetime | None = None,
    ) -> PerformanceAttributionReport:
        """完整归因——Brinson + 因子 + 风险 (可选) + 交易成本拖累。

        total_return = excess_return (= allocation + selection + interaction)。
        交易成本拖累从 total_return 中扣除 (transaction_cost_drag ≥ 0)。

        Args:
            portfolio_id: 组合 ID
            period_start: 期间起始
            period_end: 期间结束
            idempotency_key: 幂等键
            segments: Brinson 分段数据
            weights: 标产权重 (因子归因用, 可选)
            factor_exposures: 因子暴露 (可选)
            factor_returns: 因子收益 (可选)
            covariance: 协方差矩阵 (风险归因用, 可选)
            assets: 资产代码列表 (可选)
            transaction_cost_drag: 交易成本拖累 (≥0, 默认 0)
            now: 时间戳

        Returns:
            PerformanceAttributionReport (CTR-P1-009)

        Raises:
            AttributionDataIncompleteError: segments 为空或 transaction_cost_drag < 0
        """
        if transaction_cost_drag < 0:
            raise AttributionDataIncompleteError(f"transaction_cost_drag must be ≥ 0, got {transaction_cost_drag}")

        # 1. Brinson 三因子
        brinson = self.brinson_attribute(segments, now=now)

        # 2. 因子归因 (可选)
        factor_contributions: dict[str, float] = {}
        if weights and factor_exposures and factor_returns:
            factor_contributions = self.factor_attribute(weights, factor_exposures, factor_returns)

        # 3. 风险归因 (可选, 失败则降级跳过)
        if covariance is not None:
            try:
                self.risk_attribute(covariance, weights or {}, assets=assets, now=now)
            except RiskDecompositionUnavailable as exc:
                logger.warning("risk attribution skipped: %s", exc)

        # 4. total_return = excess_return - transaction_cost_drag
        total_return = brinson.excess_return - transaction_cost_drag

        return PerformanceAttributionReport(
            portfolio_id=portfolio_id,
            period_start=period_start,
            period_end=period_end,
            total_return=total_return,
            allocation_effect=brinson.allocation_effect,
            selection_effect=brinson.selection_effect,
            interaction_effect=brinson.interaction_effect,
            transaction_cost_drag=transaction_cost_drag,
            factor_contributions=factor_contributions,
            idempotency_key=idempotency_key,
            schema_version="1.0",
        )

    # ── 多期归因 (链式链接) ──

    def attribute_multi_period(
        self,
        periods: list[BrinsonResult],
    ) -> BrinsonResult:
        """多期归因——链式链接 (linking) 单期 Brinson 结果。

        使用算术链接: 各期效应直接累加, total = Σ single_period。
        适用于短周期 (乘法链接需对数化, 此处简化为算术和)。

        Args:
            periods: 各单期 BrinsonResult

        Returns:
            汇总 BrinsonResult (各效应 = 各期之和)
        """
        if not periods:
            raise AttributionDataIncompleteError("periods list is empty")
        alloc = sum(p.allocation_effect for p in periods)
        select = sum(p.selection_effect for p in periods)
        interact = sum(p.interaction_effect for p in periods)
        excess = sum(p.excess_return for p in periods)
        port_ret = sum(p.portfolio_return for p in periods)
        bench_ret = sum(p.benchmark_return for p in periods)
        all_segs: list[SegmentReturn] = []
        for p in periods:
            all_segs.extend(p.segments)
        return BrinsonResult(
            allocation_effect=alloc,
            selection_effect=select,
            interaction_effect=interact,
            excess_return=excess,
            portfolio_return=port_ret,
            benchmark_return=bench_ret,
            segments=all_segs,
        )
