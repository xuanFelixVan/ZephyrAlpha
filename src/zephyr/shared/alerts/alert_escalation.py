# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.alerts.alert_escalation
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.alerts.threshold_loader
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 自动升级超时真源=alert_threshold_registry(THD-ALERT-002,fail-closed)
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AlertThresholdConfigError(注册表缺失/畸形)
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
AlertEscalation — re-homed to eliminate shared->infrastructure circular import.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: alert_escalation.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 AlertEscalation, EscalationLevel（共 2 符号）
#   desc: __init__ import L0；__all__ 2 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 数据契约声明（2 类）
#   name_en: data classes
#   intro: EscalationLevel, AlertEscalation
#   downstream: N/A (all consumers verified as phantom — stale references removed)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from zephyr.shared.alerts.threshold_loader import load_alert_thresholds
from zephyr.shared.utils.time_utils import now_utc

__all__ = ["AlertEscalation", "EscalationLevel"]


class EscalationLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


def _load_auto_escalate_after_seconds(registry_path: Path | None = None) -> int:
    """从告警阈值注册表加载自动升级超时秒数（fail-closed；registry_path 为测试逃生门）。

    55 号 §3.3 统读：THD-ALERT-002（默认 300 秒）。
    """
    return load_alert_thresholds(
        {"THD-ALERT-002": "auto_escalate_after_seconds"},
        registry_path=registry_path,
        cast="int",
    )["auto_escalate_after_seconds"]


class AlertEscalation(BaseModel):
    """告警触达——触发->分级->行动->超时->自动升级。

    Re-homed from infrastructure_runtime_integration.pipeline.pipeline_roadmap.AlertEscalationTracker
    to eliminate shared->infrastructure circular import.
    """

    alert_id: str = Field(default="")
    title: str = Field(default="")
    level: EscalationLevel = Field(default=EscalationLevel.WARNING)
    source: str = Field(default="")
    triggered_at: str = Field(default_factory=lambda: now_utc().isoformat())
    acknowledged_at: str | None = None
    resolved_at: str | None = None
    escalation_chain: list[str] = Field(default_factory=list)
    auto_escalate_after_seconds: int = Field(
        default_factory=_load_auto_escalate_after_seconds
    )  # 构造期 fail-closed 加载（真源=注册表）；显式传参可覆盖
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def is_resolved(self) -> bool:
        return self.resolved_at is not None

    @property
    def is_acknowledged(self) -> bool:
        return self.acknowledged_at is not None
