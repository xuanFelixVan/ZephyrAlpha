"""测试: ConflictDetector"""

from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.conflict_detector import (
    ConflictDetector,
    ChangeSet,
    Conflict,
    ConflictSeverity,
    ConflictType,
)


def test_detect_no_overlap():
    cd = ConflictDetector()
    a = ChangeSet(agent_id="agent-a")
    b = ChangeSet(agent_id="agent-b")
    assert cd.detect(a, b) == []


def test_detect_line_overlap():
    cd = ConflictDetector()
    a = ChangeSet(agent_id="agent-a")
    a.add_file("src/main.py", 1, 50, ["func_a"])
    b = ChangeSet(agent_id="agent-b")
    b.add_file("src/main.py", 30, 80, ["func_b"])
    conflicts = cd.detect(a, b)
    assert len(conflicts) > 0


def test_detect_symbol_conflict():
    cd = ConflictDetector()
    a = ChangeSet(agent_id="agent-a")
    a.add_file("src/main.py", 1, 50, ["func_a"])
    b = ChangeSet(agent_id="agent-b")
    b.add_file("src/main.py", 1, 50, ["func_a"])
    conflicts = cd.detect(a, b)
    assert any(c.conflict_type == ConflictType.SYMBOL_CONFLICT for c in conflicts)
    assert any(c.severity == ConflictSeverity.BLOCKING for c in conflicts)


def test_detect_resource_lock_conflict():
    cd = ConflictDetector(resource_exclusive=True)
    a = ChangeSet(agent_id="agent-a", locked_resources=["db.table_x"])
    b = ChangeSet(agent_id="agent-b", locked_resources=["db.table_x"])
    conflicts = cd.detect(a, b)
    assert any(c.conflict_type == ConflictType.RESOURCE_LOCK for c in conflicts)


def test_has_conflict():
    cd = ConflictDetector()
    a = ChangeSet(agent_id="agent-a")
    a.add_file("f.py", 1, 50, ["func"])
    b = ChangeSet(agent_id="agent-b")
    b.add_file("f.py", 1, 50, ["func"])
    assert cd.has_conflict(a, b)


def test_is_blocking():
    cd = ConflictDetector()
    a = ChangeSet(agent_id="agent-a")
    a.add_file("f.py", 1, 100, ["func"])
    b = ChangeSet(agent_id="agent-b")
    b.add_file("f.py", 1, 100, ["func"])
    assert cd.is_blocking(a, b)


def test_summary():
    cd = ConflictDetector()
    a = ChangeSet(agent_id="agent-a")
    a.add_file("f.py", 1, 50, ["func"])
    b = ChangeSet(agent_id="agent-b")
    b.add_file("f.py", 1, 50, ["func"])
    conflicts = cd.detect(a, b)
    s = ConflictDetector.summary(conflicts)
    assert s["total_conflicts"] > 0
    assert s["blocking"] >= 0
