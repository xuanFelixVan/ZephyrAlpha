# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_undefined_name_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_undefined_name_gate.py — UNDEFINED-NAME 门禁单测

权威依据：undefined_name_gate.py（make_undefined_name_gate /
scan_content_for_undefined_names / scan_all_for_undefined_names，
GATE-DEPGRAPH-OPS 治本 Phase 1，F821 零防护缺口）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestScanContent: 单文件内容扫描（未定义符号检测/放行场景全覆盖）
- TestCheckGate: mock gateway 完整流程（阻断/放行/范围外跳过/fail-open）
- TestScanAll: 全仓 baseline 扫描（tmp_path 隔离）

测试隔离：MagicMock 模拟 gateway.run_git；scan_all 用 tmp_path 构造文件树。
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates.undefined_name_gate import (  # noqa: E402
    make_undefined_name_gate,
    scan_all_for_undefined_names,
    scan_content_for_undefined_names,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _make_gateway(staged_files: list[str], file_contents: dict[str, str]) -> MagicMock:
    """构造 mock gateway：按 git 子命令路由返回 staged 文件列表/文件内容。"""

    gw = MagicMock()
    gw.run_git = MagicMock()

    def _run(cmd):
        if "--name-only" in cmd:
            return _MockResult(stdout="\n".join(staged_files), returncode=0)
        if cmd[:2] == ["git", "show"] and len(cmd) >= 3:
            path = cmd[2]
            if path.startswith(":"):
                path = path[1:]
            content = file_contents.get(path, "")
            return _MockResult(stdout=content, returncode=0 if content else 1)
        return _MockResult(returncode=1)

    gw.run_git.side_effect = _run
    return gw


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------


class TestGateSpecFields:
    """gate_id / priority / isinstance(GateSpec)。"""

    def test_gate_id(self) -> None:
        assert make_undefined_name_gate().gate_id == "UNDEFINED-NAME"

    def test_priority(self) -> None:
        assert make_undefined_name_gate().priority == 106

    def test_is_gate_spec(self) -> None:
        assert isinstance(make_undefined_name_gate(), GateSpec)


# ---------------------------------------------------------------------------
# TestScanContent — 单文件内容扫描
# ---------------------------------------------------------------------------


class TestScanContent:
    """scan_content_for_undefined_names 检测逻辑。"""

    def test_undefined_name_detected(self) -> None:
        content = "def main():\n    return _Path('x')\n"
        violations = scan_content_for_undefined_names("scripts/governance/foo.py", content)
        assert len(violations) == 1
        assert "_Path" in violations[0]
        assert ":2:" in violations[0]

    def test_imported_name_passes(self) -> None:
        content = "from pathlib import Path\n\ndef main():\n    return Path('x')\n"
        assert scan_content_for_undefined_names("src/zephyr/foo.py", content) == []

    def test_import_as_passes(self) -> None:
        content = "import pathlib as pl\n\ndef main():\n    return pl.Path('x')\n"
        assert scan_content_for_undefined_names("src/zephyr/foo.py", content) == []

    def test_dotted_import_binds_top_level(self) -> None:
        content = "import os.path\n\ndef main():\n    return os.path.join('a', 'b')\n"
        assert scan_content_for_undefined_names("src/zephyr/foo.py", content) == []

    def test_local_definition_passes(self) -> None:
        content = "_Path = str\n\ndef main():\n    return _Path('x')\n"
        assert scan_content_for_undefined_names("src/zephyr/foo.py", content) == []

    def test_function_and_class_defs_pass(self) -> None:
        content = "class Foo:\n    pass\n\ndef bar():\n    return Foo()\n\nasync def baz():\n    return bar()\n"
        assert scan_content_for_undefined_names("src/zephyr/foo.py", content) == []

    def test_params_and_locals_pass(self) -> None:
        content = (
            "def main(event, *args, key=None, **kwargs):\n"
            "    x = event\n"
            "    for item in args:\n"
            "        x = item\n"
            "    with open('f') as fh:\n"
            "        data = fh.read()\n"
            "    try:\n"
            "        pass\n"
            "    except ValueError as exc:\n"
            "        return (x, data, key, kwargs, exc)\n"
        )
        assert scan_content_for_undefined_names("src/zephyr/foo.py", content) == []

    def test_comprehension_vars_pass(self) -> None:
        content = (
            "def main(items):\n"
            "    a = [x for x in items]\n"
            "    b = {k: v for k, v in items}\n"
            "    c = (y async for y in items)\n"
            "    return a, b, c\n"
        )
        assert scan_content_for_undefined_names("src/zephyr/foo.py", content) == []

    def test_lambda_params_pass(self) -> None:
        content = "f = lambda a, b=1, *c, **d: (a, b, c, d)\n"
        assert scan_content_for_undefined_names("src/zephyr/foo.py", content) == []

    def test_global_nonlocal_pass(self) -> None:
        content = (
            "X = 1\n"
            "def outer():\n"
            "    y = 2\n"
            "    def inner():\n"
            "        global X\n"
            "        nonlocal y\n"
            "        X = y\n"
            "    return inner\n"
        )
        assert scan_content_for_undefined_names("src/zephyr/foo.py", content) == []

    def test_match_capture_passes(self) -> None:
        content = (
            "def main(event):\n"
            "    match event:\n"
            "        case {'kind': kind, **rest}:\n"
            "            return kind, rest\n"
            "        case [first, *others]:\n"
            "            return first, others\n"
        )
        assert scan_content_for_undefined_names("src/zephyr/foo.py", content) == []

    def test_walrus_passes(self) -> None:
        content = "def main(data):\n    if (n := len(data)) > 0:\n        return n\n"
        assert scan_content_for_undefined_names("src/zephyr/foo.py", content) == []

    def test_builtins_pass(self) -> None:
        content = "def main(items):\n    return len([str(x) for x in items if isinstance(x, int)])\n"
        assert scan_content_for_undefined_names("src/zephyr/foo.py", content) == []

    def test_dunder_names_pass(self) -> None:
        content = "if __name__ == '__main__':\n    print(__file__, __doc__)\n"
        assert scan_content_for_undefined_names("src/zephyr/foo.py", content) == []

    def test_wildcard_import_skipped(self) -> None:
        content = "from somewhere import *\n\ndef main():\n    return mystery()\n"
        assert scan_content_for_undefined_names("src/zephyr/foo.py", content) == []

    def test_syntax_error_fail_open(self) -> None:
        content = "def broken(:\n"
        assert scan_content_for_undefined_names("src/zephyr/foo.py", content) == []

    def test_multiple_missing_all_reported(self) -> None:
        content = "def main():\n    return foo(Bar()) + baz\n"
        violations = scan_content_for_undefined_names("src/zephyr/foo.py", content)
        text = "\n".join(violations)
        assert "foo" in text
        assert "Bar" in text
        assert "baz" in text
        assert len(violations) == 3


# ---------------------------------------------------------------------------
# TestCheckGate — mock gateway 完整流程
# ---------------------------------------------------------------------------


class TestCheckGate:
    """_check 闭包（mock gateway）。"""

    def test_blocks_src_violation(self) -> None:
        gw = _make_gateway(
            ["src/zephyr/foo.py"],
            {"src/zephyr/foo.py": "def main():\n    return _Path('x')\n"},
        )
        passed, detail = make_undefined_name_gate().check(gw, ["src/zephyr/foo.py"])
        assert passed is False
        assert "_Path" in detail
        assert "UNDEFINED-NAME" in detail

    def test_blocks_governance_violation(self) -> None:
        gw = _make_gateway(
            ["scripts/governance/foo.py"],
            {"scripts/governance/foo.py": "X = get_depgraph_pg_connection()\n"},
        )
        passed, detail = make_undefined_name_gate().check(gw, ["scripts/governance/foo.py"])
        assert passed is False
        assert "get_depgraph_pg_connection" in detail

    def test_clean_file_passes(self) -> None:
        gw = _make_gateway(
            ["src/zephyr/foo.py"],
            {"src/zephyr/foo.py": "from pathlib import Path\nX = Path('a')\n"},
        )
        passed, detail = make_undefined_name_gate().check(gw, ["src/zephyr/foo.py"])
        assert passed is True
        assert detail == ""

    def test_out_of_scope_skipped(self) -> None:
        """tests/ 等非扫描范围文件不检测。"""
        gw = _make_gateway(
            ["tests/foo_test.py"],
            {"tests/foo_test.py": "X = undefined_symbol()\n"},
        )
        passed, _ = make_undefined_name_gate().check(gw, ["tests/foo_test.py"])
        assert passed is True

    def test_archive_staged_skipped(self) -> None:
        """staged 路径 _archive 豁免（裁定#E 同口径，2026-08-20 波3 补齐）——
        归档一次性死代码不参与 F821 扫描（format 重排存量符号伪"新增"不阻断）。"""
        archived = "scripts/governance/_archive/one_off/migrate_foo.py"
        gw = _make_gateway(
            [archived],
            {archived: "X = DB_DISPLAY_NAME\n"},
        )
        passed, detail = make_undefined_name_gate().check(gw, [archived])
        assert passed is True
        assert detail == ""

    def test_no_staged_files_passes(self) -> None:
        gw = _make_gateway([], {})
        passed, detail = make_undefined_name_gate().check(gw, [])
        assert passed is True
        assert detail == ""


# ---------------------------------------------------------------------------
# TestScanAll — 全仓 baseline 扫描（tmp_path 隔离）
# ---------------------------------------------------------------------------


class TestScanAll:
    """scan_all_for_undefined_names（磁盘全扫）。"""

    def test_missing_dirs_skip(self, tmp_path: Path) -> None:
        violations, error_msg = scan_all_for_undefined_names(tmp_path)
        assert violations == []
        assert error_msg is not None

    def test_scans_both_trees(self, tmp_path: Path) -> None:
        gov = tmp_path / "scripts" / "governance"
        src = tmp_path / "src"
        gov.mkdir(parents=True)
        src.mkdir(parents=True)
        (gov / "a.py").write_text("X = missing_a()\n", encoding="utf-8")
        (src / "b.py").write_text("Y = missing_b()\n", encoding="utf-8")
        violations, error_msg = scan_all_for_undefined_names(tmp_path)
        assert error_msg is None
        text = "\n".join(violations)
        assert "missing_a" in text
        assert "missing_b" in text

    def test_clean_tree_zero_violations(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir(parents=True)
        (src / "ok.py").write_text("from pathlib import Path\nX = Path('a')\n", encoding="utf-8")
        violations, error_msg = scan_all_for_undefined_names(tmp_path)
        assert error_msg is None
        assert violations == []
