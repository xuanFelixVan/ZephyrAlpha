# [BLUEPRINT] MOD-POS-010 | docs/03_modules/_domain_position/position_limit_enforcer/blueprint.md
# [MODULE] zephyr.position.core.position_limit_enforcer
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-POS-001(仓位决策) ; D-RISK ; D-GOVERNANCE(审计)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬边界不可绕过;整体裁决=max(违规)按严重度;KillSwitch激活短路P0;单票/行业约束对OPEN/ADD生效
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidPositionPlanError
# [TESTS] tests/position/test_position_limit_enforcer.py
# [A_module] module_id=MOD-POS-010 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Position Limit Enforcer — 限仓执行器 (MOD-POS-010)

仓位方案硬约束检查器: 单票/行业/总仓位/亏损加仓/压力测试, 产出 5 级否决裁决+违规告警。
硬边界不可绕过。

5 级否决 (D-POSITION §1.3 POS-10):
    P0 Kill Switch > P1 强制减仓 > P2 否决新开仓 > P3 否决单笔 > P4 建议性告警 > PASS

约束:
    - 单票 ≤ 5% NAV
    - 行业 ≤ 30% (绝对) / 基准 ±10%
    - 总仓位 ≤ 上限
    - 亏损标的加仓: 持仓亏损 > X% → Hard Block
    - 压力测试: 情景最大亏损 > 15% → 收紧上限

属A类基础设施(约束检查+阈值判定+5级裁决, 逻辑明确), 阈值为C类可调参数。
依据: D:\\临时工作区\\依赖图\\07-D-POSITION-仓位管理域.md §1.3 POS-10
SSoT: depgraph MOD-POS-010
Version: 0.1.0
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Callable

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "PositionAction",
    "LimitVerdict",
    "PositionLimitConfig",
    "PositionEntry",
    "PositionPlan",
    "LimitViolation",
    "LimitCheckResult",
    "PositionLimitEnforcer",
    "InvalidPositionPlanError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class PositionAction(str, Enum):
    """持仓动作。"""

    OPEN = "OPEN"      # 新开仓
    ADD = "ADD"        # 加仓
    HOLD = "HOLD"      # 持有
    REDUCE = "REDUCE"  # 减仓


class LimitVerdict(str, Enum):
    """限仓裁决级别 (严重度递增)。"""

    PASS = "PASS"
    P4_WARN = "P4_WARN"                  # 建议性告警
    P3_BLOCK_TRADE = "P3_BLOCK_TRADE"    # 否决单笔 (Hard Block)
    P2_BLOCK_NEW = "P2_BLOCK_NEW"        # 否决新开仓
    P1_FORCE_REDUCE = "P1_FORCE_REDUCE"  # 强制减仓
    P0_KILL_SWITCH = "P0_KILL_SWITCH"    # Kill Switch 全否决

    @property
    def severity(self) -> int:
        return {
            "PASS": 0, "P4_WARN": 1, "P3_BLOCK_TRADE": 2,
            "P2_BLOCK_NEW": 3, "P1_FORCE_REDUCE": 4, "P0_KILL_SWITCH": 5,
        }[self.value]

    @classmethod
    def worst(cls, verdicts: list[LimitVerdict]) -> LimitVerdict:
        if not verdicts:
            return cls.PASS
        return max(verdicts, key=lambda v: v.severity)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidPositionPlanError(ZephyrBaseError):
    """仓位方案非法(如权重越界、动作非法)。"""

    error_code = "ZA-POS-0010"


# ──────────────────────────────────────────────────────────────────────────────
# 配置 (C 类可调参数)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class PositionLimitConfig:
    """限仓约束配置 (设计真源 §1.3 POS-10)。"""

    single_instrument_cap: float = 0.05        # 单票 ≤ 5% NAV
    sector_absolute_cap: float = 0.30          # 行业 ≤ 30% (绝对)
    sector_baseline_deviation: float = 0.10    # 行业 基准 ±10%
    total_position_cap: float = 1.0            # 总仓位上限
    loss_add_block_threshold: float = 0.08     # 持仓亏损 > 8% → 禁止加仓
    stress_loss_threshold: float = 0.15        # 压力测试: 亏损 > 15% NAV

    def __post_init__(self) -> None:
        for name, val in (
            ("single_instrument_cap", self.single_instrument_cap),
            ("sector_absolute_cap", self.sector_absolute_cap),
            ("sector_baseline_deviation", self.sector_baseline_deviation),
            ("total_position_cap", self.total_position_cap),
            ("loss_add_block_threshold", self.loss_add_block_threshold),
            ("stress_loss_threshold", self.stress_loss_threshold),
        ):
            if not 0 < val <= 1:
                raise InvalidPositionPlanError(f"{name} must be in (0,1], got {val}")


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class PositionEntry:
    """单只标的持仓方案条目。"""

    symbol: str
    weight: float                # 占 NAV 权重
    sector: str
    action: PositionAction = PositionAction.HOLD
    existing_pnl_pct: float = 0.0  # 现有持仓未实现盈亏% (负=亏损)


@dataclass(frozen=True)
class PositionPlan:
    """仓位方案。"""

    positions: list[PositionEntry]
    sector_baselines: dict[str, float] = field(default_factory=dict)

    @property
    def total_position(self) -> float:
        return sum(p.weight for p in self.positions)


@dataclass(frozen=True)
class LimitViolation:
    """单条限仓违规。"""

    rule: str
    dimension: str
    value: float
    threshold: float
    verdict: LimitVerdict
    symbol: str | None = None
    sector: str | None = None


@dataclass(frozen=True)
class LimitCheckResult:
    """限仓检查结果。"""

    overall_verdict: LimitVerdict
    violations: list[LimitViolation] = field(default_factory=list)
    kill_switch_active: bool = False
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def blocked(self) -> bool:
        """是否被强制否决 (P0~P3)。"""
        return self.overall_verdict.severity >= LimitVerdict.P3_BLOCK_TRADE.severity

    @property
    def force_reduce(self) -> bool:
        """是否需强制减仓 (P0/P1)。"""
        return self.overall_verdict.severity >= LimitVerdict.P1_FORCE_REDUCE.severity


# ──────────────────────────────────────────────────────────────────────────────
# 限仓执行器
# ──────────────────────────────────────────────────────────────────────────────


class PositionLimitEnforcer:
    """限仓执行器——硬约束检查+5级否决裁决。

    用法:
        enforcer = PositionLimitEnforcer()
        plan = PositionPlan(positions=[
            PositionEntry("000001.SZ", 0.06, "银行", PositionAction.OPEN),  # 超 5%
        ])
        result = enforcer.check(plan)
        if result.blocked:
            # 否决新开仓 (P2)

    Args:
        config: 限仓约束配置
        clock: 可选时间源 (测试注入)
    """

    def __init__(
        self,
        config: PositionLimitConfig | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._config = config or PositionLimitConfig()
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    @property
    def config(self) -> PositionLimitConfig:
        return self._config

    def check(
        self,
        plan: PositionPlan,
        kill_switch_active: bool = False,
        stress_loss: float = 0.0,
        now: datetime | None = None,
    ) -> LimitCheckResult:
        """检查仓位方案所有限仓约束。

        Args:
            plan: 仓位方案
            kill_switch_active: Kill Switch 是否激活
            stress_loss: 压力测试情景最大亏损 (占 NAV 比例, 正数)
            now: 时间戳

        Returns:
            LimitCheckResult (整体裁决=最严重违规, 含全部违规明细)
        """
        now = now or self._clock()
        self._validate_plan(plan)
        cfg = self._config
        violations: list[LimitViolation] = []

        # P0: Kill Switch 短路 (硬边界, 不可绕过)
        if kill_switch_active:
            violations.append(LimitViolation(
                rule="kill_switch_active", dimension="kill_switch",
                value=1.0, threshold=0.0, verdict=LimitVerdict.P0_KILL_SWITCH,
            ))
            # Kill Switch 短路: 直接返回 P0 (不再检查其他)
            return LimitCheckResult(
                overall_verdict=LimitVerdict.P0_KILL_SWITCH,
                violations=violations,
                kill_switch_active=True,
                timestamp=now,
            )

        # P1: 总仓位 > 上限 → 强制减仓
        total = plan.total_position
        if total > cfg.total_position_cap:
            violations.append(LimitViolation(
                rule="total_position_exceeded", dimension="total_position",
                value=total, threshold=cfg.total_position_cap,
                verdict=LimitVerdict.P1_FORCE_REDUCE,
            ))

        # P2: 单票 > 上限 (对 OPEN/ADD 动作)
        for p in plan.positions:
            if p.action in (PositionAction.OPEN, PositionAction.ADD) and p.weight > cfg.single_instrument_cap:
                violations.append(LimitViolation(
                    rule="single_instrument_exceeded", dimension="single_instrument",
                    value=p.weight, threshold=cfg.single_instrument_cap,
                    verdict=LimitVerdict.P2_BLOCK_NEW, symbol=p.symbol,
                ))

        # P2: 行业集中度 (绝对上限 + 基准偏离)
        sector_weights: dict[str, float] = defaultdict(float)
        for p in plan.positions:
            sector_weights[p.sector] += p.weight
        for sector, w in sector_weights.items():
            if w > cfg.sector_absolute_cap:
                violations.append(LimitViolation(
                    rule="sector_absolute_exceeded", dimension="sector_absolute",
                    value=w, threshold=cfg.sector_absolute_cap,
                    verdict=LimitVerdict.P2_BLOCK_NEW, sector=sector,
                ))
            baseline = plan.sector_baselines.get(sector, 0.0)
            if abs(w - baseline) > cfg.sector_baseline_deviation:
                violations.append(LimitViolation(
                    rule="sector_baseline_deviation", dimension="sector_baseline",
                    value=abs(w - baseline), threshold=cfg.sector_baseline_deviation,
                    verdict=LimitVerdict.P2_BLOCK_NEW, sector=sector,
                ))

        # P3: 亏损标的加仓 Hard Block (ADD 动作 + 现有亏损 > 阈值)
        for p in plan.positions:
            if p.action is PositionAction.ADD and p.existing_pnl_pct < -cfg.loss_add_block_threshold:
                violations.append(LimitViolation(
                    rule="loss_add_block", dimension="loss_add",
                    value=abs(p.existing_pnl_pct), threshold=cfg.loss_add_block_threshold,
                    verdict=LimitVerdict.P3_BLOCK_TRADE, symbol=p.symbol,
                ))

        # P4: 压力测试 (情景最大亏损 > 阈值 → 建议性告警/收紧上限)
        if stress_loss > cfg.stress_loss_threshold:
            violations.append(LimitViolation(
                rule="stress_loss_exceeded", dimension="stress_loss",
                value=stress_loss, threshold=cfg.stress_loss_threshold,
                verdict=LimitVerdict.P4_WARN,
            ))

        overall = LimitVerdict.worst([v.verdict for v in violations])
        return LimitCheckResult(
            overall_verdict=overall,
            violations=violations,
            kill_switch_active=False,
            timestamp=now,
        )

    # ── 内部 ──

    @staticmethod
    def _validate_plan(plan: PositionPlan) -> None:
        for p in plan.positions:
            if not 0 <= p.weight <= 1:
                raise InvalidPositionPlanError(
                    f"weight for {p.symbol} must be in [0,1], got {p.weight}"
                )
            if not isinstance(p.action, PositionAction):
                raise InvalidPositionPlanError(f"invalid action for {p.symbol}: {p.action}")
