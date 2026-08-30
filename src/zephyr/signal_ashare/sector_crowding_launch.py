# [BLUEPRINT] MOD-SIG-119 | docs/03_modules/_domain_signal/sector_crowding_launch/blueprint.md
# [MODULE] zephyr.signal_ashare.sector_crowding_launch
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 无（协议核心纯内存；历史分位序列/时钟/告警回调全注入，不 import zephyr 内部件）
# [CONSUMERS] 运行时装配批（统一注入点装配：板块拥挤度预警层 / 启动条件择时消费方）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 拥挤度词表闭合(normal|elevated|overheated)；三分量分位∈[0,1]、合成=权重归一加权均值、>90%分位过热；过热预警=过热∧动量衰减>30%（告警回调注入不阻断）；启动状态机 IDLE→RS_BREAKOUT→CONFIRMING→LAUNCHED、RS失守归IDLE、资金非正回退RS_BREAKOUT streak清零、LAUNCHED保持至RS失守；同输入必同输出（确定性）
# [MODIFY-GUARD] docs/03_modules/_domain_signal/sector_crowding_launch/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] SectorCrowdingError(占位 ZA-SIG-UNREGISTERED-SECTOR-CROWDING)——空历史/非有限读数/分位越界/非法配置/非法状态机输入时抛
# [TESTS] tests/signal_ashare/test_sector_crowding_launch.py
# [A_module] module_id=MOD-SIG-119 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
SectorCrowdingLauncher — 板块拥挤度与启动条件（MOD-SIG-119）。

B10-01384（AUD-DRAFT-001-DIGEST P2 波 P2-W05，CAND-TESTB-039，A1 模块40）：
板块拥挤度（换手率 + 融资余额占比 + 持仓相关性三分量，>90% 分位过热）
+ 过热预警（拥挤 >90% 分位 + 动量衰减 >30% → 回撤概率高）
+ 启动条件（RS 突破 + 资金转正 3 日确认状态机）。

纯内存/DI 设计：历史分位序列/时钟/告警回调全注入；不触网、不触盘、
无 subprocess。同输入必同输出。非法输入 Fail-Closed 抛 SectorCrowdingError。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: confirm_days 参数
#   fields: 参数 confirm_days（无注解）
#   code: sector_crowding_launch.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① LaunchStateMachine
#   name_en: LaunchStateMachine
#   intro: 启动条件状态机：RS突破 + 资金转正 N 日确认。
#   desc: 启动条件状态机：RS突破 + 资金转正 N 日确认。 迁移规则（确定性）： - rs_breakout=False → IDLE（streak 清零）； - 已 LAUNCHED…；公共方法（定义序）: phase,…
#   inputs: confirm_days
#   outputs: 返回值
# - id: A2
#   name_zh: ② SectorCrowdingLauncher
#   name_en: SectorCrowdingLauncher
#   intro: 板块拥挤度评估 + 过热预警 + 启动状态机门面。
#   desc: 板块拥挤度评估 + 过热预警 + 启动状态机门面。；公共方法（定义序）: percentile_of, assess_crowding, step_launch, launch_phase；源码 L232-L327
#   inputs: config clock alert_sink
#   outputs: 返回值
#   （注：A2 之后另有 7 个公共定义未列入（含 7 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（9 定义）
#   name_en: public defs
#   intro: LaunchStateMachine, SectorCrowdingLauncher
#   downstream: 运行时装配批（统一注入点装配：板块拥挤度预警层 / 启动条件择时消费方）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import datetime
import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "CrowdingAssessment",
    "CrowdingComponents",
    "CrowdingConfig",
    "CrowdingLevel",
    "LaunchPhase",
    "LaunchStateMachine",
    "OverheatWarning",
    "SectorCrowdingError",
    "SectorCrowdingLauncher",
]


class SectorCrowdingError(Exception):
    """板块拥挤度/启动条件输入非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SIG-UNREGISTERED-SECTOR-CROWDING。
    """


class CrowdingLevel(str, Enum):
    """拥挤度档位（词表闭合）。"""

    NORMAL = "normal"
    ELEVATED = "elevated"
    OVERHEATED = "overheated"


class LaunchPhase(str, Enum):
    """启动状态机相位（词表闭合）。"""

    IDLE = "idle"
    RS_BREAKOUT = "rs_breakout"
    CONFIRMING = "confirming"
    LAUNCHED = "launched"


def _check_finite(name: str, v: float) -> None:
    if isinstance(v, bool) or not math.isfinite(v):
        raise SectorCrowdingError(f"{name} 非有限数: {v!r}")


@dataclass(frozen=True)
class CrowdingComponents:
    """拥挤度三分量分位读数（frozen；各 ∈ [0,1]）。"""

    turnover_pct: float
    margin_pct: float
    correlation_pct: float

    def __post_init__(self) -> None:
        for name in ("turnover_pct", "margin_pct", "correlation_pct"):
            v = getattr(self, name)
            _check_finite(name, v)
            if not (0.0 <= v <= 1.0):
                raise SectorCrowdingError(f"{name} 须在 [0,1]: {v}")


@dataclass(frozen=True)
class CrowdingConfig:
    """拥挤度与启动配置（frozen）。"""

    overheat_percentile: float = 0.90
    elevated_percentile: float = 0.70
    momentum_decay_threshold: float = 0.30
    confirm_days: int = 3
    weights: tuple[float, float, float] = (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0)

    def __post_init__(self) -> None:
        for name in ("overheat_percentile", "elevated_percentile", "momentum_decay_threshold"):
            _check_finite(name, getattr(self, name))
        if not (0.0 < self.elevated_percentile < self.overheat_percentile <= 1.0):
            raise SectorCrowdingError(
                f"分位阈值须 0<elevated<overheat≤1: {self.elevated_percentile}/{self.overheat_percentile}"
            )
        if not (0.0 < self.momentum_decay_threshold < 1.0):
            raise SectorCrowdingError(f"momentum_decay_threshold 须在 (0,1): {self.momentum_decay_threshold}")
        if isinstance(self.confirm_days, bool) or self.confirm_days < 1:
            raise SectorCrowdingError(f"confirm_days 必须 ≥1: {self.confirm_days!r}")
        if len(self.weights) != 3:
            raise SectorCrowdingError(f"weights 长度须为 3: {len(self.weights)}")
        for w in self.weights:
            _check_finite("weight", w)
            if w < 0:
                raise SectorCrowdingError(f"weight 不可为负: {w}")
        if sum(self.weights) <= 0:
            raise SectorCrowdingError("weights 全零非法")


@dataclass(frozen=True)
class OverheatWarning:
    """过热预警载荷（frozen）。"""

    composite: float
    momentum_decay: float
    reason: str
    raised_at: datetime.datetime


@dataclass(frozen=True)
class CrowdingAssessment:
    """拥挤度评估（frozen）。"""

    components: CrowdingComponents
    composite: float
    level: CrowdingLevel
    overheated: bool
    warning: OverheatWarning | None
    generated_at: datetime.datetime


class LaunchStateMachine:
    """启动条件状态机：RS突破 + 资金转正 N 日确认。

    迁移规则（确定性）：
    - rs_breakout=False → IDLE（streak 清零）；
    - 已 LAUNCHED 且 RS 未失守 → 保持 LAUNCHED（滞回）；
    - RS 突破中且资金 > 0 → streak+1，达 confirm_days → LAUNCHED，否则 CONFIRMING；
    - RS 突破中但资金 ≤ 0 → RS_BREAKOUT（streak 清零）。
    """

    def __init__(self, *, confirm_days: int = 3) -> None:
        if isinstance(confirm_days, bool) or confirm_days < 1:
            raise SectorCrowdingError(f"confirm_days 必须 ≥1: {confirm_days!r}")
        self._confirm_days = confirm_days
        self._phase = LaunchPhase.IDLE
        self._streak = 0

    @property
    def phase(self) -> LaunchPhase:
        """当前相位。"""
        return self._phase

    @property
    def streak(self) -> int:
        """当前资金转正连续日数。"""
        return self._streak

    def step(self, *, rs_breakout: bool, capital_flow: float) -> LaunchPhase:
        """推进一日：输入 RS 突破标记与当日资金流，输出新相位。"""
        if not isinstance(rs_breakout, bool):
            raise SectorCrowdingError(f"rs_breakout 须为 bool: {rs_breakout!r}")
        _check_finite("capital_flow", capital_flow)
        if not rs_breakout:
            self._phase = LaunchPhase.IDLE
            self._streak = 0
        elif self._phase is LaunchPhase.LAUNCHED:
            pass  # 滞回：RS 未失守保持 LAUNCHED
        elif capital_flow > 0:
            self._streak += 1
            self._phase = LaunchPhase.LAUNCHED if self._streak >= self._confirm_days else LaunchPhase.CONFIRMING
        else:
            self._phase = LaunchPhase.RS_BREAKOUT
            self._streak = 0
        return self._phase


class SectorCrowdingLauncher:
    """板块拥挤度评估 + 过热预警 + 启动状态机门面。"""

    def __init__(
        self,
        *,
        config: CrowdingConfig | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
        alert_sink: Callable[[OverheatWarning], None] | None = None,
    ) -> None:
        self._config = config or CrowdingConfig()
        self._clock = clock or datetime.datetime.now
        self._alert_sink = alert_sink
        self._machine = LaunchStateMachine(confirm_days=self._config.confirm_days)

    # ── 分位计算 ──────────────────────────────────────────────────────────

    @staticmethod
    def percentile_of(history: Sequence[float], current: float) -> float:
        """current 在注入 history 中的分位（严格小于计数/样本数，确定性）。"""
        history = tuple(history)
        if not history:
            raise SectorCrowdingError("分位历史序列为空")
        for v in history:
            _check_finite("history", v)
        _check_finite("current", current)
        below = sum(1 for v in history if v < current)
        return below / len(history)

    # ── 拥挤度评估 ────────────────────────────────────────────────────────

    def assess_crowding(
        self,
        *,
        turnover_history: Sequence[float],
        turnover_current: float,
        margin_history: Sequence[float],
        margin_current: float,
        correlation_history: Sequence[float],
        correlation_current: float,
        momentum_decay: float,
    ) -> CrowdingAssessment:
        """三分量分位 → 合成拥挤度 → 档位 → 过热预警（告警注入不阻断）。"""
        _check_finite("momentum_decay", momentum_decay)
        components = CrowdingComponents(
            turnover_pct=self.percentile_of(turnover_history, turnover_current),
            margin_pct=self.percentile_of(margin_history, margin_current),
            correlation_pct=self.percentile_of(correlation_history, correlation_current),
        )
        w = self._config.weights
        wsum = w[0] + w[1] + w[2]
        composite = (
            w[0] * components.turnover_pct + w[1] * components.margin_pct + w[2] * components.correlation_pct
        ) / wsum
        if composite > self._config.overheat_percentile:
            level = CrowdingLevel.OVERHEATED
        elif composite >= self._config.elevated_percentile:
            level = CrowdingLevel.ELEVATED
        else:
            level = CrowdingLevel.NORMAL
        overheated = level is CrowdingLevel.OVERHEATED

        warning: OverheatWarning | None = None
        if overheated and momentum_decay > self._config.momentum_decay_threshold:
            warning = OverheatWarning(
                composite=composite,
                momentum_decay=momentum_decay,
                reason=(f"拥挤度{composite:.3f}>90%分位且动量衰减{momentum_decay:.3f}>30%，回撤概率高"),
                raised_at=self._clock(),
            )
            _log.warning("板块过热预警: composite=%.3f decay=%.3f", composite, momentum_decay)
            if self._alert_sink is not None:
                try:
                    self._alert_sink(warning)
                except Exception:  # noqa: BLE001 — 告警不阻断
                    _log.exception("alert_sink 告警失败")

        return CrowdingAssessment(
            components=components,
            composite=composite,
            level=level,
            overheated=overheated,
            warning=warning,
            generated_at=self._clock(),
        )

    # ── 启动状态机 ────────────────────────────────────────────────────────

    def step_launch(self, *, rs_breakout: bool, capital_flow: float) -> LaunchPhase:
        """推进启动状态机一日。"""
        return self._machine.step(rs_breakout=rs_breakout, capital_flow=capital_flow)

    @property
    def launch_phase(self) -> LaunchPhase:
        """当前启动相位。"""
        return self._machine.phase
