# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l01_infrastructure.a2a_protocol.test_checkpoint
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""测试: Checkpoint"""

def test_checkpoint():
    from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_checkpoint import A2ACheckpoint
    cp = A2ACheckpoint()
    cp.save("t1", {"x": 1})
    assert cp.load("t1")["x"] == 1
