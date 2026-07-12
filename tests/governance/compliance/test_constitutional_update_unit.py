# [A_test] module_id: SRC-TST-1991 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-608 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_constitutional_update
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
Unit tests for constitutional_update.py
"""

import json
import tempfile
from pathlib import Path

from zephyr.gov_rule.constitutional_update.constitutional_update import (
    ConstitutionalAutoUpdate,
    Learning,
    ProposedUpdate,
)


class TestLearning:
    def test_create(self):
        l = Learning(
            pattern_id="L-RECOVER-001",
            category="recovery",
            summary="test",
            source_session="s1",
            proposed_rule="// rule",
        )
        assert l.pattern_id == "L-RECOVER-001"
        assert l.category == "recovery"
        assert l.severity == "info"


class TestProposedUpdate:
    def test_diff(self):
        proposal = ProposedUpdate(
            section="Test",
            original_lines=["old line"],
            new_lines=["new line"],
            rationale="testing",
        )
        diff = proposal.diff
        assert "--- a/" in diff
        assert "+++ b/" in diff
        assert "-old line" in diff
        assert "+new line" in diff


class TestConstitutionalAutoUpdate:
    def test_extract_learnings_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            agents = Path(tmpdir) / "AGENTS.md"
            agents.write_text("# Test", encoding="utf-8")

            auto = ConstitutionalAutoUpdate(agents_path=str(agents), audit_dir=tmpdir)
            learnings = auto.extract_learnings("nonexistent")
            assert learnings == []

    def test_extract_learnings_with_data(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            agents = Path(tmpdir) / "AGENTS.md"
            agents.write_text("# Test", encoding="utf-8")

            audit_file = Path(tmpdir) / "s1.jsonl"
            record = {
                "session_id": "s1",
                "errors": [
                    {
                        "type": "ValueError",
                        "message": "bad input",
                        "recovery": "fallback",
                        "recovered": True,
                    },
                ],
                "decisions": [],
            }
            audit_file.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")

            auto = ConstitutionalAutoUpdate(agents_path=str(agents), audit_dir=tmpdir)
            learnings = auto.extract_learnings("s1")
            assert len(learnings) >= 1
            assert learnings[0].category == "recovery"

    def test_extract_learnings_risk_decisions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            agents = Path(tmpdir) / "AGENTS.md"
            agents.write_text("# Test", encoding="utf-8")

            audit_file = Path(tmpdir) / "s1.jsonl"
            record = {
                "session_id": "s1",
                "errors": [],
                "decisions": [
                    {
                        "ts": "2026-01-01T00:00:00Z",
                        "id": "D-RISK-001",
                        "summary": "Risky move",
                        "rationale": "Had to try",
                        "alternatives": [],
                    },
                ],
            }
            audit_file.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")

            auto = ConstitutionalAutoUpdate(agents_path=str(agents), audit_dir=tmpdir)
            learnings = auto.extract_learnings("s1")
            assert len(learnings) >= 1
            assert learnings[0].category == "decision"

    def test_propose_update_empty(self):
        auto = ConstitutionalAutoUpdate(agents_path="AGENTS.md")
        result = auto.propose_update([])
        assert result is None

    def test_propose_update(self):
        auto = ConstitutionalAutoUpdate(agents_path="AGENTS.md")
        learnings = [
            Learning(
                pattern_id="L-TEST-001",
                category="test",
                summary="test learning",
                source_session="s1",
            )
        ]
        proposal = auto.propose_update(learnings)
        assert proposal is not None
        assert "Auto-Generated Learnings" in proposal.diff
        assert "L-TEST-001" in proposal.diff

    def test_apply_update_creates_backup(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            agents = Path(tmpdir) / "AGENTS.md"
            agents.write_text("# Test AGENTS\n\n## Section 1\nContent\n\n## Section 2\nMore", encoding="utf-8")

            auto = ConstitutionalAutoUpdate(agents_path=str(agents), audit_dir=tmpdir)
            learnings = [
                Learning(
                    pattern_id="L-APPLY-001",
                    category="apply",
                    summary="apply test",
                    source_session="s1",
                )
            ]
            proposal = auto.propose_update(learnings)
            assert proposal is not None

            result = auto.apply_update(proposal)
            assert result is True

            content = agents.read_text(encoding="utf-8")
            assert "Auto-Generated Learnings" in content
            assert "L-APPLY-001" in content

            backups = list(Path(tmpdir).glob("AGENTS.md.backup-*"))
            assert len(backups) >= 1

    def test_apply_update_missing_file(self):
        auto = ConstitutionalAutoUpdate(agents_path="nonexistent.md")
        proposal = ProposedUpdate(
            section="test",
            original_lines=[],
            new_lines=["line"],
            rationale="test",
        )
        result = auto.apply_update(proposal)
        assert result is False

    def test_get_existing_learnings_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            agents = Path(tmpdir) / "AGENTS.md"
            agents.write_text("# No learnings here", encoding="utf-8")
            auto = ConstitutionalAutoUpdate(agents_path=str(agents), audit_dir=tmpdir)
            result = auto.get_existing_learnings()
            assert result == []

    def test_get_existing_learnings(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            agents = Path(tmpdir) / "AGENTS.md"
            agents.write_text(
                "# Test\n\n## Auto-Generated Learnings\n| L-RECOVER-001 | recovery | test | info |\n\n## Next Section\n",
                encoding="utf-8",
            )
            auto = ConstitutionalAutoUpdate(agents_path=str(agents), audit_dir=tmpdir)
            result = auto.get_existing_learnings()
            assert "L-RECOVER-001" in result

    def test_extract_cross_session(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            agents = Path(tmpdir) / "AGENTS.md"
            agents.write_text("# Test", encoding="utf-8")

            for sid in ["s1", "s2"]:
                audit_file = Path(tmpdir) / f"{sid}.jsonl"
                record = {
                    "session_id": sid,
                    "errors": [
                        {"type": "Error", "message": f"fail_in_{sid}", "recovery": "fix", "recovered": True},
                    ],
                    "decisions": [],
                }
                audit_file.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")

            auto = ConstitutionalAutoUpdate(agents_path=str(agents), audit_dir=tmpdir)
            learnings = auto.extract_cross_session(["s1", "s2"])
            assert len(learnings) >= 2
