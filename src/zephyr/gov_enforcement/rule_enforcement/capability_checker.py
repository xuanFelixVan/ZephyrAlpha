# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.capability_checker
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES] zephyr.gov_audit.bridge; zephyr.gov_enforcement.rule_enforcement.cbac_matrix
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
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测

"""
能力检查器（Capability Checker）

依据：MOD-MASTER_BLUEPRINT 蓝图 §十五 CT-CBAC-001
Runtime capability_check() + checksum校验 + 离线更新流程 T。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: matrix 参数
#   fields: 参数 matrix（无注解）
#   code: capability_checker.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① CapabilityChecker
#   name_en: CapabilityChecker
#   intro: class CapabilityChecker 源码 L70-L109
#   desc: 公共方法（定义序）: capability_check, audit_log, get_checksum；源码 L70-L109
#   inputs: matrix
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: CapabilityChecker
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import logging

from zephyr.gov_audit.bridge import write_to_core
from zephyr.gov_enforcement.rule_enforcement.cbac_matrix import CbacMatrix

logger = logging.getLogger(__name__)


class AuditLogEntry:
    def __init__(self, action: str, caller: str, target: str, result: str, detail: str = ""):
        self.action = action
        self.caller = caller
        self.target = target
        self.result = result
        self.detail = detail


class CapabilityChecker:
    def __init__(self, matrix: CbacMatrix | None = None):
        self._matrix = matrix or CbacMatrix()
        self._audit_log: list[AuditLogEntry] = []

    def capability_check(self, caller: str, target: str, action: str) -> bool:
        allowed, reason = self._matrix.check(caller, target, action)

        entry = AuditLogEntry(
            action=action,
            caller=caller,
            target=target,
            result=reason,
        )

        if allowed:
            self._audit_log.append(entry)
            write_to_core("capability_check", {"action": action, "caller": caller, "target": target, "result": reason})
            return True

        logger.critical("CBAC DENIED: %s -> %s / %s — %s", caller, target, action, reason)
        self._audit_log.append(
            AuditLogEntry(
                action=action,
                caller=caller,
                target=target,
                result="DENIED",
                detail=reason,
            )
        )
        write_to_core(
            "capability_check_denied", {"action": action, "caller": caller, "target": target, "detail": reason}
        )
        return False

    def audit_log(self) -> list[AuditLogEntry]:
        return list(self._audit_log)

    def get_checksum(self) -> str:
        return self._matrix.checksum
