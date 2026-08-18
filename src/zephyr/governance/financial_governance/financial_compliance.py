# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.governance.financial_governance.financial_compliance
# [DOMAIN] D_GOV_AUDIT
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
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""financial_compliance — 金融合规框架目录（合规层/保障措施/协议定义）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 合规目录查询
#   fields: Protocol / Safeguard 枚举成员
#   code: get_protocol (L92) / get_safeguard (L96)
# 层: 算法
# - id: A1
#   name_zh: 合规目录声明
#   name_en: compliance_catalog_declare
#   intro: 三层合规(L1-L3)×7项保障措施×4协议的枚举与标签/定义字典
#   code: ComplianceLayer / Safeguard / Protocol / SAFEGUARD_LABELS / PROTOCOL_DEFS
# - id: A2
#   name_zh: 目录查询
#   name_en: catalog_lookup
#   intro: 按键查 PROTOCOL_DEFS / SAFEGUARD_LABELS，未命中返回 None/空
#   code: get_protocol (L92) / get_safeguard (L96)
# 层: 输出
# - id: O1
#   name_zh: 合规定义/标签
#   name_en: compliance_defs
#   intro: ProtocolDef / 中文标签字符串
#   downstream: 合规报告与审计消费者
# [/ALGO_FLOW]
# 边: I1 --> A1 ; A1 --> A2 ; A2 --> O1
"""

from enum import Enum
from typing import Final

from pydantic import BaseModel


class ComplianceLayer(str, Enum):
    L1_PREVENTATIVE = "L1_PREVENTATIVE"
    L2_DETECTIVE = "L2_DETECTIVE"
    L3_CORRECTIVE = "L3_CORRECTIVE"


class Safeguard(str, Enum):
    S1_ACCESS_CONTROL = "S1_ACCESS_CONTROL"
    S2_DATA_PROTECTION = "S2_DATA_PROTECTION"
    S3_AUDIT_TRAIL = "S3_AUDIT_TRAIL"
    S4_INCIDENT_RESPONSE = "S4_INCIDENT_RESPONSE"
    S5_BUSINESS_CONTINUITY = "S5_BUSINESS_CONTINUITY"
    S6_MODEL_RISK = "S6_MODEL_RISK"
    S7_INSIDER_THREAT = "S7_INSIDER_THREAT"


class Protocol(str, Enum):
    CLIENT_STATEMENT = "CLIENT_STATEMENT"
    MRM = "MRM"
    RECORD_KEEPING = "RECORD_KEEPING"
    INCIDENT_NOTIFICATION = "INCIDENT_NOTIFICATION"


class ProtocolDef(BaseModel):
    name: Protocol
    description: str
    owner: str = "Owner"
    review_date: str | None = None


SAFEGUARD_LABELS: Final[dict[Safeguard, str]] = {
    Safeguard.S1_ACCESS_CONTROL: "访问控制 — GateController + Role-Based Access",
    Safeguard.S2_DATA_PROTECTION: "数据保护 — Encryption + L1-L4 Classification",
    Safeguard.S3_AUDIT_TRAIL: "审计轨迹 — Every mutation logged",
    Safeguard.S4_INCIDENT_RESPONSE: "事件响应 — L1-L5 Incident Protocol",
    Safeguard.S5_BUSINESS_CONTINUITY: "业务连续性 — DR + Hot Restart",
    Safeguard.S6_MODEL_RISK: "模型风险 — SR11-7 + Drift Monitor",
    Safeguard.S7_INSIDER_THREAT: "内部威胁 — Dual AI Review + Session Auditing",
}

PROTOCOL_DEFS: Final[dict[Protocol, ProtocolDef]] = {
    Protocol.CLIENT_STATEMENT: ProtocolDef(
        name=Protocol.CLIENT_STATEMENT,
        description="每日客户对账单自动生成与加密分发",
        owner="Owner",
        review_date="2026-06-01",
    ),
    Protocol.MRM: ProtocolDef(
        name=Protocol.MRM,
        description="模型风险管理——季度审查+回测+漂移检测",
        owner="Owner",
        review_date="2026-06-01",
    ),
    Protocol.RECORD_KEEPING: ProtocolDef(
        name=Protocol.RECORD_KEEPING,
        description="交易记录保留——5年全量+7年索引",
        owner="Owner",
        review_date="2026-06-01",
    ),
    Protocol.INCIDENT_NOTIFICATION: ProtocolDef(
        name=Protocol.INCIDENT_NOTIFICATION,
        description="事故通知——L3+事故自动触发通知链",
        owner="Owner",
        review_date="2026-06-01",
    ),
}


def get_protocol(protocol: Protocol) -> ProtocolDef | None:
    return PROTOCOL_DEFS.get(protocol)


def get_safeguard(safeguard: Safeguard) -> str:
    return SAFEGUARD_LABELS.get(safeguard, str(safeguard))


FRAMEWORK_DIMENSIONS: Final[dict[str, int]] = {
    "compliance_layers": 3,
    "safeguards": 7,
    "protocols": 4,
}
