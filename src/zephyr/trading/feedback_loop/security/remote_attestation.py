# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.security.remote_attestation
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-SEC_remote_attestation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Remote Attestation — v0.15.0 R211

Blindspot: FLE runtime integrity unverifiable remotely; trusted only by self-report.
Risk: R211 — Compromised FLE reports "I'm fine"; no hardware-rooted trust verification.

Mitigation: TPM-based remote attestation with runtime measurement verification.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AttestationReport:
    pcr_values: dict[int, str]
    quote: str
    signature: str
    verified: bool = False


@dataclass
class RemoteAttestation:
    reports: list[AttestationReport] = field(default_factory=list)
    expected_pcr_hashes: dict[int, str] = field(default_factory=dict)
    attestation_required: bool = True

    def verify(self, report: AttestationReport) -> bool:
        for pcr_idx, expected_hash in self.expected_pcr_hashes.items():
            if report.pcr_values.get(pcr_idx, "") != expected_hash:
                report.verified = False
                self.reports.append(report)
                return False
        report.verified = True
        self.reports.append(report)
        return True

    def last_verified(self) -> AttestationReport | None:
        return self.reports[-1] if self.reports else None
