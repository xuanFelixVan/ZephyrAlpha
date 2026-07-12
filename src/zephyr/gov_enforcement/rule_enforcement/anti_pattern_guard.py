# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.anti_pattern_guard
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-GOV_anti_pattern_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Anti-Patterns 防护引擎（Anti-Pattern Guard）

依据：MOD-MASTER-002 蓝图 §七 Anti-Patterns
实现 AP1~AP8 八条 AI 集成行为禁止规则的运行时强制执行。

每条 AP 实现为独立 check 方法，集成到 Gate Engine 调用链中。
"""

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class APViolation(BaseModel):
    ap_id: str
    description: str
    agent_id: str = ""
    context: dict = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AntiPatternGuard:
    def __init__(self):
        self._violations: list[APViolation] = []

    def violations(self) -> list[APViolation]:
        return list(self._violations)

    def check_ap1_bypass_contract(self, target_system: str, has_ct_contract: bool, agent_id: str = "") -> bool:
        if not has_ct_contract:
            self._violations.append(
                APViolation(
                    ap_id="AP1",
                    description=f"绕过集成契约：未登记 CT-* 的跨系统调用 -> {target_system}",
                    agent_id=agent_id,
                    context={"target_system": target_system, "has_ct": False},
                )
            )
            return False
        return True

    def check_ap2_silent_exception(self, has_audit_log: bool, agent_id: str = "") -> bool:
        if not has_audit_log:
            self._violations.append(
                APViolation(
                    ap_id="AP2",
                    description="静默吞异常：degrade 路径未记录 audit_log",
                    agent_id=agent_id,
                    context={"has_audit_log": False},
                )
            )
            return False
        return True

    def check_ap3_ignore_circuit_breaker(self, circuit_open: bool, agent_id: str = "") -> bool:
        if circuit_open:
            self._violations.append(
                APViolation(
                    ap_id="AP3",
                    description="忽略熔断器：circuit_breaker OPEN 时仍然调用",
                    agent_id=agent_id,
                    context={"circuit_open": True},
                )
            )
            return False
        return True

    def check_ap4_code_over_document(
        self, tier0_value: object, code_value: object, fact_id: str = "", agent_id: str = ""
    ) -> bool:
        if tier0_value != code_value:
            self._violations.append(
                APViolation(
                    ap_id="AP4",
                    description=f"文档代码不一致时以代码为准（反Tier0）：{fact_id} Tier0={tier0_value!r} Code={code_value!r}",
                    agent_id=agent_id,
                    context={"fact_id": fact_id, "tier0": str(tier0_value), "code": str(code_value)},
                )
            )
            return False
        return True

    def check_ap5_modify_upstream(self, is_upstream_modification: bool, has_finding: bool, agent_id: str = "") -> bool:
        if is_upstream_modification and not has_finding:
            self._violations.append(
                APViolation(
                    ap_id="AP5",
                    description="修改上游蓝图未先创建 Finding",
                    agent_id=agent_id,
                    context={"is_upstream": True, "has_finding": False},
                )
            )
            return False
        return True

    def check_ap6_shared_mutable_state(self, share_path: str, is_ct_path: bool, agent_id: str = "") -> bool:
        if not is_ct_path:
            self._violations.append(
                APViolation(
                    ap_id="AP6",
                    description=f"跨系统共享可变状态（非CT-*路径）：{share_path}",
                    agent_id=agent_id,
                    context={"share_path": share_path, "is_ct_path": False},
                )
            )
            return False
        return True

    def check_ap7_ignore_gate_decision(self, gate_result: str, agent_id: str = "") -> bool:
        if gate_result == "FAIL":
            self._violations.append(
                APViolation(
                    ap_id="AP7",
                    description="忽略门禁裁决：G0-G7 门禁 FAIL 仍继续执行",
                    agent_id=agent_id,
                    context={"gate_result": "FAIL"},
                )
            )
            return False
        return True

    def check_ap8_session_orphan_tasks(self, orphan_count: int, session_id: str = "", agent_id: str = "") -> bool:
        if orphan_count > 0:
            self._violations.append(
                APViolation(
                    ap_id="AP8",
                    description=f"跨 Session 遗留在途任务：{orphan_count} 个未清理 task",
                    agent_id=agent_id,
                    context={"orphan_count": orphan_count, "session_id": session_id},
                )
            )
            return False
        return True
