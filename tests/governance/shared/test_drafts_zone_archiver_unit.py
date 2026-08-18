# [A_test] module_id: MOD-GOV_drafts_zone_archiver_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-630 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_drafts_zone_archiver
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-TEST-630 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
import textwrap
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from scripts.governance.d1_structure.archive_drafts_zone import (
    STATUS_ARBITRATED,
    compute_archive_target,
    execute_archive,
    scan_drafts,
)
from scripts.governance.shared.frontmatter import parse_frontmatter_from_file


class TestParseFrontmatter:
    def test_valid_frontmatter(self, tmp_path: Path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            ---
            audit_status: arbitrated
            arbitrated_date: "2026-03-01"
            ---
            # Content
            """),
            encoding="utf-8",
        )
        fm = parse_frontmatter_from_file(md)
        assert fm is not None
        assert fm["audit_status"] == "arbitrated"
        assert fm["arbitrated_date"] == "2026-03-01"

    def test_no_frontmatter(self, tmp_path: Path):
        md = tmp_path / "no_fm.md"
        md.write_text("# No frontmatter\n", encoding="utf-8")
        fm = parse_frontmatter_from_file(md)
        assert fm is None

    def test_invalid_yaml(self, tmp_path: Path):
        md = tmp_path / "bad_yaml.md"
        md.write_text("---\n: invalid\n---\n", encoding="utf-8")
        fm = parse_frontmatter_from_file(md)
        assert fm is None


class TestScanDrafts:
    def test_scan_with_arbitrated_old(self, tmp_path: Path):
        drafts_dir = tmp_path / "drafts"
        drafts_dir.mkdir()
        old_date = (datetime.now(UTC) - timedelta(days=65)).strftime("%Y-%m-%d")
        (drafts_dir / "old-draft.md").write_text(
            f"---\naudit_status: arbitrated\narbitrated_date: '{old_date}'\n---\n# Old\n",
            encoding="utf-8",
        )
        results = scan_drafts(drafts_dir)
        assert len(results) == 1
        assert results[0]["action"] == "archive"

    def test_scan_with_arbitrated_warn(self, tmp_path: Path):
        drafts_dir = tmp_path / "drafts"
        drafts_dir.mkdir()
        warn_date = (datetime.now(UTC) - timedelta(days=35)).strftime("%Y-%m-%d")
        (drafts_dir / "warn-draft.md").write_text(
            f"---\naudit_status: arbitrated\narbitrated_date: '{warn_date}'\n---\n# Warn\n",
            encoding="utf-8",
        )
        results = scan_drafts(drafts_dir)
        assert len(results) == 1
        assert results[0]["action"] == "warn"

    def test_scan_with_arbitrated_recent(self, tmp_path: Path):
        drafts_dir = tmp_path / "drafts"
        drafts_dir.mkdir()
        recent_date = (datetime.now(UTC) - timedelta(days=10)).strftime("%Y-%m-%d")
        (drafts_dir / "recent-draft.md").write_text(
            f"---\naudit_status: arbitrated\narbitrated_date: '{recent_date}'\n---\n# Recent\n",
            encoding="utf-8",
        )
        results = scan_drafts(drafts_dir)
        assert len(results) == 1
        assert results[0]["action"] == "skip"

    def test_scan_non_arbitrated(self, tmp_path: Path):
        drafts_dir = tmp_path / "drafts"
        drafts_dir.mkdir()
        (drafts_dir / "draft-draft.md").write_text(
            "---\naudit_status: draft\n---\n# Draft\n",
            encoding="utf-8",
        )
        results = scan_drafts(drafts_dir)
        assert len(results) == 1
        assert results[0]["action"] == "skip"

    def test_scan_skip_readme(self, tmp_path: Path):
        drafts_dir = tmp_path / "drafts"
        drafts_dir.mkdir()
        (drafts_dir / "README.md").write_text("# Readme\n", encoding="utf-8")
        results = scan_drafts(drafts_dir)
        assert len(results) == 0

    def test_scan_nonexistent_dir(self, tmp_path: Path):
        results = scan_drafts(tmp_path / "nonexistent")
        assert results == []


class TestComputeArchiveTarget:
    def test_target_path(self, tmp_path: Path):
        draft = tmp_path / "drafts" / "my-subdir" / "draft.md"
        target = compute_archive_target(draft, "2026-03-15")
        assert "2026-03" in str(target)
        assert "my-subdir" in str(target)

    def test_target_undated(self, tmp_path: Path):
        draft = tmp_path / "drafts" / "my-subdir" / "draft.md"
        target = compute_archive_target(draft, "invalid-date")
        assert "undated" in str(target)


class TestExecuteArchive:
    def test_warn_action(self, tmp_path: Path):
        drafts = [
            {
                "path": tmp_path / "warn.md",
                "relative": Path("warn.md"),
                "audit_status": STATUS_ARBITRATED,
                "arbitrated_date": "2026-02-01",
                "age_days": 35,
                "action": "warn",
            }
        ]
        with patch("scripts.governance.d1_structure.archive_drafts_zone.write_audit_log"):
            actions = execute_archive(drafts, confirm=False)
        assert len(actions) == 1
        assert "WARN" in actions[0]

    def test_archive_proposed_dry_run(self, tmp_path: Path):
        draft_file = tmp_path / "old-draft.md"
        draft_file.write_text("---\naudit_status: arbitrated\n---\n", encoding="utf-8")
        drafts = [
            {
                "path": draft_file,
                "relative": Path("old-draft.md"),
                "audit_status": STATUS_ARBITRATED,
                "arbitrated_date": "2026-01-01",
                "age_days": 65,
                "action": "archive",
            }
        ]
        with (
            patch("scripts.governance.d1_structure.archive_drafts_zone.write_audit_log"),
            patch("scripts.governance.d1_structure.archive_drafts_zone.REPO_ROOT", tmp_path),
            patch("scripts.governance.d1_structure.archive_drafts_zone.ARCHIVE_ROOT", tmp_path / "archive"),
        ):
            actions = execute_archive(drafts, confirm=False)
        assert len(actions) == 1
        assert "PROPOSED" in actions[0]

    def test_archive_confirmed(self, tmp_path: Path):
        draft_file = tmp_path / "old-draft.md"
        draft_file.write_text("---\naudit_status: arbitrated\n---\n", encoding="utf-8")
        archive_root = tmp_path / "archive"
        drafts = [
            {
                "path": draft_file,
                "relative": Path("old-draft.md"),
                "audit_status": STATUS_ARBITRATED,
                "arbitrated_date": "2026-01-01",
                "age_days": 65,
                "action": "archive",
            }
        ]
        with (
            patch("scripts.governance.d1_structure.archive_drafts_zone.write_audit_log"),
            patch("scripts.governance.d1_structure.archive_drafts_zone.REPO_ROOT", tmp_path),
            patch("scripts.governance.d1_structure.archive_drafts_zone.ARCHIVE_ROOT", archive_root),
        ):
            actions = execute_archive(drafts, confirm=True)
        assert len(actions) == 1
        assert "ARCHIVED" in actions[0]

    def test_no_actions_for_skip(self, tmp_path: Path):
        drafts = [
            {
                "path": tmp_path / "skip.md",
                "relative": Path("skip.md"),
                "audit_status": "draft",
                "arbitrated_date": None,
                "age_days": None,
                "action": "skip",
            }
        ]
        with patch("scripts.governance.d1_structure.archive_drafts_zone.write_audit_log"):
            actions = execute_archive(drafts, confirm=False)
        assert len(actions) == 0
