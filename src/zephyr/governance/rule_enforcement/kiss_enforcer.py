# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.governance.rule_enforcement.kiss_enforcer
# [DOMAIN] D_GOV_RULE
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
# [A_module] module_id=MOD-GOV_kiss_enforcer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""KISS 约束执行器（CT-KISS-001）——AI产出复杂度检测+bloat check。"""


class KissEnforcer:
    MAX_CLASSES: int = 3
    MAX_METHOD_LINES: int = 30
    MAX_INHERITANCE: int = 2

    def check_class_count(self, class_count: int) -> tuple[bool, str]:
        if class_count > self.MAX_CLASSES:
            return False, f"类数 {class_count} > {self.MAX_CLASSES}"
        return True, "OK"

    def check_method_length(self, method_lines: int) -> tuple[bool, str]:
        if method_lines > self.MAX_METHOD_LINES:
            return False, f"方法行数 {method_lines} > {self.MAX_METHOD_LINES}"
        return True, "OK"

    def check_inheritance_depth(self, depth: int) -> tuple[bool, str]:
        if depth > self.MAX_INHERITANCE:
            return False, f"继承层次 {depth} > {self.MAX_INHERITANCE}"
        return True, "OK"

    def self_check(self, class_count: int, max_method_lines: int, inheritance_depth: int) -> bool:
        return (
            self.check_class_count(class_count)[0]
            and self.check_method_length(max_method_lines)[0]
            and self.check_inheritance_depth(inheritance_depth)[0]
        )
