# [A_test] module_id: SRC-TST-1672 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-434 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_spof_checker
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.governance.escalation.spof_checker import (
    SPOF_CHECKS,
    SPOFReport,
    SPOFType,
    all_mitigated,
    check_spof,
)


class TestSPOFType:
    def test_enum_values(self):
        assert SPOFType.BROKER == "BROKER"
        assert SPOFType.DATA_SOURCE == "DATA_SOURCE"
        assert SPOFType.LLM_MODEL == "LLM_MODEL"
        assert SPOFType.OWNER == "OWNER"

    def test_enum_members_count(self):
        assert len(SPOFType) == 4


class TestSPOFReport:
    def test_create_report(self):
        report = SPOFReport(
            spof_type=SPOFType.BROKER,
            current="Single broker",
            risk_level="CRITICAL",
        )
        assert report.spof_type == SPOFType.BROKER
        assert report.current == "Single broker"
        assert report.risk_level == "CRITICAL"
        assert report.mitigated is False
        assert report.backup == []

    def test_report_with_backup(self):
        report = SPOFReport(
            spof_type=SPOFType.BROKER,
            current="Single broker",
            risk_level="CRITICAL",
            backup=["Multi-broker", "Emergency close"],
            mitigated=True,
        )
        assert len(report.backup) == 2
        assert report.mitigated is True


class TestCheckSpof:
    def test_broker_spof(self):
        report = check_spof(SPOFType.BROKER)
        assert report.spof_type == SPOFType.BROKER
        assert report.risk_level == "CRITICAL"
        assert report.mitigated is True

    def test_data_source_spof(self):
        report = check_spof(SPOFType.DATA_SOURCE)
        assert report.spof_type == SPOFType.DATA_SOURCE
        assert report.mitigated is True

    def test_llm_model_spof(self):
        report = check_spof(SPOFType.LLM_MODEL)
        assert report.spof_type == SPOFType.LLM_MODEL

    def test_owner_spof(self):
        report = check_spof(SPOFType.OWNER)
        assert report.spof_type == SPOFType.OWNER

    def test_unknown_spof_type(self):
        with pytest.raises(Exception):
            check_spof("NONEXISTENT")


class TestAllMitigated:
    def test_all_mitigated(self):
        assert all_mitigated() is True

    def test_all_checks_have_mitigation(self):
        for spof_type, report in SPOF_CHECKS.items():
            assert report.mitigated is True, f"{spof_type} not mitigated"
