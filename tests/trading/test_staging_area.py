# [A_test] module_id: MOD-GOV_staging_area | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from zephyr.trading.staging_area import CommitStatus, StagingArea


def test_write_draft_and_commit():
    with tempfile.TemporaryDirectory() as tmpdir:
        sa = StagingArea(project_root=tmpdir)
        target = Path(tmpdir) / "src" / "foo.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("original content", encoding="utf-8")

        sa.write_draft("session-001", "src/foo.py", "new content")
        drafts = sa.list_drafts("session-001")
        assert "src/foo.py" in drafts, f"Expected src/foo.py in drafts, got {drafts}"

        result = sa.commit("session-001", "src/foo.py")
        assert result.status == CommitStatus.OK, f"Expected OK, got {result.status}: {result.message}"
        assert target.read_text(encoding="utf-8") == "new content"
        assert sa.list_drafts("session-001") == []
    print("test_write_draft_and_commit PASSED")


def test_conflict_detection():
    with tempfile.TemporaryDirectory() as tmpdir:
        sa = StagingArea(project_root=tmpdir)
        target = Path(tmpdir) / "src" / "bar.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("original", encoding="utf-8")

        sa.write_draft("session-001", "src/bar.py", "draft content")

        import time

        time.sleep(0.05)
        target.write_text("modified by another session", encoding="utf-8")

        result = sa.commit("session-001", "src/bar.py")
        assert result.status == CommitStatus.CONFLICT, f"Expected CONFLICT, got {result.status}: {result.message}"
        assert result.conflict is not None
    print("test_conflict_detection PASSED")


def test_two_sessions_different_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        sa = StagingArea(project_root=tmpdir)
        f1 = Path(tmpdir) / "src" / "a.py"
        f2 = Path(tmpdir) / "src" / "b.py"
        f1.parent.mkdir(parents=True, exist_ok=True)
        f1.write_text("a-original", encoding="utf-8")
        f2.write_text("b-original", encoding="utf-8")

        sa.write_draft("session-001", "src/a.py", "a-new")
        sa.write_draft("session-002", "src/b.py", "b-new")

        r1 = sa.commit("session-001", "src/a.py")
        r2 = sa.commit("session-002", "src/b.py")
        assert r1.status == CommitStatus.OK
        assert r2.status == CommitStatus.OK
        assert f1.read_text(encoding="utf-8") == "a-new"
        assert f2.read_text(encoding="utf-8") == "b-new"
    print("test_two_sessions_different_files PASSED")


def test_discard_draft():
    with tempfile.TemporaryDirectory() as tmpdir:
        sa = StagingArea(project_root=tmpdir)
        target = Path(tmpdir) / "src" / "c.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("original", encoding="utf-8")

        sa.write_draft("session-001", "src/c.py", "draft")
        assert "src/c.py" in sa.list_drafts("session-001")

        ok = sa.discard("session-001", "src/c.py")
        assert ok, "discard should return True"
        assert sa.list_drafts("session-001") == []
    print("test_discard_draft PASSED")


def test_commit_no_draft():
    with tempfile.TemporaryDirectory() as tmpdir:
        sa = StagingArea(project_root=tmpdir)
        result = sa.commit("session-001", "src/nonexistent.py")
        assert result.status == CommitStatus.NO_DRAFT
    print("test_commit_no_draft PASSED")


def test_get_conflict():
    with tempfile.TemporaryDirectory() as tmpdir:
        sa = StagingArea(project_root=tmpdir)
        target = Path(tmpdir) / "src" / "d.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("original", encoding="utf-8")

        sa.write_draft("session-001", "src/d.py", "draft")

        conflict = sa.get_conflict("session-001", "src/d.py")
        assert conflict is None, "No conflict yet"

        import time

        time.sleep(0.05)
        target.write_text("modified", encoding="utf-8")

        conflict = sa.get_conflict("session-001", "src/d.py")
        assert conflict is not None, "Should detect conflict now"
    print("test_get_conflict PASSED")


def test_auto_merge_non_overlapping():
    with tempfile.TemporaryDirectory() as tmpdir:
        sa = StagingArea(project_root=tmpdir)
        target = Path(tmpdir) / "src" / "e.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("line1\nline2\nline3\n", encoding="utf-8")

        sa.write_draft("session-001", "src/e.py", "line1\nline2-draft\nline3\n")

        import time

        time.sleep(0.05)
        target.write_text("line1-modified\nline2\nline3\n", encoding="utf-8")

        result = sa.try_auto_merge("session-001", "src/e.py")
        assert result.status in (
            CommitStatus.MERGED,
            CommitStatus.CONFLICT_NEEDS_OWNER,
        ), f"Expected MERGED or CONFLICT_NEEDS_OWNER, got {result.status}: {result.message}"
    print("test_auto_merge_non_overlapping PASSED")


if __name__ == "__main__":
    test_write_draft_and_commit()
    test_conflict_detection()
    test_two_sessions_different_files()
    test_discard_draft()
    test_commit_no_draft()
    test_get_conflict()
    test_auto_merge_non_overlapping()
    print("\nAll staging_area tests PASSED!")
