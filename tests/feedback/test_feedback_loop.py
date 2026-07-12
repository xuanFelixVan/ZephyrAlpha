# [A_test] module_id: SRC-TST-0903 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] tests.test_feedback_loop
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] tests never raise; all assertions within pytest
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

import yaml

from zephyr.feedback_loop import EvolutionProposal, FeedbackLoop


class TestEvolutionProposal:
    def test_default_values(self) -> None:
        prop = EvolutionProposal()
        assert prop.proposal_id.startswith("PROP-")
        assert prop.source == ""
        assert prop.pattern == ""
        assert prop.suggested_rule_change == ""
        assert prop.confidence == 0.0
        assert prop.status == "DRAFT"

    def test_custom_values(self) -> None:
        prop = EvolutionProposal(
            proposal_id="PROP-001",
            source="NSL-0001",
            pattern="Recurring ambiguity",
            suggested_rule_change="Add rule X",
            confidence=0.8,
            status="APPROVED",
        )
        assert prop.proposal_id == "PROP-001"
        assert prop.confidence == 0.8
        assert prop.status == "APPROVED"


class TestFeedbackLoopInit:
    def test_init_creates_proposal_dir(self, tmp_path: Path) -> None:
        proposal_dir = tmp_path / "proposals"
        loop = FeedbackLoop(proposal_dir=proposal_dir)
        assert proposal_dir.exists()


class TestAnalyzePending:
    def test_analyze_empty_list(self, tmp_path: Path) -> None:
        loop = FeedbackLoop(proposal_dir=tmp_path / "proposals")
        result = loop.analyze_pending([])
        assert result == []

    def test_analyze_pending_entries(self, tmp_path: Path) -> None:
        loop = FeedbackLoop(proposal_dir=tmp_path / "proposals")
        entries = [
            {"id": "001", "module": "test_module", "context": "ambiguous behavior"},
            {"id": "002", "module": "other_module", "context": "missing rule"},
        ]
        proposals = loop.analyze_pending(entries)
        assert len(proposals) == 2
        assert proposals[0].source == "NSL-001"
        assert "test_module" in proposals[0].pattern
        assert proposals[1].source == "NSL-002"

    def test_analyze_pending_missing_fields(self, tmp_path: Path) -> None:
        loop = FeedbackLoop(proposal_dir=tmp_path / "proposals")
        entries = [{}]
        proposals = loop.analyze_pending(entries)
        assert len(proposals) == 1
        assert proposals[0].source == "NSL-?"

    def test_analyze_pending_confidence(self, tmp_path: Path) -> None:
        loop = FeedbackLoop(proposal_dir=tmp_path / "proposals")
        entries = [{"id": "1", "module": "m", "context": "c"}]
        proposals = loop.analyze_pending(entries)
        assert proposals[0].confidence == 0.6


class TestGenerateProposals:
    def test_generate_equals_analyze(self, tmp_path: Path) -> None:
        loop = FeedbackLoop(proposal_dir=tmp_path / "proposals")
        entries = [{"id": "1", "module": "m", "context": "c"}]
        analyzed = loop.analyze_pending(entries)
        generated = loop.generate_proposals(entries)
        assert len(analyzed) == len(generated)
        assert analyzed[0].source == generated[0].source


class TestApplyProposal:
    def test_apply_creates_yaml_file(self, tmp_path: Path) -> None:
        proposal_dir = tmp_path / "proposals"
        loop = FeedbackLoop(proposal_dir=proposal_dir)
        proposal = EvolutionProposal(
            proposal_id="PROP-TEST001",
            source="NSL-001",
            pattern="test pattern",
            suggested_rule_change="add rule",
            confidence=0.7,
        )
        result = loop.apply_proposal(proposal)
        assert result is True
        yaml_path = proposal_dir / "PROP-TEST001.yaml"
        assert yaml_path.exists()
        data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        assert data["proposal_id"] == "PROP-TEST001"
        assert data["confidence"] == 0.7


class TestReviewProposals:
    def test_review_empty_dir(self, tmp_path: Path) -> None:
        loop = FeedbackLoop(proposal_dir=tmp_path / "proposals")
        result = loop.review_proposals()
        assert result == []

    def test_review_returns_applied_proposals(self, tmp_path: Path) -> None:
        proposal_dir = tmp_path / "proposals"
        loop = FeedbackLoop(proposal_dir=proposal_dir)
        proposal = EvolutionProposal(
            proposal_id="PROP-REVIEW001",
            source="NSL-001",
            pattern="review pattern",
            suggested_rule_change="change",
            confidence=0.9,
        )
        loop.apply_proposal(proposal)
        reviewed = loop.review_proposals()
        assert len(reviewed) == 1
        assert reviewed[0].proposal_id == "PROP-REVIEW001"

    def test_review_skips_invalid_yaml(self, tmp_path: Path) -> None:
        proposal_dir = tmp_path / "proposals"
        proposal_dir.mkdir(parents=True, exist_ok=True)
        bad_file = proposal_dir / "PROP-BAD.yaml"
        bad_file.write_text("invalid: [yaml: {broken", encoding="utf-8")
        loop = FeedbackLoop(proposal_dir=proposal_dir)
        result = loop.review_proposals()
        assert result == []

    def test_review_multiple_proposals(self, tmp_path: Path) -> None:
        proposal_dir = tmp_path / "proposals"
        loop = FeedbackLoop(proposal_dir=proposal_dir)
        for i in range(3):
            proposal = EvolutionProposal(
                proposal_id=f"PROP-MULTI{i:03d}",
                source=f"NSL-{i}",
                pattern=f"pattern {i}",
                suggested_rule_change=f"change {i}",
            )
            loop.apply_proposal(proposal)
        reviewed = loop.review_proposals()
        assert len(reviewed) == 3
