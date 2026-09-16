# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §
# [MODULE] tests.governance.test_check_blueprint_code_alignment
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.checkers.check_blueprint_code_alignment
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 测试目录隔离：monkeypatch BLUEPRINTS_DIR/REPO_ROOT 到 tmp_path，避免扫描真实项目文件
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""tests for check_blueprint_code_alignment.py — ARCH-FRONTMATTER-STATE-001 Phase 4 gate."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CHECKER_DIR = _REPO_ROOT / "scripts" / "governance" / "d5_architecture" / "checkers"
if str(_CHECKER_DIR) not in sys.path:
    sys.path.insert(0, str(_CHECKER_DIR))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import check_blueprint_code_alignment as cbca  # noqa: E402


@pytest.fixture(autouse=True)
def _isolate_dirs(monkeypatch, tmp_path):
    """隔离 BLUEPRINTS_DIR 和 REPO_ROOT，防止扫描真实项目文件。"""
    monkeypatch.setattr(cbca, "BLUEPRINTS_DIR", tmp_path / "docs" / "03_modules")
    monkeypatch.setattr(cbca, "REPO_ROOT", tmp_path)


class TestAggregateBuildStatus:
    def test_first_non_empty_wins(self):
        rows = [
            {"blueprint_id": "MOD-A", "build_status": "generated"},
            {"blueprint_id": "MOD-A", "build_status": "stable"},
        ]
        assert cbca.aggregate_build_status(rows) == {"MOD-A": "generated"}

    def test_skip_empty_then_take_first_non_empty(self):
        rows = [
            {"blueprint_id": "MOD-A", "build_status": ""},
            {"blueprint_id": "MOD-A", "build_status": "planned"},
            {"blueprint_id": "MOD-A", "build_status": "generated"},
        ]
        assert cbca.aggregate_build_status(rows) == {"MOD-A": "planned"}

    def test_none_build_status_skipped(self):
        rows = [
            {"blueprint_id": "MOD-A", "build_status": None},
            {"blueprint_id": "MOD-A", "build_status": "stable"},
        ]
        assert cbca.aggregate_build_status(rows) == {"MOD-A": "stable"}

    def test_multiple_modules(self):
        rows = [
            {"blueprint_id": "MOD-A", "build_status": "generated"},
            {"blueprint_id": "MOD-B", "build_status": "planned"},
            {"blueprint_id": "MOD-A", "build_status": "stable"},
        ]
        assert cbca.aggregate_build_status(rows) == {
            "MOD-A": "generated",
            "MOD-B": "planned",
        }

    def test_empty_rows(self):
        assert cbca.aggregate_build_status([]) == {}


class TestCheckFrontmatterStateStale:
    def test_mismatch_reports_medium(self):
        findings = cbca.check_frontmatter_state_stale(
            [{"file": "a.md", "module_id": "MOD-A", "build_status": "planned"}],
            {"MOD-A": "generated"},
        )
        assert len(findings) == 1
        assert findings[0]["type"] == "FRONTMATTER_STATE_STALE"
        assert findings[0]["severity"] == "MEDIUM"
        assert findings[0]["file"] == "a.md"
        assert "planned" in findings[0]["detail"]
        assert "generated" in findings[0]["detail"]

    def test_match_no_finding(self):
        findings = cbca.check_frontmatter_state_stale(
            [{"file": "a.md", "module_id": "MOD-A", "build_status": "generated"}],
            {"MOD-A": "generated"},
        )
        assert findings == []

    def test_module_not_in_depgraph_skipped(self):
        findings = cbca.check_frontmatter_state_stale(
            [{"file": "a.md", "module_id": "MOD-A", "build_status": "planned"}],
            {},
        )
        assert findings == []

    def test_depgraph_empty_status_skipped(self):
        findings = cbca.check_frontmatter_state_stale(
            [{"file": "a.md", "module_id": "MOD-A", "build_status": "planned"}],
            {"MOD-A": ""},
        )
        assert findings == []

    def test_frontmatter_empty_status_reports(self):
        findings = cbca.check_frontmatter_state_stale(
            [{"file": "a.md", "module_id": "MOD-A", "build_status": ""}],
            {"MOD-A": "generated"},
        )
        assert len(findings) == 1
        assert "(空)" in findings[0]["detail"]

    def test_multiple_entries(self):
        findings = cbca.check_frontmatter_state_stale(
            [
                {"file": "a.md", "module_id": "MOD-A", "build_status": "planned"},
                {"file": "b.md", "module_id": "MOD-B", "build_status": "stable"},
                {"file": "c.md", "module_id": "MOD-C", "build_status": "generated"},
            ],
            {"MOD-A": "generated", "MOD-B": "stable", "MOD-C": "generated"},
        )
        assert len(findings) == 1
        assert findings[0]["file"] == "a.md"


class TestScanBlueprintFrontmatterEntries:
    def test_skip_index_md(self, tmp_path):
        bp_dir = tmp_path / "docs" / "03_modules"
        bp_dir.mkdir(parents=True)
        (bp_dir / "index.md").write_text("---\nmodule_id: MOD-INDEX\nbuild_status: planned\n---\n", encoding="utf-8")
        entries = cbca.scan_blueprint_frontmatter_entries()
        assert entries == []

    def test_extract_module_id_and_build_status(self, tmp_path):
        bp_dir = tmp_path / "docs" / "03_modules"
        bp_dir.mkdir(parents=True)
        (bp_dir / "mod_a.md").write_text(
            "---\nmodule_id: MOD-A\nbuild_status: generated\n---\nbody\n",
            encoding="utf-8",
        )
        entries = cbca.scan_blueprint_frontmatter_entries()
        assert len(entries) == 1
        assert entries[0]["module_id"] == "MOD-A"
        assert entries[0]["build_status"] == "generated"
        assert entries[0]["file"].endswith("mod_a.md")

    def test_no_frontmatter_skipped(self, tmp_path):
        bp_dir = tmp_path / "docs" / "03_modules"
        bp_dir.mkdir(parents=True)
        (bp_dir / "no_fm.md").write_text("# just body\n", encoding="utf-8")
        entries = cbca.scan_blueprint_frontmatter_entries()
        assert entries == []

    def test_no_module_id_skipped(self, tmp_path):
        bp_dir = tmp_path / "docs" / "03_modules"
        bp_dir.mkdir(parents=True)
        (bp_dir / "no_mid.md").write_text("---\nbuild_status: planned\n---\n", encoding="utf-8")
        entries = cbca.scan_blueprint_frontmatter_entries()
        assert entries == []

    def test_nested_directories(self, tmp_path):
        bp_dir = tmp_path / "docs" / "03_modules" / "sub" / "dir"
        bp_dir.mkdir(parents=True)
        (bp_dir / "mod_nested.md").write_text(
            "---\nmodule_id: MOD-NESTED\nbuild_status: stable\n---\n",
            encoding="utf-8",
        )
        entries = cbca.scan_blueprint_frontmatter_entries()
        assert len(entries) == 1
        assert entries[0]["module_id"] == "MOD-NESTED"

    def test_blueprints_dir_not_exists(self, tmp_path):
        entries = cbca.scan_blueprint_frontmatter_entries()
        assert entries == []


class TestBlueprintTargetResolution:
    """裁定#262 后续批治本：[BLUEPRINT] 落点账实校验（存在性 + 自述 id 一致）。"""

    @staticmethod
    def _entry(target: str, modid: str = "MOD-A") -> dict:
        return {"file": "src/zephyr/pkg/mod.py", "package": "pkg", "header_modid": modid, "target": target}

    def test_missing_target_reports_high(self):
        findings = cbca.check_blueprint_target_resolution([self._entry("docs/03_modules/gone/blueprint.md")])
        assert len(findings) == 1
        assert findings[0]["type"] == "BLUEPRINT_TARGET_MISSING"
        assert findings[0]["severity"] == "HIGH"
        assert "docs/03_modules/gone/blueprint.md" in findings[0]["detail"]

    def test_id_mismatch_reports_high(self, tmp_path):
        bp = tmp_path / "docs" / "03_modules" / "mod_a" / "blueprint.md"
        bp.parent.mkdir(parents=True)
        bp.write_text("---\nmodule_id: MOD-B\n---\n# body\n", encoding="utf-8")
        findings = cbca.check_blueprint_target_resolution([self._entry("docs/03_modules/mod_a/blueprint.md")])
        assert [f["type"] for f in findings] == ["BLUEPRINT_TARGET_ID_MISMATCH"]
        assert findings[0]["severity"] == "HIGH"
        assert "MOD-B" in findings[0]["detail"]

    def test_matching_module_id_no_finding(self, tmp_path):
        bp = tmp_path / "docs" / "03_modules" / "mod_a" / "blueprint.md"
        bp.parent.mkdir(parents=True)
        bp.write_text('---\nmodule_id: "MOD-A"\n---\n# body\n', encoding="utf-8")
        assert cbca.check_blueprint_target_resolution([self._entry("docs/03_modules/mod_a/blueprint.md")]) == []

    def test_blueprint_id_key_also_accepted(self, tmp_path):
        """批量生成的蓝图用 blueprint_id 键——两种键并存都算自述 id。"""
        bp = tmp_path / "docs" / "03_modules" / "mod_a" / "blueprint.md"
        bp.parent.mkdir(parents=True)
        bp.write_text("---\nblueprint_id: MOD-A\n---\n", encoding="utf-8")
        assert cbca.check_blueprint_target_resolution([self._entry("docs/03_modules/mod_a/blueprint.md")]) == []

    def test_no_declared_id_only_checks_existence(self, tmp_path):
        bp = tmp_path / "docs" / "03_modules" / "mod_a" / "blueprint.md"
        bp.parent.mkdir(parents=True)
        bp.write_text("---\ntitle: no id here\n---\n", encoding="utf-8")
        assert cbca.check_blueprint_target_resolution([self._entry("docs/03_modules/mod_a/blueprint.md")]) == []

    @pytest.mark.parametrize(
        "target",
        [
            "待统筹登记（10号文 §4 Phase 0/1.1 + 18号清单 §5 裁定）",
            "",
            "scripts/ops/some_tool.py",
            "src/zephyr/pkg/other.py",
        ],
    )
    def test_non_docs_or_prose_target_skipped(self, target):
        assert cbca.check_blueprint_target_resolution([self._entry(target)]) == []

    def test_scan_headers_surfaces_target(self, tmp_path):
        pkg = tmp_path / "src" / "zephyr" / "pkg"
        pkg.mkdir(parents=True)
        (pkg / "mod.py").write_text(
            "# [BLUEPRINT] MOD-A | docs/03_modules/mod_a/blueprint.md | §3.1\n"
            '"""docstring."""\n',
            encoding="utf-8",
        )
        headers = cbca.scan_code_blueprint_headers()
        assert len(headers) == 1
        assert headers[0]["header_modid"] == "MOD-A"
        assert headers[0]["target"] == "docs/03_modules/mod_a/blueprint.md"


class TestTransportBlueprintIdLanded:
    """裁定#262 后续批交付钉：transport 双节点 blueprint_id=MOD-DATA-072 落位且账实一致。

    真源=docs/03_modules/_domain_data/transport/blueprint.md（st-transport-20260916 转正批）。
    本测试防的是"落位后再漂移"——头注释 id 改走、蓝图文件被删、蓝图自述 id 与头不一致。
    """

    TRANSPORT_ID = "MOD-DATA-072"
    TRANSPORT_BP = "docs/03_modules/_domain_data/transport/blueprint.md"
    TRANSPORT_SOURCES = (
        "src/zephyr/data/transport/__init__.py",
        "src/zephyr/data/transport/cross_border_dual.py",
    )

    def _headers(self) -> list[dict]:
        out: list[dict] = []
        for rel in self.TRANSPORT_SOURCES:
            content = (_REPO_ROOT / rel).read_text(encoding="utf-8")
            m = cbca.BLUEPRINT_HEADER_RE.search(content)
            assert m, f"{rel} 丢失 [BLUEPRINT] 头（blueprint_id 欠账复发）"
            pair = cbca.BLUEPRINT_HEADER_PAIR_RE.search(content)
            out.append(
                {
                    "file": rel,
                    "package": "data",
                    "header_modid": m.group(1),
                    "target": pair.group(2).strip() if pair else "",
                }
            )
        return out

    def test_both_sources_carry_landed_id(self):
        for entry in self._headers():
            assert entry["header_modid"] == self.TRANSPORT_ID
            assert entry["target"] == self.TRANSPORT_BP

    def test_blueprint_file_exists_and_declares_same_id(self, monkeypatch):
        monkeypatch.setattr(cbca, "REPO_ROOT", _REPO_ROOT)
        bp = _REPO_ROOT / self.TRANSPORT_BP
        assert bp.is_file(), f"{self.TRANSPORT_BP} 不存在——#262 后续批落位被回退"
        declared = cbca.TARGET_ID_RE.search(bp.read_text(encoding="utf-8"))
        assert declared is not None
        assert declared.group(1).strip() == self.TRANSPORT_ID

    def test_resolution_findings_empty(self, monkeypatch):
        monkeypatch.setattr(cbca, "REPO_ROOT", _REPO_ROOT)
        assert cbca.check_blueprint_target_resolution(self._headers()) == []
