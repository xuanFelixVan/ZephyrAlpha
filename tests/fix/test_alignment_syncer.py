# [A_test] module_id: MOD-GOV_alignment_syncer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §test
# [MODULE] tests.test_alignment_syncer
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_alignment_syncer.py
# [TTL] task_bound

import os
import tempfile

import pytest

syncer_mod = pytest.importorskip(
    "zephyr.infrastructure.auto_fix_engine.alignment_syncer", reason="alignment_syncer not available"
)
AlignmentSyncer = syncer_mod.AlignmentSyncer

models = pytest.importorskip("zephyr.infrastructure.auto_fix_engine.models", reason="models not available")
FixStatus = models.FixStatus
FixLevel = models.FixLevel


class TestAlignmentSyncerInstantiation:
    def test_fixer_id(self):
        syncer = AlignmentSyncer()
        assert syncer.fixer_id == "alignment_syncer"

    def test_action_type(self):
        syncer = AlignmentSyncer()
        assert syncer.action_type == "alignment_sync"

    def test_level_is_l1_rule(self):
        syncer = AlignmentSyncer()
        assert syncer.level == FixLevel.L1_RULE


class TestAlignmentSyncerScan:
    def test_scan_returns_list(self):
        syncer = AlignmentSyncer()
        result = syncer.scan()
        assert isinstance(result, list)

    def test_scan_finding_has_type_field(self):
        syncer = AlignmentSyncer()
        result = syncer.scan()
        for finding in result:
            assert "type" in finding
            assert finding["type"] == "code_missing_from_blueprint"


class TestAlignmentSyncerFix:
    def test_fix_nonexistent_target(self):
        syncer = AlignmentSyncer()
        action = syncer.fix("/nonexistent/path/file.py")
        assert action.status == FixStatus.FAILED
        assert "error" in action.metadata

    def test_fix_file_without_blueprint_header(self):
        syncer = AlignmentSyncer()
        content = "x = 1\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = f.name
        try:
            action = syncer.fix(path, dry_run=True)
            assert action.status == FixStatus.COMPLETED
            assert "note" in action.metadata
            assert "No [BLUEPRINT] header" in action.metadata["note"]
        finally:
            os.unlink(path)

    def test_fix_file_with_blueprint_header(self):
        syncer = AlignmentSyncer()
        content = "# [BLUEPRINT] MOD-INF-031 | some/path | §3\n\nx = 1\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = f.name
        try:
            action = syncer.fix(path, dry_run=True)
            assert action.status == FixStatus.COMPLETED
            assert action.metadata.get("sync_direction") == "code_to_blueprint"
            assert action.metadata.get("auto_fix") is False
        finally:
            os.unlink(path)

    def test_fix_does_not_auto_modify(self):
        syncer = AlignmentSyncer()
        content = "# [BLUEPRINT] MOD-INF-031 | some/path | §3\n\nx = 1\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = f.name
        try:
            action = syncer.fix(path, dry_run=False)
            assert action.metadata.get("auto_fix") is False
            assert "human review" in action.metadata.get("reason", "").lower()
        finally:
            os.unlink(path)


class TestAlignmentSyncerValidate:
    def test_validate_nonexistent_target(self):
        syncer = AlignmentSyncer()
        result = syncer.validate("/nonexistent/path/file.py")
        assert result.valid is False

    def test_validate_file_with_blueprint_header(self):
        syncer = AlignmentSyncer()
        content = "# [BLUEPRINT] MOD-INF-031 | some/path | §3\n\nx = 1\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = f.name
        try:
            result = syncer.validate(path)
            assert result.valid is True
            assert result.check_name == "alignment_sync"
        finally:
            os.unlink(path)

    def test_validate_file_without_blueprint_header(self):
        syncer = AlignmentSyncer()
        content = "x = 1\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = f.name
        try:
            result = syncer.validate(path)
            assert result.valid is False
            assert "Missing blueprint" in result.error or "missing" in result.error.lower()
        finally:
            os.unlink(path)


class TestAlignmentSyncerRollback:
    def test_rollback_returns_false(self):
        syncer = AlignmentSyncer()
        assert syncer.rollback("any_target") is False
