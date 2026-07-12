# [A_test] module_id: SRC-TST-0530 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_code_archaeology
# [INVARIANTS] BlameRecord fields; EvolutionGraph timeline ordering
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass; exit non-zero on fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_audit.code_archaeology import (
    BlameRecord,
    CommitNode,
    EvolutionGraph,
    auto_doc,
    blame,
)


class TestBlameRecord:
    def test_creation_with_required_fields(self):
        rec = BlameRecord(file="src/main.py", line=42)
        assert rec.file == "src/main.py"
        assert rec.line == 42
        assert rec.agent_id is None
        assert rec.session_id is None
        assert rec.task_id is None
        assert rec.provenance is None

    def test_creation_with_all_fields(self):
        rec = BlameRecord(
            file="src/main.py",
            line=42,
            agent_id="agent-1",
            session_id="sess-1",
            task_id="task-1",
            provenance={"source": "git"},
        )
        assert rec.agent_id == "agent-1"
        assert rec.session_id == "sess-1"
        assert rec.task_id == "task-1"
        assert rec.provenance == {"source": "git"}


class TestCommitNode:
    def test_creation(self):
        node = CommitNode(
            commit_hash="abc123",
            message="initial commit",
            author="dev",
            date="2026-05-22",
        )
        assert node.commit_hash == "abc123"
        assert node.parents == []
        assert node.files_changed == []


class TestEvolutionGraph:
    def test_add_commit(self):
        graph = EvolutionGraph()
        node = CommitNode(
            commit_hash="abc123",
            message="initial",
            author="dev",
            date="2026-05-22",
        )
        graph.add_commit(node)
        assert "abc123" in graph.nodes
        assert len(graph.edges) == 0

    def test_add_commit_with_parent(self):
        graph = EvolutionGraph()
        parent = CommitNode(commit_hash="p1", message="parent", author="dev", date="2026-05-20")
        child = CommitNode(
            commit_hash="c1",
            message="child",
            author="dev",
            date="2026-05-22",
            parents=["p1"],
        )
        graph.add_commit(parent)
        graph.add_commit(child)
        assert ("p1", "c1") in graph.edges

    def test_timeline_sorted_by_date(self):
        graph = EvolutionGraph()
        n1 = CommitNode(commit_hash="h1", message="first", author="dev", date="2026-05-20")
        n2 = CommitNode(commit_hash="h2", message="second", author="dev", date="2026-05-22")
        graph.add_commit(n2)
        graph.add_commit(n1)
        timeline = graph.timeline()
        assert timeline[0].commit_hash == "h1"
        assert timeline[1].commit_hash == "h2"

    def test_empty_graph(self):
        graph = EvolutionGraph()
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0
        assert graph.timeline() == []


class TestBlame:
    def test_blame_returns_record(self):
        rec = blame("src/main.py", 10)
        assert isinstance(rec, BlameRecord)
        assert rec.file == "src/main.py"
        assert rec.line == 10


class TestAutoDoc:
    def test_auto_doc_contains_module_id(self):
        result = auto_doc("MOD-INF-020", ["func1", "func2"])
        assert "MOD-INF-020" in result
        assert "func1()" in result
        assert "func2()" in result

    def test_auto_doc_empty_functions(self):
        result = auto_doc("MOD-001", [])
        assert "MOD-001" in result
        assert "Key Functions" in result
