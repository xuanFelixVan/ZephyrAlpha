# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_feedback
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
# [A_module] module_id=MOD-ORC_skill_feedback | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Feedback Loop
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.2.0

Skill 反馈环 —— ModuleResult → SkillLifecycle → 自动优化闭.
每次 Skill 执行后自动记录质量指标，触发 freshness 衰减/boost，
并在异常情况下自动触发 Kill Switch.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from zephyr.shared.io.serialization import filter_dataclass_fields


@dataclass
class FeedbackSignal:
    skill_id: str
    module_id: str
    task_id: str
    success: bool
    error_count: int
    latency_ms: int
    tokens_used: int
    cost_usd: float
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "module_id": self.module_id,
            "task_id": self.task_id,
            "success": self.success,
            "error_count": self.error_count,
            "latency_ms": self.latency_ms,
            "tokens_used": self.tokens_used,
            "cost_usd": self.cost_usd,
            "timestamp": self.timestamp,
        }


class SkillFeedback:
    """Skill 反馈环 —— ModuleResult→SkillLifecycle→自动优化."""

    _FEEDBACK_LOG = Path("_journals/skill_feedback.jsonl")
    _MAX_HISTORY = 100
    _SUCCESS_BOOST = 10.0
    _FAILURE_DECAY = 25.0
    _CONSECUTIVE_FAILURE_KILL = 3

    def __init__(self):
        self._history: list[FeedbackSignal] = []
        self._consecutive_failures: dict[str, int] = {}
        self._load_history()

    def record_module_result(
        self,
        skill_id: str,
        module_result: Any,
        task_id: str,
    ) -> dict[str, Any]:
        error_count = 0
        success = True
        tokens_used = 0
        cost_usd = 0.0
        latency_ms = 0

        if hasattr(module_result, "status"):
            status_val = str(getattr(module_result, "status", "")).upper()
            success = status_val == "SUCCESS"
        if hasattr(module_result, "errors"):
            error_count = len(getattr(module_result, "errors", []) or [])

        raw = getattr(module_result, "raw_output", {}) or {}
        if isinstance(raw, dict):
            tokens_used = raw.get("tokens_used", 0)
            cost_usd = raw.get("cost_usd", 0.0)
            latency_ms = raw.get("latency_ms", 0)

        signal = FeedbackSignal(
            skill_id=skill_id,
            module_id=getattr(module_result, "module_id", ""),
            task_id=task_id,
            success=success,
            error_count=error_count,
            latency_ms=latency_ms,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
        )

        self._history.append(signal)
        if len(self._history) > self._MAX_HISTORY:
            self._history = self._history[-self._MAX_HISTORY :]

        actions = []
        if success:
            actions.append(self._boost_freshness(skill_id, signal))
        else:
            actions.append(self._decay_freshness(skill_id, signal))
            kill_action = self._check_auto_kill(skill_id, signal)
            if kill_action:
                actions.append(kill_action)

        self._append_signal_to_log(signal)

        return {
            "skill_id": skill_id,
            "signal": signal.to_dict(),
            "actions": actions,
            "success": success,
        }

    def _boost_freshness(self, skill_id: str, signal: FeedbackSignal) -> dict[str, Any]:
        from zephyr.autonomy_core.skills.skill_freshness import FreshnessDecayModel

        fdm = FreshnessDecayModel()
        fdm.boost(skill_id, self._SUCCESS_BOOST)
        return {
            "action": "freshness_boost",
            "skill_id": skill_id,
            "amount": self._SUCCESS_BOOST,
            "reason": "module_success",
        }

    def _decay_freshness(self, skill_id: str, signal: FeedbackSignal) -> dict[str, Any]:
        self._consecutive_failures[skill_id] = self._consecutive_failures.get(skill_id, 0) + 1
        from zephyr.autonomy_core.skills.skill_freshness import FreshnessDecayModel

        fdm = FreshnessDecayModel()
        fdm.decay(skill_id, self._FAILURE_DECAY)
        return {
            "action": "freshness_decay",
            "skill_id": skill_id,
            "amount": self._FAILURE_DECAY,
            "consecutive_failures": self._consecutive_failures[skill_id],
        }

    def _check_auto_kill(self, skill_id: str, signal: FeedbackSignal) -> dict[str, Any] | None:
        count = self._consecutive_failures.get(skill_id, 0)
        if count >= self._CONSECUTIVE_FAILURE_KILL:
            from zephyr.autonomy_core.skills.skill_kill_switch import SkillKillSwitch

            return SkillKillSwitch.auto_kill_on_errors(skill_id, count)
        return None

    def on_success_reset(self, skill_id: str):
        self._consecutive_failures.pop(skill_id, None)

    def get_history(self, skill_id: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
        if skill_id:
            return [s.to_dict() for s in self._history if s.skill_id == skill_id][-limit:]
        return [s.to_dict() for s in self._history[-limit:]]

    def stats(self, skill_id: str | None = None) -> dict[str, Any]:
        subset = self._history
        if skill_id:
            subset = [s for s in subset if s.skill_id == skill_id]
        if not subset:
            return {"total_signals": 0}
        successes = sum(1 for s in subset if s.success)
        return {
            "total_signals": len(subset),
            "success_rate": round(successes / len(subset), 3),
            "total_cost_usd": round(sum(s.cost_usd for s in subset), 6),
            "total_tokens": sum(s.tokens_used for s in subset),
            "avg_latency_ms": int(sum(s.latency_ms for s in subset) / len(subset)),
        }

    def _load_history(self):
        try:
            if self._FEEDBACK_LOG.exists():
                with open(self._FEEDBACK_LOG, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                data = json.loads(line)
                                self._history.append(FeedbackSignal(**filter_dataclass_fields(FeedbackSignal, data)))
                            except (json.JSONDecodeError, TypeError):
                                pass
                if len(self._history) > self._MAX_HISTORY:
                    self._history = self._history[-self._MAX_HISTORY :]
        except OSError:
            pass

    def _append_signal_to_log(self, signal: FeedbackSignal):
        try:
            self._FEEDBACK_LOG.parent.mkdir(parents=True, exist_ok=True)
            with open(self._FEEDBACK_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(signal.to_dict(), ensure_ascii=False) + "\n")
        except OSError:
            pass


__all__ = ["FeedbackSignal", "SkillFeedback"]
