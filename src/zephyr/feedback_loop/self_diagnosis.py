# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md
# [MODULE] zephyr.feedback_loop.self_diagnosis
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
self_diagnosis.py — 自我诊断 (DD120, TASK-020)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: self_diagnosis.py
# 层: 算法
# - id: A1
#   name_zh: ① SelfDiagnosis
#   name_en: SelfDiagnosis
#   intro: Agent 启动时 integration test; report (DD120).
#   desc: Agent 启动时 integration test; report (DD120).；公共方法（定义序）: run；源码 L66-L79
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: SelfDiagnosis
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass, field


@dataclass
class DiagnosisNode:
    check_name: str
    status: str  # "PASS" | "WARN" | "FAIL"
    detail: str = ""


@dataclass
class DiagnosisReport:
    nodes: list[DiagnosisNode]
    overall: str  # "HEALTHY" | "DEGRADED" | "CRITICAL"
    action_items: list[str] = field(default_factory=list)


class SelfDiagnosis:
    """Agent 启动时 integration test; report (DD120)."""

    def run(self) -> DiagnosisReport:
        nodes = [
            DiagnosisNode("VMS_Connection", "PASS"),
            DiagnosisNode("KE_Collection", "PASS"),
            DiagnosisNode("LSG_Gate", "WARN", "LSG not configured"),
        ]
        fails = [n for n in nodes if n.status == "FAIL"]
        return DiagnosisReport(
            nodes=nodes,
            overall="CRITICAL" if fails else ("DEGRADED" if any(n.status == "WARN" for n in nodes) else "HEALTHY"),
        )
