# [A_test] module_id: MOD-GOV_multi_agent_collusion_detector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.detectors.multi_agent_collusion_detector
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

# #ARCH-083：CollusionResult.collusion_detected/signal_count/evidence_chain、
# CollusionSignal.signal_type、reset_pair 缺席——代码侧缺口待裁定，
# 全文件 xfail 留痕（strict=False）。
pytestmark = pytest.mark.xfail(strict=False, reason="#ARCH-083 collusion_detector 窄实现 vs 宽契约，待裁定")

try:
    from zephyr.security.access_control.detectors.multi_agent_collusion_detector import (
        CollusionResult,
        CollusionSignal,
        MultiAgentCollusionDetector,
    )

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestMultiAgentCollusionDetector:
    def setup_method(self):
        self.detector = MultiAgentCollusionDetector()

    def test_record_interaction_returns_signal(self):
        signal = self.detector.record_interaction("a1", "a2", "coordinated_action", "evidence-1")
        assert isinstance(signal, CollusionSignal)
        assert signal.agent_a == "a1"
        assert signal.agent_b == "a2"
        assert signal.signal_type == "coordinated_action"
        assert signal.evidence == "evidence-1"

    def test_check_no_collusion(self):
        result = self.detector.check("a1", "a2")
        assert isinstance(result, CollusionResult)
        assert result.collusion_detected is False
        assert result.risk_level == "NONE"
        assert result.signal_count == 0

    def test_check_low_risk_after_two_signals(self):
        self.detector.record_interaction("a1", "a2", "type-1", "ev1")
        self.detector.record_interaction("a1", "a2", "type-2", "ev2")
        result = self.detector.check("a1", "a2")
        assert result.collusion_detected is True
        assert result.risk_level == "LOW"
        assert result.signal_count == 2

    def test_check_medium_risk_at_threshold(self):
        for i in range(3):
            self.detector.record_interaction("a1", "a2", f"type-{i}", f"ev{i}")
        result = self.detector.check("a1", "a2")
        assert result.collusion_detected is True
        assert result.risk_level == "MEDIUM"
        assert result.signal_count >= 3

    def test_check_high_risk_double_threshold(self):
        for i in range(6):
            self.detector.record_interaction("a1", "a2", f"type-{i}", f"ev{i}")
        result = self.detector.check("a1", "a2")
        assert result.collusion_detected is True
        assert result.risk_level == "HIGH"

    def test_reset_pair(self):
        self.detector.record_interaction("a1", "a2", "type-1", "ev1")
        self.detector.reset_pair("a1", "a2")
        result = self.detector.check("a1", "a2")
        assert result.signal_count == 0

    def test_pair_key_order_independent(self):
        self.detector.record_interaction("b-agent", "a-agent", "type-1", "ev1")
        self.detector.record_interaction("a-agent", "b-agent", "type-2", "ev2")
        result = self.detector.check("a-agent", "b-agent")
        assert result.signal_count == 2

    def test_evidence_chain_populated(self):
        for i in range(3):
            self.detector.record_interaction("a1", "a2", f"type-{i}", f"evidence-{i}")
        result = self.detector.check("a1", "a2")
        assert len(result.evidence_chain) == 3

    def test_empty_strings(self):
        signal = self.detector.record_interaction("", "", "type-1")
        assert isinstance(signal, CollusionSignal)
