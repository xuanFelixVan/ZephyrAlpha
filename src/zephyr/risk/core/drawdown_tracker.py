# [BLUEPRINT] MOD-RK-011 | docs/03_modules/_domain_risk/drawdown_tracker/blueprint.md
# [MODULE] zephyr.risk.core.drawdown_tracker
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors; zephyr.shared.alerts.threshold_loader
# [CONSUMERS] MOD-RK-17(Kill Switch,EMERGENCY触发) ; D-FRONTEND ; D-AUTONOMY ; D-REPORTING
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] peak单调非减;trough≤peak;drawdown≤0;告警级别由当前回撤唯一决定;事件去抖(连续相同级别不重复发射);阈值唯一真源=alert_threshold_registry(THD-DRAWDOWN-001/002/003,fail-closed)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidDrawdownInputError; AlertThresholdConfigError(注册表缺失/畸形)
# [TESTS] tests/risk/test_drawdown_tracker.py
# [A_module] module_id=MOD-RK-011 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Drawdown Real-Time Tracker — 回撤实时追踪器 (MOD-RK-011)

盘中实时跟踪组合净值最大回撤(峰值/谷值), 三级阈值告警, 回撤恢复检测, 资金曲线诊断。
产出 E-RK-03 DrawdownAlerted 事件, EMERGENCY 级触发 RK-17 Kill Switch。

三级阈值 (D-RISK §1 RK-11, §4 E-RK-03):
    - 5% ~ 10%   WARNING    提醒关注
    - 10% ~ 15%  CRITICAL   严重回撤
    - > 15%      EMERGENCY  触发 Kill Switch
    (< 5% 为 NONE, 无告警)

与 POS-007 区别: POS-007 是仓位上限联动(行动导向); RK-11 是实时告警(监控导向)。
属A类基础设施(峰值谷值+阈值判定+恢复检测, 逻辑明确), 阈值为C类可调参数。
依据: D:\\临时工作区\\依赖图\\11-D-RISK-风控域.md §1 RK-11, §4 E-RK-03
SSoT: depgraph MOD-RK-011
Version: 0.1.0
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Final

from zephyr.shared.alerts.threshold_loader import load_alert_thresholds
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "DrawdownAlertLevel",
    "DrawdownTrackerConfig",
    "DrawdownSnapshot",
    "DrawdownAlertedEvent",
    "DrawdownTracker",
    "InvalidDrawdownInputError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class DrawdownAlertLevel(str, Enum):
    """回撤告警级别 (严重度递增)。"""

    NONE = "NONE"            # < 5% 无告警
    WARNING = "WARNING"      # 5% ~ 10%
    CRITICAL = "CRITICAL"    # 10% ~ 15%
    EMERGENCY = "EMERGENCY"  # > 15% 触发 Kill Switch

    @property
    def severity(self) -> int:
        return {"NONE": 0, "WARNING": 1, "CRITICAL": 2, "EMERGENCY": 3}[self.value]


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidDrawdownInputError(ZephyrBaseError):
    """回撤追踪输入数据非法(如净值非正)。"""

    error_code = "ZA-RK-0003"


# ──────────────────────────────────────────────────────────────────────────────
# 配置 (C 类可调参数)
# ──────────────────────────────────────────────────────────────────────────────

#: 回撤三级阈值 ↔ 注册表条目映射（55 号 §3.3 统读：THD-DRAWDOWN-001/002/003）
_DRAWDOWN_THRESHOLD_SPEC: Final[dict[str, str]] = {
    "THD-DRAWDOWN-001": "warning_threshold",
    "THD-DRAWDOWN-002": "critical_threshold",
    "THD-DRAWDOWN-003": "emergency_threshold",
}


def _load_drawdown_thresholds(registry_path: Path | None = None) -> dict[str, float]:
    """从告警阈值注册表加载回撤三级阈值（fail-closed；registry_path 为测试逃生门）。"""
    return load_alert_thresholds(_DRAWDOWN_THRESHOLD_SPEC, registry_path=registry_path)


#: import 期 fail-closed 加载（注册表缺失/畸形 → import 即 raise，禁止码内第二真源兜底）
_REGISTRY_DEFAULTS: Final[dict[str, float]] = _load_drawdown_thresholds()


@dataclass(frozen=True)
class DrawdownTrackerConfig:
    """回撤追踪阈值配置 (设计真源 §1 RK-11；默认值真源=alert_threshold_registry，显式传参可覆盖)。"""

    warning_threshold: float = _REGISTRY_DEFAULTS["warning_threshold"]    # -5%（THD-DRAWDOWN-001）
    critical_threshold: float = _REGISTRY_DEFAULTS["critical_threshold"]  # -10%（THD-DRAWDOWN-002）
    emergency_threshold: float = _REGISTRY_DEFAULTS["emergency_threshold"]  # -15%（THD-DRAWDOWN-003）

    def __post_init__(self) -> None:
        for name, val in (
            ("warning_threshold", self.warning_threshold),
            ("critical_threshold", self.critical_threshold),
            ("emergency_threshold", self.emergency_threshold),
        ):
            if not 0 < val < 1:
                raise InvalidDrawdownInputError(f"{name} must be in (0,1), got {val}")
        if not (self.warning_threshold < self.critical_threshold < self.emergency_threshold):
            raise InvalidDrawdownInputError(
                "thresholds must satisfy warning < critical < emergency"
            )


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class DrawdownSnapshot:
    """回撤追踪快照。"""

    net_value: float                  # 当前净值
    peak: float                        # 历史峰值 (高水位)
    trough: float                      # 自最近峰值以来最低点
    drawdown: float                    # 有符号回撤 (≤0, 0=无回撤)
    level: DrawdownAlertLevel          # 当前告警级别
    in_recovery: bool                  # 是否处于恢复期(谷底回升但未创新高)
    peak_timestamp: datetime           # 最近峰值时间
    duration_since_peak: float         # 自峰值以来秒数
    timestamp: datetime

    @property
    def abs_drawdown(self) -> float:
        return abs(self.drawdown)

    @property
    def is_emergency(self) -> bool:
        """是否 EMERGENCY (应触发 Kill Switch)。"""
        return self.level is DrawdownAlertLevel.EMERGENCY


@dataclass(frozen=True)
class DrawdownAlertedEvent:
    """E-RK-03 DrawdownAlerted 事件。

    仅在告警级别*变化*时发射 (含恢复降级)。
    """

    level: DrawdownAlertLevel          # 新级别
    previous_level: DrawdownAlertLevel  # 旧级别
    snapshot: DrawdownSnapshot
    timestamp: datetime
    context_snapshot: dict[str, Any] = field(default_factory=dict)

    @property
    def is_recovery(self) -> bool:
        """是否为恢复事件 (级别降级)。"""
        return self.level.severity < self.previous_level.severity

    @property
    def is_escalation(self) -> bool:
        """是否为升级事件 (级别升级)。"""
        return self.level.severity > self.previous_level.severity


# ──────────────────────────────────────────────────────────────────────────────
# 回撤实时追踪器
# ──────────────────────────────────────────────────────────────────────────────


class DrawdownTracker:
    """回撤实时追踪器——峰值谷值跟踪+三级阈值告警+恢复检测+事件去抖。

    用法:
        tracker = DrawdownTracker(initial_net_value=1_000_000.0)
        snap = tracker.update(940_000.0, now=t)   # -6% → WARNING, 发射 E-RK-03
        snap = tracker.update(930_000.0, now=t)   # -7% 仍 WARNING, 不重复发射
        snap = tracker.update(890_000.0, now=t)   # -11% → CRITICAL, 发射升级事件
        if snap.is_emergency:
            # 触发 Kill Switch (RK-17)

    Args:
        initial_net_value: 初始净值 (峰值起点)
        config: 阈值配置
        clock: 可选时间源 (测试注入)
    """

    def __init__(
        self,
        initial_net_value: float,
        config: DrawdownTrackerConfig | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if initial_net_value <= 0:
            raise InvalidDrawdownInputError(
                f"initial_net_value must be positive, got {initial_net_value}"
            )
        self._config = config or DrawdownTrackerConfig()
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._listeners: list[Callable[[DrawdownAlertedEvent], None]] = []

        # 状态
        self._peak = initial_net_value
        self._trough = initial_net_value
        self._net_value = initial_net_value
        self._peak_ts = self._clock()
        self._last_level = DrawdownAlertLevel.NONE

    @property
    def config(self) -> DrawdownTrackerConfig:
        return self._config

    @property
    def peak(self) -> float:
        return self._peak

    @property
    def trough(self) -> float:
        return self._trough

    @property
    def net_value(self) -> float:
        return self._net_value

    @property
    def last_level(self) -> DrawdownAlertLevel:
        return self._last_level

    # ── 公开 API ──

    def update(self, net_value: float, now: datetime | None = None) -> DrawdownSnapshot:
        """记录最新净值, 更新峰值谷值, 返回快照 (级别变化时发射 E-RK-03)。

        Args:
            net_value: 当前组合净值 (必须为正)
            now: 时间戳

        Returns:
            DrawdownSnapshot

        Raises:
            InvalidDrawdownInputError: 净值非正或非有限值
        """
        # 非有限值门禁（AI-R2 红队 ATK-1）：NaN 所有比较为 False → 静默失明轮；
        # +Inf 使 peak=inf 永久中毒（后续 drawdown 恒为 NaN，EMERGENCY 永不触发）
        if not math.isfinite(net_value) or net_value <= 0:
            raise InvalidDrawdownInputError(
                f"net_value must be positive and finite, got {net_value}"
            )
        now = now or self._clock()

        # 1. 峰值更新 (单调非减)
        if net_value > self._peak:
            self._peak = net_value
            self._peak_ts = now
            self._trough = net_value  # 新峰值 → 重置谷值

        # 2. 谷值更新 (自最近峰值以来最低)
        if net_value < self._trough:
            self._trough = net_value

        # 3. 回撤计算
        drawdown = (net_value - self._peak) / self._peak if self._peak > 0 else 0.0

        # 4. 级别判定
        level = self._classify(drawdown)

        # 5. 恢复检测: 谷底回升但未创新高
        in_recovery = (
            drawdown < 0
            and net_value > self._trough
            and net_value < self._peak
        )

        duration = (now - self._peak_ts).total_seconds()
        self._net_value = net_value

        snapshot = DrawdownSnapshot(
            net_value=net_value,
            peak=self._peak,
            trough=self._trough,
            drawdown=drawdown,
            level=level,
            in_recovery=in_recovery,
            peak_timestamp=self._peak_ts,
            duration_since_peak=duration,
            timestamp=now,
        )

        # 6. 事件去抖: 仅级别变化时发射
        if level is not self._last_level:
            event = DrawdownAlertedEvent(
                level=level,
                previous_level=self._last_level,
                snapshot=snapshot,
                timestamp=now,
                context_snapshot={
                    "drawdown": drawdown,
                    "level": level.value,
                    "previous_level": self._last_level.value,
                    "is_recovery": level.severity < self._last_level.severity,
                    "peak": self._peak,
                    "trough": self._trough,
                },
            )
            self._last_level = level
            self._emit(event)

        return snapshot

    def on_drawdown_alerted(self, listener: Callable[[DrawdownAlertedEvent], None]) -> None:
        """订阅 E-RK-03 DrawdownAlerted 事件。"""
        self._listeners.append(listener)

    # ── 内部 ──

    def _classify(self, drawdown: float) -> DrawdownAlertLevel:
        """根据回撤 (≤0) 判定告警级别。"""
        ad = abs(drawdown)
        cfg = self._config
        if ad >= cfg.emergency_threshold:
            return DrawdownAlertLevel.EMERGENCY
        if ad >= cfg.critical_threshold:
            return DrawdownAlertLevel.CRITICAL
        if ad >= cfg.warning_threshold:
            return DrawdownAlertLevel.WARNING
        return DrawdownAlertLevel.NONE

    def _emit(self, event: DrawdownAlertedEvent) -> None:
        for listener in self._listeners:
            try:
                listener(event)
            except Exception as exc:  # noqa: BLE001 — 5.135治标: 隔离监听器故障
                logger.error("Drawdown alert listener error: %s", exc, exc_info=True)
