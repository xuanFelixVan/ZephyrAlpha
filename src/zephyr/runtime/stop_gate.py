"""
StopGate — 质量闸门
====================
蓝图: ARC-0001 §4.1 (二阶)
借鉴: Claude Code 45天自主实验——被动质量闸门
阻止 AI 什么都不做就退出。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class StopGateResult:
    can_stop: bool = True
    reasons: list[str] = field(default_factory=list)


class StopGate:
    """质量闸门——AI 不能空手退出。

    借鉴: Claude Code 45天自主实验——Stop Gate 阻止了 19/30 的空转 session。
    设计原理:
      - 不告诉 AI 该做什么（避免过度约束）
      - 只阻止 AI 什么都不做就退出（最低质量标准）
    """

    def __init__(self) -> None:
        self._session_start: str = ""
        self._shutdown_acknowledged = False

    def initialize(self) -> None:
        self._session_start = datetime.now().isoformat()
        self._shutdown_acknowledged = False

    def check(
        self,
        audit_has_new_entries: bool = True,
        night_shift_all_resolved: bool = True,
        dream_cycle_archived: bool = True,
        git_clean: bool = True,
    ) -> StopGateResult:
        result = StopGateResult(can_stop=True, reasons=[])

        if not audit_has_new_entries:
            result.can_stop = False
            result.reasons.append("AiAuditLogger: no new entries since last check")

        if not night_shift_all_resolved:
            result.can_stop = False
            result.reasons.append("NightShiftQueue: unresolved entries remain")

        if not dream_cycle_archived:
            result.can_stop = False
            result.reasons.append("DreamCycle: unarchived memory remains")

        if not git_clean:
            result.can_stop = False
            result.reasons.append("Git: uncommitted changes remain")

        return result

    def can_stop(self, **kwargs: bool) -> bool:
        return self.check(**kwargs).can_stop

    def acknowledge_shutdown(self) -> None:
        self._shutdown_acknowledged = True
