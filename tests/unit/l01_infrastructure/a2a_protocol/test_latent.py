# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l01_infrastructure.a2a_protocol.test_latent
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""测试: LatentComm"""

from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_latent_comm import (
    A2ALatentComm,
    LatentCommSignal,
)


def test_detect_no_shared_resources():
    lc = A2ALatentComm()
    lc.record_access("agent-a", "file1.py")
    lc.record_access("agent-b", "file2.py")
    signals = lc.detect()
    assert signals == []


def test_detect_shared_resource():
    lc = A2ALatentComm(confidence_threshold=0.5)
    lc.record_access("agent-a", "shared.py")
    lc.record_access("agent-b", "shared.py")
    signals = lc.detect()
    assert len(signals) > 0
    assert isinstance(signals[0], LatentCommSignal)
    assert signals[0].shared_resource == "shared.py"


def test_detect_no_signal_below_threshold():
    lc = A2ALatentComm(confidence_threshold=0.99)
    lc.record_access("agent-a", "file.py")
    lc.record_access("agent-b", "file.py")
    signals = lc.detect()
    assert signals == []


def test_multiple_agents_same_resource():
    lc = A2ALatentComm(confidence_threshold=0.5)
    lc.record_access("agent-a", "db.table_x")
    lc.record_access("agent-b", "db.table_x")
    lc.record_access("agent-c", "db.table_x")
    signals = lc.detect()
    assert len(signals) >= 2
