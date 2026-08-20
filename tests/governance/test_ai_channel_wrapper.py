# [BLUEPRINT] MOD-D5_ARCH_TOOLS | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""tests/governance/test_ai_channel_wrapper.py

tracker #58 验收——Trae AI RunCommand 通道（-NoProfile 硬编码）经 profile-snapshot
注入恢复 wrapper 防护 + AI 会话归因（65 memo §7.33）。

ALGO_FLOW:
  1. 伪造 process-*/powershell-profile-snapshot.ps1 快照目录（tmp_path）
  2. ensure_ai_wrapper_injection.ps1 -SnapshotRoot 注入/幂等/卸载/缺根静默
  3. dot-source 注入后快照起 powershell 子进程，断言 git=Function/危险命令 BLOCKED/
     安全命令透传/Session ID 注入
  4. AI 归因：TEMP 复制 powershell.exe 改名 agent-tool-host.exe 作假父进程，
     断言子会话 session=ai-<pid>-<ts> 且 channel=ai-runcommand；普通父进程保持 UUID
  5. 保活计划任务 ZephyrAlpha-AI-Wrapper-Inject 注册断言

NOTE: 本套件不执行任何 git 写操作（clean 用例在 wrapper 层被 BLOCKED，不触达真 git），
      tmp_path（仓内 .runtime/tmp）使用安全；审计经 USERPROFILE 重定向隔离到 tmp。
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
WRAPPER = REPO_ROOT / "scripts" / "git_safety_wrapper.ps1"
ENSURE = REPO_ROOT / "scripts" / "ensure_ai_wrapper_injection.ps1"
PS = "powershell.exe"
MARKER = "ZEPHYR-AI-WRAPPER-INJECT"
TASK_NAME = "ZephyrAlpha-AI-Wrapper-Inject"


def _clean_env() -> dict[str, str]:
    """剔除继承的 ZEPHYR_SESSION_ID（AI 会话内跑 pytest 时父链会带上已注入的 session），
    让每个用例从'无 session'起点验证 wrapper 自身的归因分支。"""
    import os

    env = dict(os.environ)
    env.pop("ZEPHYR_SESSION_ID", None)
    env.pop("ZEPHYR_SESSION_START", None)
    return env


def _run_ps(args: list[str], timeout: int = 90) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [PS, "-NoProfile", "-ExecutionPolicy", "Bypass"] + args,
        capture_output=True,
        text=True,
        timeout=timeout,
        encoding="utf-8",
        errors="replace",
        env=_clean_env(),
    )


def _make_snapshot_root(tmp_path: Path) -> Path:
    """伪造单进程快照目录，返回快照根。"""
    proc_dir = tmp_path / "native-runcommand-snapshots" / "process-1234-1786700000000"
    proc_dir.mkdir(parents=True)
    (proc_dir / "powershell-profile-snapshot.ps1").write_text(
        "$env:PAGER = 'cat'\n$env:GIT_EDITOR = 'true'\n", encoding="utf-8"
    )
    return tmp_path / "native-runcommand-snapshots"


def _snapshot_file(root: Path) -> Path:
    return root / "process-1234-1786700000000" / "powershell-profile-snapshot.ps1"


def _inject(root: Path, extra: str = "") -> subprocess.CompletedProcess[str]:
    return _run_ps(["-File", str(ENSURE), "-SnapshotRoot", str(root)] + ([extra] if extra else []))


# ---------------------------------------------------------------- 注入脚本行为（幂等/卸载/缺根）


def test_inject_creates_marker(tmp_path: Path):
    root = _make_snapshot_root(tmp_path)
    r = _inject(root)
    assert r.returncode == 0, r.stderr
    assert "injected=1" in r.stdout
    content = _snapshot_file(root).read_text(encoding="utf-8")
    assert MARKER in content
    assert "git_safety_wrapper.ps1" in content
    assert "$env:PAGER" in content  # 原有内容保留


def test_inject_idempotent(tmp_path: Path):
    root = _make_snapshot_root(tmp_path)
    _inject(root)
    r = _inject(root)
    assert r.returncode == 0
    assert "injected=0" in r.stdout and "skipped=1" in r.stdout
    assert _snapshot_file(root).read_text(encoding="utf-8").count(MARKER) == 1


def test_inject_missing_root_silent(tmp_path: Path):
    r = _inject(tmp_path / "nonexistent-root")
    assert r.returncode == 0
    assert "injected=0" in r.stdout


def test_inject_remove_strips_marker(tmp_path: Path):
    root = _make_snapshot_root(tmp_path)
    _inject(root)
    r = _run_ps(["-File", str(ENSURE), "-SnapshotRoot", str(root), "-Remove"])
    assert r.returncode == 0
    assert "removed=1" in r.stdout
    content = _snapshot_file(root).read_text(encoding="utf-8")
    assert MARKER not in content
    assert "$env:PAGER" in content


def test_inject_fails_without_wrapper(tmp_path: Path):
    """wrapper 真源缺失时 fail-closed（复制脚本到无 wrapper 的目录）。"""
    fake_dir = tmp_path / "fake_scripts"
    fake_dir.mkdir()
    fake_ensure = fake_dir / ENSURE.name
    fake_ensure.write_text(ENSURE.read_text(encoding="utf-8"), encoding="utf-8")
    root = _make_snapshot_root(tmp_path)
    r = _run_ps(["-File", str(fake_ensure), "-SnapshotRoot", str(root)])
    assert r.returncode == 1
    assert "wrapper source not found" in (r.stdout + r.stderr)


# ---------------------------------------------------------------- 注入后快照的端到端防护行为


@pytest.fixture()
def injected_snapshot(tmp_path: Path) -> Path:
    root = _make_snapshot_root(tmp_path)
    r = _inject(root)
    assert r.returncode == 0, r.stderr
    return _snapshot_file(root)


def _in_snapshot_shell(snapshot: Path, tmp_path: Path, cmd: str) -> str:
    """模拟 AI 通道：-NoProfile 子进程仅 dot-source 注入后的快照（USERPROFILE 隔离审计）。"""
    script = f"$env:USERPROFILE='{tmp_path}'; . '{snapshot}'; {cmd}"
    r = _run_ps(["-Command", script])
    return r.stdout + r.stderr


def test_snapshot_loads_wrapper_git_is_function(injected_snapshot: Path, tmp_path: Path):
    out = _in_snapshot_shell(injected_snapshot, tmp_path, "(Get-Command git).CommandType")
    assert "Function" in out


def test_snapshot_blocks_git_clean(injected_snapshot: Path, tmp_path: Path):
    out = _in_snapshot_shell(injected_snapshot, tmp_path, "git clean -fd")
    assert "BLOCKED" in out


def test_snapshot_blocks_plumbing_read_tree(injected_snapshot: Path, tmp_path: Path):
    """66 memo 裁定 7：plumbing 四命令在 AI 通道同样硬阻断。"""
    out = _in_snapshot_shell(injected_snapshot, tmp_path, "git read-tree HEAD")
    assert "BLOCKED" in out


def test_snapshot_passthrough_git_status(injected_snapshot: Path, tmp_path: Path):
    out = _in_snapshot_shell(injected_snapshot, tmp_path, "git status --short; echo EXIT=$LASTEXITCODE")
    assert "EXIT=0" in out


def test_snapshot_remove_item_recurse_force_blocked(injected_snapshot: Path, tmp_path: Path):
    out = _in_snapshot_shell(
        injected_snapshot,
        tmp_path,
        "Remove-Item -Recurse -Force 'D:\\nonexistent-zeph58-target'",
    )
    assert "BLOCKED" in out


def test_snapshot_session_id_injected(injected_snapshot: Path, tmp_path: Path):
    out = _in_snapshot_shell(injected_snapshot, tmp_path, "$env:ZEPHYR_SESSION_ID")
    assert re.search(r"[0-9a-f-]{36}", out), f"no UUID session id: {out}"


# ---------------------------------------------------------------- AI 通道归因（§7.33）


def test_ai_channel_attribution_via_toolhost_parent(tmp_path: Path):
    """假 agent-tool-host.exe 父进程 -> 子会话 session=ai-<pid>-<yyyyMMddHHmmss>。"""
    fake_host = tmp_path / "agent-tool-host.exe"
    shutil.copy(r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe", fake_host)
    child = tmp_path / "child.ps1"
    child.write_text(
        f". '{WRAPPER}'; Write-Output ($env:ZEPHYR_SESSION_ID + '|' + $global:_zephyrChannel)",
        encoding="utf-8",
    )
    launcher = f"$env:USERPROFILE='{tmp_path}'; & powershell -NoProfile -ExecutionPolicy Bypass -File '{child}'"
    r = subprocess.run(
        [str(fake_host), "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", launcher],
        capture_output=True,
        text=True,
        timeout=90,
        encoding="utf-8",
        errors="replace",
        env=_clean_env(),
    )
    out = r.stdout + r.stderr
    assert re.search(r"ai-\d+-\d{14}\|ai-runcommand", out), f"AI attribution failed: {out}"


def test_interactive_parent_keeps_uuid(tmp_path: Path):
    """普通父进程（pytest->powershell）保持 UUID + interactive channel。"""
    r = _run_ps(
        [
            "-Command",
            f"$env:USERPROFILE='{tmp_path}'; . '{WRAPPER}'; "
            "Write-Output ($env:ZEPHYR_SESSION_ID + '|' + $global:_zephyrChannel)",
        ]
    )
    out = r.stdout + r.stderr
    assert re.search(r"[0-9a-f-]{36}\|interactive", out), f"unexpected identity: {out}"


def test_ai_channel_audit_channel_field(tmp_path: Path):
    """AI 通道审计条目带 channel=ai-runcommand 且聚合到单一 ai-* session 文件。"""
    fake_host = tmp_path / "agent-tool-host.exe"
    shutil.copy(r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe", fake_host)
    child = tmp_path / "child.ps1"
    child.write_text(
        f". '{WRAPPER}'; git clean -fd; git clean -fdx",
        encoding="utf-8",
    )
    launcher = f"$env:USERPROFILE='{tmp_path}'; & powershell -NoProfile -ExecutionPolicy Bypass -File '{child}'"
    subprocess.run(
        [str(fake_host), "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", launcher],
        capture_output=True,
        text=True,
        timeout=90,
        encoding="utf-8",
        errors="replace",
        env=_clean_env(),
    )
    audit_dir = tmp_path / ".zephyr_audit"
    files = list(audit_dir.glob("audit_*_ai-*.jsonl"))
    assert len(files) == 1, f"expected single aggregated ai audit file, got: {files}"
    lines = [l for l in files[0].read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines) == 2  # 两条 BLOCKED 聚合进同一文件
    import json

    for line in lines:
        entry = json.loads(line)
        assert entry["action"] == "BLOCKED"
        assert entry["channel"] == "ai-runcommand"
        assert entry["session"].startswith("ai-")


# ---------------------------------------------------------------- 保活计划任务


def test_keepalive_scheduled_task_registered():
    r = subprocess.run(
        ["schtasks", "/query", "/tn", TASK_NAME],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"keepalive task missing: {r.stdout}{r.stderr}"
    assert TASK_NAME in r.stdout
