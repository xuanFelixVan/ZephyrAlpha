# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_domain_infra_runtime/task-system/blueprint.md
# [MODULE] zephyr.trading.task_gate
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.intelligence.model_profiling.capability_passport
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_task_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
TaskGate --- 任务门控

在 dispatch 前检查模型的能力护照。
只允许模型执行其 'safe_capabilities' 中列出的能力类型。

用法:
    gate = TaskGate()
    gate.load_passports()  # 加载所有护照

    ok, reason = gate.can_dispatch("qwen3:8b", "code_fix")
    # -> (False, "low_accuracy: low_precision_below_threshold")

    ok, reason = gate.can_dispatch("qwen3:8b", "task_classification")
    # -> (True, "ok")
"""

from __future__ import annotations

import logging

from zephyr.intelligence.model_profiling.capability_passport import CapabilityPassport

_log = logging.getLogger(__name__)


class TaskGate:
    """任务门控 — 根据护照决定是否允许模型执行某个能力类型。"""

    def __init__(self) -> None:
        self._passports: dict[str, CapabilityPassport] = {}
        self._fallback_allowed: set[str] = set()

    # ── 加载 ────────────────────────────────────────────

    def load_passports(self) -> int:
        model_ids = CapabilityPassport.list_all()
        loaded = 0
        for mid in model_ids:
            passport = CapabilityPassport.load(mid)
            if passport is not None:
                self._passports[mid] = passport
                loaded += 1
        _log.info("TaskGate: loaded %d passports: %s", loaded, list(self._passports.keys()))
        return loaded

    def load_passport(self, model_id: str) -> CapabilityPassport | None:
        passport = CapabilityPassport.load(model_id)
        if passport is not None:
            self._passports[model_id] = passport
            _log.info("TaskGate: loaded passport for %s", model_id)
        return passport

    # ── 查询 ────────────────────────────────────────────

    def can_dispatch(self, model_id: str, capability: str) -> tuple[bool, str]:
        passport = self._passports.get(model_id)
        if passport is None:
            return (False, "no_passport")

        depth = passport.depth
        if not depth or not depth.capabilities:
            return (False, "no_depth_data")

        cap_result = depth.capabilities.get(capability)
        if cap_result is None:
            return (False, "capability_not_tested")

        if not cap_result.pass_:
            return (False, f"low_accuracy: {cap_result.failure_reason}")

        return (True, "ok")

    def can_do_any(self, model_id: str) -> bool:
        passport = self._passports.get(model_id)
        if passport is None:
            return False
        return len(passport.recommendations.safe_capabilities) > 0

    def get_safe_capabilities(self, model_id: str) -> list[str]:
        passport = self._passports.get(model_id)
        if passport is None:
            return []
        return list(passport.recommendations.safe_capabilities)

    def get_unsafe_capabilities(self, model_id: str) -> list[str]:
        passport = self._passports.get(model_id)
        if passport is None:
            return []
        return list(passport.recommendations.unsafe_capabilities)

    def get_passport(self, model_id: str) -> CapabilityPassport | None:
        return self._passports.get(model_id)

    def has_passport(self, model_id: str) -> bool:
        return model_id in self._passports

    # ── 统计 ────────────────────────────────────────────

    def summary(self) -> dict:
        result = {"models": len(self._passports), "details": {}}
        for mid, passport in self._passports.items():
            result["details"][mid] = {
                "grade": passport.overall_grade,
                "score": passport.overall_score,
                "safe": passport.recommendations.safe_capabilities,
                "unsafe": passport.recommendations.unsafe_capabilities,
            }
        return result

    def __repr__(self) -> str:
        return f"TaskGate(models={len(self._passports)})"
