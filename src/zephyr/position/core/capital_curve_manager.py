# [BLUEPRINT] MOD-POS-007 | docs/03_modules/_domain_position/capital_curve_manager/blueprint.md
# [MODULE] zephyr.position.core.capital_curve_manager
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-POS-001(仓位上限联动) ; MOD-POS-008(回撤控制器) ; D-RISK ; D-PF-CORE
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 回撤≤0且peak单调非减;position_cap仅由drawdown_level决定不可被盈利放大;EMERGENCY级defensive_only=True禁止新开仓;capital_curve_discount受框架硬上限封顶
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidCapitalCurveInputError
# [TESTS] tests/position/test_capital_curve_manager.py
# [A_module] module_id=MOD-POS-007 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Capital Curve Manager — 资金曲线管理器 (MOD-POS-007)

跟踪已实现盈亏驱动的净值曲线, 根据回撤分级动态调整仓位上限,
盈利期扩张 / 亏损期收缩资金基础, 产出 E-POS-04 CapitalCurveUpdated 事件。

回撤分级 (D-POSITION §1.3 POS-07):
    - < 5%      NORMAL     仓位上限 100%
    - 5% ~ 10%  WARNING    仓位上限 80%
    - 10% ~ 15% CRITICAL   仓位上限 50%
    - > 15%     EMERGENCY  仓位上限 30% + 仅防御(禁止新开仓)

盈利扩张: 每次净值创新高 → 资金基础 +5% (复利累计, 封顶框架硬上限)
亏损收缩: 回撤 > 5% 缩减 10% / 回撤 > 10% 缩减 20%
恢复条件: 净值回到回撤前高点 → 解除收缩, 保留累计扩张因子
本金 = 当前净值 (天然复利)

属A类基础设施(回撤计算+分级+缩放系数, 逻辑明确), 阈值与扩张步长为C类可调参数。
依据: D:\临时工作区\依赖图-D-POSITION-仓位管理域.md §1.3 POS-07, §4 E-POS-04
SSoT: depgraph MOD-POS-007
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 最新净值 net_value
#   fields: float（已实现盈亏后的本金基准，必须为正，否则抛错）
#   code: capital_curve_manager.py L251-265 record(net_value)
# - id: I2
#   name: 初始本金与框架硬上限
#   fields: initial_capital>0（净值/峰值起点）+ framework_hard_cap∈(0,1]（总仓位硬顶，默认 1.0）
#   code: capital_curve_manager.py L205-217 __init__ 参数
# - id: I3
#   name: 资金曲线配置 CapitalCurveConfig
#   fields: 分级阈值 5%/10%/15% + 仓位上限 100/80/50/30% + 扩张步长 5% + 扩张硬上限 2x + 收缩 10%/20%
#   code: capital_curve_manager.py L93-114 CapitalCurveConfig
# 层: 算法
# - id: A1
#   name_zh: ① 创新高判定与盈利扩张
#   name_en: record 扩张段
#   intro: 净值每次创新高，扩张因子加 5%，封顶 2 倍硬上限
#   desc: L269-276 is_new_high=net_value>peak；expansion_factor=min(+0.05, 2.0)；peak 刷新（peak 单调非减）；回撤期不削减扩张因子
#   inputs: I1 I2 I3
#   outputs: is_new_high + expansion_factor + 新 peak
#   invariant: peak 单调非减
# - id: A2
#   name_zh: ② 回撤计算
#   name_en: record 回撤段
#   intro: 当前净值相对历史峰值的有符号回撤，恒不大于零
#   desc: L278-279 drawdown=(net_value-peak)/peak（peak>0 否则 0）
#   inputs: A1 I1
#   outputs: drawdown ≤ 0
#   invariant: drawdown≤0
# - id: A3
#   name_zh: ③ 回撤分级
#   name_en: _classify
#   intro: 按回撤深度分四档：正常/警告/严重/紧急
#   desc: L328-338 |dd|≥15%→EMERGENCY；≥10%→CRITICAL；≥5%→WARNING；否则 NORMAL
#   inputs: A2 I3
#   outputs: DrawdownLevel
# - id: A4
#   name_zh: ④ 仓位上限映射
#   name_en: _cap_for_level + min(framework_hard_cap)
#   intro: 分级直接决定仓位上限，盈利再好也不放大，且不破框架硬顶
#   desc: L284-285+L340-348 NORMAL 1.0/WARNING 0.8/CRITICAL 0.5/EMERGENCY 0.3；position_cap=min(level_cap, framework_hard_cap)
#   inputs: A3 I2 I3
#   outputs: position_cap ∈[0.3,1.0]
#   invariant: position_cap 仅由 drawdown_level 决定，不可被盈利放大
# - id: A5
#   name_zh: ⑤ 亏损收缩与折扣合成
#   name_en: _contraction_factor + discount 合成
#   intro: 回撤期打一个瞬时收缩乘子，和累计扩张因子相乘得缩放系数
#   desc: L287-290+L350-363 |dd|>10%→×0.8；>5%→×0.9；否则 1.0；discount=expansion_factor×contraction；净值回峰值自动解除收缩
#   inputs: A1 A2 I3
#   outputs: capital_curve_discount
# - id: A6
#   name_zh: ⑥ 快照装配与事件发布
#   name_en: record 装配段 + _emit
#   intro: 组装资金曲线快照并广播 E-POS-04 事件，监听器故障不传染
#   desc: L294-320 CapitalCurveSnapshot（含 defensive_only=level==EMERGENCY）；L365-370 逐监听器回调，异常隔离记日志
#   inputs: A3 A4 A5 A1
#   outputs: CapitalCurveSnapshot + CapitalCurveUpdatedEvent
#   invariant: EMERGENCY 级 defensive_only=True 禁止新开仓
# 层: 输出
# - id: O1
#   name_zh: 资金曲线快照 CapitalCurveSnapshot
#   name_en: CapitalCurveSnapshot
#   intro: 净值/峰值/回撤/分级/仓位上限/缩放系数/是否新高/仅防御/扩张因子十字段快照
#   invariant: position_cap∈[0.3,1.0]；expansion_factor≥1 且 ≤2.0
#   downstream: MOD-POS-001 仓位上限联动；MOD-POS-008 回撤控制器；D-RISK；D-PF-CORE（[CONSUMERS] 头）
# - id: O2
#   name_zh: E-POS-04 资金曲线更新事件
#   name_en: CapitalCurveUpdatedEvent
#   intro: 快照+上下文的事件，推给所有 on_capital_curve_updated 订阅者
#   downstream: 事件订阅者（MOD-POS-001 / MOD-POS-008 等经 on_capital_curve_updated 注册）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# I1 --> A2
# A2 --> A3
# I3 --> A3
# A3 --> A4
# I2 --> A4
# I3 --> A4
# A1 --> A5
# A2 --> A5
# I3 --> A5
# A3 --> A6
# A4 --> A6
# A5 --> A6
# A1 --> A6
# A6 --> O1
# A6 --> O2
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "DrawdownLevel",
    "CapitalCurveConfig",
    "CapitalCurveSnapshot",
    "CapitalCurveUpdatedEvent",
    "CapitalCurveManager",
    "InvalidCapitalCurveInputError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class DrawdownLevel(str, Enum):
    """回撤分级 (决定仓位上限)。"""

    NORMAL = "NORMAL"        # < 5%        仓位上限 100%
    WARNING = "WARNING"      # 5% ~ 10%    仓位上限 80%
    CRITICAL = "CRITICAL"    # 10% ~ 15%   仓位上限 50%
    EMERGENCY = "EMERGENCY"  # > 15%       仓位上限 30% + 仅防御


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidCapitalCurveInputError(ZephyrBaseError):
    """资金曲线输入数据非法(如净值非正、盈亏快照非法)。"""

    error_code = "ZA-POS-0005"


# ──────────────────────────────────────────────────────────────────────────────
# 配置 (C 类可调参数, 默认值来自设计真源)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class CapitalCurveConfig:
    """资金曲线管理配置。

    所有阈值均为正数 (回撤幅度绝对值), 内部计算时取负。
    """

    # 回撤分级阈值 (正数, 表示回撤幅度)
    warning_threshold: float = 0.05    # -5%
    critical_threshold: float = 0.10   # -10%
    emergency_threshold: float = 0.15  # -15%
    # 仓位上限 (per drawdown level)
    normal_cap: float = 1.00
    warning_cap: float = 0.80
    critical_cap: float = 0.50
    emergency_cap: float = 0.30
    # 盈利扩张
    profit_expansion_step: float = 0.05         # 每次新高 +5%
    profit_expansion_hard_limit: float = 2.00   # 框架硬上限 (2x 初始本金)
    # 亏损收缩
    loss_contraction_5pct: float = 0.10   # 回撤 > 5% 缩减 10%
    loss_contraction_10pct: float = 0.20  # 回撤 > 10% 缩减 20%

    def __post_init__(self) -> None:
        for name, val in (
            ("warning_threshold", self.warning_threshold),
            ("critical_threshold", self.critical_threshold),
            ("emergency_threshold", self.emergency_threshold),
        ):
            if not 0 < val < 1:
                raise InvalidCapitalCurveInputError(f"{name} must be in (0,1), got {val}")
        if not (self.warning_threshold < self.critical_threshold < self.emergency_threshold):
            raise InvalidCapitalCurveInputError(
                "thresholds must satisfy warning < critical < emergency"
            )
        for name, val in (
            ("normal_cap", self.normal_cap),
            ("warning_cap", self.warning_cap),
            ("critical_cap", self.critical_cap),
            ("emergency_cap", self.emergency_cap),
        ):
            if not 0 < val <= 1:
                raise InvalidCapitalCurveInputError(f"{name} must be in (0,1], got {val}")
        if self.profit_expansion_step <= 0:
            raise InvalidCapitalCurveInputError("profit_expansion_step must be positive")
        if self.profit_expansion_hard_limit <= 1:
            raise InvalidCapitalCurveInputError("profit_expansion_hard_limit must be > 1")


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class CapitalCurveSnapshot:
    """资金曲线快照 (一次 update 的结果)。"""

    net_value: float                       # 当前净值 (本金基准)
    peak: float                            # 历史峰值
    drawdown: float                        # 有符号回撤 (≤0, 0=无回撤)
    drawdown_level: DrawdownLevel           # 回撤分级
    position_cap: float                    # 仓位上限 (0.3~1.0), 联动 POS-01
    capital_curve_discount: float          # 缩放系数 (>1 盈利扩张, <1 回撤收缩)
    is_new_high: bool                      # 本次是否创新高
    defensive_only: bool                   # EMERGENCY 时仅防御(禁止新开仓)
    expansion_factor: float                # 当前累计扩张因子 (≥1, 受硬上限封顶)
    timestamp: datetime

    @property
    def abs_drawdown(self) -> float:
        """回撤绝对值 (正数)。"""
        return abs(self.drawdown)

    @property
    def in_drawdown(self) -> bool:
        """是否处于回撤期。"""
        return self.drawdown < 0


@dataclass(frozen=True)
class CapitalCurveUpdatedEvent:
    """E-POS-04 CapitalCurveUpdated 事件 (D-POSITION §4)。"""

    snapshot: CapitalCurveSnapshot
    timestamp: datetime
    context_snapshot: dict[str, Any] = field(default_factory=dict)


# ──────────────────────────────────────────────────────────────────────────────
# 资金曲线管理器
# ──────────────────────────────────────────────────────────────────────────────


class CapitalCurveManager:
    """资金曲线管理器——回撤分级+仓位上限联动+盈利扩张/亏损收缩。

    用法:
        mgr = CapitalCurveManager(initial_capital=1_000_000.0)
        snap = mgr.record(net_value=1_050_000.0)   # 盈利创新高 → 扩张
        snap = mgr.record(net_value=980_000.0)     # 回撤 → 分级降仓
        if snap.defensive_only:
            # EMERGENCY: 禁止新开仓
        # POS-01 消费 snap.position_cap 与 snap.capital_curve_discount

    Args:
        initial_capital: 初始本金 (净值起点)
        config: 资金曲线配置 (阈值/上限/扩张步长)
        framework_hard_cap: 框架硬上限 (总仓位不可超, 默认 1.0=100%)
        clock: 可选时间源 (测试注入)
    """

    def __init__(
        self,
        initial_capital: float,
        config: CapitalCurveConfig | None = None,
        framework_hard_cap: float = 1.0,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if initial_capital <= 0:
            raise InvalidCapitalCurveInputError(f"initial_capital must be positive, got {initial_capital}")
        if not 0 < framework_hard_cap <= 1:
            raise InvalidCapitalCurveInputError(
                f"framework_hard_cap must be in (0,1], got {framework_hard_cap}"
            )
        self._config = config or CapitalCurveConfig()
        self._framework_hard_cap = framework_hard_cap
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._listeners: list[Callable[[CapitalCurveUpdatedEvent], None]] = []

        # 状态: peak 单调非减; expansion_factor 仅在新高时增长, 回撤期不削减
        #       (亏损收缩通过 contraction 瞬时乘子体现, 恢复自动解除)
        self._peak = initial_capital
        self._net_value = initial_capital
        self._expansion_factor = 1.0

    @property
    def config(self) -> CapitalCurveConfig:
        return self._config

    @property
    def peak(self) -> float:
        return self._peak

    @property
    def net_value(self) -> float:
        return self._net_value

    @property
    def expansion_factor(self) -> float:
        return self._expansion_factor

    @property
    def framework_hard_cap(self) -> float:
        return self._framework_hard_cap

    # ── 公开 API ──

    def record(self, net_value: float, now: datetime | None = None) -> CapitalCurveSnapshot:
        """记录最新净值, 更新资金曲线, 产出快照。

        Args:
            net_value: 当前净值 (已实现盈亏后的本金, 必须为正)
            now: 时间戳

        Returns:
            CapitalCurveSnapshot (含仓位上限+缩放系数+回撤分级)

        Raises:
            InvalidCapitalCurveInputError: 净值非正
        """
        if net_value <= 0:
            raise InvalidCapitalCurveInputError(f"net_value must be positive, got {net_value}")
        now = now or self._clock()
        cfg = self._config

        # 1. 创新高判定 + 盈利扩张 (每次新高 +5%, 封顶框架硬上限)
        is_new_high = net_value > self._peak
        if is_new_high:
            self._expansion_factor = min(
                self._expansion_factor + cfg.profit_expansion_step,
                cfg.profit_expansion_hard_limit,
            )
            self._peak = net_value

        # 2. 回撤计算 (peak 单调非减, 故 drawdown ≤ 0)
        drawdown = (net_value - self._peak) / self._peak if self._peak > 0 else 0.0

        # 3. 回撤分级
        level = self._classify(drawdown)

        # 4. 仓位上限 (仅由分级决定, 不可被盈利放大, 受框架硬上限封顶)
        position_cap = min(self._cap_for_level(level), self._framework_hard_cap)

        # 5. 亏损收缩: 回撤期施加瞬时 contraction 乘子; 净值回到峰值自动解除
        #    expansion_factor 在回撤期不削减 (恢复后保留累计扩张)
        contraction = self._contraction_factor(drawdown) if drawdown < 0 else 1.0
        capital_curve_discount = self._expansion_factor * contraction

        self._net_value = net_value

        snapshot = CapitalCurveSnapshot(
            net_value=net_value,
            peak=self._peak,
            drawdown=drawdown,
            drawdown_level=level,
            position_cap=position_cap,
            capital_curve_discount=capital_curve_discount,
            is_new_high=is_new_high,
            defensive_only=(level is DrawdownLevel.EMERGENCY),
            expansion_factor=self._expansion_factor,
            timestamp=now,
        )

        event = CapitalCurveUpdatedEvent(
            snapshot=snapshot,
            timestamp=now,
            context_snapshot={
                "drawdown": drawdown,
                "drawdown_level": level.value,
                "position_cap": position_cap,
                "capital_curve_discount": capital_curve_discount,
                "is_new_high": is_new_high,
                "defensive_only": snapshot.defensive_only,
            },
        )
        self._emit(event)
        return snapshot

    def on_capital_curve_updated(self, listener: Callable[[CapitalCurveUpdatedEvent], None]) -> None:
        """订阅 E-POS-04 CapitalCurveUpdated 事件。"""
        self._listeners.append(listener)

    def restore_peak(self, persisted_peak: float) -> None:
        """启动恢复持久化 peak NAV（35 号 memo §3.15 阶段 3 基线校准）。

        peak 单调非减（§3.8 不变量）——从持久化加载，不可当日重算；
        恢复值低于内存 peak 时取 max（不变量优先，防持久化回退造成假新高）。

        Args:
            persisted_peak: 持久化的历史峰值（必须为正）

        Raises:
            InvalidCapitalCurveInputError: persisted_peak 非正
        """
        if persisted_peak <= 0:
            raise InvalidCapitalCurveInputError(
                f"persisted_peak must be positive, got {persisted_peak}"
            )
        if persisted_peak > self._peak:
            self._peak = persisted_peak

    # ── 内部 ──

    def _classify(self, drawdown: float) -> DrawdownLevel:
        """根据回撤 (≤0) 判定分级。"""
        ad = abs(drawdown)
        cfg = self._config
        if ad >= cfg.emergency_threshold:
            return DrawdownLevel.EMERGENCY
        if ad >= cfg.critical_threshold:
            return DrawdownLevel.CRITICAL
        if ad >= cfg.warning_threshold:
            return DrawdownLevel.WARNING
        return DrawdownLevel.NORMAL

    def _cap_for_level(self, level: DrawdownLevel) -> float:
        cfg = self._config
        if level is DrawdownLevel.EMERGENCY:
            return cfg.emergency_cap
        if level is DrawdownLevel.CRITICAL:
            return cfg.critical_cap
        if level is DrawdownLevel.WARNING:
            return cfg.warning_cap
        return cfg.normal_cap

    def _contraction_factor(self, drawdown: float) -> float:
        """亏损收缩系数 (回撤越深缩减越多)。

        回撤 > 10% → 0.8 (缩减 20%)
        回撤 > 5%  → 0.9 (缩减 10%)
        其余       → 1.0
        """
        cfg = self._config
        ad = abs(drawdown)
        if ad > cfg.critical_threshold:
            return 1.0 - cfg.loss_contraction_10pct
        if ad > cfg.warning_threshold:
            return 1.0 - cfg.loss_contraction_5pct
        return 1.0

    def _emit(self, event: CapitalCurveUpdatedEvent) -> None:
        for listener in self._listeners:
            try:
                listener(event)
            except Exception as exc:  # noqa: BLE001 — 5.135治标: 隔离监听器故障
                logger.error("CapitalCurve listener error: %s", exc, exc_info=True)
