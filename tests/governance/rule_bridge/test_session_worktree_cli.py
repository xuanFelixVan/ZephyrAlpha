# [A_test] module_id: MOD-GOV_session_worktree_cli | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-005 | scripts/governance/session_worktree_cli.py | §FP-ISO.4C
# [MODULE] tests.governance.rule_bridge.test_session_worktree_cli
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-INF-005 | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_session_worktree_cli.py — session_worktree_cli CLI 测试（治本遗留项#2, 2026-07-17）

测试组：
- test_cli_sweep_runs: sweep 子命令可执行且 exit 0
- test_cli_list_runs: list 子命令可执行且 exit 0
- test_cli_list_json: list --json 输出合法 JSON
- test_cli_no_subcommand_errors: 无子命令时 exit 非 0（argparse required=True）
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

# parents[0]=rule_bridge  [1]=governance  [2]=tests  [3]=ZephyrAlpha(repo root)
_CLI_SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "governance" / "session_worktree_cli.py"


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    """执行 CLI 脚本，返回 CompletedProcess。"""
    return subprocess.run(
        [sys.executable, str(_CLI_SCRIPT), *args],
        capture_output=True,
        text=True,
        timeout=60,
    )


@pytest.mark.parametrize("extra_args", [[], ["--max-age", "60"]])
def test_cli_sweep_runs(extra_args):
    """sweep 子命令可执行且 exit 0（无 stale worktree 时也正常）。"""
    r = _run_cli("sweep", *extra_args)
    assert r.returncode == 0, f"sweep failed: {r.stderr}"
    assert "swept=" in r.stdout


def test_cli_list_runs():
    """list 子命令可执行且 exit 0。"""
    r = _run_cli("list")
    assert r.returncode == 0, f"list failed: {r.stderr}"


def test_cli_list_json():
    """list --json 输出合法 JSON。"""
    r = _run_cli("list", "--json")
    assert r.returncode == 0, f"list --json failed: {r.stderr}"
    data = json.loads(r.stdout)
    assert isinstance(data, list)


def test_cli_no_subcommand_errors():
    """无子命令时 exit 非 0（argparse required=True）。"""
    r = _run_cli()
    assert r.returncode != 0, f"expected non-zero exit, got {r.returncode}: {r.stderr}"
