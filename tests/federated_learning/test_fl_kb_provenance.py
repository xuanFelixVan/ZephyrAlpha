# [A_test] module_id: SRC-TST-0969 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_kb_provenance
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.collectors.kb_provenance
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_kb_provenance.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.collectors.kb_provenance import KBProvenance


class TestKBProvenanceInstantiation:
    def test_creates_with_defaults(self):
        prov = KBProvenance()
        assert prov.source == "unknown"
        assert prov.reliability == 0.5

    def test_creates_with_custom_params(self):
        prov = KBProvenance(source="human_expert", reliability=0.95)
        assert prov.source == "human_expert"
        assert prov.reliability == 0.95


class TestKBProvenanceAttributes:
    def test_source_mutable(self):
        prov = KBProvenance()
        prov.source = "automated_scan"
        assert prov.source == "automated_scan"

    def test_reliability_mutable(self):
        prov = KBProvenance()
        prov.reliability = 0.1
        assert prov.reliability == 0.1

    def test_boundary_zero_reliability(self):
        prov = KBProvenance(reliability=0.0)
        assert prov.reliability == 0.0

    def test_boundary_max_reliability(self):
        prov = KBProvenance(reliability=1.0)
        assert prov.reliability == 1.0
