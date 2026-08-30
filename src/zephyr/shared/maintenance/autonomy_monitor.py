# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.maintenance.autonomy_monitor
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.maintenance.zero_config
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Autonomy Monitor — AI 自主等级监控与降级。

依据：
    蓝图 MOD-TASK_SYSTEM §6.5.3 + v0.6.0
    任务卡 TASK-INF-0110 (Part 3/4)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: data_dir 参数
#   fields: 参数 data_dir（无注解）
#   code: autonomy_monitor.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① AutonomyMonitor
#   name_en: AutonomyMonitor
#   intro: class AutonomyMonitor 源码 L84-L188
#   desc: 公共方法（定义序）: event_log, state, get_level, downgrade, upgrade, can_auto_execute, needs_human_approval, generate_…
#   inputs: data_dir
#   outputs: 返回值
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: AutonomyMonitor
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any


class AutonomyLevel(str, Enum):
    FULL = "full_autonomy"
    SUPERVISED = "supervised"
    RESTRICTED = "restricted"
    READ_ONLY = "read_only"


@dataclass
class AutonomyState:
    current_level: AutonomyLevel
    previous_level: AutonomyLevel | None = None
    downgrade_count: int = 0
    upgrade_count: int = 0
    last_changed: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class AutonomyReport:
    level: AutonomyLevel
    uptime_downgrade_free_hours: float
    downgrade_history: list[dict[str, Any]]
    recommendation: str


class AutonomyMonitor:
    def __init__(self, data_dir: Path | None = None) -> None:
        self._data_dir = data_dir or Path("data/maintenance/autonomy")
        self._state = AutonomyState(current_level=AutonomyLevel.SUPERVISED)
        self._event_log: list[dict[str, Any]] = []

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def event_log(self) -> list[dict[str, Any]]:
        """只读：event_log（Stage 4 公共化）。"""
        return self._event_log

    @event_log.setter
    def event_log(self, value):
        """写入：event_log（Stage 4 公共化）。"""
        self._event_log = value

    @property
    def state(self):
        """只读：state（Stage 4 公共化）。"""
        return self._state

    @state.setter
    def state(self, value):
        """写入：state（Stage 4 公共化）。"""
        self._state = value

    def get_level(self) -> AutonomyLevel:
        return self._state.current_level

    def downgrade(self, reason: str, to_level: AutonomyLevel | None = None) -> AutonomyLevel:
        new_level = to_level or self._next_lower(self._state.current_level)
        self._state.previous_level = self._state.current_level
        self._state.current_level = new_level
        self._state.downgrade_count += 1
        self._state.last_changed = datetime.now(UTC).isoformat()

        self._event_log.append(
            {
                "type": "DOWNGRADE",
                "from": self._state.previous_level.value,
                "to": new_level.value,
                "reason": reason,
                "timestamp": self._state.last_changed,
            }
        )

        return new_level

    def upgrade(self, reason: str) -> AutonomyLevel:
        new_level = self._next_higher(self._state.current_level)
        self._state.previous_level = self._state.current_level
        self._state.current_level = new_level
        self._state.upgrade_count += 1
        self._state.last_changed = datetime.now(UTC).isoformat()

        self._event_log.append(
            {
                "type": "UPGRADE",
                "from": self._state.previous_level.value,
                "to": new_level.value,
                "reason": reason,
                "timestamp": self._state.last_changed,
            }
        )

        return new_level

    def can_auto_execute(self) -> bool:
        return self._state.current_level in (AutonomyLevel.FULL, AutonomyLevel.SUPERVISED)

    def needs_human_approval(self) -> bool:
        return self._state.current_level in (AutonomyLevel.RESTRICTED, AutonomyLevel.READ_ONLY)

    def generate_report(self) -> AutonomyReport:
        downgrades = [e for e in self._event_log if e["type"] == "DOWNGRADE"]

        return AutonomyReport(
            level=self._state.current_level,
            uptime_downgrade_free_hours=0.0,
            downgrade_history=downgrades[-10:],
            recommendation=(
                "Full autonomy recommended"
                if self._state.current_level is AutonomyLevel.FULL
                else "Human supervision recommended"
            ),
        )

    @staticmethod
    def _next_lower(level: AutonomyLevel) -> AutonomyLevel:
        order = [AutonomyLevel.FULL, AutonomyLevel.SUPERVISED, AutonomyLevel.RESTRICTED, AutonomyLevel.READ_ONLY]
        try:
            idx = order.index(level)
            return order[min(idx + 1, len(order) - 1)]
        except ValueError:
            return AutonomyLevel.READ_ONLY

    @staticmethod
    def _next_higher(level: AutonomyLevel) -> AutonomyLevel:
        order = [AutonomyLevel.FULL, AutonomyLevel.SUPERVISED, AutonomyLevel.RESTRICTED, AutonomyLevel.READ_ONLY]
        try:
            idx = order.index(level)
            return order[max(idx - 1, 0)]
        except ValueError:
            return AutonomyLevel.SUPERVISED
