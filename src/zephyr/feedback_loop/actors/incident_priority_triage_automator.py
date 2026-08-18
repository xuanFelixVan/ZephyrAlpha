# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.actors.incident_priority_triage_automator
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
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

"""Incident Priority Triage Automator — v0.37.0 R463

Blindspot: Security/operational incidents arrive at varying velocities;
manual triage causes delay in critical response.

Risk: R463 — Low-priority incident blocks response to high-priority one.

Mitigation: Automated SEV-level classification based on blast radius,
data sensitivity, and system criticality. P0/P1 auto-page; P3/P4 batch.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 安全/运维事件
#   fields: incident(data_sensitive / user_facing / system_critical / blast_radius)
#   code: IncidentPriorityTriageAutomator.triage
# 层: 算法
# - id: A1
#   name_zh: SEV 评分分级
#   name_en: severity_score_classification
#   intro: 数据敏感+3、用户可见+2、系统关键+2、爆炸半径≤4 累加，总分映射 P0-P4
#   code: IncidentPriorityTriageAutomator.classify
# - id: A2
#   name_zh: 分诊动作裁决
#   name_en: triage_action_decision
#   intro: 严重度优于等于 auto_page_threshold(P1) → PAGE，否则 BATCH 批量处理
#   code: IncidentPriorityTriageAutomator.triage
# 层: 输出
# - id: O1
#   name_zh: 分诊结果
#   name_en: triage_result
#   intro: 带 severity 与 action(PAGE/BATCH) 的事件 dict，并累计 triage_count
#   downstream: 告警通道与值班响应（secondary_alert_channel / owner）
# [/ALGO_FLOW]
# 边: I1 --> A1 ; A1 --> A2 ; A2 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


@dataclass
class IncidentPriorityTriageAutomator:
    auto_page_threshold: Severity = Severity.P1
    batch_window: float = 600.0

    incidents: list[dict] = field(default_factory=list)
    triage_count: dict[str, int] = field(default_factory=lambda: {s.value: 0 for s in Severity})

    def classify(self, incident: dict) -> Severity:
        score = 0
        if incident.get("data_sensitive", False):
            score += 3
        if incident.get("user_facing", False):
            score += 2
        if incident.get("system_critical", False):
            score += 2
        blast = incident.get("blast_radius", 0)
        score += min(blast, 4)

        if score >= 7:
            return Severity.P0
        elif score >= 5:
            return Severity.P1
        elif score >= 3:
            return Severity.P2
        elif score >= 1:
            return Severity.P3
        return Severity.P4

    def triage(self, incident: dict) -> dict:
        severity = self.classify(incident)
        incident["severity"] = severity.value
        incident["triaged_at"] = __import__("time").time()
        self.incidents.append(incident)
        self.triage_count[severity.value] = self.triage_count.get(severity.value, 0) + 1

        should_page = self._severity_rank(severity) <= self._severity_rank(self.auto_page_threshold)
        return {
            **incident,
            "action": "PAGE" if should_page else "BATCH",
            "severity": severity.value,
        }

    @staticmethod
    def _severity_rank(s: Severity) -> int:
        return list(Severity).index(s)

    def get_counts(self) -> dict:
        return dict(self.triage_count)
