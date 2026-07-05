# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain-governance/audit-trail/blueprint.md
# [MODULE] zephyr.governance.audit_trail.wqa_scorer
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] MOD-INF-027;MOD-INF-015;MOD-FEEDBACK_LOOP
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 不可变审计记录;密码学完整性;只追加
# [MODIFY-GUARD] docs/03_modules/_domain-governance/audit-trail/blueprint.md;src/zephyr/audit-trail/__init__.py
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] IntegrityError;WriteError
# [TESTS] tests/test_audit_trail/
# [A_module] module_id=MOD-GOV_wqa_scorer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WQAScore:
    w1_test_coverage: float = 0.0
    w2_blueprint_alignment: float = 0.0
    w3_ruff_zero_warn: float = 0.0
    w4_gate_no_new_fail: float = 0.0
    w5_owner_no_revert: float = 0.0
    w6_session_completion: float = 0.0
    w7_token_efficiency: float = 0.0

    @property
    def composite(self) -> float:
        weights = {
            "w1": 0.20,
            "w2": 0.15,
            "w3": 0.10,
            "w4": 0.20,
            "w5": 0.15,
            "w6": 0.10,
            "w7": 0.10,
        }
        total = (
            self.w1_test_coverage * weights["w1"]
            + self.w2_blueprint_alignment * weights["w2"]
            + self.w3_ruff_zero_warn * weights["w3"]
            + self.w4_gate_no_new_fail * weights["w4"]
            + self.w5_owner_no_revert * weights["w5"]
            + self.w6_session_completion * weights["w6"]
            + self.w7_token_efficiency * weights["w7"]
        )
        return round(total, 3)

    @property
    def rating(self) -> str:
        c = self.composite
        if c >= 0.90:
            return "A+"
        if c >= 0.80:
            return "A"
        if c >= 0.70:
            return "B"
        if c >= 0.60:
            return "C"
        if c >= 0.50:
            return "D"
        return "F"


WQA_DIMENSIONS: dict[str, tuple[int, float, str]] = {
    "W1": (1, 0.20, "Test增量覆盖率"),
    "W2": (2, 0.15, "蓝图对齐度"),
    "W3": (3, 0.10, "ruff 0 warning"),
    "W4": (4, 0.20, "Gate不新增失败"),
    "W5": (5, 0.15, "Owner不回退"),
    "W6": (6, 0.10, "Session完成率"),
    "W7": (7, 0.10, "Token效率"),
}
