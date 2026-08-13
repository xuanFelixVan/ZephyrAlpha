# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic-auditor/blueprint.md
# [MODULE] zephyr.governance.semantic_audit.compliance_map
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_audit.models
# [CONSUMERS] 见蓝图 §4 接口契约
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 蓝图 §4 文件清单与代码双向对齐
# [MODIFY-GUARD] semantic-auditor/blueprint.md; semantic-auditor/__init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SemanticAuditError
# [TESTS] tests/semantic-auditor/
# [A_module] module_id=MOD-INF-028 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

[BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic-auditor/blueprint.md

audit-trail.compliance_map — MOD-INF-020 · 合规框架映射

========================================================

蓝图 D-020-25 · GDPR/HIPAA/EU AI Act/NIST 映射表

映射规则

--------

  将审计事件类型映射到合规框架的具体条款/要求

  支持多框架交叉映射

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 审计事件类型 event_type（字符串）
#   fields: AuditEventType.value 小写串，如 file_write / permission_violation
#   code: compliance_map.py L305 map_event(event_type)
# - id: I2
#   name: 自定义合规映射 custom_mappings（dict，可选）
#   fields: {event_type: [ComplianceRequirement]}
#   code: compliance_map.py L294 __init__(custom_mappings)
# - id: I3
#   name: 合规框架过滤 framework（枚举，可选）
#   fields: GDPR/HIPAA/EU_AI_ACT/NIST/SOC2/ISO27001
#   code: compliance_map.py L314 get_requirements(framework)
# 层: 算法
# - id: A1
#   name_zh: ① 内置合规映射表
#   name_en: _COMPLIANCE_TABLE
#   intro: 10 类审计事件到 6 大合规框架条款/严重度的静态映射
#   desc: compliance_map.py L87-290，事件 → ComplianceRequirement(framework/article/title/description/severity) 列表
#   inputs: I1
#   outputs: 内置要求清单
# - id: A2
#   name_zh: ② 自定义映射合并
#   name_en: ComplianceMapper.__init__
#   intro: 复制内置表后合并自定义映射：已存在事件 extend、新事件直接挂载
#   desc: L295-303：dict(_COMPLIANCE_TABLE) 拷贝 → event_type 存在则 extend(requirements) 否则整体赋值
#   inputs: I2
#   outputs: 合并后映射表 self._mappings
# - id: A3
#   name_zh: ③ 事件映射查询
#   name_en: map_event
#   intro: 按事件类型查表并封装带 UTC 时间戳的 ComplianceMapping
#   desc: L305-312：self._mappings.get(event_type, []) → ComplianceMapping(event_type, requirements, mapped_at=now(UTC))
#   inputs: A1 A2 I1
#   outputs: ComplianceMapping
# - id: A4
#   name_zh: ④ 框架/事件双条件过滤
#   name_en: get_requirements
#   intro: 按框架（可选）与事件（可选）过滤聚合要求清单
#   desc: L314-332：event_type 命中则只扫该事件，否则全表；逐条过滤 req.framework != framework
#   inputs: A2 I3 I1
#   outputs: list[ComplianceRequirement]
# - id: A5
#   name_zh: ⑤ 事件涉及框架去重
#   name_en: get_frameworks_for_event
#   intro: 对事件映射结果按框架枚举 set 去重
#   desc: L334-337：map_event 后 list({r.framework for r in requirements})
#   inputs: A3
#   outputs: list[ComplianceFramework]
# 层: 输出
# - id: O1
#   name_zh: ComplianceMapping 事件合规映射
#   name_en: ComplianceMapping
#   intro: 事件类型 → 合规要求清单 + mapped_at 时间戳（pydantic extra=forbid）
#   downstream: semantic_audit 包 __init__ re-export；蓝图 §4 接口契约（[CONSUMERS]）
# - id: O2
#   name_zh: 合规要求/框架查询列表
#   name_en: list[ComplianceRequirement] / list[ComplianceFramework]
#   intro: 过滤后的要求清单或事件涉及框架列表
#   downstream: semantic_audit 包内审计器内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A2
# A1 --> A3
# A2 --> A3
# I1 --> A3
# A2 --> A4
# I3 --> A4
# I1 --> A4
# A3 --> A5
# A3 --> O1
# A4 --> O2
# A5 --> O2
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from zephyr.gov_audit.models import AuditEventType

_logger = logging.getLogger(__name__)


class ComplianceFramework(str, Enum):
    GDPR = "gdpr"

    HIPAA = "hipaa"

    EU_AI_ACT = "eu_ai_act"

    NIST = "nist"

    SOC2 = "soc2"

    ISO27001 = "iso27001"


class ComplianceRequirement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    framework: ComplianceFramework = ComplianceFramework.GDPR

    article: str = ""

    title: str = ""

    description: str = ""

    severity: str = "medium"


class ComplianceMapping(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_type: str = ""

    requirements: list[ComplianceRequirement] = Field(default_factory=list)

    mapped_at: str = ""


_COMPLIANCE_TABLE: dict[str, list[ComplianceRequirement]] = {
    AuditEventType.PERMISSION_VIOLATION.value: [
        ComplianceRequirement(
            framework=ComplianceFramework.GDPR,
            article="Art.25",
            title="Data Protection by Design",
            description="Access control violations must be logged",
            severity="high",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.NIST,
            article="AC-2",
            title="Account Management",
            description="Unauthorized access attempts must be audited",
            severity="high",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.SOC2,
            article="CC6.1",
            title="Logical Access",
            description="Access violations tracked",
            severity="high",
        ),
    ],
    AuditEventType.FILE_DELETE.value: [
        ComplianceRequirement(
            framework=ComplianceFramework.GDPR,
            article="Art.17",
            title="Right to Erasure",
            description="Data deletion must be recorded",
            severity="high",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.HIPAA,
            article="164.312(b)",
            title="Audit Controls",
            description="Record information system activity",
            severity="high",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.NIST,
            article="AU-2",
            title="Audit Events",
            description="Delete operations must be auditable",
            severity="medium",
        ),
    ],
    AuditEventType.FILE_WRITE.value: [
        ComplianceRequirement(
            framework=ComplianceFramework.GDPR,
            article="Art.30",
            title="Records of Processing",
            description="Data modification must be logged",
            severity="medium",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.HIPAA,
            article="164.312(b)",
            title="Audit Controls",
            description="Record system activity including writes",
            severity="medium",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.NIST,
            article="AU-2",
            title="Audit Events",
            description="Write operations must be auditable",
            severity="medium",
        ),
    ],
    AuditEventType.ANOMALY_DETECTED.value: [
        ComplianceRequirement(
            framework=ComplianceFramework.GDPR,
            article="Art.33",
            title="Breach Notification",
            description="Anomalies may indicate data breaches",
            severity="high",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.HIPAA,
            article="164.312(b)",
            title="Audit Controls",
            description="Anomaly detection supports audit review",
            severity="medium",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.EU_AI_ACT,
            article="Art.14",
            title="Human Oversight",
            description="Anomalies require human review",
            severity="high",
        ),
    ],
    AuditEventType.TRUST_SCORE_CHANGE.value: [
        ComplianceRequirement(
            framework=ComplianceFramework.EU_AI_ACT,
            article="Art.9",
            title="Risk Management",
            description="Trust score changes indicate risk level changes",
            severity="medium",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.NIST,
            article="RA-3",
            title="Risk Assessment",
            description="Trust changes must be tracked for risk management",
            severity="medium",
        ),
    ],
    AuditEventType.KB_POISONING_ATTEMPT.value: [
        ComplianceRequirement(
            framework=ComplianceFramework.EU_AI_ACT,
            article="Art.15",
            title="Accuracy and Robustness",
            description="KB poisoning threatens AI system integrity",
            severity="critical",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.NIST,
            article="SI-3",
            title="Malicious Code Protection",
            description="Poisoning is a form of malicious content injection",
            severity="high",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.GDPR,
            article="Art.25",
            title="Data Protection by Design",
            description="Input validation required",
            severity="high",
        ),
    ],
    AuditEventType.SUPPLY_CHAIN_INSTALL.value: [
        ComplianceRequirement(
            framework=ComplianceFramework.NIST,
            article="SR-3",
            title="Supply Chain Protection",
            description="Package integrity must be verified",
            severity="high",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.EU_AI_ACT,
            article="Art.15",
            title="Accuracy and Robustness",
            description="Supply chain integrity affects AI robustness",
            severity="medium",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.ISO27001,
            article="A.15",
            title="Supplier Relationships",
            description="Supply chain security controls",
            severity="medium",
        ),
    ],
    AuditEventType.DELEGATION_CHAIN_ISSUE.value: [
        ComplianceRequirement(
            framework=ComplianceFramework.GDPR,
            article="Art.25",
            title="Data Protection by Design",
            description="Delegation must enforce least privilege",
            severity="high",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.NIST,
            article="AC-4",
            title="Information Flow Enforcement",
            description="Delegation chains must be controlled",
            severity="high",
        ),
    ],
    AuditEventType.FEEDBACK_LOOP_SELF_REINFORCING.value: [
        ComplianceRequirement(
            framework=ComplianceFramework.EU_AI_ACT,
            article="Art.9",
            title="Risk Management",
            description="Self-reinforcing loops create systemic risk",
            severity="high",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.NIST,
            article="SI-4",
            title="System Monitoring",
            description="Feedback loops must be monitored",
            severity="medium",
        ),
    ],
    AuditEventType.DRIFT_DETECTED.value: [
        ComplianceRequirement(
            framework=ComplianceFramework.EU_AI_ACT,
            article="Art.15",
            title="Accuracy and Robustness",
            description="Drift affects AI accuracy",
            severity="high",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.NIST,
            article="SI-4",
            title="System Monitoring",
            description="Drift indicates system changes",
            severity="medium",
        ),
    ],
}


class ComplianceMapper:
    def __init__(self, custom_mappings: dict[str, list[ComplianceRequirement]] | None = None) -> None:
        self._mappings: dict[str, list[ComplianceRequirement]] = dict(_COMPLIANCE_TABLE)

        if custom_mappings:
            for event_type, requirements in custom_mappings.items():
                if event_type in self._mappings:
                    self._mappings[event_type].extend(requirements)

                else:
                    self._mappings[event_type] = requirements

    def map_event(self, event_type: str) -> ComplianceMapping:
        requirements = self._mappings.get(event_type, [])

        return ComplianceMapping(
            event_type=event_type,
            requirements=requirements,
            mapped_at=datetime.now(UTC).isoformat(),
        )

    def get_requirements(
        self,
        framework: ComplianceFramework | None = None,
        event_type: str | None = None,
    ) -> list[ComplianceRequirement]:
        requirements: list[ComplianceRequirement] = []

        source = (
            {event_type: self._mappings[event_type]} if event_type and event_type in self._mappings else self._mappings
        )

        for reqs in source.values():
            for req in reqs:
                if framework and req.framework != framework:
                    continue

                requirements.append(req)

        return requirements

    def get_frameworks_for_event(self, event_type: str) -> list[ComplianceFramework]:
        mapping = self.map_event(event_type)

        return list({r.framework for r in mapping.requirements})
