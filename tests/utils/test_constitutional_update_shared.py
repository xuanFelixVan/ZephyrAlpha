# [A_test] module_id: SRC-TST-1942 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-559 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.shared.test_constitutional_update
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
单元测试：src/zephyr/shared/constitutional_update.py
======================================================
覆盖矩阵：
  Learning：
    - 构造 & 属性 × 1
    - 默认值 × 1
  ProposedUpdate：
    - 构造 & diff 属性 × 1
    - diff 包含移除/新增行 × 1
  ConstitutionalAutoUpdate：
    - extract_learnings 空 session × 1
    - extract_learnings 含 error 记录 × 1
    - extract_learnings 去重 × 1
    - extract_cross_session × 1
    - propose_update 空 learnings × 1
    - propose_update 含 learnings × 1
    - apply_update 创建新 section × 1
    - apply_update 替换已有 section × 1
    - apply_update agents_path 不存在 × 1
    - get_existing_learnings × 2

Safety: HIGH（宪法自愈直接修改 AGENTS.md 工程宪法）
"""

from zephyr.gov_rule.constitutional_update.constitutional_update import (
    ConstitutionalAutoUpdate,
    Learning,
    ProposedUpdate,
)


class TestLearning:
    def test_construction(self):
        l = Learning(
            pattern_id="L-RECOVER-sess-001",
            category="recovery",
            summary="Recovered from ImportError",
            source_session="sess-001",
            severity="warn",
            proposed_rule="// On ImportError: pip install",
        )
        assert l.pattern_id == "L-RECOVER-sess-001"
        assert l.category == "recovery"
        assert l.severity == "warn"
        assert l.source_session == "sess-001"

    def test_defaults(self):
        l = Learning(
            pattern_id="L-TEST-001",
            category="test",
            summary="A test learning",
            source_session="sess-001",
        )
        assert l.severity == "info"
        assert l.proposed_rule == ""


class TestProposedUpdate:
    def test_construction_and_diff(self):
        prop = ProposedUpdate(
            section="Test Section",
            original_lines=["old line 1", "old line 2"],
            new_lines=["new line 1", "new line 2"],
            rationale="Testing diff output",
        )
        diff = prop.diff
        assert "--- a/AGENTS.md (section: Test Section)" in diff
        assert "+++ b/AGENTS.md (section: Test Section)" in diff
        assert "-old line 1" in diff
        assert "+new line 1" in diff
        assert "Rationale: Testing diff output" in diff


class TestConstitutionalAutoUpdate:
    def test_extract_learnings_empty_session(self):
        auto = ConstitutionalAutoUpdate(
            agents_path="nonexistent.md",
            audit_dir="logs/test_constitutional/",
        )
        learnings = auto.extract_learnings("nonexistent-session")
        assert learnings == []

    def test_extract_learnings_with_errors(self, tmp_path):
        audit_dir = str(tmp_path / "audit")
        agents_path = str(tmp_path / "AGENTS.md")
        agents_path_file = tmp_path / "AGENTS.md"
        agents_path_file.write_text("", encoding="utf-8")

        from zephyr.shared.session.session_audit import SessionAuditTrail

        trail = SessionAuditTrail(audit_dir=audit_dir)
        record = trail.start_session("sess-001")
        record.add_error("ImportError", "missing module", "pip install", True)
        record.add_error("KeyError", "missing key", "retry", False)
        trail.append_record(record)

        auto = ConstitutionalAutoUpdate(agents_path=str(agents_path_file), audit_dir=audit_dir)
        learnings = auto.extract_learnings("sess-001")
        recovered = [l for l in learnings if l.category == "recovery"]
        assert len(recovered) == 1
        assert "ImportError" in recovered[0].summary

    def test_extract_learnings_with_decisions(self, tmp_path):
        audit_dir = str(tmp_path / "audit")
        agents_path = str(tmp_path / "AGENTS.md")
        (tmp_path / "AGENTS.md").write_text("", encoding="utf-8")

        from zephyr.shared.session.session_audit import SessionAuditTrail

        trail = SessionAuditTrail(audit_dir=audit_dir)
        record = trail.start_session("sess-002")
        record.add_decision("D-RISK-001", "risky choice", "because X")
        trail.append_record(record)

        auto = ConstitutionalAutoUpdate(agents_path=str(tmp_path / "AGENTS.md"), audit_dir=audit_dir)
        learnings = auto.extract_learnings("sess-002")
        decision_learnings = [l for l in learnings if l.category == "decision"]
        assert len(decision_learnings) == 1
        assert decision_learnings[0].severity == "warn"

    def test_extract_cross_session(self, tmp_path):
        audit_dir = str(tmp_path / "audit")
        (tmp_path / "AGENTS.md").write_text("", encoding="utf-8")

        from zephyr.shared.session.session_audit import SessionAuditTrail

        trail = SessionAuditTrail(audit_dir=audit_dir)

        rec1 = trail.start_session("sess-a")
        rec1.add_error("E1", "msg", recovered=True)
        trail.append_record(rec1)

        rec2 = trail.start_session("sess-b")
        rec2.add_error("E2", "msg", recovered=True)
        trail.append_record(rec2)

        auto = ConstitutionalAutoUpdate(agents_path=str(tmp_path / "AGENTS.md"), audit_dir=audit_dir)
        learnings = auto.extract_cross_session(["sess-a", "sess-b"])
        assert len(learnings) == 2

    def test_propose_update_empty(self):
        auto = ConstitutionalAutoUpdate()
        assert auto.propose_update([]) is None

    def test_propose_update_with_learnings(self):
        auto = ConstitutionalAutoUpdate()
        learnings = [
            Learning(
                pattern_id="L-TEST-001",
                category="recovery",
                summary="Test learning 1",
                source_session="sess-001",
            ),
            Learning(
                pattern_id="L-TEST-002",
                category="decision",
                summary="Test learning 2",
                source_session="sess-001",
            ),
        ]
        prop = auto.propose_update(learnings)
        assert prop is not None
        assert prop.section == "Auto-Generated Learnings"
        assert "L-TEST-001" in "\n".join(prop.new_lines)
        assert "L-TEST-002" in "\n".join(prop.new_lines)
        assert len(prop.learnings) == 2

    def test_apply_update_new_section(self, tmp_path):
        agents_path = tmp_path / "AGENTS.md"
        agents_path.write_text("## Original Section\nSome content\n", encoding="utf-8")

        auto = ConstitutionalAutoUpdate(agents_path=str(agents_path), audit_dir=str(tmp_path / "audit"))
        prop = ProposedUpdate(
            section="Auto-Generated Learnings",
            original_lines=[],
            new_lines=["## Auto-Generated Learnings (from ConstitutionalAutoUpdate)", "| pattern | cat |", "|---|---|"],
            rationale="test",
        )

        result = auto.apply_update(prop)
        assert result is True
        content = agents_path.read_text(encoding="utf-8")
        assert "## Original Section" in content
        assert "## Auto-Generated Learnings" in content

    def test_apply_update_replaces_existing(self, tmp_path):
        agents_path = tmp_path / "AGENTS.md"
        agents_path.write_text(
            "## Auto-Generated Learnings\nold content\n\n## Next Section\nnext content\n",
            encoding="utf-8",
        )

        auto = ConstitutionalAutoUpdate(agents_path=str(agents_path), audit_dir=str(tmp_path / "audit"))
        prop = ProposedUpdate(
            section="Auto-Generated Learnings",
            original_lines=[],
            new_lines=["## Auto-Generated Learnings (from ConstitutionalAutoUpdate)", "| new | table |", "|---|---|"],
            rationale="replace",
        )

        result = auto.apply_update(prop)
        assert result is True
        content = agents_path.read_text(encoding="utf-8")
        assert "old content" not in content
        assert "new" in content
        assert "## Next Section" in content

    def test_apply_update_file_not_exist(self):
        auto = ConstitutionalAutoUpdate(agents_path="nonexistent.md")
        prop = ProposedUpdate(
            section="test",
            original_lines=[],
            new_lines=["test"],
            rationale="test",
        )
        assert auto.apply_update(prop) is False

    def test_get_existing_learnings_empty(self, tmp_path):
        agents_path = tmp_path / "AGENTS.md"
        agents_path.write_text("## No learnings here\n", encoding="utf-8")

        auto = ConstitutionalAutoUpdate(agents_path=str(agents_path))
        assert auto.get_existing_learnings() == []

    def test_get_existing_learnings_with_data(self, tmp_path):
        agents_path = tmp_path / "AGENTS.md"
        agents_path.write_text(
            "## Auto-Generated Learnings\n| L-RECOVER-001 | recovery | msg |\n| L-DEC-002 | decision | msg |\n\n## Next\n",
            encoding="utf-8",
        )

        auto = ConstitutionalAutoUpdate(agents_path=str(agents_path))
        ids = auto.get_existing_learnings()
        assert "L-RECOVER-001" in ids
        assert "L-DEC-002" in ids
