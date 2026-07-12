# [A_test] module_id: SRC-TST-1443 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_regulatory_audit
# [INVARIANTS] RegulatoryAudit.regulations is list[str]; default contains MiFID II and SEC Rule 606
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_regulatory_audit.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.regulatory_audit import RegulatoryAudit


class TestRegulatoryAuditInstantiation:
    def test_default_regulations(self):
        obj = RegulatoryAudit()
        assert obj.regulations == ["MiFID II", "SEC Rule 606"]

    def test_custom_regulations(self):
        custom = ["GDPR", "SOX"]
        obj = RegulatoryAudit(regulations=custom)
        assert obj.regulations == custom

    def test_empty_regulations(self):
        obj = RegulatoryAudit(regulations=[])
        assert obj.regulations == []

    def test_regulations_is_list_type(self):
        obj = RegulatoryAudit()
        assert isinstance(obj.regulations, list)


class TestRegulatoryAuditRegulations:
    def test_regulations_can_be_appended(self):
        obj = RegulatoryAudit()
        obj.regulations.append("GDPR")
        assert "GDPR" in obj.regulations
        assert len(obj.regulations) == 3

    def test_regulations_can_be_removed(self):
        obj = RegulatoryAudit()
        obj.regulations.remove("MiFID II")
        assert "MiFID II" not in obj.regulations
        assert len(obj.regulations) == 1

    def test_separate_instances_have_independent_regulations(self):
        a = RegulatoryAudit()
        b = RegulatoryAudit()
        a.regulations.append("GDPR")
        assert "GDPR" not in b.regulations

    def test_regulations_accepts_duplicate_entries(self):
        obj = RegulatoryAudit(regulations=["SOX", "SOX"])
        assert obj.regulations.count("SOX") == 2
