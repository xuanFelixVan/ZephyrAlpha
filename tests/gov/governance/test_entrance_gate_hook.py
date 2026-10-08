# [TTL] permanent
"""进场检票钩子纯逻辑单测（st-entrance-gate-20261007，tmp_path 隔离，零生产路径写）。

覆盖面：业务路径判定矩阵 / 主仓锚定（worktree 三形态）/ 合格记录判据（与 commit 门
同口径）/ 别名桥 / run() 决策矩阵（deny/allow/bypass/fail-open）/ 时序审计落盘 /
stderr 话术含正门命令。端到端经 .ps1 启动器一例试跑（Windows 才执行）。
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_HOOK = _REPO_ROOT / "scripts" / "governance" / "entrance_gate_hook.py"

_spec = importlib.util.spec_from_file_location("entrance_gate_hook", _HOOK)
egh = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(egh)


def _make_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / ".git").mkdir(parents=True)
    (root / ".runtime" / "lookup_audit").mkdir(parents=True)
    return root


def _payload(root: Path, rel: str = "src/zephyr/pkg/demo.py", sid: str = "sess-t1") -> dict:
    return {
        "session_id": sid,
        "tool_name": "Edit",
        "cwd": str(root),
        "tool_input": {"file_path": str(root / rel)},
    }


def _write_lookup(root: Path, sid: str, tool: str = "capability_lookup.find") -> None:
    audit = root / ".runtime" / "lookup_audit" / f"{sid}.jsonl"
    audit.write_text(
        json.dumps({"ts": "2026-10-07T00:00:00Z", "tool": tool, "query": {"query": "x"}}),
        encoding="utf-8",
    )


def _last_timing(root: Path, sid: str = "sess-t1") -> dict:
    timing = root / ".runtime" / "entrance_audit" / f"{sid}.jsonl"
    return json.loads(timing.read_text(encoding="utf-8").splitlines()[-1])


# ---------------------------------------------------------------------------
# classify_rel 业务路径判定矩阵
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("rel", "expected"),
    [
        ("src/zephyr/pkg/demo.py", "business"),
        ("src/frontend/x.js", "outside"),  # src/ 仅 .py 触发
        ("scripts/governance/foo.py", "business"),
        ("scripts/governance/foo.ps1", "business"),
        ("scripts/governance/foo.md", "outside"),
        ("config/schedule_gate_policy.yaml", "business"),
        ("config/nested/deep.json", "business"),
        ("tests/gov/test_x.py", "exempt"),
        (".runtime/tmp/snap.py", "exempt"),
        (".worktrees/sid/src/a.py", "exempt"),
        ("docs/01_policies_and_standards/rules/trae_001.yaml", "outside"),
        ("README.md", "outside"),
        ("main.py", "outside"),  # 根散 .py 不在 v1 触发面（commit 门 src/zephyr 口径的有限放宽）
    ],
)
def test_classify_rel_matrix(rel: str, expected: str) -> None:
    assert egh.classify_rel(rel) == expected


# ---------------------------------------------------------------------------
# anchor_main_root 三形态
# ---------------------------------------------------------------------------


def test_anchor_plain_repo_identity(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    assert egh.anchor_main_root(root) == root


def test_anchor_worktree_structural_strip(tmp_path: Path) -> None:
    main = _make_repo(tmp_path)
    wt = main / ".worktrees" / "st-x"
    wt.mkdir(parents=True)
    (wt / ".git").mkdir()
    assert egh.anchor_main_root(wt) == main


def test_anchor_worktree_gitdir_resolution(tmp_path: Path) -> None:
    main = _make_repo(tmp_path)
    wt_gitdir = main / ".git" / "worktrees" / "wt9"
    wt_gitdir.mkdir(parents=True)
    wt = tmp_path / "elsewhere" / "wt9"
    wt.mkdir(parents=True)
    (wt / ".git").write_text(f"gitdir: {wt_gitdir}", encoding="utf-8")
    assert egh.anchor_main_root(wt) == main


# ---------------------------------------------------------------------------
# 合格记录判据（与 commit 门 _count_valid_log_entries 同口径）+ 别名桥
# ---------------------------------------------------------------------------


def test_qualifying_record_tool_key_criterion(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    audit = root / ".runtime" / "lookup_audit" / "s1.jsonl"
    assert not egh._has_qualifying_record(audit)  # 文件不存在
    audit.write_text('{"ts": "t"}\n', encoding="utf-8")  # dict 但无 tool 键
    assert not egh._has_qualifying_record(audit)
    audit.write_text(
        '{"ts": "t", "tool": "zephyr.library.lookup"}\nnot-even-json\n',
        encoding="utf-8",
    )
    assert egh._has_qualifying_record(audit)  # 坏行忽略，tool 行命中


def test_alias_bridge(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    _write_lookup(root, "st-work-20261007")
    ok, via = egh.lookup_passed(root / ".runtime" / "lookup_audit", "sess-harness")
    assert not ok and via == ""
    alias_dir = root / ".runtime" / "lookup_audit" / ".aliases"
    alias_dir.mkdir()
    (alias_dir / "sess-harness").write_text("st-work-20261007\n", encoding="utf-8")
    ok, via = egh.lookup_passed(root / ".runtime" / "lookup_audit", "sess-harness")
    assert ok and via == "st-work-20261007"


# ---------------------------------------------------------------------------
# run() 决策矩阵
# ---------------------------------------------------------------------------


def test_run_denies_first_business_write_and_audits(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    assert egh.run(_payload(root)) == egh.EXIT_DENY
    record = _last_timing(root)
    assert record["decision"] == "deny" and record["tool"] == "entrance_gate.first_write"


def test_run_denial_message_contains_paved_road(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    root = _make_repo(tmp_path)
    egh.run(_payload(root))
    err = capsys.readouterr().err
    assert "python -m zephyr.library.lookup" in err
    assert "--session sess-t1" in err
    assert ".aliases/sess-t1" in err
    assert "L0-JOURNEY" in err  # 拒绝话术内嵌全程地图锚点（正门给路）


def test_run_allows_after_lookup_and_audits(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    _write_lookup(root, "sess-t1")
    assert egh.run(_payload(root)) == egh.EXIT_PASS
    record = _last_timing(root)
    assert record["decision"] == "allow" and record["lookup_sid"] == "sess-t1"


def test_run_bypass_env_passes_with_audit(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    assert egh.run(_payload(root), env={egh.BYPASS_ENV_VAR: "1"}) == egh.EXIT_PASS
    assert _last_timing(root)["decision"] == "bypass"


def test_run_fail_open_matrix(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    assert egh.run({"tool_name": "Read", "session_id": "s", "cwd": str(root)}) == 0
    assert egh.run({"tool_name": "Edit", "cwd": str(root)}) == 0  # sid 缺失
    assert egh.run({"tool_name": "Edit", "session_id": "s", "cwd": str(root)}) == 0  # 无 file_path
    assert egh.run(_payload(root, rel="docs/x.md")) == 0  # 非业务面不检票不落审计
    assert not (root / ".runtime" / "entrance_audit").exists()
    outside = _payload(root)
    outside["tool_input"]["file_path"] = str(tmp_path / "elsewhere" / "a.py")
    assert egh.run(outside) == 0  # 仓外路径放行


def test_run_relative_file_path(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    payload = _payload(root)
    payload["tool_input"] = {"file_path": "src/zephyr/pkg/demo.py"}
    assert egh.run(payload) == egh.EXIT_DENY


def test_main_fail_open_on_garbage_argv() -> None:
    assert egh.main(["entrance_gate_hook.py", str(_REPO_ROOT / "docs" / "AGENTS.md")]) == 0


# ---------------------------------------------------------------------------
# 端到端：.ps1 启动器链路（仅 Windows；stdin 经字节临时文件中转）
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    sys.platform != "win32" or shutil.which("powershell") is None,
    reason="Windows + PowerShell 专属链路",
)
def test_end_to_end_via_ps1_launcher(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    ps1 = _REPO_ROOT / "scripts" / "governance" / "entrance_gate_hook.ps1"
    env = dict(os.environ)
    env["LOCALAPPDATA"] = str(Path(sys.executable).parents[3])  # ps1 候选探测定位本解释器
    proc = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps1)],
        input=json.dumps(_payload(root)).encode("utf-8"),
        capture_output=True,
        cwd=str(root),
        timeout=60,
        env=env,
    )
    assert proc.returncode == egh.EXIT_DENY
    assert b"zephyr.library.lookup" in proc.stderr
