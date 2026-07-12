# [A_test] module_id: SRC-TST-0568 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_config_governance
# [INVARIANTS] Snapshot version index must be sequential
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.config_governance import ConfigGovernance


class TestConfigGovernanceInstantiation:
    def test_default_empty_versions(self):
        cg = ConfigGovernance()
        assert cg.versions == []


class TestSnapshot:
    def test_first_snapshot_returns_zero(self):
        cg = ConfigGovernance()
        idx = cg.snapshot({"key": "val"})
        assert idx == 0

    def test_second_snapshot_returns_one(self):
        cg = ConfigGovernance()
        cg.snapshot({"key": "val1"})
        idx = cg.snapshot({"key": "val2"})
        assert idx == 1

    def test_snapshot_stores_copy(self):
        cg = ConfigGovernance()
        config = {"key": "val"}
        cg.snapshot(config)
        config["key"] = "modified"
        assert cg.versions[0]["key"] == "val"

    def test_empty_config_snapshot(self):
        cg = ConfigGovernance()
        idx = cg.snapshot({})
        assert idx == 0
        assert cg.versions[0] == {}

    def test_multiple_snapshots(self):
        cg = ConfigGovernance()
        for i in range(5):
            cg.snapshot({"v": i})
        assert len(cg.versions) == 5
