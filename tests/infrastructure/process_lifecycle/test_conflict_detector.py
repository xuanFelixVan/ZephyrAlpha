# [A_test] module_id: MOD-GOV_conflict_detector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §
# [MODULE] tests.test_conflict_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_conflict_detector.py
# [TTL] task_bound

from zephyr.infrastructure.a2a_protocol.layer3_coordination.conflict_detector import (
    ChangeSet,
    ConflictDetector,
    ConflictType,
)


class TestChangeSet:
    def test_add_file(self):
        cs = ChangeSet(agent_id="a")
        cs.add_file("src/main.py", 1, 20, ["MyClass"])
        assert "src/main.py" in cs.files
        assert cs.files["src/main.py"].symbols == ["MyClass"]


class TestConflictDetector:
    def test_no_conflict_disjoint_files(self):
        cd = ConflictDetector()
        a = ChangeSet(agent_id="a")
        a.add_file("file_a.py", 1, 10)
        b = ChangeSet(agent_id="b")
        b.add_file("file_b.py", 1, 10)
        conflicts = cd.detect(a, b)
        assert conflicts == []

    def test_line_overlap_conflict(self):
        cd = ConflictDetector()
        a = ChangeSet(agent_id="a")
        a.add_file("shared.py", 1, 50)
        b = ChangeSet(agent_id="b")
        b.add_file("shared.py", 1, 50)
        conflicts = cd.detect(a, b)
        assert len(conflicts) > 0
        assert conflicts[0].conflict_type in (ConflictType.LINE_OVERLAP, ConflictType.SYMBOL_CONFLICT)

    def test_symbol_conflict(self):
        cd = ConflictDetector()
        a = ChangeSet(agent_id="a")
        a.add_file("shared.py", 1, 50, ["MyClass"])
        b = ChangeSet(agent_id="b")
        b.add_file("shared.py", 1, 50, ["MyClass"])
        conflicts = cd.detect(a, b)
        assert any(c.conflict_type == ConflictType.SYMBOL_CONFLICT for c in conflicts)

    def test_resource_lock_conflict(self):
        cd = ConflictDetector(resource_exclusive=True)
        a = ChangeSet(agent_id="a")
        a.locked_resources = ["lock-1"]
        b = ChangeSet(agent_id="b")
        b.locked_resources = ["lock-1"]
        conflicts = cd.detect(a, b)
        assert any(c.conflict_type == ConflictType.RESOURCE_LOCK for c in conflicts)

    def test_has_conflict(self):
        cd = ConflictDetector()
        a = ChangeSet(agent_id="a")
        a.add_file("f.py", 1, 50)
        b = ChangeSet(agent_id="b")
        b.add_file("f.py", 1, 50)
        assert cd.has_conflict(a, b) is True

    def test_is_blocking(self):
        cd = ConflictDetector()
        a = ChangeSet(agent_id="a")
        a.add_file("f.py", 1, 50, ["Sym"])
        b = ChangeSet(agent_id="b")
        b.add_file("f.py", 1, 50, ["Sym"])
        assert cd.is_blocking(a, b) is True

    def test_summary(self):
        cd = ConflictDetector()
        a = ChangeSet(agent_id="a")
        a.add_file("f.py", 1, 50, ["Sym"])
        b = ChangeSet(agent_id="b")
        b.add_file("f.py", 1, 50, ["Sym"])
        conflicts = cd.detect(a, b)
        s = ConflictDetector.summary(conflicts)
        assert s["total_conflicts"] > 0
        assert s["has_blocking"] is True

    def test_tolerance_zero(self):
        cd = ConflictDetector(line_overlap_tolerance=100)
        a = ChangeSet(agent_id="a")
        a.add_file("f.py", 1, 50)
        b = ChangeSet(agent_id="b")
        b.add_file("f.py", 40, 50)
        conflicts = cd.detect(a, b)
        line_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.LINE_OVERLAP]
        assert len(line_conflicts) == 0
