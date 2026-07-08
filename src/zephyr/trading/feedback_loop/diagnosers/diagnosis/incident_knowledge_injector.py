# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers.diagnosis.incident_knowledge_injector
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.diagnosers.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_incident_knowledge_injector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
R504: IncidentKnowledgeInjector
RCA发现->规则/阈值自动注入闭环 — 不让知识腐烂
对标: SRE Blameless Postmortem -> Action Items automation
"""

import hashlib
from dataclasses import dataclass, field


@dataclass
class InjectedRule:
    rule_id: str
    source_rca_id: str
    rule_type: str
    condition: str
    threshold: float
    created_at: float
    validated: bool = False
    active: bool = False


@dataclass
class IncidentKnowledgeInjector:
    injected_rules: dict[str, InjectedRule] = field(default_factory=dict)
    max_rules_per_rca: int = 5
    total_rules_injected: int = 0

    def extract_and_inject(self, rca_findings: dict) -> list[str]:
        new_rule_ids = []

        root_causes = rca_findings.get("root_causes", [])
        for cause in root_causes[: self.max_rules_per_rca]:
            rule = self._cause_to_rule(cause, rca_findings.get("incident_id", "unknown"))
            if rule:
                self.injected_rules[rule.rule_id] = rule
                self.total_rules_injected += 1
                new_rule_ids.append(rule.rule_id)

        metrics = rca_findings.get("metric_deviations", {})
        for metric, deviation in list(metrics.items())[:2]:
            threshold_rule = self._deviation_to_threshold_rule(
                metric, deviation, rca_findings.get("incident_id", "unknown")
            )
            if threshold_rule:
                self.injected_rules[threshold_rule.rule_id] = threshold_rule
                self.total_rules_injected += 1
                new_rule_ids.append(threshold_rule.rule_id)

        return new_rule_ids

    def validate_rules(self) -> dict:
        results = {}
        for rule_id, rule in self.injected_rules.items():
            if not rule.validated:
                rule.validated = True
                rule.active = self._validate_single_rule(rule)
                results[rule_id] = {"active": rule.active}
        return results

    def get_active_rules(self) -> list[dict]:
        return [
            {
                "rule_id": r.rule_id,
                "type": r.rule_type,
                "condition": r.condition,
                "threshold": r.threshold,
                "source": r.source_rca_id,
            }
            for r in self.injected_rules.values()
            if r.active
        ]

    def _cause_to_rule(self, cause: str, incident_id: str) -> InjectedRule | None:
        if len(cause) < 10:
            return None
        rule_id = f"INJ-{hashlib.md5(cause.encode()).hexdigest()[:8]}"
        return InjectedRule(
            rule_id=rule_id,
            source_rca_id=incident_id,
            rule_type="detection",
            condition=cause[:200],
            threshold=0.5,
            created_at=__import__("time").time(),
        )

    def _deviation_to_threshold_rule(self, metric: str, deviation: float, incident_id: str) -> InjectedRule | None:
        rule_id = f"THR-{hashlib.md5(f'{metric}_{deviation}'.encode()).hexdigest()[:8]}"
        new_threshold = abs(deviation) * 1.2
        return InjectedRule(
            rule_id=rule_id,
            source_rca_id=incident_id,
            rule_type="threshold",
            condition=f"{metric} > {new_threshold:.4f}",
            threshold=new_threshold,
            created_at=__import__("time").time(),
        )

    @staticmethod
    def _validate_single_rule(rule: InjectedRule) -> bool:
        if rule.threshold <= 0:
            return False
        if len(rule.condition) < 5:
            return False
        return True
