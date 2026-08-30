# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.blueprint_tools.blueprint_code_auditor
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.governance.__init__ ; zephyr.gov_enforcement.rule_enforcement.gate_engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: blueprint_code_auditor.py
# 层: 算法
# - id: A1
#   name_zh: ① BlueprintCodeAuditor
#   name_en: BlueprintCodeAuditor
#   intro: class BlueprintCodeAuditor 源码 L72-L103
#   desc: 公共方法（定义序）: check_file_header, check_drift, audit, get_drifts, clear；源码 L72-L103
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: BlueprintCodeAuditor
#   downstream: zephyr.governance.__init__ ; zephyr.gov_enforcement.rule_enforcement.gate_engine
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DriftFinding:
    blueprint_section: str
    code_file: str
    drift_type: str
    description: str


@dataclass
class AuditReport:
    blueprint_path: str
    findings: list[DriftFinding]
    drift_count: int
    compliant: bool


DriftItem = DriftFinding


class BlueprintCodeAuditor:
    def __init__(self):
        self._findings: list[DriftFinding] = []

    def check_file_header(self, blueprint_id: str, code_file: str, header_blueprint_field: str) -> DriftFinding | None:
        if blueprint_id not in header_blueprint_field:
            finding = DriftFinding(
                blueprint_id, code_file, "header_mismatch", f"Blueprint {blueprint_id} not in [BLUEPRINT] field"
            )
            self._findings.append(finding)
            return finding
        return None

    def check_drift(
        self, blueprint_path: str, code_path: str, expected_field: str, actual_value: str | None
    ) -> DriftFinding | None:
        if actual_value is None:
            drift = DriftFinding(
                blueprint_path, code_path, "missing_field", f"Field '{expected_field}' not found in code"
            )
            self._findings.append(drift)
            return drift
        return None

    def audit(self, blueprint_path: str) -> AuditReport:
        return AuditReport(blueprint_path, list(self._findings), len(self._findings), len(self._findings) == 0)

    def get_drifts(self) -> list[DriftFinding]:
        return list(self._findings)

    def clear(self) -> None:
        self._findings.clear()
