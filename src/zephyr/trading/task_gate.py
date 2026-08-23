# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.task_gate
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.intelligence.model_profiling.capability_passport
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-035 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

    # ── Stage 4 公共化（2026-07-28）：只读 property ──
    @property
    def passports(self) -> dict[str, CapabilityPassport]:
        """只读：passports（Stage 4 公共化）。"""
        return self._passports

    @passports.setter
    def passports(self, value):
        """写入：passports（Stage 4 公共化）。"""
        self._passports = value

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

    def _resolve_key(self, model_id: str) -> str | None:
        """护照 ID 口径双向兼容查询（GP0 #255④ 裁定：真源=护照 JSON 内 model_id
        原样；文件名 `:`→`_` 为有损安全编码不可反推）。

        查询侧冒号/下划线形态互认（dispatch 链可能持任一形态）；存储键不改写、
        归一化只发生在查询侧（命中面不放大：两变体均不在册仍 miss）。
        """
        if model_id in self._passports:
            return model_id
        variants = [model_id.replace(":", "_"), model_id.replace("_", ":")]
        for alt in variants:
            if alt != model_id and alt in self._passports:
                return alt
        return None

    def can_dispatch(self, model_id: str, capability: str) -> tuple[bool, str]:
        key = self._resolve_key(model_id)
        if key is None:
            return (False, "no_passport")
        passport = self._passports[key]

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
        key = self._resolve_key(model_id)
        if key is None:
            return False
        return len(self._passports[key].recommendations.safe_capabilities) > 0

    def get_safe_capabilities(self, model_id: str) -> list[str]:
        key = self._resolve_key(model_id)
        if key is None:
            return []
        return list(self._passports[key].recommendations.safe_capabilities)

    def get_unsafe_capabilities(self, model_id: str) -> list[str]:
        key = self._resolve_key(model_id)
        if key is None:
            return []
        return list(self._passports[key].recommendations.unsafe_capabilities)

    def get_passport(self, model_id: str) -> CapabilityPassport | None:
        key = self._resolve_key(model_id)
        return self._passports.get(key) if key is not None else None

    def has_passport(self, model_id: str) -> bool:
        return self._resolve_key(model_id) is not None

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
