# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.breaking_change_detector
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_breaking_change_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Breaking Change 检测器（GATE-CDC-2）——字段删除/类型变更->CI FAIL。"""

from enum import Enum


class ChangeType(str, Enum):
    FIELD_REMOVED = "field_removed"
    TYPE_CHANGED = "type_changed"
    FIELD_ADDED_OPTIONAL = "field_added_optional"
    FIELD_ADDED_REQUIRED = "field_added_required"
    FIELD_RENAMED = "field_renamed"


class BreakingChangeDetector:
    BREAKING_CHANGES: set[ChangeType] = {
        ChangeType.FIELD_REMOVED,
        ChangeType.TYPE_CHANGED,
        ChangeType.FIELD_RENAMED,
        ChangeType.FIELD_ADDED_REQUIRED,
    }

    def is_breaking(self, change_type: ChangeType) -> bool:
        return change_type in self.BREAKING_CHANGES

    def detect(self, old_schema: dict, new_schema: dict) -> list[str]:
        breaking: list[str] = []
        old_fields = set(old_schema.get("fields", {}).keys())
        new_fields = set(new_schema.get("fields", {}).keys())

        removed = old_fields - new_fields
        for f in removed:
            breaking.append(f"FIELD_REMOVED: {f}")

        for f in old_fields & new_fields:
            if old_schema["fields"][f] != new_schema["fields"][f]:
                breaking.append(f"TYPE_CHANGED: {f}")

        return breaking
