# [A_test] module_id: MOD-GOV_blueprint_node_id_hardcode_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_blueprint_node_id_hardcode_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_blueprint_node_id_hardcode_gate.py — BLUEPRINT-NODE-ID-HARDCODE 门禁单测

权威依据：blueprint_node_id_hardcode_gate.py（make_blueprint_node_id_hardcode_gate）
SSoT 治本（2026-08-04）：检测逻辑真源 = check_doc_node_id_hardcode.py，本 gate 是
subprocess thin wrapper（对标 pure_shim_gate.py → check_pure_shim.py 模式）。

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestGatewayIntegration: 真实 subprocess 调用 check_doc_node_id_hardcode.py --ci --files
  - staged blueprint.md 含 node_id 硬编码 → 阻断 (passed=False)
  - staged blueprint.md 含 edge_id 硬编码 → 阻断 (passed=False)
  - staged blueprint.md 仅含 module_id（稳定标识）→ 放行 (passed=True)
  - 非 blueprint.md 文件含 node_id → 忽略（放行）
  - 多违规聚合
  - fail-open on git diff 失败/异常
  - fail-open on 脚本缺失（monkeypatch _CHECKER_SCRIPT）
  - 无 staged 文件 → 放行
  - Windows 反斜杠路径归一化

测试隔离：MagicMock 模拟 gateway.run_git + tmp_path 真实文件 + 真实 subprocess 调用
check_doc_node_id_hardcode.py（检测真源），不 mock subprocess（集成测试价值 > 速度）。
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

from zephyr.gov_enforcement.commit_gates.blueprint_node_id_hardcode_gate import (  # noqa: E402
    make_blueprint_node_id_hardcode_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _make_gateway(staged_files=None, project_root=None, diff_fails=False, diff_raises=False):
    """构造 mock gateway：--name-only 返回 staged 文件列表；rev-parse --show-toplevel
    返回 project_root。文件内容/存在性由 tmp_path 真实文件提供。"""
    gw = MagicMock()
    gw.project_root = project_root or str(_PROJECT_ROOT)

    if diff_raises:

        def _raise(*a, **k):
            raise RuntimeError("git not found")

        gw.run_git = _raise
        return gw

    def _run_git(cmd):
        if diff_fails and "--name-only" in cmd:
            return _MockResult(1, "")
        if "--name-only" in cmd:
            return _MockResult(0, "\n".join(staged_files or []))
        if "rev-parse" in cmd:
            return _MockResult(0, str(gw.project_root))
        return _MockResult(0, "")

    gw.run_git = _run_git
    return gw


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    def test_is_gate_spec(self):
        assert isinstance(make_blueprint_node_id_hardcode_gate(), GateSpec)

    def test_gate_id(self):
        assert make_blueprint_node_id_hardcode_gate().gate_id == "BLUEPRINT-NODE-ID-HARDCODE"

    def test_priority(self):
        assert make_blueprint_node_id_hardcode_gate().priority == 57


# ---------------------------------------------------------------------------
# TestGatewayIntegration — 真实 subprocess 调用 check_doc_node_id_hardcode.py
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    def test_blueprint_with_node_id_blocked(self, tmp_path):
        """staged blueprint.md 含 node_id=数字 → 阻断。"""
        mods = tmp_path / "docs" / "03_modules" / "foo"
        mods.mkdir(parents=True)
        (mods / "blueprint.md").write_text("**depgraph**: MOD-EX-049 (node_id=8005442)", encoding="utf-8")
        rel = "docs/03_modules/foo/blueprint.md"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_blueprint_node_id_hardcode_gate().check(gw, [])
        assert not passed
        assert "node_id" in msg

    def test_blueprint_with_edge_id_blocked(self, tmp_path):
        """staged blueprint.md 含 edge_id=数字 → 阻断。"""
        mods = tmp_path / "docs" / "03_modules" / "bar"
        mods.mkdir(parents=True)
        (mods / "blueprint.md").write_text("edge_id=12345", encoding="utf-8")
        rel = "docs/03_modules/bar/blueprint.md"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_blueprint_node_id_hardcode_gate().check(gw, [])
        assert not passed
        assert "edge_id" in msg

    def test_blueprint_with_module_id_only_passes(self, tmp_path):
        """module_id/blueprint_id/path 是稳定标识，应放行。"""
        mods = tmp_path / "docs" / "03_modules" / "baz"
        mods.mkdir(parents=True)
        (mods / "blueprint.md").write_text(
            "module_id=MOD-EX-049\nblueprint_id=BP-001\npath=src/zephyr/ex_core/foo",
            encoding="utf-8",
        )
        rel = "docs/03_modules/baz/blueprint.md"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_blueprint_node_id_hardcode_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_non_blueprint_md_ignored(self, tmp_path):
        """非 blueprint.md 文件含 node_id 硬编码 → 忽略（放行）。"""
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "readme.md").write_text("node_id=999", encoding="utf-8")
        rel = "docs/readme.md"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_blueprint_node_id_hardcode_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_multiple_violations_reported(self, tmp_path):
        """多个 node_id/edge_id 硬编码 → 多条 WARN 汇报。"""
        mods = tmp_path / "docs" / "03_modules" / "multi"
        mods.mkdir(parents=True)
        content = "node_id=1\nnode_id=2\nedge_id=3"
        (mods / "blueprint.md").write_text(content, encoding="utf-8")
        rel = "docs/03_modules/multi/blueprint.md"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_blueprint_node_id_hardcode_gate().check(gw, [])
        assert not passed
        # 脚本按行汇报，3 行各含一个违规 → 至少 3 条 WARN
        assert msg.count("WARN") >= 3

    def test_multiple_files_aggregated(self, tmp_path):
        """多个 staged blueprint.md 都违规 → 聚合报错。"""
        mods = tmp_path / "docs" / "03_modules"
        mods.mkdir(parents=True)
        for name in ("a", "b"):
            d = mods / name
            d.mkdir()
            (d / "blueprint.md").write_text(f"node_id={100 if name == 'a' else 200}", encoding="utf-8")
        gw = _make_gateway(
            staged_files=["docs/03_modules/a/blueprint.md", "docs/03_modules/b/blueprint.md"],
            project_root=str(tmp_path),
        )
        passed, msg = make_blueprint_node_id_hardcode_gate().check(gw, [])
        assert not passed
        # 两个文件各至少一条 WARN
        assert msg.count("WARN") >= 2

    def test_no_staged_files_passes(self, tmp_path):
        gw = _make_gateway(staged_files=[], project_root=str(tmp_path))
        passed, msg = make_blueprint_node_id_hardcode_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_git_diff_failure(self, tmp_path):
        gw = _make_gateway(diff_fails=True, project_root=str(tmp_path))
        passed, msg = make_blueprint_node_id_hardcode_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_git_diff_exception(self, tmp_path):
        gw = _make_gateway(diff_raises=True, project_root=str(tmp_path))
        passed, msg = make_blueprint_node_id_hardcode_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_staged_file_missing_on_disk_skipped(self, tmp_path):
        """staged 列表含 blueprint.md 但磁盘不存在 → 跳过（放行）。"""
        rel = "docs/03_modules/ghost/blueprint.md"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_blueprint_node_id_hardcode_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_script_missing(self, tmp_path, monkeypatch):
        """check_doc_node_id_hardcode.py 不存在 → fail-open（放行）。"""
        mods = tmp_path / "docs" / "03_modules" / "noscript"
        mods.mkdir(parents=True)
        (mods / "blueprint.md").write_text("node_id=42", encoding="utf-8")
        rel = "docs/03_modules/noscript/blueprint.md"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        # monkeypatch 脚本路径为不存在的文件
        from zephyr.gov_enforcement.commit_gates import blueprint_node_id_hardcode_gate as gate_mod

        monkeypatch.setattr(gate_mod, "_CHECKER_SCRIPT", str(tmp_path / "nonexistent.py"))
        passed, msg = make_blueprint_node_id_hardcode_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_backslash_path_normalized(self, tmp_path):
        """Windows 反斜杠路径归一化后正确检测。"""
        mods = tmp_path / "docs" / "03_modules" / "win"
        mods.mkdir(parents=True)
        (mods / "blueprint.md").write_text("node_id=42", encoding="utf-8")
        # git diff 返回反斜杠路径
        rel = r"docs\03_modules\win\blueprint.md"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_blueprint_node_id_hardcode_gate().check(gw, [])
        assert not passed
        assert "node_id" in msg
