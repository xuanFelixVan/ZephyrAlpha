# [A_test] module_id: SRC-TST-0705 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_db_integrity
# [INVARIANTS] Checksum verification must be exact string match
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.db_integrity import DBIntegrity


class TestDBIntegrityInstantiation:
    def test_default_empty_checksum(self):
        dbi = DBIntegrity()
        assert dbi.checksum == ""

    def test_custom_checksum(self):
        dbi = DBIntegrity(checksum="abc123")
        assert dbi.checksum == "abc123"


class TestVerify:
    def test_matching_checksum(self):
        dbi = DBIntegrity(checksum="abc123")
        assert dbi.verify("abc123") is True

    def test_mismatched_checksum(self):
        dbi = DBIntegrity(checksum="abc123")
        assert dbi.verify("xyz789") is False

    def test_empty_checksum_matches_empty(self):
        dbi = DBIntegrity(checksum="")
        assert dbi.verify("") is True

    def test_empty_checksum_mismatches_nonempty(self):
        dbi = DBIntegrity(checksum="")
        assert dbi.verify("something") is False

    def test_case_sensitive(self):
        dbi = DBIntegrity(checksum="ABC")
        assert dbi.verify("abc") is False
