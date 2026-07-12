# [A_test] module_id: SRC-TST-1893 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-512 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.governance.test_validate_blueprint_overlap
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
import textwrap
from pathlib import Path
from unittest.mock import patch

import sys; sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts" / "governance")); from _shared.frontmatter import parse_frontmatter_from_file

from scripts.governance.d11_compliance.validate_blueprint_overlap import (
    detect_overlaps,
    extract_components,
    run_validation,
    scan_draft_components,
)


class TestParseFrontmatter:
    def test_valid_frontmatter(self, tmp_path: Path):
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent("""\
            ---
            components:
              - comp-a
              - comp-b
            ---
            # Content
            """),
            encoding="utf-8",
        )
        fm = parse_frontmatter_from_file(md)
        assert fm is not None
        assert "components" in fm
        assert fm["components"] == ["comp-a", "comp-b"]

    def test_no_frontmatter(self, tmp_path: Path):
        md = tmp_path / "no_fm.md"
        md.write_text("# No frontmatter\n", encoding="utf-8")
        fm = parse_frontmatter_from_file(md)
        assert fm is None

    def test_comma_separated_components(self, tmp_path: Path):
        md = tmp_path / "comma.md"
        md.write_text(
            "---\ncomponents: comp-x, comp-y, comp-z\n---\n# Content\n",
            encoding="utf-8",
        )
        fm = parse_frontmatter_from_file(md)
        assert fm is not None
        comps = extract_components(fm)
        assert len(comps) == 3


class TestExtractComponents:
    def test_list_components(self):
        fm = {"components": ["comp-a", "comp-b"]}
        assert extract_components(fm) == ["comp-a", "comp-b"]

    def test_string_components(self):
        fm = {"components": "comp-a, comp-b"}
        assert extract_components(fm) == ["comp-a", "comp-b"]

    def test_none_frontmatter(self):
        assert extract_components(None) == []

    def test_empty_components(self):
        fm = {"components": []}
        assert extract_components(fm) == []

    def test_no_components_key(self):
        fm = {"name": "test"}
        assert extract_components(fm) == []


class TestDetectOverlaps:
    def test_no_overlaps(self):
        component_map = {
            "comp-a": [Path("draft1.md")],
            "comp-b": [Path("draft2.md")],
        }
        overlaps = detect_overlaps(component_map)
        assert len(overlaps) == 0

    def test_overlap_found(self):
        component_map = {
            "comp-a": [Path("draft1.md"), Path("draft2.md")],
            "comp-b": [Path("draft2.md")],
        }
        overlaps = detect_overlaps(component_map)
        assert len(overlaps) == 1
        assert overlaps[0]["component_id"] == "comp-a"
        assert overlaps[0]["draft_count"] == 2

    def test_triple_overlap(self):
        component_map = {
            "comp-x": [Path("d1.md"), Path("d2.md"), Path("d3.md")],
        }
        overlaps = detect_overlaps(component_map)
        assert len(overlaps) == 1
        assert overlaps[0]["draft_count"] == 3


class TestScanDraftComponents:
    def test_scan_with_components(self, tmp_path: Path):
        drafts_dir = tmp_path / "drafts"
        drafts_dir.mkdir()
        (drafts_dir / "draft-alpha.md").write_text(
            "---\ncomponents:\n  - comp-a\n  - comp-b\n---\n# Alpha\n",
            encoding="utf-8",
        )
        (drafts_dir / "draft-beta.md").write_text(
            "---\ncomponents:\n  - comp-b\n  - comp-c\n---\n# Beta\n",
            encoding="utf-8",
        )
        result = scan_draft_components(drafts_dir)
        assert "comp-a" in result
        assert "comp-b" in result
        assert len(result["comp-b"]) == 2

    def test_scan_skip_readme(self, tmp_path: Path):
        drafts_dir = tmp_path / "drafts"
        drafts_dir.mkdir()
        (drafts_dir / "README.md").write_text("# Readme\n", encoding="utf-8")
        result = scan_draft_components(drafts_dir)
        assert len(result) == 0

    def test_scan_nonexistent_dir(self, tmp_path: Path):
        result = scan_draft_components(tmp_path / "nonexistent")
        assert result == {}


class TestRunValidation:
    def test_missing_drafts_root(self, tmp_path: Path):
        fake_root = tmp_path / "nonexistent"
        with patch("scripts.governance.d11_compliance.validate_blueprint_overlap.DRAFTS_ROOT", fake_root):
            overlaps, count = run_validation()
            assert overlaps == []
            assert count == 0

    def test_no_overlaps_pass(self, tmp_path: Path):
        drafts_dir = tmp_path / "drafts"
        drafts_dir.mkdir()
        (drafts_dir / "draft-a.md").write_text(
            "---\ncomponents:\n  - comp-a\n---\n# A\n",
            encoding="utf-8",
        )
        (drafts_dir / "draft-b.md").write_text(
            "---\ncomponents:\n  - comp-b\n---\n# B\n",
            encoding="utf-8",
        )
        with patch("scripts.governance.d11_compliance.validate_blueprint_overlap.DRAFTS_ROOT", drafts_dir):
            overlaps, count = run_validation(verbose=True)
        assert len(overlaps) == 0
        assert count >= 2

    def test_overlap_detected(self, tmp_path: Path):
        drafts_dir = tmp_path / "drafts"
        drafts_dir.mkdir()
        (drafts_dir / "draft-a.md").write_text(
            "---\ncomponents:\n  - shared-comp\n---\n# A\n",
            encoding="utf-8",
        )
        (drafts_dir / "draft-b.md").write_text(
            "---\ncomponents:\n  - shared-comp\n---\n# B\n",
            encoding="utf-8",
        )
        with patch("scripts.governance.d11_compliance.validate_blueprint_overlap.DRAFTS_ROOT", drafts_dir):
            overlaps, count = run_validation()
        assert len(overlaps) == 1
        assert overlaps[0]["component_id"] == "shared-comp"
