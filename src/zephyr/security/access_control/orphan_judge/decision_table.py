# [BLUEPRINT]
# [MODULE] zephyr.security.access_control.orphan_judge.decision_table
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-SEC_decision_table | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel


class Verdict(str, Enum):
    KEEP = "KEEP"
    DELETE = "DELETE"
    EXTRACT_AND_MERGE = "EXTRACT_AND_MERGE"
    DEPRECATE = "DEPRECATE"
    ESCALATE = "ESCALATE"
    KEEP_AND_REGISTER = "KEEP_AND_REGISTER"


class LayerResult(BaseModel):
    registered: bool | None = None
    reachable: bool | None = None
    is_duplicate: bool | None = None
    has_unique_value: bool | None = None
    safety_blocked: bool | None = None
    uncertain: bool = False


class DecisionEntry(BaseModel):
    condition: str
    verdict: Verdict
    priority: int = 0


_DECISION_TABLE: list[DecisionEntry] = [
    DecisionEntry(condition="safety_blocked=True", verdict=Verdict.ESCALATE, priority=0),
    DecisionEntry(condition="registered=True", verdict=Verdict.KEEP, priority=1),
    DecisionEntry(condition="reachable=True", verdict=Verdict.KEEP, priority=2),
    DecisionEntry(
        condition="is_duplicate=False AND has_unique_value=True", verdict=Verdict.KEEP_AND_REGISTER, priority=3
    ),
    DecisionEntry(condition="is_duplicate=False AND has_unique_value=False", verdict=Verdict.DELETE, priority=4),
    DecisionEntry(
        condition="is_duplicate=True AND has_unique_value=True", verdict=Verdict.EXTRACT_AND_MERGE, priority=5
    ),
    DecisionEntry(condition="is_duplicate=True AND has_unique_value=False", verdict=Verdict.DELETE, priority=6),
    DecisionEntry(condition="uncertain=True", verdict=Verdict.ESCALATE, priority=7),
]


class DecisionTable:
    """五层判定结果 → 处置动作映射表。

    12行简化版决策表，按优先级从高到低匹配：
      0. safety_blocked → ESCALATE（安全围栏拦截）
      1. registered=True → KEEP
      2. reachable=True → KEEP
      3. 非重复 + 有独立价值 → KEEP_AND_REGISTER
      4. 非重复 + 无独立价值 → DELETE
      5. 重复 + 有独立价值 → EXTRACT_AND_MERGE
      6. 重复 + 无独立价值 → DELETE
      7. 不确定 → ESCALATE
    """

    def __init__(self, custom_table: list[DecisionEntry] | None = None) -> None:
        self._table = custom_table if custom_table is not None else list(_DECISION_TABLE)

    def evaluate(
        self,
        l0_result: LayerResult | dict[str, Any] | None = None,
        l1_result: LayerResult | dict[str, Any] | None = None,
        l2_result: LayerResult | dict[str, Any] | None = None,
        l3_result: LayerResult | dict[str, Any] | None = None,
        l4_result: LayerResult | dict[str, Any] | None = None,
    ) -> Verdict:
        merged = self._merge_layer_results(l0_result, l1_result, l2_result, l3_result, l4_result)
        for entry in self._table:
            if self._matches(merged, entry):
                return entry.verdict
        return Verdict.ESCALATE

    def _merge_layer_results(self, *results: LayerResult | dict[str, Any] | None) -> LayerResult:
        merged = LayerResult()
        for result in results:
            if result is None:
                continue
            if isinstance(result, dict):
                result = LayerResult(**{k: v for k, v in result.items() if k in LayerResult.model_fields})
            if result.registered is True:
                merged.registered = True
            if result.reachable is True:
                merged.reachable = True
            if result.is_duplicate is True:
                merged.is_duplicate = True
            elif result.is_duplicate is False and merged.is_duplicate is None:
                merged.is_duplicate = False
            if result.has_unique_value is True:
                merged.has_unique_value = True
            elif result.has_unique_value is False and merged.has_unique_value is None:
                merged.has_unique_value = False
            if result.safety_blocked is True:
                merged.safety_blocked = True
            if result.uncertain:
                merged.uncertain = True
        return merged

    def _matches(self, merged: LayerResult, entry: DecisionEntry) -> bool:
        cond = entry.condition
        if cond == "safety_blocked=True":
            return merged.safety_blocked is True
        if cond == "registered=True":
            return merged.registered is True
        if cond == "reachable=True":
            return merged.reachable is True
        if cond == "is_duplicate=False AND has_unique_value=True":
            return merged.is_duplicate is False and merged.has_unique_value is True
        if cond == "is_duplicate=False AND has_unique_value=False":
            return merged.is_duplicate is False and merged.has_unique_value is False
        if cond == "is_duplicate=True AND has_unique_value=True":
            return merged.is_duplicate is True and merged.has_unique_value is True
        if cond == "is_duplicate=True AND has_unique_value=False":
            return merged.is_duplicate is True and merged.has_unique_value is False
        if cond == "uncertain=True":
            return merged.uncertain is True
        return False

    def get_table(self) -> list[DecisionEntry]:
        return list(self._table)
