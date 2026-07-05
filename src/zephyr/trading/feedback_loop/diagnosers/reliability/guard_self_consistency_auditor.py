# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers.reliability.guard_self_consistency_auditor
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.diagnosers.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_guard_self_consistency_auditor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
R512: GuardSelfConsistencyAuditor
每个Guard监控自身pass/fail分布漂移 — >3σ = Guard自身故障
"""

from dataclasses import dataclass, field


@dataclass
class GuardHealthRecord:
    guard_id: str
    pass_count: int = 0
    fail_count: int = 0
    total_count: int = 0
    baseline_pass_rate: float | None = None


@dataclass
class GuardSelfConsistencyAuditor:
    guard_records: dict[str, GuardHealthRecord] = field(default_factory=dict)
    deviation_threshold: float = 3.0
    establish_baseline_after: int = 50

    def record_outcome(self, guard_id: str, passed: bool) -> None:
        if guard_id not in self.guard_records:
            self.guard_records[guard_id] = GuardHealthRecord(guard_id=guard_id)
        rec = self.guard_records[guard_id]

        if passed:
            rec.pass_count += 1
        else:
            rec.fail_count += 1
        rec.total_count += 1

        if rec.total_count == self.establish_baseline_after:
            rec.baseline_pass_rate = rec.pass_count / rec.total_count

    def audit_consistency(self) -> dict:
        findings = {}
        for guard_id, rec in self.guard_records.items():
            if rec.total_count < 10 or rec.baseline_pass_rate is None:
                continue

            current_rate = rec.pass_count / rec.total_count
            expected = rec.baseline_pass_rate
            n = rec.total_count
            std = (expected * (1 - expected) / n) ** 0.5

            deviation = abs(current_rate - expected) / max(std, 1e-10)

            status = "healthy"
            if deviation > self.deviation_threshold:
                if current_rate > 0.95:
                    status = "always_pass"
                elif current_rate < 0.05:
                    status = "always_fail"
                else:
                    status = "distribution_drifted"

            findings[guard_id] = {
                "status": status,
                "current_pass_rate": round(current_rate, 4),
                "baseline_pass_rate": round(expected, 4),
                "sigma_deviation": round(deviation, 2),
                "total_evaluations": rec.total_count,
                "is_healthy": status == "healthy",
            }

        unhealthy = {k: v for k, v in findings.items() if not v["is_healthy"]}
        return {
            "unhealthy_guards": list(unhealthy.keys()),
            "findings": findings,
            "total_guards_audited": len(findings),
            "silent_failures_detected": sum(
                1 for v in findings.values() if v["status"] in ("always_pass", "always_fail")
            ),
        }
