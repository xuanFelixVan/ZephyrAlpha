# [BLUEPRINT] MOD-D5_ARCH_TOOLS | (auto-injected by S4 reconciler) | §
# [A_module] module_id=MOD-D5_ARCH_TOOLS | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [MODULE] tests.governance.test_ast_import_rewriter
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.ast_import_rewriter
# [STARTUP] on_demand
# [MATURITY] production
# [TTL] task_bound
"""Tests for scripts/governance/ast_import_rewriter.py."""

from __future__ import annotations

import importlib.util
import sys
import textwrap
from pathlib import Path

import pytest

# Load ast_import_rewriter directly from file path to avoid package name
# collision between scripts/governance/ and src/zephyr/governance/
_REPO = Path(__file__).resolve().parents[2]
_MODULE_PATH = _REPO / "scripts" / "governance" / "ast_import_rewriter.py"
_spec = importlib.util.spec_from_file_location("ast_import_rewriter", _MODULE_PATH)
assert _spec is not None and _spec.loader is not None
_mod = importlib.util.module_from_spec(_spec)
sys.modules["ast_import_rewriter"] = _mod  # required by @dataclass in Python 3.12
_spec.loader.exec_module(_mod)

Change = _mod.Change
ImportRewriter = _mod.ImportRewriter
MoveEntry = _mod.MoveEntry
RewriteResult = _mod.RewriteResult
load_move_map = _mod.load_move_map


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture
def simple_moves() -> list[MoveEntry]:
    return [
        MoveEntry(
            old_module="zephyr.governance.escalation_api",
            new_module="zephyr.governance.escalation.escalation_api",
            old_path="src/zephyr/governance/escalation_api.py",
            new_path="src/zephyr/governance/escalation/escalation_api.py",
        ),
        MoveEntry(
            old_module="zephyr.governance.cost_budget",
            new_module="zephyr.governance.budget.cost_budget",
            old_path="src/zephyr/governance/cost_budget.py",
            new_path="src/zephyr/governance/budget/cost_budget.py",
        ),
    ]


@pytest.fixture
def rewriter(simple_moves: list[MoveEntry]) -> ImportRewriter:
    return ImportRewriter(simple_moves)


# ------------------------------------------------------------------
# _find_replacement
# ------------------------------------------------------------------


class TestFindReplacement:
    def test_exact_match(self, rewriter: ImportRewriter):
        assert (
            rewriter.find_replacement("zephyr.governance.escalation_api")
            == "zephyr.governance.escalation.escalation_api"
        )

    def test_no_match(self, rewriter: ImportRewriter):
        assert rewriter.find_replacement("zephyr.governance.unknown") is None

    def test_prefix_match(self, rewriter: ImportRewriter):
        # zephyr.governance.escalation_api.models should map to ...escalation.escalation_api.models
        result = rewriter.find_replacement("zephyr.governance.escalation_api.models")
        assert result == "zephyr.governance.escalation.escalation_api.models"

    def test_idempotent_already_new(self, rewriter: ImportRewriter):
        # Already a new module path → should return None (no change needed)
        assert rewriter.find_replacement("zephyr.governance.escalation.escalation_api") is None

    def test_empty_module(self, rewriter: ImportRewriter):
        assert rewriter.find_replacement("") is None


# ------------------------------------------------------------------
# rewrite_file: ImportFrom
# ------------------------------------------------------------------


class TestRewriteImportFrom:
    def test_basic_from_import(self, rewriter: ImportRewriter, tmp_path: Path):
        f = tmp_path / "consumer.py"
        f.write_text(
            textwrap.dedent("""\
            from zephyr.governance.escalation_api import trigger

            def use():
                trigger()
            """),
            encoding="utf-8",
        )
        r = rewriter.rewrite_file(f, dry_run=False)
        assert r.modified
        assert len(r.changes) == 1
        assert r.changes[0].change_type == "ImportFrom"
        content = f.read_text(encoding="utf-8")
        assert "from zephyr.governance.escalation.escalation_api import trigger" in content

    def test_from_import_with_alias(self, rewriter: ImportRewriter, tmp_path: Path):
        f = tmp_path / "consumer.py"
        f.write_text(
            "from zephyr.governance.cost_budget import Budget as B\n",
            encoding="utf-8",
        )
        r = rewriter.rewrite_file(f, dry_run=False)
        assert r.modified
        content = f.read_text(encoding="utf-8")
        assert "from zephyr.governance.budget.cost_budget import Budget as B" in content

    def test_from_import_multiple_names(self, rewriter: ImportRewriter, tmp_path: Path):
        f = tmp_path / "consumer.py"
        f.write_text(
            "from zephyr.governance.escalation_api import trigger, cancel\n",
            encoding="utf-8",
        )
        r = rewriter.rewrite_file(f, dry_run=False)
        assert r.modified
        content = f.read_text(encoding="utf-8")
        assert "from zephyr.governance.escalation.escalation_api import trigger, cancel" in content


# ------------------------------------------------------------------
# rewrite_file: Import (plain)
# ------------------------------------------------------------------


class TestRewriteImport:
    def test_basic_import(self, rewriter: ImportRewriter, tmp_path: Path):
        f = tmp_path / "consumer.py"
        f.write_text(
            "import zephyr.governance.escalation_api\n",
            encoding="utf-8",
        )
        r = rewriter.rewrite_file(f, dry_run=False)
        assert r.modified
        assert any(c.change_type == "Import" for c in r.changes)
        content = f.read_text(encoding="utf-8")
        assert "import zephyr.governance.escalation.escalation_api" in content

    def test_import_with_alias(self, rewriter: ImportRewriter, tmp_path: Path):
        f = tmp_path / "consumer.py"
        f.write_text(
            "import zephyr.governance.cost_budget as cb\n",
            encoding="utf-8",
        )
        r = rewriter.rewrite_file(f, dry_run=False)
        assert r.modified
        content = f.read_text(encoding="utf-8")
        assert "import zephyr.governance.budget.cost_budget as cb" in content


# ------------------------------------------------------------------
# rewrite_file: MODULE header
# ------------------------------------------------------------------


class TestRewriteModuleHeader:
    def test_module_header_updated(self, rewriter: ImportRewriter, tmp_path: Path):
        f = tmp_path / "moved.py"
        f.write_text(
            textwrap.dedent("""\
            # [MODULE] zephyr.governance.escalation_api
            # [DOMAIN] D_GOVERNANCE
            \"\"\"Escalation API.\"\"\"
            """),
            encoding="utf-8",
        )
        r = rewriter.rewrite_file(f, dry_run=False)
        assert r.modified
        header_changes = [c for c in r.changes if c.change_type == "MODULE_HEADER"]
        assert len(header_changes) == 1
        content = f.read_text(encoding="utf-8")
        assert "[MODULE] zephyr.governance.escalation.escalation_api" in content


# ------------------------------------------------------------------
# rewrite_file: dry-run & idempotency
# ------------------------------------------------------------------


class TestDryRunAndIdempotency:
    def test_dry_run_no_modification(self, rewriter: ImportRewriter, tmp_path: Path):
        f = tmp_path / "consumer.py"
        original = "from zephyr.governance.escalation_api import trigger\n"
        f.write_text(original, encoding="utf-8")
        r = rewriter.rewrite_file(f, dry_run=True)
        assert r.modified  # result reports changes
        assert f.read_text(encoding="utf-8") == original  # but file unchanged

    def test_idempotent_second_run(self, rewriter: ImportRewriter, tmp_path: Path):
        f = tmp_path / "consumer.py"
        f.write_text(
            "from zephyr.governance.escalation_api import trigger\n",
            encoding="utf-8",
        )
        # First run
        r1 = rewriter.rewrite_file(f, dry_run=False)
        assert r1.modified
        # Second run on the same (now updated) file
        r2 = rewriter.rewrite_file(f, dry_run=False)
        assert not r2.modified

    def test_no_match_unchanged(self, rewriter: ImportRewriter, tmp_path: Path):
        f = tmp_path / "consumer.py"
        original = "from zephyr.governance.unrelated import thing\n"
        f.write_text(original, encoding="utf-8")
        r = rewriter.rewrite_file(f, dry_run=False)
        assert not r.modified
        assert f.read_text(encoding="utf-8") == original

    def test_syntax_error_skipped(self, rewriter: ImportRewriter, tmp_path: Path):
        f = tmp_path / "broken.py"
        f.write_text("def broken(:\n", encoding="utf-8")
        r = rewriter.rewrite_file(f, dry_run=False)
        assert not r.modified


# ------------------------------------------------------------------
# rewrite_file: formatting preservation
# ------------------------------------------------------------------


class TestFormattingPreservation:
    def test_comments_preserved(self, rewriter: ImportRewriter, tmp_path: Path):
        f = tmp_path / "consumer.py"
        f.write_text(
            textwrap.dedent("""\
            # This is a comment
            from zephyr.governance.escalation_api import trigger  # inline comment

            # Another comment
            x = 1
            """),
            encoding="utf-8",
        )
        r = rewriter.rewrite_file(f, dry_run=False)
        assert r.modified
        content = f.read_text(encoding="utf-8")
        assert "# This is a comment" in content
        assert "# inline comment" in content
        assert "# Another comment" in content
        assert "from zephyr.governance.escalation.escalation_api import trigger  # inline comment" in content

    def test_multiline_from_import(self, rewriter: ImportRewriter, tmp_path: Path):
        f = tmp_path / "consumer.py"
        f.write_text(
            textwrap.dedent("""\
            from zephyr.governance.escalation_api import (
                trigger,
                cancel,
            )
            """),
            encoding="utf-8",
        )
        r = rewriter.rewrite_file(f, dry_run=False)
        assert r.modified
        content = f.read_text(encoding="utf-8")
        assert "from zephyr.governance.escalation.escalation_api import (" in content


# ------------------------------------------------------------------
# load_move_map
# ------------------------------------------------------------------


class TestLoadMoveMap:
    def test_load_yaml(self, tmp_path: Path):
        yaml_file = tmp_path / "moves.yaml"
        yaml_file.write_text(
            textwrap.dedent("""\
            moves:
              - old_module: zephyr.governance.foo
                new_module: zephyr.governance.sub.foo
                old_path: src/zephyr/governance/foo.py
                new_path: src/zephyr/governance/sub/foo.py
              - old_module: zephyr.governance.bar
                new_module: zephyr.governance.sub.bar
                old_path: src/zephyr/governance/bar.py
                new_path: src/zephyr/governance/sub/bar.py
            """),
            encoding="utf-8",
        )
        moves = load_move_map(yaml_file)
        assert len(moves) == 2
        assert moves[0].old_module == "zephyr.governance.foo"
        assert moves[0].new_module == "zephyr.governance.sub.foo"
        assert moves[1].old_module == "zephyr.governance.bar"


# ------------------------------------------------------------------
# Integration: multiple changes in one file
# ------------------------------------------------------------------


class TestIntegration:
    def test_multiple_imports_one_file(self, rewriter: ImportRewriter, tmp_path: Path):
        f = tmp_path / "consumer.py"
        f.write_text(
            textwrap.dedent("""\
            # [MODULE] zephyr.governance.escalation_api
            from zephyr.governance.escalation_api import trigger
            from zephyr.governance.cost_budget import Budget
            import zephyr.governance.escalation_api as ea

            def use():
                trigger()
                b = Budget()
                ea.cancel()
            """),
            encoding="utf-8",
        )
        r = rewriter.rewrite_file(f, dry_run=False)
        assert r.modified
        # Should have: 2 ImportFrom + 1 Import + 1 MODULE_HEADER = 4 changes
        assert len(r.changes) == 4
        content = f.read_text(encoding="utf-8")
        assert "[MODULE] zephyr.governance.escalation.escalation_api" in content
        assert "from zephyr.governance.escalation.escalation_api import trigger" in content
        assert "from zephyr.governance.budget.cost_budget import Budget" in content
        assert "import zephyr.governance.escalation.escalation_api as ea" in content

    def test_prefix_match_submodule(self, rewriter: ImportRewriter, tmp_path: Path):
        f = tmp_path / "consumer.py"
        f.write_text(
            "from zephyr.governance.escalation_api.models import Alert\n",
            encoding="utf-8",
        )
        r = rewriter.rewrite_file(f, dry_run=False)
        assert r.modified
        content = f.read_text(encoding="utf-8")
        assert "from zephyr.governance.escalation.escalation_api.models import Alert" in content
