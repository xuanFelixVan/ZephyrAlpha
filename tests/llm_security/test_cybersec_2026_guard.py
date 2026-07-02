# [A_test] module_id: SRC-TST-0692 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.guards.cybersec_2026_guard
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.access_control.guards.cybersec_2026_guard import (
        CYBERSEC_2026_VECTORS,
        Cybersec2026Guard,
        CyberSecVerdict,
    )

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestCyberSecVerdict:
    def test_defaults(self):
        v = CyberSecVerdict(threat_category="none")
        assert v.severity == "LOW"
        assert v.detected is False
        assert v.evidence == []
        assert v.recommendation == ""

    def test_with_values(self):
        v = CyberSecVerdict(
            threat_category="agent_supply_chain",
            severity="HIGH",
            detected=True,
            evidence=["untrusted_hub"],
            recommendation="review",
        )
        assert v.detected is True
        assert len(v.evidence) == 1


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestCybersec2026Guard:
    def test_scan_clean_context(self):
        guard = Cybersec2026Guard()
        result = guard.scan({"source": "internal", "model": "verified"})
        assert result.detected is False
        assert result.threat_category == "none"

    def test_scan_empty_context(self):
        guard = Cybersec2026Guard()
        result = guard.scan({})
        assert result.detected is False

    def test_scan_agent_supply_chain(self):
        guard = Cybersec2026Guard()
        result = guard.scan({"model_source": "untrusted_hub"})
        assert result.detected is True
        assert "agent_supply_chain" in result.threat_category
        assert "untrusted_hub" in result.evidence

    def test_scan_lmops_backdoor(self):
        guard = Cybersec2026Guard()
        result = guard.scan({"training": "hidden_training_trigger detected"})
        assert result.detected is True
        assert "lmops_backdoor" in result.threat_category

    def test_scan_synthetic_identity(self):
        guard = Cybersec2026Guard()
        result = guard.scan({"user": "identity_out_of_band"})
        assert result.detected is True
        assert "synthetic_identity" in result.threat_category

    def test_scan_multi_modal_jailbreak(self):
        guard = Cybersec2026Guard()
        result = guard.scan({"input": "image_embedded_prompt found"})
        assert result.detected is True
        assert "multi_modal_jailbreak" in result.threat_category

    def test_scan_multiple_evidence_high_severity(self):
        guard = Cybersec2026Guard()
        result = guard.scan({"data": "untrusted_hub and unverified_model found"})
        assert result.severity == "HIGH"
        assert len(result.evidence) >= 2

    def test_scan_single_evidence_medium_severity(self):
        guard = Cybersec2026Guard()
        result = guard.scan({"data": "untrusted_hub found"})
        assert result.severity == "MEDIUM"

    def test_vectors_constant(self):
        assert len(CYBERSEC_2026_VECTORS) == 4
        assert "agent_supply_chain" in CYBERSEC_2026_VECTORS
        assert "lmops_backdoor" in CYBERSEC_2026_VECTORS
        assert "synthetic_identity" in CYBERSEC_2026_VECTORS
        assert "multi_modal_jailbreak" in CYBERSEC_2026_VECTORS
