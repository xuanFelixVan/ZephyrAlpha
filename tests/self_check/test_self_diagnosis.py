# [A_test] module_id: SRC-TST-1554 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_self_diagnosis
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_self_diagnosis.py -q
# [TTL] task_bound
from __future__ import annotations

from zephyr.feedback_loop.self_diagnosis import (
    DiagnosisNode,
    DiagnosisReport,
    SelfDiagnosis,
)


class TestDiagnosisNode:
    def test_required_fields(self):
        node = DiagnosisNode(check_name="VMS_Connection", status="PASS")
        assert node.check_name == "VMS_Connection"
        assert node.status == "PASS"
        assert node.detail == ""

    def test_detail_field_optional(self):
        node = DiagnosisNode(check_name="LSG_Gate", status="WARN", detail="LSG not configured")
        assert node.detail == "LSG not configured"


class TestDiagnosisReport:
    def test_default_action_items_empty(self):
        report = DiagnosisReport(nodes=[], overall="HEALTHY")
        assert report.action_items == []

    def test_action_items_can_be_set(self):
        report = DiagnosisReport(
            nodes=[],
            overall="CRITICAL",
            action_items=["Fix VMS", "Restart LSG"],
        )
        assert report.action_items == ["Fix VMS", "Restart LSG"]


class TestSelfDiagnosisInstantiation:
    def test_can_instantiate(self):
        sd = SelfDiagnosis()
        assert sd is not None


class TestRun:
    def test_returns_diagnosis_report(self):
        sd = SelfDiagnosis()
        report = sd.run()
        assert isinstance(report, DiagnosisReport)

    def test_report_contains_three_nodes(self):
        sd = SelfDiagnosis()
        report = sd.run()
        assert len(report.nodes) == 3

    def test_node_check_names(self):
        sd = SelfDiagnosis()
        report = sd.run()
        names = [n.check_name for n in report.nodes]
        assert names == ["VMS_Connection", "KE_Collection", "LSG_Gate"]

    def test_vms_connection_passes(self):
        sd = SelfDiagnosis()
        report = sd.run()
        assert report.nodes[0].status == "PASS"

    def test_ke_collection_passes(self):
        sd = SelfDiagnosis()
        report = sd.run()
        assert report.nodes[1].status == "PASS"

    def test_lsg_gate_warns(self):
        sd = SelfDiagnosis()
        report = sd.run()
        assert report.nodes[2].status == "WARN"
        assert report.nodes[2].detail == "LSG not configured"

    def test_overall_is_degraded_when_warn_present(self):
        sd = SelfDiagnosis()
        report = sd.run()
        assert report.overall == "DEGRADED"

    def test_no_fail_nodes_in_default_run(self):
        sd = SelfDiagnosis()
        report = sd.run()
        fail_nodes = [n for n in report.nodes if n.status == "FAIL"]
        assert len(fail_nodes) == 0

    def test_each_node_is_diagnosis_node_type(self):
        sd = SelfDiagnosis()
        report = sd.run()
        for node in report.nodes:
            assert isinstance(node, DiagnosisNode)
