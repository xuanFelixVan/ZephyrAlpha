# [A_test] module_id: SRC-TST-0566 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_config_drift
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_config_drift.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.detectors.drift.config_drift import ConfigDrift


class TestConfigDriftInstantiation:
    def test_default_construction(self):
        cd = ConfigDrift()
        assert cd.snapshots == {}

    def test_with_initial_snapshots(self):
        cd = ConfigDrift(snapshots={"prod": {"cpu_limit": 80}})
        assert "prod" in cd.snapshots


class TestSnapshotsAttribute:
    def test_add_snapshot(self):
        cd = ConfigDrift()
        cd.snapshots["prod"] = {"cpu_limit": 80, "mem_limit": 90}
        assert cd.snapshots["prod"]["cpu_limit"] == 80

    def test_multiple_environments(self):
        cd = ConfigDrift()
        cd.snapshots["prod"] = {"cpu_limit": 80}
        cd.snapshots["canary"] = {"cpu_limit": 60}
        assert len(cd.snapshots) == 2

    def test_snapshot_replacement(self):
        cd = ConfigDrift()
        cd.snapshots["prod"] = {"cpu_limit": 80}
        cd.snapshots["prod"] = {"cpu_limit": 90}
        assert cd.snapshots["prod"]["cpu_limit"] == 90

    def test_empty_snapshot(self):
        cd = ConfigDrift()
        cd.snapshots["prod"] = {}
        assert cd.snapshots["prod"] == {}

    def test_nested_config(self):
        cd = ConfigDrift()
        cd.snapshots["prod"] = {"limits": {"cpu": 80, "mem": 90}}
        assert cd.snapshots["prod"]["limits"]["cpu"] == 80

    def test_independent_instances(self):
        a = ConfigDrift()
        b = ConfigDrift()
        a.snapshots["prod"] = {"cpu_limit": 80}
        assert b.snapshots == {}
