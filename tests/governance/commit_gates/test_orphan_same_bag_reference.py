# [A_test] module_id: MOD-GOV_orphan_module_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_ORPHAN_MODULE_GATE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_orphan_same_bag_reference
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_orphan_module_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_orphan_same_bag_reference.py — P3 链 ORPHAN↔IMPORT 循环互锁处方回归测试（SW3 2026-09-29）

背景：0138 死袋实证——新模块单独成袋（无引用同袋）必死于 ORPHAN-MODULE；处方=引用者
（git_commit_gateway）与被引者（derived_dirty_ledger）同袋。机理（源码级）：ORPHAN 门
`git grep`（无 tree-ish）搜 belt 专用 worktree 中 tracked 文件的**工作树内容**；队列落地器
_apply_snapshot 先物化全部袋内文件到盘（write_bytes），再走网关 commit pathspec——
故同袋修改文件的 import 行对 grep 可见。

红蓝（先证能红再修绿）：
- RED  ：新模块落盘、无任何文件引用（0138 形态）→ ORPHAN 阻断（passed=False）。
- GREEN：同袋场景——tracked 引用文件被改写落盘含 import + 新模块落盘 → ORPHAN 放行
  （passed=True）。全程真实 git 沙箱（tmp_path），不经 MagicMock 假设扫描面。

测试隔离：git init 于 tmp_path；不触生产路径；git 环境剥离（GIT_DIR 等清空防外泄）。
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates.orphan_module_gate import make_orphan_module_gate  # noqa: E402

_GATEWAY_REL = "src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py"
_LEDGER_REL = "src/zephyr/gov_enforcement/derived_dirty_ledger.py"

_GATEWAY_STUB = '"""gateway stub"""\n\nclass _Gateway:\n    pass\n'
_LEDGER_STUB = '"""ledger stub"""\n\nLEDGER_REL = ".runtime/derived_dirty/integrity_intent.jsonl"\n'
_IMPORT_LINE = "from zephyr.gov_enforcement.derived_dirty_ledger import append_intent\n"


class _RealGitGateway:
    """最小 gateway 替身：run_git=真实 git 子进程（cwd=沙箱仓），project_root=沙箱根。"""

    def __init__(self, repo: Path):
        self.project_root = str(repo)

    def run_git(self, cmd, cwd=None):
        return subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else self.project_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )


def _git(repo: Path, *args: str) -> None:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    subprocess.run(
        ["git", *args],
        cwd=str(repo),
        check=True,
        capture_output=True,
        env={
            **env,
            "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@t",
        },
    )


@pytest.fixture()
def sandbox(tmp_path: Path):
    """真实 git 沙箱：含一个已 commit 的 tracked gateway 替身。"""
    repo = tmp_path / "repo"
    (repo / "src/zephyr/gov_enforcement/rule_bridge").mkdir(parents=True)
    (repo / "src/zephyr/gov_enforcement/commit_gates").mkdir(parents=True)
    _git(repo, "init", "-q")
    gw = repo / _GATEWAY_REL
    gw.write_text(_GATEWAY_STUB, encoding="utf-8")
    (repo / "src/zephyr/gov_enforcement/__init__.py").write_text("", encoding="utf-8")
    (repo / "src/zephyr/gov_enforcement/rule_bridge/__init__.py").write_text("", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "init: gateway stub")
    return repo


def _write_ledger(repo: Path) -> None:
    p = repo / _LEDGER_REL
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(_LEDGER_STUB, encoding="utf-8")


def _run_gate(repo: Path, own_files: list[str]) -> tuple[bool, str]:
    gate = make_orphan_module_gate()
    gw = _RealGitGateway(repo)
    return gate.check(gw, own_files, session_id=None)


def test_red_new_module_alone_without_reference_is_blocked(sandbox: Path) -> None:
    """RED（0138 死袋形态）：新模块落盘、仓库无引用 → ORPHAN 阻断。"""
    _write_ledger(sandbox)
    _git(sandbox, "add", _LEDGER_REL)
    passed, detail = _run_gate(sandbox, [_LEDGER_REL])
    assert passed is False, "新模块无任何 import 引用必须被 ORPHAN 阻断（0138 再现）"
    assert "derived_dirty_ledger" in detail


def test_green_same_bag_working_tree_reference_passes(sandbox: Path) -> None:
    """GREEN（处方形态）：引用者+被引者同袋——tracked 引用文件工作树改写含 import → 放行。"""
    _write_ledger(sandbox)
    gw_file = sandbox / _GATEWAY_REL
    gw_file.write_text(_GATEWAY_STUB + "\n" + _IMPORT_LINE, encoding="utf-8")
    _git(sandbox, "add", _LEDGER_REL, _GATEWAY_REL)
    passed, detail = _run_gate(sandbox, [_LEDGER_REL, _GATEWAY_REL])
    assert passed is True, f"同袋引用（工作树物化可见）必须放行 ORPHAN：{detail}"


def test_green_reference_visible_via_working_tree_even_unstaged(sandbox: Path) -> None:
    """GREEN（扫描面语义钉死）：引用行只在工作树、未暂存也可见——git grep 读工作树内容。"""
    _write_ledger(sandbox)
    _git(sandbox, "add", _LEDGER_REL)
    gw_file = sandbox / _GATEWAY_REL
    gw_file.write_text(_GATEWAY_STUB + "\n" + _IMPORT_LINE, encoding="utf-8")  # 不 add
    passed, detail = _run_gate(sandbox, [_LEDGER_REL])
    assert passed is True, f"ORPHAN 扫描面=tracked 文件工作树内容（非 HEAD 快照）：{detail}"
