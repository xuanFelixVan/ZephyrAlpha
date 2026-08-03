# [BLUEPRINT] MOD-PF-003 | docs/03_modules/_domain_portfolio_core/rebalance_scheduler/blueprint.md
# [MODULE] zephyr.pf_core.core.rebalance_scheduler
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.pf_core.core.portfolio_optimizer(MOD-PF-002); zephyr.shared.contracts.target_portfolio(CTR-007); zephyr.shared.contracts.risk_limits(CTR-003); zephyr.shared.foundation.errors
# [CONSUMERS] D_POSITION(持仓级执行 POS-004 复用成本判定) ; MOD-PF-002(触发重优化)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 四触发源任一满足即triggered;benefit>2×cost才执行;压力市场⑦⑧⑨成本×1.5;decision单调
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidRebalanceInputError
# [TESTS] tests/pf_core/test_rebalance_scheduler.py
# [A_module] module_id=MOD-PF-003 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Rebalance Scheduler — 再平衡调度器 (MOD-PF-003)

D-PF-CORE §1.2 L2 组合构建核心模块。组合级再平衡调度: 决定是否重跑组合优化器 (PC-02)。
与 POS-004 RebalanceEngine 的边界: PC-03=组合级调度(决定是否重优化), POS-004=持仓级执行
(复用其成本收益判定逻辑)。本模块复用 POS-004 的成本公式 (cost_rate × stress_multiplier)。

四触发源 (任一满足即 triggered):
    1. drift_threshold: 组合总漂移 > 2% 或单标的漂移 > 3%
    2. calendar: 周五 (weekday==4) 定期再平衡
    3. event: 外部事件 (信号变更/策略切换等)
    4. risk_breach: 风控告警 (E-RK-01 VaR 突破 / E-RK-03 回撤熔断)

成本感知再平衡:
    - benefit = 当前组合漂移 (再平衡可消除的漂移)
    - cost = 换手率 × cost_rate × (压力市场 ⑦⑧⑨ 时 ×1.5)
    - 执行条件: benefit > 2 × cost (improvement_ratio)

属 A 类纯基础设施 (触发判定+成本公式+调度决策), 阈值为 C 类可调参数。
依据: D:\\临时工作区\\依赖图\\05-D-PF-CORE-组合核心域.md §1.2 PC-03, §10.1 组合降级
SSoT: depgraph MOD-PF-003
Version: 0.1.0
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable

from zephyr.pf_core.core.portfolio_optimizer import PortfolioOptimizer
from zephyr.shared.contracts.risk_limits import RiskLimits
from zephyr.shared.contracts.target_portfolio import TargetPortfolio
from zephyr.shared.foundation.errors import ZephyrBaseError

if TYPE_CHECKING:
    import numpy as np

__all__ = [
    "RebalanceTriggerSource",
    "RebalanceDecision",
    "RebalanceConfig",
    "RebalanceEvaluation",
    "RebalanceScheduler",
    "InvalidRebalanceInputError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class RebalanceTriggerSource(str, Enum):
    """再平衡触发源 (优先级: risk_breach > drift > event > calendar)。"""

    RISK_BREACH = "risk_breach"        # 风控告警 (E-RK-01/03, 最高优先级)
    DRIFT_THRESHOLD = "drift_threshold"  # 漂移阈值
    EVENT = "event"                    # 外部事件
    CALENDAR = "calendar"              # 日历 (周五)
    NONE = "none"                      # 未触发


class RebalanceDecision(str, Enum):
    """再平衡决策结果。"""

    REBALANCE = "rebalance"            # 触发+成本收益通过 → 执行再平衡
    SKIP_NO_TRIGGER = "skip_no_trigger"  # 无触发源
    SKIP_COST_BENEFIT = "skip_cost_benefit"  # 触发但成本收益不通过


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidRebalanceInputError(ZephyrBaseError):
    """再平衡输入数据非法 (如权重负值/标的集合不一致)。"""

    error_code = "ZA-PF-0031"


# ──────────────────────────────────────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class RebalanceConfig:
    """再平衡调度配置 (设计真源 §1.2 PC-03)。

    Attributes:
        portfolio_drift_threshold: 组合总漂移阈值, 默认 0.02 (±2%)
        single_asset_drift_threshold: 单标的漂移阈值, 默认 0.03 (±3%)
        calendar_weekday: 日历触发星期 (0=Mon...4=Fri), 默认 4 (周五)
        improvement_ratio: 收益改善比阈值, 默认 2.0 (benefit>2×cost)
        stress_market_states: 压力市场状态集合, 默认 {7,8,9}
        stress_cost_multiplier: 压力状态成本系数, 默认 1.5
        cost_rate: 单边交易成本率, 默认 0.001 (0.1%)
    """

    portfolio_drift_threshold: float = 0.02
    single_asset_drift_threshold: float = 0.03
    calendar_weekday: int = 4
    improvement_ratio: float = 2.0
    stress_market_states: frozenset[int] = frozenset({7, 8, 9})
    stress_cost_multiplier: float = 1.5
    cost_rate: float = 0.001

    def __post_init__(self) -> None:
        if self.portfolio_drift_threshold <= 0:
            raise InvalidRebalanceInputError("portfolio_drift_threshold must be >0")
        if self.single_asset_drift_threshold <= 0:
            raise InvalidRebalanceInputError("single_asset_drift_threshold must be >0")
        if not 0 <= self.calendar_weekday <= 6:
            raise InvalidRebalanceInputError("calendar_weekday must be in [0,6]")
        if self.improvement_ratio <= 0:
            raise InvalidRebalanceInputError("improvement_ratio must be >0")
        if self.stress_cost_multiplier < 1.0:
            raise InvalidRebalanceInputError("stress_cost_multiplier must be >=1.0")
        if self.cost_rate <= 0:
            raise InvalidRebalanceInputError("cost_rate must be >0")


# ──────────────────────────────────────────────────────────────────────────────
# 评估结果
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class RebalanceEvaluation:
    """再平衡评估结果 (PC-03 → 调度决策)。

    Attributes:
        triggered: 是否被四触发源触发
        trigger_source: 触发源 (NONE=未触发)
        decision: 决策 (rebalance/skip_no_trigger/skip_cost_benefit)
        cost_benefit_passed: 成本收益是否通过
        portfolio_drift: 组合总漂移 (Σ|Δw|/2)
        max_single_drift: 单标的最大漂移
        estimated_cost: 估计交易成本 (含压力系数)
        estimated_benefit: 估计收益改善 (= portfolio_drift)
        new_target_portfolio: 重优化后的目标组合 (未执行则 None)
        timestamp: 评估时间
        idempotency_key: 幂等键
    """

    triggered: bool
    trigger_source: RebalanceTriggerSource
    decision: RebalanceDecision
    cost_benefit_passed: bool
    portfolio_drift: float
    max_single_drift: float
    estimated_cost: float
    estimated_benefit: float
    new_target_portfolio: TargetPortfolio | None
    timestamp: datetime
    idempotency_key: str

    @property
    def should_rebalance(self) -> bool:
        """是否应执行再平衡 (decision==REBALANCE)。"""
        return self.decision == RebalanceDecision.REBALANCE

    def to_dict(self) -> dict[str, Any]:
        return {
            "triggered": self.triggered,
            "trigger_source": self.trigger_source.value,
            "decision": self.decision.value,
            "cost_benefit_passed": self.cost_benefit_passed,
            "portfolio_drift": self.portfolio_drift,
            "max_single_drift": self.max_single_drift,
            "estimated_cost": self.estimated_cost,
            "estimated_benefit": self.estimated_benefit,
            "has_new_target": self.new_target_portfolio is not None,
            "idempotency_key": self.idempotency_key,
        }


# ──────────────────────────────────────────────────────────────────────────────
# 再平衡调度器
# ──────────────────────────────────────────────────────────────────────────────


class RebalanceScheduler:
    """再平衡调度器——四触发源 + 成本感知 → 决定是否重跑组合优化器。

    用法:
        scheduler = RebalanceScheduler(optimizer=optimizer)
        eval_result = scheduler.evaluate(
            current_weights={"A": 0.45, "B": 0.55},
            target_weights={"A": 0.50, "B": 0.50},
            market_state=3,
            now=datetime(2026, 8, 7, tzinfo=timezone.utc),  # 周五
        )
        if eval_result.should_rebalance:
            new_tp = eval_result.new_target_portfolio  # 已重优化

    Args:
        config: 调度配置
        optimizer: 组合优化器 (PC-02, 注入; 为 None 时仅评估不重优化)
        clock: 可选时间源 (测试注入)
    """

    def __init__(
        self,
        config: RebalanceConfig | None = None,
        optimizer: PortfolioOptimizer | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._config = config or RebalanceConfig()
        self._optimizer = optimizer
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    @property
    def config(self) -> RebalanceConfig:
        return self._config

    # ── 公开 API ──

    def evaluate(
        self,
        current_weights: dict[str, float],
        target_weights: dict[str, float],
        market_state: int = 0,
        now: datetime | None = None,
        risk_alert: bool = False,
        event_trigger: bool = False,
        covariance: np.ndarray | None = None,
        risk_limits: RiskLimits | None = None,
        strategy_id: str = "",
        portfolio_id: str = "",
    ) -> RebalanceEvaluation:
        """评估是否需要再平衡 (四触发源 + 成本收益)。

        Args:
            current_weights: 当前持仓权重
            target_weights: 目标权重 (上次优化产出)
            market_state: 市场状态码 (7/8/9 为压力状态)
            now: 评估时间 (日历触发用)
            risk_alert: 风控告警标志 (E-RK-01/03)
            event_trigger: 外部事件触发标志
            covariance: 协方差矩阵 (重优化用, 可选)
            risk_limits: 风险限额 (重优化用, 可选)
            strategy_id: 策略 ID (重优化用)
            portfolio_id: 组合 ID (重优化用)

        Returns:
            RebalanceEvaluation

        Raises:
            InvalidRebalanceInputError: 权重非法
        """
        now = now or self._clock()
        self._validate_weights(current_weights, target_weights)

        # 1. 计算漂移
        portfolio_drift, max_single_drift = self._compute_drift(
            current_weights, target_weights
        )

        # 2. 触发源评估 (优先级: risk > drift > event > calendar)
        trigger_source = self._check_triggers(
            portfolio_drift, max_single_drift, now, risk_alert, event_trigger
        )
        triggered = trigger_source != RebalanceTriggerSource.NONE

        # 3. 成本收益分析
        cost, benefit, cost_benefit_passed = self._compute_cost_benefit(
            current_weights, target_weights, portfolio_drift, market_state
        )

        # 4. 决策
        if not triggered:
            decision = RebalanceDecision.SKIP_NO_TRIGGER
        elif not cost_benefit_passed:
            decision = RebalanceDecision.SKIP_COST_BENEFIT
        else:
            decision = RebalanceDecision.REBALANCE

        # 5. 重优化 (仅当 decision==REBALANCE 且 optimizer+输入齐备)
        new_tp: TargetPortfolio | None = None
        if (
            decision == RebalanceDecision.REBALANCE
            and self._optimizer is not None
            and covariance is not None
            and risk_limits is not None
        ):
            new_tp = self._reoptimize(
                target_weights, covariance, risk_limits,
                list(target_weights.keys()), current_weights,
                strategy_id, portfolio_id, trigger_source, now,
            )

        return RebalanceEvaluation(
            triggered=triggered,
            trigger_source=trigger_source,
            decision=decision,
            cost_benefit_passed=cost_benefit_passed,
            portfolio_drift=portfolio_drift,
            max_single_drift=max_single_drift,
            estimated_cost=cost,
            estimated_benefit=benefit,
            new_target_portfolio=new_tp,
            timestamp=now,
            idempotency_key=str(uuid.uuid4()),
        )

    # ── 内部: 触发源 ──

    def _check_triggers(
        self,
        portfolio_drift: float,
        max_single_drift: float,
        now: datetime,
        risk_alert: bool,
        event_trigger: bool,
    ) -> RebalanceTriggerSource:
        """评估四触发源, 返回最高优先级触发源。"""
        cfg = self._config
        # 优先级: risk_breach > drift > event > calendar
        if risk_alert:
            return RebalanceTriggerSource.RISK_BREACH
        if (
            portfolio_drift > cfg.portfolio_drift_threshold
            or max_single_drift > cfg.single_asset_drift_threshold
        ):
            return RebalanceTriggerSource.DRIFT_THRESHOLD
        if event_trigger:
            return RebalanceTriggerSource.EVENT
        if now.weekday() == cfg.calendar_weekday:
            return RebalanceTriggerSource.CALENDAR
        return RebalanceTriggerSource.NONE

    # ── 内部: 成本收益 ──

    def _compute_cost_benefit(
        self,
        current_weights: dict[str, float],
        target_weights: dict[str, float],
        portfolio_drift: float,
        market_state: int,
    ) -> tuple[float, float, bool]:
        """计算成本收益 (复用 POS-004 公式)。

        cost = 换手率 × cost_rate × (压力市场 ×stress_multiplier)
        benefit = portfolio_drift (再平衡可消除的漂移)
        passed = benefit > improvement_ratio × cost
        """
        cfg = self._config
        # 换手率 = Σ|Δw| (双边)
        turnover = sum(
            abs(current_weights.get(s, 0.0) - target_weights.get(s, 0.0))
            for s in set(current_weights) | set(target_weights)
        )
        # 压力市场成本系数
        multiplier = (
            cfg.stress_cost_multiplier
            if market_state in cfg.stress_market_states
            else 1.0
        )
        cost = turnover * cfg.cost_rate * multiplier
        benefit = portfolio_drift
        passed = benefit > cfg.improvement_ratio * cost
        return cost, benefit, passed

    # ── 内部: 重优化 ──

    def _reoptimize(
        self,
        target_weights: dict[str, float],
        covariance: np.ndarray,
        risk_limits: RiskLimits,
        assets: list[str],
        current_weights: dict[str, float],
        strategy_id: str,
        portfolio_id: str,
        trigger_source: RebalanceTriggerSource,
        now: datetime,
    ) -> TargetPortfolio | None:
        """调用 PC-02 组合优化器重新优化, 返回新 TargetPortfolio。"""
        try:
            import numpy as np  # 延迟导入
            result = self._optimizer.optimize(  # type: ignore[union-attr]
                candidate_weights=target_weights,
                risk_limits=risk_limits,
                covariance=np.asarray(covariance, dtype=float),
                assets=assets,
                current_weights=current_weights,
                strategy_id=strategy_id,
                portfolio_id=portfolio_id,
                rebalance_reason=trigger_source.value,
                now=now,
            )
            return result.target_portfolio
        except Exception as exc:  # noqa: BLE001 — 重优化失败降级为不执行
            logger.warning("RebalanceScheduler: reoptimize failed (%s), skip", exc)
            return None

    # ── 内部: 工具 ──

    @staticmethod
    def _compute_drift(
        current: dict[str, float], target: dict[str, float]
    ) -> tuple[float, float]:
        """计算组合漂移 (portfolio_drift, max_single_drift)。

        portfolio_drift = Σ|Δw| / 2 (归一化漂移)
        max_single_drift = max(|Δw_i|)
        """
        symbols = set(current) | set(target)
        total_delta = 0.0
        max_delta = 0.0
        for s in symbols:
            delta = abs(current.get(s, 0.0) - target.get(s, 0.0))
            total_delta += delta
            if delta > max_delta:
                max_delta = delta
        return total_delta / 2.0, max_delta

    @staticmethod
    def _validate_weights(
        current: dict[str, float], target: dict[str, float]
    ) -> None:
        if not current and not target:
            raise InvalidRebalanceInputError("weights cannot both be empty")
        for name, w in current.items():
            if w < 0:
                raise InvalidRebalanceInputError(
                    f"current weight for {name} must be non-negative, got {w}"
                )
        for name, w in target.items():
            if w < 0:
                raise InvalidRebalanceInputError(
                    f"target weight for {name} must be non-negative, got {w}"
                )
