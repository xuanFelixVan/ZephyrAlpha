# [A_test] module_id: MOD-GOV_skill_lineage | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_lineage
# [INVARIANTS] SkillLineage must maintain version tree integrity
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] diff returns found=False for missing versions
# [TESTS] tests/test_skill_lineage.py
# [TTL] task_bound

from zephyr.autonomy_core.skills.skill_lineage import SkillLineage


class TestSkillLineageInstantiation:
    def test_default_instantiation(self):
        lin = SkillLineage()
        assert isinstance(lin.lineages, dict)
        assert len(lin.lineages) == 0


class TestRecordVersion:
    def test_record_single_version(self):
        lin = SkillLineage()
        entry = lin.record_version("skill-1", "1.0.0", None, "initial release")
        assert entry["version"] == "1.0.0"
        assert entry["parent"] is None
        assert entry["changes"] == "initial release"
        assert isinstance(entry["timestamp"], float)

    def test_record_multiple_versions(self):
        lin = SkillLineage()
        lin.record_version("skill-2", "1.0.0", None, "initial")
        lin.record_version("skill-2", "1.1.0", "1.0.0", "added feature")
        lin.record_version("skill-2", "2.0.0", "1.1.0", "breaking change")
        lineage = lin.get_lineage("skill-2")
        assert len(lineage) == 3

    def test_record_version_stores_in_lineages(self):
        lin = SkillLineage()
        lin.record_version("skill-3", "0.1.0", None, "draft")
        assert "skill-3" in lin.lineages
        assert len(lin.lineages["skill-3"]) == 1


class TestGetLineage:
    def test_get_lineage_existing(self):
        lin = SkillLineage()
        lin.record_version("s1", "1.0.0", None, "init")
        lin.record_version("s1", "1.1.0", "1.0.0", "update")
        result = lin.get_lineage("s1")
        assert len(result) == 2

    def test_get_lineage_nonexistent(self):
        lin = SkillLineage()
        result = lin.get_lineage("unknown")
        assert result == []


class TestLatest:
    def test_latest_returns_last(self):
        lin = SkillLineage()
        lin.record_version("s2", "1.0.0", None, "init")
        lin.record_version("s2", "2.0.0", "1.0.0", "major")
        result = lin.latest("s2")
        assert result["version"] == "2.0.0"

    def test_latest_none_for_empty(self):
        lin = SkillLineage()
        result = lin.latest("unknown")
        assert result is None

    def test_latest_single_version(self):
        lin = SkillLineage()
        lin.record_version("s3", "0.1.0", None, "draft")
        result = lin.latest("s3")
        assert result["version"] == "0.1.0"


class TestRollbackPath:
    def test_rollback_path_to_root(self):
        lin = SkillLineage()
        lin.record_version("s4", "1.0.0", None, "init")
        lin.record_version("s4", "1.1.0", "1.0.0", "update")
        lin.record_version("s4", "2.0.0", "1.1.0", "major")
        path = lin.rollback_path("s4", "1.0.0")
        versions = [e["version"] for e in path]
        assert "2.0.0" in versions
        assert "1.0.0" in versions

    def test_rollback_path_target_is_latest(self):
        lin = SkillLineage()
        lin.record_version("s5", "1.0.0", None, "init")
        lin.record_version("s5", "2.0.0", "1.0.0", "major")
        path = lin.rollback_path("s5", "2.0.0")
        assert len(path) == 1
        assert path[0]["version"] == "2.0.0"

    def test_rollback_path_empty_lineage(self):
        lin = SkillLineage()
        path = lin.rollback_path("unknown", "1.0.0")
        assert path == []

    def test_rollback_path_version_not_found(self):
        lin = SkillLineage()
        lin.record_version("s6", "1.0.0", None, "init")
        path = lin.rollback_path("s6", "9.9.9")
        assert len(path) > 0


class TestDiff:
    def test_diff_existing_versions(self):
        lin = SkillLineage()
        lin.record_version("s7", "1.0.0", None, "initial release")
        lin.record_version("s7", "2.0.0", "1.0.0", "breaking change")
        result = lin.diff("s7", "1.0.0", "2.0.0")
        assert result["found"] is True
        assert result["v1_changes"] == "initial release"
        assert result["v2_changes"] == "breaking change"

    def test_diff_missing_version(self):
        lin = SkillLineage()
        lin.record_version("s8", "1.0.0", None, "init")
        result = lin.diff("s8", "1.0.0", "9.9.9")
        assert result["found"] is False

    def test_diff_both_missing(self):
        lin = SkillLineage()
        result = lin.diff("unknown", "1.0.0", "2.0.0")
        assert result["found"] is False

    def test_diff_includes_timestamps(self):
        lin = SkillLineage()
        lin.record_version("s9", "1.0.0", None, "init")
        lin.record_version("s9", "2.0.0", "1.0.0", "major")
        result = lin.diff("s9", "1.0.0", "2.0.0")
        assert result["v1_ts"] is not None
        assert result["v2_ts"] is not None


class TestClear:
    def test_clear_specific_skill(self):
        lin = SkillLineage()
        lin.record_version("s10", "1.0.0", None, "init")
        lin.record_version("s11", "1.0.0", None, "init")
        lin.clear("s10")
        assert lin.get_lineage("s10") == []
        assert len(lin.get_lineage("s11")) == 1

    def test_clear_all(self):
        lin = SkillLineage()
        lin.record_version("s12", "1.0.0", None, "init")
        lin.record_version("s13", "1.0.0", None, "init")
        lin.clear()
        assert len(lin.lineages) == 0

    def test_clear_nonexistent_skill_no_error(self):
        lin = SkillLineage()
        lin.clear("nonexistent")
        assert len(lin.lineages) == 0
