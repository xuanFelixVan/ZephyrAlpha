# [A_test] module_id: SRC-TST-2221 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-exempt_zone_frontmatter_gate | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_exempt_zone_frontmatter_gate
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_exempt_zone_frontmatter_gate.py — EXEMPT-ZONE-FM 门禁单测

权威依据：exempt_zone_frontmatter_gate.py（make_exempt_zone_frontmatter_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestExtractDocType: _extract_doc_type frontmatter 解析（markdown / yaml / 边界）
- TestGatewayIntegration: mock gateway + mock subprocess.run(git ls-tree)
  - 豁免区 .md/.yaml 带 frontmatter doc_type → 阻断 (passed=False)
  - 豁免区无 doc_type → 放行
  - 非豁免区 → 放行
  - 历史违规（HEAD 已存在）→ 跳过
  - git ls-tree 异常 → 继续检查（不豁免）

注意：gate 用 Path(f).read_text()（已正确关闭，无需 shadow open）；
subprocess.run 用 monkeypatch 隔离，不触碰真实 git。

测试隔离：MagicMock gateway + tmp_path 真实文件，不读/不写真实仓库。
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.governance.commit_gates.exempt_zone_frontmatter_gate import (  # noqa: E402
    _EXEMPT_ZONE_PREFIXES,
    _FRONTMATTER_EXTS,
    _extract_doc_type,
    make_exempt_zone_frontmatter_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _make_gateway(project_root=None):
    """构造 mock gateway——本 gate 只读 gateway.project_root。"""
    gw = MagicMock()
    gw.project_root = project_root or str(_PROJECT_ROOT)
    return gw


def _install_ls_tree(monkeypatch, historical=None, raises=False):
    """mock subprocess.run（git ls-tree HEAD <rel>）。
    historical: set of rel paths 视为 HEAD 已存在（历史违规豁免）。"""
    historical = set(historical or [])
    import zephyr.governance.commit_gates.exempt_zone_frontmatter_gate as mod

    if raises:
        def _raise(*a, **k):
            raise OSError("git not available")
        monkeypatch.setattr(mod.subprocess, "run", _raise)
        return

    def _run(cmd, **kwargs):
        rel = cmd[3] if len(cmd) > 3 else ""

        class _R:
            returncode = 0
            stdout = (rel + "\n") if rel in historical else ""
            stderr = ""
        return _R()

    monkeypatch.setattr(mod.subprocess, "run", _run)


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    def test_is_gate_spec(self):
        assert isinstance(make_exempt_zone_frontmatter_gate(), GateSpec)

    def test_gate_id(self):
        assert make_exempt_zone_frontmatter_gate().gate_id == "EXEMPT-ZONE-FM"

    def test_priority(self):
        assert make_exempt_zone_frontmatter_gate().priority == 87


# ---------------------------------------------------------------------------
# TestExtractDocType — frontmatter 解析纯函数
# ---------------------------------------------------------------------------
class TestExtractDocType:
    def test_markdown_with_doc_type(self):
        content = "---\ndoc_type: architecture\n---\n# Title\n"
        assert _extract_doc_type(content, True) == "architecture"

    def test_yaml_with_doc_type(self):
        content = "---\ndoc_type: policy\nkey: value\n"
        assert _extract_doc_type(content, False) == "policy"

    def test_no_frontmatter(self):
        content = "# Title\n\nbody\n"
        assert _extract_doc_type(content, True) == ""

    def test_no_doc_type_field(self):
        content = "---\ntitle: foo\n---\nbody\n"
        assert _extract_doc_type(content, True) == ""

    def test_unclosed_markdown_frontmatter(self):
        content = "---\ndoc_type: x\nbody without close\n"
        assert _extract_doc_type(content, True) == ""

    def test_strips_double_quotes(self):
        content = '---\ndoc_type: "quoted"\n---\n'
        assert _extract_doc_type(content, True) == "quoted"

    def test_strips_single_quotes(self):
        content = "---\ndoc_type: 'sq'\n---\n"
        assert _extract_doc_type(content, True) == "sq"

    def test_empty_doc_type_value(self):
        content = "---\ndoc_type:\n---\n"
        assert _extract_doc_type(content, True) == ""

    def test_exempt_zone_prefixes_contains_working(self):
        assert "docs/_working/" in _EXEMPT_ZONE_PREFIXES

    def test_frontmatter_exts_contains_md_yaml(self):
        assert ".md" in _FRONTMATTER_EXTS
        assert ".yaml" in _FRONTMATTER_EXTS


# ---------------------------------------------------------------------------
# TestGatewayIntegration — mock gateway + mock subprocess
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    def test_exempt_zone_md_with_doc_type_blocked(self, tmp_path, monkeypatch):
        zone = tmp_path / "docs" / "_working"
        zone.mkdir(parents=True)
        f = zone / "note.md"
        f.write_text("---\ndoc_type: architecture\n---\nbody\n", encoding="utf-8")
        _install_ls_tree(monkeypatch)
        gw = _make_gateway(project_root=str(tmp_path))
        passed, msg = make_exempt_zone_frontmatter_gate().check(gw, [str(f)])
        assert not passed
        assert "EXEMPT-ZONE-FM" in msg

    def test_exempt_zone_yaml_with_doc_type_blocked(self, tmp_path, monkeypatch):
        zone = tmp_path / ".runtime"
        zone.mkdir(parents=True)
        f = zone / "config.yaml"
        f.write_text("---\ndoc_type: runtime-config\nkey: v\n", encoding="utf-8")
        _install_ls_tree(monkeypatch)
        gw = _make_gateway(project_root=str(tmp_path))
        passed, msg = make_exempt_zone_frontmatter_gate().check(gw, [str(f)])
        assert not passed
        assert "runtime-config" in msg

    def test_exempt_zone_no_doc_type_passes(self, tmp_path, monkeypatch):
        zone = tmp_path / "docs" / "_archive"
        zone.mkdir(parents=True)
        f = zone / "old.md"
        f.write_text("---\ntitle: foo\n---\nbody\n", encoding="utf-8")
        _install_ls_tree(monkeypatch)
        gw = _make_gateway(project_root=str(tmp_path))
        passed, msg = make_exempt_zone_frontmatter_gate().check(gw, [str(f)])
        assert passed

    def test_non_exempt_zone_passes(self, tmp_path, monkeypatch):
        regular = tmp_path / "docs" / "regular"
        regular.mkdir(parents=True)
        f = regular / "note.md"
        f.write_text("---\ndoc_type: architecture\n---\nbody\n", encoding="utf-8")
        _install_ls_tree(monkeypatch)
        gw = _make_gateway(project_root=str(tmp_path))
        passed, msg = make_exempt_zone_frontmatter_gate().check(gw, [str(f)])
        assert passed

    def test_historical_violation_skipped(self, tmp_path, monkeypatch):
        zone = tmp_path / "docs" / "_working"
        zone.mkdir(parents=True)
        f = zone / "legacy.md"
        f.write_text("---\ndoc_type: legacy\n---\nbody\n", encoding="utf-8")
        _install_ls_tree(monkeypatch, historical={"docs/_working/legacy.md"})
        gw = _make_gateway(project_root=str(tmp_path))
        passed, msg = make_exempt_zone_frontmatter_gate().check(gw, [str(f)])
        assert passed
        assert "historical" in msg

    def test_non_frontmatter_ext_passes(self, tmp_path, monkeypatch):
        zone = tmp_path / "docs" / "_working"
        zone.mkdir(parents=True)
        f = zone / "note.txt"
        f.write_text("---\ndoc_type: x\n---\n", encoding="utf-8")
        _install_ls_tree(monkeypatch)
        gw = _make_gateway(project_root=str(tmp_path))
        passed, msg = make_exempt_zone_frontmatter_gate().check(gw, [str(f)])
        assert passed

    def test_git_ls_tree_exception_continues_check(self, tmp_path, monkeypatch):
        zone = tmp_path / ".trae"
        zone.mkdir(parents=True)
        f = zone / "note.md"
        f.write_text("---\ndoc_type: trae-note\n---\nbody\n", encoding="utf-8")
        _install_ls_tree(monkeypatch, raises=True)
        gw = _make_gateway(project_root=str(tmp_path))
        passed, msg = make_exempt_zone_frontmatter_gate().check(gw, [str(f)])
        # git 失败时不豁免 -> 继续检查 -> doc_type 命中 -> 阻断
        assert not passed
        assert "trae-note" in msg

    def test_missing_file_skipped(self, tmp_path, monkeypatch):
        _install_ls_tree(monkeypatch)
        gw = _make_gateway(project_root=str(tmp_path))
        passed, msg = make_exempt_zone_frontmatter_gate().check(
            gw, [str(tmp_path / "nonexistent.md")]
        )
        assert passed

    def test_empty_files_passes(self, tmp_path, monkeypatch):
        _install_ls_tree(monkeypatch)
        gw = _make_gateway(project_root=str(tmp_path))
        passed, msg = make_exempt_zone_frontmatter_gate().check(gw, [])
        assert passed

    def test_multiple_violations_counted(self, tmp_path, monkeypatch):
        zone = tmp_path / "docs" / "_working"
        zone.mkdir(parents=True)
        f1 = zone / "a.md"
        f1.write_text("---\ndoc_type: a\n---\n", encoding="utf-8")
        f2 = zone / "b.md"
        f2.write_text("---\ndoc_type: b\n---\n", encoding="utf-8")
        _install_ls_tree(monkeypatch)
        gw = _make_gateway(project_root=str(tmp_path))
        passed, msg = make_exempt_zone_frontmatter_gate().check(gw, [str(f1), str(f2)])
        assert not passed
        assert "2 exempt-zone file(s)" in msg
