# [A_test] module_id: SRC-TST-2220 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-doc_ref_broken_gate | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_doc_ref_broken_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_doc_ref_broken_gate.py — DOC-REF-BROKEN 门禁单测

权威依据：doc_ref_broken_gate.py（make_doc_ref_broken_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestHelpers: _MD_LINK_RE / _is_url_or_anchor / _find_broken_refs 纯函数
- TestGatewayIntegration: mock gateway 流程
  - 新增 .md 含断裂相对路径引用 → 阻断 (passed=False)
  - 新增 .md 引用存在文件 → 放行 (passed=True)
  - URL/锚点链接豁免
  - tests/ 豁免
  - fail-open on git diff 失败/异常

注意：gate 用 open(path).read() 未关闭（ResourceWarning），autouse fixture
注入 shadow open 包装为读取后自动关闭。

测试隔离：MagicMock 模拟 gateway._run_git + tmp_path 真实文件，不读/不写真实仓库。
"""
from __future__ import annotations

import builtins
import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates.doc_ref_broken_gate import (  # noqa: E402
    _MD_LINK_RE,
    _find_broken_refs,
    _is_url_or_anchor,
    make_doc_ref_broken_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _make_gateway(staged_files=None, project_root=None, diff_fails=False, diff_raises=False):
    """构造 mock gateway：--name-only 返回新增文件列表；rev-parse --show-toplevel
    返回 project_root。文件内容/存在性由 tmp_path 真实文件提供。"""
    gw = MagicMock()
    gw.project_root = project_root or str(_PROJECT_ROOT)

    if diff_raises:
        def _raise(*a, **k):
            raise RuntimeError("git not found")
        gw._run_git = _raise
        return gw

    def _run_git(cmd):
        if diff_fails and "--name-only" in cmd:
            return _MockResult(1, "")
        if "--name-only" in cmd:
            return _MockResult(0, "\n".join(staged_files or []))
        if "rev-parse" in cmd:
            return _MockResult(0, str(gw.project_root))
        return _MockResult(0, "")

    gw._run_git = _run_git
    return gw


@pytest.fixture(autouse=True)
def _shadow_open(monkeypatch):
    """源文件 open(abs_path).read() 未关闭（ResourceWarning），包装为读取后自动关闭。"""
    real_open = builtins.open

    class _ShadowFile:
        def __init__(self, fh):
            self._fh = fh

        def read(self, *a, **k):
            try:
                return self._fh.read(*a, **k)
            finally:
                self._fh.close()

        def readlines(self, *a, **k):
            try:
                return self._fh.readlines(*a, **k)
            finally:
                self._fh.close()

        def __enter__(self):
            return self

        def __exit__(self, *a):
            self._fh.close()

        def __getattr__(self, name):
            return getattr(self._fh, name)

        def close(self):
            self._fh.close()

    def _shadowed_open(file, mode="r", *args, **kwargs):
        return _ShadowFile(real_open(file, mode, *args, **kwargs))

    monkeypatch.setattr(builtins, "open", _shadowed_open)


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    def test_is_gate_spec(self):
        assert isinstance(make_doc_ref_broken_gate(), GateSpec)

    def test_gate_id(self):
        assert make_doc_ref_broken_gate().gate_id == "DOC-REF-BROKEN"

    def test_priority(self):
        assert make_doc_ref_broken_gate().priority == 91


# ---------------------------------------------------------------------------
# TestHelpers — 纯函数检测
# ---------------------------------------------------------------------------
class TestHelpers:
    def test_md_link_re_captures_target(self):
        m = _MD_LINK_RE.search("[详情](./architecture.md)")
        assert m is not None
        assert m.group(2) == "./architecture.md"

    def test_md_link_re_captures_text(self):
        m = _MD_LINK_RE.search("[text](target.md)")
        assert m is not None
        assert m.group(1) == "text"

    def test_is_url_or_anchor_http(self):
        assert _is_url_or_anchor("http://example.com")

    def test_is_url_or_anchor_https(self):
        assert _is_url_or_anchor("https://example.com")

    def test_is_url_or_anchor_mailto(self):
        assert _is_url_or_anchor("mailto:a@b.com")

    def test_is_url_or_anchor_ftp(self):
        assert _is_url_or_anchor("ftp://example.com")

    def test_is_url_or_anchor_hash(self):
        assert _is_url_or_anchor("#section")

    def test_is_url_or_anchor_relative_not_exempt(self):
        assert not _is_url_or_anchor("./relative.md")
        assert not _is_url_or_anchor("../up.md")

    def test_find_broken_returns_missing(self, tmp_path):
        content = "[x](./missing.md)"
        broken = _find_broken_refs(content, str(tmp_path))
        assert "./missing.md" in broken

    def test_find_broken_empty_when_exists(self, tmp_path):
        (tmp_path / "existing.md").write_text("ok", encoding="utf-8")
        content = "[x](./existing.md)"
        assert _find_broken_refs(content, str(tmp_path)) == []

    def test_find_broken_exempts_url(self, tmp_path):
        content = "[x](https://example.com) and [y](mailto:a@b.com)"
        assert _find_broken_refs(content, str(tmp_path)) == []

    def test_find_broken_strips_anchor(self, tmp_path):
        (tmp_path / "doc.md").write_text("ok", encoding="utf-8")
        content = "[x](./doc.md#section)"
        assert _find_broken_refs(content, str(tmp_path)) == []

    def test_find_broken_pure_anchor_exempt(self, tmp_path):
        content = "[x](#section)"
        assert _find_broken_refs(content, str(tmp_path)) == []


# ---------------------------------------------------------------------------
# TestGatewayIntegration — mock gateway 流程
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    def test_new_md_with_broken_ref_blocked(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "design.md").write_text("[详情](./missing.md)", encoding="utf-8")
        rel = "docs/design.md"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_doc_ref_broken_gate().check(gw, [])
        assert not passed
        assert "missing.md" in msg or "断裂" in msg

    def test_new_md_with_valid_ref_passes(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "existing.md").write_text("ok", encoding="utf-8")
        (docs / "design.md").write_text("[x](./existing.md)", encoding="utf-8")
        rel = "docs/design.md"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_doc_ref_broken_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_url_link_passes(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "design.md").write_text("[x](https://example.com)", encoding="utf-8")
        rel = "docs/design.md"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_doc_ref_broken_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_anchor_link_passes(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "design.md").write_text("[x](#section)", encoding="utf-8")
        rel = "docs/design.md"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_doc_ref_broken_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_tests_dir_exempt(self, tmp_path):
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "foo.md").write_text("[x](./missing.md)", encoding="utf-8")
        rel = "tests/foo.md"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_doc_ref_broken_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_non_md_file_ignored(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        (src / "mod.py").write_text("print('hi')", encoding="utf-8")
        rel = "src/mod.py"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_doc_ref_broken_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_git_diff_failure(self, tmp_path):
        gw = _make_gateway(diff_fails=True, project_root=str(tmp_path))
        passed, msg = make_doc_ref_broken_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_git_diff_exception(self, tmp_path):
        gw = _make_gateway(diff_raises=True, project_root=str(tmp_path))
        passed, msg = make_doc_ref_broken_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_multiple_broken_refs_dedup(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        content = "[x](./a.md) [y](./a.md) [z](./b.md)"
        (docs / "design.md").write_text(content, encoding="utf-8")
        rel = "docs/design.md"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_doc_ref_broken_gate().check(gw, [])
        assert not passed
        # 去重后 a.md 只出现一次
        assert msg.count("./a.md") == 1
