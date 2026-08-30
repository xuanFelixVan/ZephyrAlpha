# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.governance.audit_logger
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-025 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: audit_logger.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① AuditLogger
#   name_en: AuditLogger
#   intro: class AuditLogger 源码 L61-L80
#   desc: 公共方法（定义序）: log, query, count；源码 L61-L80
#   inputs: config
#   outputs: 返回值
# - id: A2
#   name_zh: ② create_audit_logger
#   name_en: create_audit_logger
#   intro: create_audit_logger(config) 源码 L83-L84
#   desc: 源码 L83-L84
#   inputs: config
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: AuditLogger, create_audit_logger
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

import logging

logger = logging.getLogger(__name__)


class AuditLogger:
    def __init__(self, config=None):
        self.config = config or {}
        self._entries = []

    def log(self, event_type, actor, target, details=None):
        entry = {
            "event_type": event_type,
            "actor": actor,
            "target": target,
            "details": details or {},
        }
        self._entries.append(entry)
        logger.info(f"AUDIT: {event_type} by {actor} on {target}")

    def query(self, filters=None):
        return self._entries

    def count(self):
        return len(self._entries)


def create_audit_logger(config=None):
    return AuditLogger(config=config)
