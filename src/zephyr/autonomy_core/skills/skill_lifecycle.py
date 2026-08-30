# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_lifecycle
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Lifecycle
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.3.0

Skill 生命周期状态机 + 跨模块协调.
v0.3.0: complete lifecycle with guard functions, transition log, rollback, batch ops.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: from_status 参数
#   fields: 参数 from_status（无注解）
#   code: skill_lifecycle.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: to_status 参数
#   fields: 参数 to_status（无注解）
#   code: skill_lifecycle.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: reason 参数
#   fields: 参数 reason（无注解）
#   code: skill_lifecycle.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: timestamp 参数
#   fields: 参数 timestamp（无注解）
#   code: skill_lifecycle.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① Transition
#   name_en: Transition
#   intro: class Transition 源码 L88-L101
#   desc: 公共方法（定义序）: to_dict；源码 L88-L101
#   inputs: from_status to_status reason timestamp
#   outputs: 返回值
# - id: A2
#   name_zh: ② SkillLifecycle
#   name_en: SkillLifecycle
#   intro: Skill 生命周期状态机 + 跨模块协调.
#   desc: Skill 生命周期状态机 + 跨模块协调.；公共方法（定义序）: guards, states, register, current_status, add_guard, transition, history, r…
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: Transition, SkillLifecycle
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, Final

from zephyr.autonomy_core.skills.skill_model import SkillStatus


class Transition:
    def __init__(self, from_status: str, to_status: str, reason: str, timestamp: float | None = None):
        self.from_status = from_status
        self.to_status = to_status
        self.reason = reason
        self.timestamp = timestamp or time.time()

    def to_dict(self) -> dict[str, Any]:
        return {
            "from": self.from_status,
            "to": self.to_status,
            "reason": self.reason,
            "timestamp": self.timestamp,
        }


VALID_TRANSITIONS: Final[set] = {
    SkillStatus.DRAFT.value: {SkillStatus.ACTIVE.value, SkillStatus.DEPRECATED.value},
    SkillStatus.ACTIVE.value: {SkillStatus.DEPRECATED.value, SkillStatus.DRAFT.value},
    SkillStatus.DEPRECATED.value: {SkillStatus.DRAFT.value},
    SkillStatus.RETIRED.value: set(),
}


class SkillLifecycle:
    """Skill 生命周期状态机 + 跨模块协调."""

    _TRANSITION_LOG = Path("_journals/skill_transitions.jsonl")

    _ALLOW_ALL = True

    def __init__(self):
        self._states: dict[str, str] = {}
        self._guards: dict[str, list[Callable[[str, str], bool]]] = {}
        self._history: dict[str, list[Transition]] = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def guards(self) -> dict[str, list[Callable[[str, str], bool]]]:
        """只读：guards（Stage 4 公共化）。"""
        return self._guards

    @guards.setter
    def guards(self, value):
        """写入：guards（Stage 4 公共化）。"""
        self._guards = value

    @property
    def states(self) -> dict[str, str]:
        """只读：states（Stage 4 公共化）。"""
        return self._states

    @states.setter
    def states(self, value):
        """写入：states（Stage 4 公共化）。"""
        self._states = value

    def register(self, skill_id: str, status: str = SkillStatus.ACTIVE.value):
        self._states[skill_id] = status

    def current_status(self, skill_id: str) -> str:
        return self._states.get(skill_id, SkillStatus.DRAFT.value)

    def add_guard(self, skill_id: str, guard_fn: Callable[[str, str], bool]):
        self._guards.setdefault(skill_id, []).append(guard_fn)

    def transition(self, skill_id: str, to_status: str, reason: str = "") -> dict[str, Any]:
        from_status = self.current_status(skill_id)
        allowed = VALID_TRANSITIONS.get(from_status, set())

        if to_status not in allowed and not self._ALLOW_ALL:
            return {
                "skill_id": skill_id,
                "from": from_status,
                "to": to_status,
                "allowed": False,
                "reason": f"Invalid transition: {from_status} -> {to_status}",
            }

        for guard in self._guards.get(skill_id, []):
            if not guard(skill_id, to_status):
                return {
                    "skill_id": skill_id,
                    "from": from_status,
                    "to": to_status,
                    "allowed": False,
                    "reason": "Guard rejected transition",
                }

        self._states[skill_id] = to_status
        t = Transition(from_status, to_status, reason)
        self._history.setdefault(skill_id, []).append(t)
        self._log_transition(skill_id, t)
        return {"skill_id": skill_id, "from": from_status, "to": to_status, "allowed": True, "reason": reason}

    def history(self, skill_id: str, limit: int = 20) -> list[dict[str, Any]]:
        return [t.to_dict() for t in self._history.get(skill_id, [])[-limit:]]

    def rollback(self, skill_id: str) -> dict[str, Any]:
        transitions = self._history.get(skill_id, [])
        if len(transitions) < 2:
            return {"skill_id": skill_id, "rolled_back": False, "reason": "Insufficient history for rollback"}
        previous = transitions[-2]
        return self.transition(skill_id, previous.from_status, reason=f"Rollback to {previous.from_status}")

    def batch_transition(self, skill_ids: list[str], to_status: str, reason: str = "") -> dict[str, Any]:
        results = {}
        for sid in skill_ids:
            results[sid] = self.transition(sid, to_status, reason)
        return {
            "results": results,
            "total": len(skill_ids),
            "succeeded": sum(1 for r in results.values() if r["allowed"]),
        }

    def all_statuses(self) -> dict[str, str]:
        return dict(self._states)

    # ---- Persistence ----

    def _log_transition(self, skill_id: str, transition: Transition):
        try:
            self._TRANSITION_LOG.parent.mkdir(parents=True, exist_ok=True)
            with open(self._TRANSITION_LOG, "a", encoding="utf-8") as f:
                f.write(
                    json.dumps(
                        {
                            "skill_id": skill_id,
                            **transition.to_dict(),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        except OSError:
            pass


__all__ = ["SkillLifecycle", "Transition"]
