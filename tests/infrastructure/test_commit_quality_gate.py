# [A_test] module_id: MOD-GOV_commit_quality_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §7
# [MODULE] tests.test_commit_quality_gate
# [INVARIANTS] revert commit必须通过lint
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.infrastructure.rollback.commit_quality_gate import (
    COMMIT_MSG_REQUIREMENTS,
    CommitQualityGate,
)


class TestCommitQualityGateInstantiation:
    def test_creates_instance(self):
        gate = CommitQualityGate()
        assert isinstance(gate, CommitQualityGate)

    def test_class_name(self):
        assert CommitQualityGate.__name__ == "CommitQualityGate"


class TestLintMessage:
    def test_valid_message_passes(self):
        gate = CommitQualityGate()
        report = gate.lint_message("abc1234", "Rollback: fix critical bug to abc1234def5678")
        assert report.passes_lint is True
        assert report.issues == []
        assert report.hash == "abc1234"

    def test_short_message_fails(self):
        gate = CommitQualityGate()
        report = gate.lint_message("abc1234", "Rollback: short")
        assert report.passes_lint is False
        assert any("too short" in i.lower() for i in report.issues)

    def test_missing_rollback_prefix_fails(self):
        gate = CommitQualityGate()
        report = gate.lint_message("abc1234", "Revert: some reason to abc1234def5678")
        assert report.passes_lint is False
        assert any("Must start with" in i for i in report.issues)

    def test_missing_sha_fails(self):
        gate = CommitQualityGate()
        report = gate.lint_message("abc1234", "Rollback: some reason without sha here")
        assert report.passes_lint is False
        assert any("SHA" in i for i in report.issues)

    def test_lowercase_first_char_fails(self):
        gate = CommitQualityGate()
        report = gate.lint_message("abc1234", "rollback: lowercase start to abc1234def5678")
        assert report.passes_lint is False
        assert any("uppercase" in i.lower() for i in report.issues)

    def test_empty_message_fails(self):
        gate = CommitQualityGate()
        report = gate.lint_message("abc1234", "")
        assert report.passes_lint is False
        assert len(report.issues) >= 2

    def test_whitespace_only_message_fails(self):
        gate = CommitQualityGate()
        report = gate.lint_message("abc1234", "   ")
        assert report.passes_lint is False

    def test_report_has_correct_hash(self):
        gate = CommitQualityGate()
        report = gate.lint_message("deadbeef", "Rollback: reason to deadbeef1234")
        assert report.hash == "deadbeef"

    def test_report_has_original_message(self):
        gate = CommitQualityGate()
        msg = "Rollback: test reason to abc1234def5678"
        report = gate.lint_message("abc1234", msg)
        assert report.message == msg


class TestGenerateRevertMessage:
    def test_with_reason(self):
        gate = CommitQualityGate()
        msg = gate.generate_revert_message("abc1234def", "fix data corruption")
        assert msg == "Rollback: fix data corruption to abc1234def"

    def test_without_reason(self):
        gate = CommitQualityGate()
        msg = gate.generate_revert_message("abc1234def")
        assert msg == "Rollback: automated revert to abc1234def"

    def test_empty_reason_defaults_to_automated(self):
        gate = CommitQualityGate()
        msg = gate.generate_revert_message("abc1234def", "")
        assert "automated revert" in msg

    def test_generated_message_passes_lint(self):
        gate = CommitQualityGate()
        sha = "abc1234def5678"
        msg = gate.generate_revert_message(sha, "critical failure detected")
        report = gate.lint_message(sha, msg)
        assert report.passes_lint is True

    def test_generated_automated_message_passes_lint(self):
        gate = CommitQualityGate()
        sha = "abc1234def5678"
        msg = gate.generate_revert_message(sha)
        report = gate.lint_message(sha, msg)
        assert report.passes_lint is True


class TestCommitMsgRequirements:
    def test_min_length_defined(self):
        assert "min_length" in COMMIT_MSG_REQUIREMENTS
        assert COMMIT_MSG_REQUIREMENTS["min_length"] == 20

    def test_must_start_with_defined(self):
        assert COMMIT_MSG_REQUIREMENTS["must_start_with"] == "Rollback"

    def test_must_contain_sha_defined(self):
        assert COMMIT_MSG_REQUIREMENTS["must_contain_sha"] is True
