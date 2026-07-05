# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_calibration
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_skill_calibration | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Calibration
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.3.0

Skill 校准 —— 置信度 vs 真实准确率对齐 + drift 监控.
当模型输出 confidence 与实际 accuracy 持续偏离时触发 recalibration 事件.
"""

from __future__ import annotations

import time
from typing import Any


class CalibrationEntry:
    def __init__(self, confidence: float, actual_accuracy: float, timestamp: float):
        self.confidence = confidence
        self.actual_accuracy = actual_accuracy
        self.timestamp = timestamp
        self.drift = confidence - actual_accuracy

    def to_dict(self) -> dict[str, Any]:
        return {
            "confidence": self.confidence,
            "accuracy": self.actual_accuracy,
            "drift": self.drift,
            "timestamp": self.timestamp,
        }


class SkillCalibration:
    """Skill 校准 —— 置信度 vs 准确率对齐."""

    _history: dict[str, list[CalibrationEntry]] = {}
    _MAX_HISTORY = 50
    _OVERCONFIDENCE_THRESHOLD = 0.15
    _UNDERCONFIDENCE_THRESHOLD = -0.10

    @classmethod
    def calibrate(cls, skill_id: str, confidence: float, actual_accuracy: float) -> dict[str, Any]:
        drift = confidence - actual_accuracy
        calibrated = abs(drift) < 0.1

        entry = CalibrationEntry(confidence, actual_accuracy, time.time())
        cls._history.setdefault(skill_id, []).append(entry)
        if len(cls._history[skill_id]) > cls._MAX_HISTORY:
            cls._history[skill_id] = cls._history[skill_id][-cls._MAX_HISTORY :]

        overconfident = drift > cls._OVERCONFIDENCE_THRESHOLD
        underconfident = drift < cls._UNDERCONFIDENCE_THRESHOLD

        return {
            "skill_id": skill_id,
            "confidence": confidence,
            "accuracy": actual_accuracy,
            "drift": round(drift, 4),
            "calibrated": calibrated,
            "overconfident": overconfident,
            "underconfident": underconfident,
        }

    @classmethod
    def drift_trend(cls, skill_id: str, window: int = 10) -> dict[str, Any]:
        entries = cls._history.get(skill_id, [])[-window:]
        if not entries:
            return {"skill_id": skill_id, "samples": 0, "avg_drift": 0.0}

        drifts = [e.drift for e in entries]
        avg_drift = sum(drifts) / len(drifts)
        recent_trend = cls._trend_direction(drifts)

        return {
            "skill_id": skill_id,
            "samples": len(entries),
            "avg_drift": round(avg_drift, 4),
            "trend": recent_trend,
            "overconfident_ratio": round(sum(1 for d in drifts if d > cls._OVERCONFIDENCE_THRESHOLD) / len(drifts), 3),
            "last_calibration": entries[-1].to_dict() if entries else {},
        }

    @classmethod
    def should_recalibrate(cls, skill_id: str) -> dict[str, Any]:
        trend = cls.drift_trend(skill_id, window=10)
        need = False
        reason = ""

        if trend["samples"] >= 5:
            if trend["overconfident_ratio"] > 0.4:
                need = True
                reason = f"overconfidence ratio={trend['overconfident_ratio']} > 0.4"
            elif abs(trend["avg_drift"]) > 0.12:
                need = True
                reason = f"avg_drift={trend['avg_drift']} > 0.12"

        return {
            "skill_id": skill_id,
            "should_recalibrate": need,
            "reason": reason,
            "trend": trend,
        }

    @staticmethod
    def _trend_direction(drifts: list[float]) -> str:
        if len(drifts) < 3:
            return "insufficient_data"
        recent = drifts[-3:]
        if all(d > 0 for d in recent):
            return "increasing_overconfidence"
        if all(d < 0 for d in recent):
            return "increasing_underconfidence"
        if recent[-1] > recent[-2] > recent[-3]:
            return "increasing_overconfidence"
        if recent[-1] < recent[-2] < recent[-3]:
            return "increasing_underconfidence"
        return "stable"

    @classmethod
    def clear_history(cls, skill_id: Optional[str] = None):
        if skill_id:
            cls._history.pop(skill_id, None)
        else:
            cls._history.clear()


__all__ = ["CalibrationEntry", "SkillCalibration"]
