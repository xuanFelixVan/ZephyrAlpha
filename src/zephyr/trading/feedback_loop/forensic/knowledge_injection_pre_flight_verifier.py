# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.forensic.knowledge_injection_pre_flight_verifier
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-UNK_knowledge_injection_pre_flight_verifier | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
R515: KnowledgeInjectionPreFlightVerifier
新规则干跑验证 — 在历史事件上回测，净收益>阈值才部署
"""

from dataclasses import dataclass, field


@dataclass
class DryRunResult:
    rule_id: str
    caught_incident_earlier: bool = False
    false_positives: int = 0
    true_positives: int = 0
    net_benefit: float = 0.0


@dataclass
class KnowledgeInjectionPreFlightVerifier:
    historical_incidents: list[dict] = field(default_factory=list)
    max_stored_incidents: int = 50
    benefit_threshold: float = 0.2
    dry_run_log: list[DryRunResult] = field(default_factory=list)

    def add_historical_incident(self, incident: dict) -> None:
        self.historical_incidents.append(incident)
        if len(self.historical_incidents) > self.max_stored_incidents:
            self.historical_incidents = self.historical_incidents[-self.max_stored_incidents :]

    def verify_rule(self, rule: dict) -> dict:
        rule_id = rule.get("rule_id", "unknown")
        true_positives = 0
        false_positives = 0
        early_catches = 0

        for incident in self.historical_incidents:
            if self._rule_would_catch(rule, incident):
                true_positives += 1
                if incident.get("would_detect_earlier"):
                    early_catches += 1
            else:
                false_positives += 1

        net_benefit = (true_positives * 1.0 - false_positives * 0.3) / max(len(self.historical_incidents), 1)

        result = DryRunResult(
            rule_id=rule_id,
            caught_incident_earlier=early_catches > 0,
            false_positives=false_positives,
            true_positives=true_positives,
            net_benefit=net_benefit,
        )
        self.dry_run_log.append(result)
        if len(self.dry_run_log) > 100:
            self.dry_run_log = self.dry_run_log[-100:]

        return {
            "rule_id": rule_id,
            "approved": net_benefit > self.benefit_threshold,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "net_benefit": round(net_benefit, 3),
            "early_catches": early_catches,
            "total_incidents_tested": len(self.historical_incidents),
            "recommendation": "DEPLOY" if net_benefit > self.benefit_threshold else "REJECT",
        }

    @staticmethod
    def _rule_would_catch(rule: dict, incident: dict) -> bool:
        condition = rule.get("condition", "")
        incident_metrics = incident.get("metrics", {})
        threshold = rule.get("threshold", 0)
        rule_type = rule.get("rule_type", "detection")

        if rule_type == "threshold":
            for metric_name, metric_value in incident_metrics.items():
                if isinstance(metric_value, (int, float)) and metric_name in condition:
                    if metric_value > threshold:
                        return True
            return False

        return False
