# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_scripts_import_integrity_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_scripts_import_integrity_gate.py — SCRIPTS-IMPORT-INTEGRITY 门禁单测

权威依据：scripts_import_integrity_gate.py
（make_scripts_import_integrity_gate，裁定 #ARCH-DATAQUALITY-V1.4 核心治本）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestCheckDetection: mock gateway 完整流程
  - 缺 import（REPO_ROOT used but not imported）→ 阻断
  - 合法 import（from _shared.constants import REPO_ROOT）→ 放行
  - wildcard import（from X import *）→ 跳过（放行）
  - _shared/constants.py → 豁免（放行）
  - 本地定义 REPO_ROOT → 放行（not a violation）
  - 多符号缺失 → 全部报告
  - 非 scripts/governance/ 文件 → 跳过
  - 无 staged .py → 放行

测试隔离：MagicMock 模拟 gateway.run_git，按 git 子命令路由返回不同结果。
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

from zephyr.gov_enforcement.commit_gates.scripts_import_integrity_gate import (  # noqa: E402
    make_scripts_import_integrity_gate,
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
        gate = make_scripts_import_integrity_gate()
        assert gate.gate_id == "SCRIPTS-IMPORT-INTEGRITY"

    def test_priority(self) -> None:
        gate = make_scripts_import_integrity_gate()
        assert gate.priority == 104

    def test_is_gate_spec(self) -> None:
        gate = make_scripts_import_integrity_gate()
        assert isinstance(gate, GateSpec)


# ---------------------------------------------------------------------------
# TestCheckDetection
# ---------------------------------------------------------------------------

class TestCheckDetection:
    """_check 闭包检测逻辑（mock gateway）。"""

    def test_missing_import_blocked(self) -> None:
        """REPO_ROOT used but not imported → 阻断。"""
        gw = _make_gateway(
            ["scripts/governance/d5_architecture/broken.py"],
            {
                "scripts/governance/d5_architecture/broken.py": (
                    "from _shared.constants import EXIT_PASS\n"
                    "\n"
                    'VOCAB_PATH = REPO_ROOT / "docs" / "foo"\n'
                    "\n"
                    "def main():\n"
                    "    return EXIT_PASS\n"
                ),
            },
        )
        gate = make_scripts_import_integrity_gate()
        passed, detail = gate.check(gw, [])
        assert passed is False
        assert "REPO_ROOT" in detail
        assert "SCRIPTS-IMPORT-INTEGRITY" in detail

    def test_proper_import_passes(self) -> None:
        """from _shared.constants import REPO_ROOT → 放行。"""
        gw = _make_gateway(
            ["scripts/governance/d5_architecture/good.py"],
            {
                "scripts/governance/d5_architecture/good.py": (
                    "from _shared.constants import EXIT_PASS, REPO_ROOT\n"
                    "\n"
                    'VOCAB_PATH = REPO_ROOT / "docs" / "foo"\n'
                    "\n"
                    "def main():\n"
                    "    return EXIT_PASS\n"
                ),
            },
        )
        gate = make_scripts_import_integrity_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True
        assert detail == ""

    def test_wildcard_import_skipped(self) -> None:
        """from X import * → 跳过（放行）。"""
        gw = _make_gateway(
            ["scripts/governance/d5_architecture/wild.py"],
            {
                "scripts/governance/d5_architecture/wild.py": (
                    "from _shared.constants import *\n"
                    "\n"
                    'VOCAB_PATH = REPO_ROOT / "docs"\n'
                ),
            },
        )
        gate = make_scripts_import_integrity_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True

    def test_constants_file_exempt(self) -> None:
        """scripts/governance/_shared/constants.py → 豁免（放行）。"""
        gw = _make_gateway(
            ["scripts/governance/_shared/constants.py"],
            {
                "scripts/governance/_shared/constants.py": (
                    'REPO_ROOT = "/some/path"\n'
                    "\n"
                    'X = REPO_ROOT / "foo"\n'
                ),
            },
        )
        gate = make_scripts_import_integrity_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True

    def test_local_definition_passes(self) -> None:
        """REPO_ROOT 本地定义 → 放行（not a violation）。"""
        gw = _make_gateway(
            ["scripts/governance/d5_architecture/local.py"],
            {
                "scripts/governance/d5_architecture/local.py": (
                    'REPO_ROOT = "/some/path"\n'
                    "\n"
                    'VOCAB_PATH = REPO_ROOT / "docs"\n'
                ),
            },
        )
        gate = make_scripts_import_integrity_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True

    def test_multiple_missing_symbols(self) -> None:
        """REPO_ROOT + get_depgraph_pg_connection 同时缺失 → 全部报告。"""
        gw = _make_gateway(
            ["scripts/governance/d5_architecture/multi.py"],
            {
                "scripts/governance/d5_architecture/multi.py": (
                    "from _shared.constants import EXIT_PASS\n"
                    "\n"
                    'PATH = REPO_ROOT / "docs"\n'
                    "\n"
                    "def get_conn():\n"
                    "    return get_depgraph_pg_connection()\n"
                ),
            },
        )
        gate = make_scripts_import_integrity_gate()
        passed, detail = gate.check(gw, [])
        assert passed is False
        assert "REPO_ROOT" in detail
        assert "get_depgraph_pg_connection" in detail

    def test_non_gov_file_skipped(self) -> None:
        """src/ 下的文件 → 跳过（不在 scripts/governance/ 下）。"""
        gw = _make_gateway(
            ["src/zephyr/some_module.py"],
            {
                "src/zephyr/some_module.py": (
                    'X = REPO_ROOT / "docs"\n'
                ),
            },
        )
        gate = make_scripts_import_integrity_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True

    def test_no_staged_files_passes(self) -> None:
        """无 staged .py → 放行。"""
        gw = _make_gateway([], {})
        gate = make_scripts_import_integrity_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True
        assert detail == ""

    def test_missing_import_with_get_connection(self) -> None:
        """get_depgraph_pg_connection used but not imported → 阻断（Task A 场景）。"""
        gw = _make_gateway(
            ["scripts/governance/d8_doc_sync/audit.py"],
            {
                "scripts/governance/d8_doc_sync/audit.py": (
                    "from _shared.constants import EXIT_PASS, REPO_ROOT\n"
                    "\n"
                    "def main():\n"
                    "    conn = get_depgraph_pg_connection()\n"
                    "    return EXIT_PASS\n"
                ),
            },
        )
        gate = make_scripts_import_integrity_gate()
        passed, detail = gate.check(gw, [])
        assert passed is False
        assert "get_depgraph_pg_connection" in detail
