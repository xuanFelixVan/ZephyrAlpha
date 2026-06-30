# [A_test] module_id: SRC-TST-2012 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-629 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_dos_launcher
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
Unit tests for dos_launcher.py (T-2-27, C53)
==============================================
Minimum: 10 tests
"""


from pathlib import Path

from zephyr.shared.api.dos_launcher import (
    DOSLauncher,
    DOSResult,
    _parse_body,
    _parse_frontmatter,
)


def _write_directive(
    base: Path, name: str, directive_id: str, title: str = "", domain: str = "", safety: str = "L", body: str = ""
) -> Path:
    p = base / name
    p.parent.mkdir(parents=True, exist_ok=True)
    content = (
        f"---\ndirective_id: {directive_id}\ntitle: {title}\ndomain: {domain}\nsafety_level: {safety}\n---\n{body}"
    )
    p.write_text(content, encoding="utf-8")
    return p


class TestParseFrontmatter:
    def test_valid_frontmatter(self) -> None:
        text = "---\ndirective_id: '325'\ntitle: Test\n---\nBody"
        fm = _parse_frontmatter(text)
        assert fm["directive_id"] == "325"
        assert fm["title"] == "Test"

    def test_no_frontmatter(self) -> None:
        text = "Just content"
        assert _parse_frontmatter(text) == {}

    def test_empty_string(self) -> None:
        assert _parse_frontmatter("") == {}


class TestParseBody:
    def test_body_after_frontmatter(self) -> None:
        text = "---\ndirective_id: 325\n---\nHello world"
        assert _parse_body(text) == "Hello world"

    def test_no_frontmatter_returns_full(self) -> None:
        text = "Just content here"
        assert _parse_body(text) == "Just content here"


class TestDOSLauncher:
    def test_load_directive_found(self, tmp_path: Path) -> None:
        _write_directive(tmp_path, "325.md", "325", "Architecture Review", "D2", "M", "Review architecture")
        launcher = DOSLauncher(directive_dir=tmp_path)
        info = launcher.load_directive("325")
        assert info is not None
        assert info.directive_id == "325"
        assert info.title == "Architecture Review"
        assert info.domain == "D2"

    def test_load_directive_not_found(self, tmp_path: Path) -> None:
        launcher = DOSLauncher(directive_dir=tmp_path)
        info = launcher.load_directive("999")
        assert info is None

    def test_load_directive_nonexistent_dir(self, tmp_path: Path) -> None:
        launcher = DOSLauncher(directive_dir=tmp_path / "nonexistent")
        info = launcher.load_directive("325")
        assert info is None

    def test_load_chain_single(self, tmp_path: Path) -> None:
        _write_directive(tmp_path, "325.md", "325", "Review", "D2", "L", "Content")
        launcher = DOSLauncher(directive_dir=tmp_path)
        result = launcher.load_chain("325")
        assert "325" in result.directives_loaded
        assert result.compliance is True

    def test_load_chain_multiple(self, tmp_path: Path) -> None:
        _write_directive(tmp_path, "325.md", "325", "Review", "D2", "L")
        _write_directive(tmp_path, "344.md", "344", "Factor", "D3", "L")
        _write_directive(tmp_path, "999.md", "999", "Commit", "D0", "L")
        launcher = DOSLauncher(directive_dir=tmp_path)
        result = launcher.load_chain("325+344+999")
        assert len(result.directives_loaded) == 3
        assert result.compliance is True

    def test_load_chain_partial_failure(self, tmp_path: Path) -> None:
        _write_directive(tmp_path, "325.md", "325", "Review", "D2", "L")
        launcher = DOSLauncher(directive_dir=tmp_path)
        result = launcher.load_chain("325+404")
        assert "325" in result.directives_loaded
        assert result.compliance is False
        assert len(result.errors) == 1

    def test_load_chain_empty(self, tmp_path: Path) -> None:
        launcher = DOSLauncher(directive_dir=tmp_path)
        result = launcher.load_chain("")
        assert result.compliance is False
        assert len(result.directives_loaded) == 0

    def test_list_available_directives(self, tmp_path: Path) -> None:
        _write_directive(tmp_path, "325.md", "325", "Review", "D2", "L")
        _write_directive(tmp_path, "999.md", "999", "Commit", "D0", "L")
        launcher = DOSLauncher(directive_dir=tmp_path)
        directives = launcher.list_available_directives()
        assert len(directives) == 2
        ids = {d.directive_id for d in directives}
        assert "325" in ids
        assert "999" in ids

    def test_cache_hit(self, tmp_path: Path) -> None:
        _write_directive(tmp_path, "325.md", "325", "Review", "D2", "L")
        launcher = DOSLauncher(directive_dir=tmp_path)
        info1 = launcher.load_directive("325")
        info2 = launcher.load_directive("325")
        assert info1 is info2

    def test_clear_cache(self, tmp_path: Path) -> None:
        _write_directive(tmp_path, "325.md", "325", "Review", "D2", "L")
        launcher = DOSLauncher(directive_dir=tmp_path)
        launcher.load_directive("325")
        launcher.clear_cache()
        assert len(launcher._cache) == 0

    def test_directive_dir_property(self, tmp_path: Path) -> None:
        launcher = DOSLauncher(directive_dir=tmp_path)
        assert launcher.directive_dir == tmp_path

    def test_dos_result_model(self) -> None:
        result = DOSResult(
            directives_loaded=["325", "999"],
            execution_log="[OK] 325\n[OK] 999",
            compliance=True,
            chain="325+999",
        )
        assert result.compliance is True
        assert len(result.directives_loaded) == 2
