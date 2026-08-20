# [BLUEPRINT] MOD-RK-13 | docs/03_modules/_domain_risk/crowding_monitor/blueprint.md
# [MODULE] zephyr.risk.core.crowding_monitor
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.risk_manager_base
# [CONSUMERS] MOD-L04-001(DefaultRiskManagerOrchestrator,拥挤度评估) ; MOD-RK-07(ConcentrationMonitor,组合内集中度输入)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] overlap=Σmin/Σmax;consensus=|Σsign|/n;crowding=0.5×overlap+0.5×consensus;is_crowded=crowding>threshold;纯机制零参数
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidCrowdingInputError
# [TESTS] tests/risk/core/test_crowding_monitor.py
# [A_module] module_id=MOD-RK-13 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

D_RISK — Crowding Monitor (MOD-RK-13)

拥挤度监控器——检测跨参与者因子拥挤。衡量"全市场多少策略挤在
同一因子/同一批股票上"，与 concentration_monitor (MOD-RK-07)
的区分:
  - concentration_monitor: 组合内集中度 (HHI) — "我的组合多集中"
  - crowding_monitor: 跨策略拥挤度 — "多少人挤在同一因子上"

核心公式 (blueprint §3):
  持仓重叠度: overlap = Σ_min(w_s) / Σ_max(w_s)  (加权 Jaccard)
  方向一致性: consensus = |Σ sign(exp_i)| / n_strategies
  拥挤评分:   crowding = 0.5 × overlap + 0.5 × consensus
  判定:       is_crowded = crowding > threshold (默认 0.6)

日志埋点:
  - INFO: 评估完成（factor + overlap + consensus + crowding + is_crowded）
  - WARNING: 策略数不足跳过
  - DEBUG: 逐标的 min/max 权重 + 逐策略 sign

CTR 契约:
  消费者 — 策略持仓快照 (CTR-P1-019)
  生产者 — CrowdingMetrics (CTR-P1-020)

SSoT: depgraph MOD-RK-13 | blueprint.md §3 核心规则

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 多策略持仓快照 嵌套字典
#   fields: {strategy_id: {symbol: weight}}需≥2个策略(CTR-P1-019消费契约)
#   code: assess() strategy_positions L223
# - id: I2
#   name: 因子暴露 字典
#   fields: {strategy_id: exposure_value}可选; 未提供或<2个则consensus=0
#   code: assess() factor_exposures L224
# - id: I3
#   name: 拥挤度阈值 浮点数
#   fields: crowding_threshold默认0.6, >此值判定为拥挤
#   code: __init__() L122-124
# 层: 特征
# - id: F1
#   name_zh: 持仓重叠度
#   name_en: position_overlap
#   intro: 各标的逐策略取最小权重和比最大权重和, 衡量持仓撞车程度(加权Jaccard)
#   formula: overlap=Σ_s min(w_s)/Σ_s max(w_s) ∈[0,1]; 1=所有策略持仓完全相同
#   code: crowding_monitor.py L162-181
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F2
#   name_zh: 方向一致性
#   name_en: direction_consensus
#   intro: 各策略因子暴露符号加总, 看多少策略挤在同一方向
#   formula: consensus=|Σ sign(exp_i)|/n_strategies ∈[0,1]; 1=全同向 0=完全对冲
#   code: crowding_monitor.py L207-217
#   registry: factor_registry: 无FCT条目
#   is_break: true
# 层: 算法
# - id: A1
#   name_zh: ① 拥挤度综合评估
#   name_en: CrowdingMonitor.assess
#   intro: 重叠度和方向一致性各半加权算拥挤分, 超阈值判拥挤
#   desc: crowding=0.5×overlap+0.5×consensus; is_crowded=crowding>threshold; 策略数<2直接返回零分快照(WARNING日志)
#   inputs: I1 I2 I3 F1 F2
#   outputs: CrowdingMetrics快照
#   invariant: crowding=0.5×overlap+0.5×consensus
# - id: A2
#   name_zh: ② 风控检查结果转换
#   name_en: to_risk_check_result
#   intro: 拥挤度快照转RiskCheckResult供编排器聚合
#   desc: passed=!is_crowded; limit=threshold; actual=crowding_score; severity拥挤=HALT否则info
#   inputs: A1
#   outputs: RiskCheckResult
# 层: 输出
# - id: O1
#   name_zh: 拥挤度快照
#   name_en: CrowdingMetrics
#   intro: 单因子跨策略拥挤度评分快照(CTR-P1-020生产契约)
#   invariant: crowding_score∈[0,1]
#   downstream: DefaultRiskManagerOrchestrator MOD-L04-001(拥挤度评估); ConcentrationMonitor MOD-RK-07
# - id: O2
#   name_zh: 风控检查结果
#   name_en: RiskCheckResult
#   intro: 供风控编排器统一聚合的拥挤度检查结果
#   downstream: DefaultRiskManagerOrchestrator MOD-L04-001
# [/ALGO_FLOW]
#
# 边:
# I1 -.->|断点| F1
# I2 -.->|断点| F2
# F1 --> A1
# F2 --> A1
# I3 --> A1
# A1 --> O1
# A1 --> A2
# A2 --> O2
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Optional

from zephyr.risk.risk_manager_base import RiskCheckResult

_logger = logging.getLogger(__name__)

__all__ = [
    "CrowdingMetrics",
    "CrowdingMonitor",
    "InvalidCrowdingInputError",
]


#: 拥挤度阈值（默认 0.6，>此值判定为拥挤）
DEFAULT_CROWDING_THRESHOLD: float = 0.6


class InvalidCrowdingInputError(ValueError):
    """拥挤度监控输入数据无效。"""


# ── 数据模型 ──────────────────────────────────────────────────────────


@dataclass(frozen=True)
class CrowdingMetrics:
    """单因子跨策略拥挤度快照（不可变）。

    Attributes:
        factor_name: 因子名称
        crowding_score: 拥挤度评分 [0, 1]，越高越拥挤
        position_overlap: 持仓重叠度 [0, 1]，1=所有策略持仓完全相同
        direction_consensus: 方向一致性 [0, 1]，1=所有策略同方向
        n_strategies: 参与策略数
        is_crowded: 综合判定（crowding_score > threshold）
        threshold: 判定阈值
        timestamp: 评估时间（UTC）
        idempotency_key: 幂等键
    """

    factor_name: str
    crowding_score: float
    position_overlap: float
    direction_consensus: float
    n_strategies: int
    is_crowded: bool
    threshold: float
    timestamp: datetime
    idempotency_key: str


# ── 拥挤度监控器 ──────────────────────────────────────────────────────


class CrowdingMonitor:
    """拥挤度监控器——跨参与者因子拥挤度检测。

    纯机制零参数：使用标准数学公式（加权 Jaccard + 方向一致性），
    阈值为 C 类参数（有默认值）。

    Usage:
        mon = CrowdingMonitor()
        metrics = mon.assess(
            factor_name="momentum",
            strategy_positions={
                "strat_a": {"600000.SH": 0.3, "000001.SZ": 0.2},
                "strat_b": {"600000.SH": 0.25, "000001.SZ": 0.15},
            },
            factor_exposures={"strat_a": 0.8, "strat_b": 0.6},
        )
    """

    def __init__(
        self,
        crowding_threshold: float = DEFAULT_CROWDING_THRESHOLD,
    ):
        self._threshold = crowding_threshold

    # ── 持仓重叠度 ──

    def compute_position_overlap(
        self,
        strategy_positions: dict[str, dict[str, float]],
    ) -> float:
        """计算多策略持仓重叠度（加权 Jaccard 变体）。

        overlap = Σ_min(w_s) / Σ_max(w_s)
        - Σ_min: 每个标的在所有策略中的最小权重之和（交集）
        - Σ_max: 每个标的在所有策略中的最大权重之和（并集）

        Args:
            strategy_positions: {strategy_id: {symbol: weight}}

        Returns:
            重叠度 [0, 1]，1=所有策略持仓完全相同

        Raises:
            InvalidCrowdingInputError: 输入为空或策略数 < 2
        """
        if len(strategy_positions) < 2:
            raise InvalidCrowdingInputError(f"持仓重叠度计算需 ≥2 个策略，实际 {len(strategy_positions)}")

        # 收集所有标的
        all_symbols: set[str] = set()
        for positions in strategy_positions.values():
            all_symbols.update(positions.keys())

        if not all_symbols:
            return 0.0

        sum_min = 0.0
        sum_max = 0.0

        for symbol in all_symbols:
            weights = [strategy_positions[s].get(symbol, 0.0) for s in strategy_positions]
            sum_min += min(weights)
            sum_max += max(weights)
            _logger.debug(
                "Overlap symbol=%s min=%.4f max=%.4f",
                symbol,
                min(weights),
                max(weights),
            )

        if sum_max == 0:
            return 0.0

        overlap = sum_min / sum_max
        return float(overlap)

    # ── 方向一致性 ──

    def compute_direction_consensus(
        self,
        factor_exposures: dict[str, float],
    ) -> float:
        """计算多策略在因子方向上的一致性。

        consensus = |Σ sign(exposure_i)| / n_strategies
        - 1.0 = 所有策略同方向
        - 0.0 = 完全对冲

        Args:
            factor_exposures: {strategy_id: exposure_value}

        Returns:
            方向一致性 [0, 1]

        Raises:
            InvalidCrowdingInputError: 输入为空
        """
        if not factor_exposures:
            raise InvalidCrowdingInputError("因子暴露字典为空")

        n = len(factor_exposures)
        sign_sum = sum(self._sign(v) for v in factor_exposures.values())
        consensus = abs(sign_sum) / n

        _logger.debug(
            "Direction consensus: n=%d sign_sum=%d consensus=%.4f",
            n,
            sign_sum,
            consensus,
        )
        return float(consensus)

    # ── 综合评估 ──

    def assess(
        self,
        factor_name: str,
        strategy_positions: dict[str, dict[str, float]],
        factor_exposures: dict[str, float] | None = None,
    ) -> CrowdingMetrics:
        """综合评估单因子拥挤度。

        Args:
            factor_name: 因子名称
            strategy_positions: {strategy_id: {symbol: weight}}
            factor_exposures: {strategy_id: exposure}（可选，无则 consensus=0）

        Returns:
            CrowdingMetrics 拥挤度快照
        """
        n_strategies = len(strategy_positions)

        if n_strategies < 2:
            _logger.warning(
                "Crowding assessment skipped (insufficient strategies): factor=%s n_strategies=%d",
                factor_name,
                n_strategies,
            )
            return CrowdingMetrics(
                factor_name=factor_name,
                crowding_score=0.0,
                position_overlap=0.0,
                direction_consensus=0.0,
                n_strategies=n_strategies,
                is_crowded=False,
                threshold=self._threshold,
                timestamp=datetime.now(UTC),
                idempotency_key=f"crowd-{factor_name}-{uuid.uuid4().hex[:8]}",
            )

        overlap = self.compute_position_overlap(strategy_positions)

        if factor_exposures and len(factor_exposures) >= 2:
            consensus = self.compute_direction_consensus(factor_exposures)
        else:
            consensus = 0.0

        crowding = 0.5 * overlap + 0.5 * consensus
        is_crowded = crowding > self._threshold

        metrics = CrowdingMetrics(
            factor_name=factor_name,
            crowding_score=float(crowding),
            position_overlap=float(overlap),
            direction_consensus=float(consensus),
            n_strategies=n_strategies,
            is_crowded=is_crowded,
            threshold=self._threshold,
            timestamp=datetime.now(UTC),
            idempotency_key=f"crowd-{factor_name}-{uuid.uuid4().hex[:8]}",
        )

        _logger.info(
            "Crowding assessed: factor=%s overlap=%.4f consensus=%.4f crowding=%.4f is_crowded=%s n_strategies=%d",
            factor_name,
            overlap,
            consensus,
            crowding,
            is_crowded,
            n_strategies,
        )
        return metrics

    # ── 批量评估 ──

    def assess_batch(
        self,
        factors: dict[str, dict[str, dict[str, float]]],
        factor_exposures_map: dict[str, dict[str, float]] | None = None,
    ) -> list[CrowdingMetrics]:
        """批量评估多因子拥挤度。

        Args:
            factors: {factor_name: {strategy_id: {symbol: weight}}}
            factor_exposures_map: {factor_name: {strategy_id: exposure}}（可选）

        Returns:
            list[CrowdingMetrics]
        """
        exposures_map = factor_exposures_map or {}
        results: list[CrowdingMetrics] = []

        for factor_name, positions in factors.items():
            try:
                metrics = self.assess(
                    factor_name=factor_name,
                    strategy_positions=positions,
                    factor_exposures=exposures_map.get(factor_name),
                )
                results.append(metrics)
            except InvalidCrowdingInputError as exc:
                _logger.warning(
                    "Batch assess skipped: factor=%s error=%s",
                    factor_name,
                    exc,
                )

        crowded_count = sum(1 for m in results if m.is_crowded)
        _logger.info(
            "Batch crowding assess complete: total=%d crowded=%d",
            len(results),
            crowded_count,
        )
        return results

    # ── 风控检查结果转换 ──

    def to_risk_check_result(
        self,
        metrics: CrowdingMetrics,
    ) -> RiskCheckResult:
        """将 CrowdingMetrics 转换为 RiskCheckResult（供编排器聚合）。

        Args:
            metrics: 拥挤度指标

        Returns:
            RiskCheckResult（passed=!is_crowded, severity=HALT/WARNING）
        """
        return RiskCheckResult(
            check_id=f"crowding-{metrics.factor_name}",
            rule_name="crowding_monitor",
            passed=not metrics.is_crowded,
            limit_value=metrics.threshold,
            actual_value=metrics.crowding_score,
            message=(
                f"crowding={metrics.crowding_score:.4f} "
                f"overlap={metrics.position_overlap:.4f} "
                f"consensus={metrics.direction_consensus:.4f} "
                f"factor={metrics.factor_name}"
            ),
            severity="HALT" if metrics.is_crowded else "info",
        )

    # ── 内部工具 ──

    @staticmethod
    def _sign(value: float) -> int:
        """符号函数：正=1, 负=-1, 零=0。"""
        if value > 0:
            return 1
        elif value < 0:
            return -1
        return 0
