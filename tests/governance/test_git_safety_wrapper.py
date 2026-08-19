# [BLUEPRINT] MOD-D5_ARCH_TOOLS | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""tests/governance/test_git_safety_wrapper.py

65 号 memo §7.7 验收 + §7.1 红队——git_safety_wrapper.ps1 / install_git_safety_wrapper.ps1 全行为测试。

ALGO_FLOW:
  1. fixture：临时 profile + 安装脚本安装（-ProfilePath 注入）
  2. 每用例起 powershell -NoProfile 子进程 dot-source 临时 profile 后执行测试命令
  3. 断言拦截标记（BLOCKED/HARDBLOCKED）/放行透传/审计落盘/幂等/卸载

覆盖：§7.1.1 git 16 类阻断+放行边界、§7.23 四命令、§7.1.2 原生删除类+CRITICAL、
      §7.17.2 .git 硬阻断、§7.10 审计、§7.7 安装/幂等/卸载、§7.32 Session ID。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
WRAPPER = REPO_ROOT / "scripts" / "git_safety_wrapper.ps1"
INSTALLER = REPO_ROOT / "scripts" / "install_git_safety_wrapper.ps1"
PS = "powershell.exe"
MARKER = "# >>> git-safety-wrapper >>>"


def _run_ps(script: str, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    """起独立 powershell 子进程执行脚本，返回完整结果。

    tracker #58：AI 通道注入后，AI 会话内 pytest 的子进程会继承 ZEPHYR_SESSION_ID
    （归因聚合特性）。测试须从"无 session"起点验证 wrapper 自身的注入/归因分支，
    故剔除继承值。"""
    env = dict(os.environ)
    env.pop("ZEPHYR_SESSION_ID", None)
    env.pop("ZEPHYR_SESSION_START", None)
    return subprocess.run(
        [PS, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        capture_output=True,
        text=True,
        timeout=timeout,
        encoding="utf-8",
        errors="replace",
        env=env,
    )


@pytest.fixture()
def installed_profile(tmp_path: Path) -> Path:
    """临时 profile 安装 wrapper，返回 profile 路径。"""
    profile = tmp_path / "profile.ps1"
    profile.write_text("# pre-existing content\n", encoding="utf-8")
    r = _run_ps(f"& '{INSTALLER}' -ProfilePath '{profile}'")
    assert r.returncode == 0, f"install failed: {r.stdout}\n{r.stderr}"
    assert MARKER in profile.read_text(encoding="utf-8-sig")
    return profile


def _in_shell(profile: Path, cmd: str, cwd: Path | None = None) -> str:
    """dot-source 临时 profile 后执行命令，返回 stdout+stderr 合并文本。"""
    cd = f"Set-Location '{cwd}';" if cwd else ""
    r = _run_ps(f"{cd} . '{profile}'; {cmd}")
    return r.stdout + r.stderr


# ---------------------------------------------------------------- 安装/幂等/卸载（§7.7）


def test_install_creates_marker(installed_profile: Path):
    assert MARKER in installed_profile.read_text(encoding="utf-8-sig")


def test_install_idempotent(installed_profile: Path):
    r = _run_ps(f"& '{INSTALLER}' -ProfilePath '{installed_profile}'")
    assert r.returncode == 0
    assert "idempotent skip" in r.stdout
    assert installed_profile.read_text(encoding="utf-8-sig").count(MARKER) == 1


def test_install_force_reinstall(installed_profile: Path):
    r = _run_ps(f"& '{INSTALLER}' -ProfilePath '{installed_profile}' -Force")
    assert r.returncode == 0
    assert installed_profile.read_text(encoding="utf-8-sig").count(MARKER) == 1


def test_uninstall_removes_marker_keeps_rest(installed_profile: Path):
    r = _run_ps(f"& '{INSTALLER}' -ProfilePath '{installed_profile}' -Uninstall")
    assert r.returncode == 0
    content = installed_profile.read_text(encoding="utf-8-sig")
    assert MARKER not in content
    assert "pre-existing content" in content


def test_uninstall_when_not_installed(tmp_path: Path):
    profile = tmp_path / "p.ps1"
    profile.write_text("# x\n", encoding="utf-8")
    r = _run_ps(f"& '{INSTALLER}' -ProfilePath '{profile}' -Uninstall")
    assert r.returncode == 0
    assert "not installed" in r.stdout


def test_install_fails_without_wrapper(tmp_path: Path):
    """wrapper 真源缺失时安装 fail-closed。"""
    fake_dir = tmp_path / "fake_scripts"
    fake_dir.mkdir()
    fake_installer = fake_dir / "install_git_safety_wrapper.ps1"
    fake_installer.write_text(INSTALLER.read_text(encoding="utf-8"), encoding="utf-8")
    r = _run_ps(f"& '{fake_installer}' -ProfilePath '{tmp_path / 'p.ps1'}'")
    assert r.returncode == 1
    assert "wrapper source not found" in r.stdout


# ---------------------------------------------------------------- git 拦截（§7.1.1 + §7.23）


def test_git_is_function(installed_profile: Path):
    out = _in_shell(installed_profile, "(Get-Command git).CommandType")
    assert "Function" in out


@pytest.mark.parametrize(
    "cmd",
    [
        "git clean -fd",
        "git clean -fdx",
        "git reset --hard HEAD",
        "git reset --merge",
        "git checkout .",
        "git restore foo.py",
        "git stash push",
        "git stash pop",
        "git rm foo.py",
        "git branch -D feature",
        "git push -f",
        "git filter-branch --all",
        "git filter-repo",
        "git reflog expire --expire=now --all",
        "git gc --prune=now",
        # 66 memo 裁定 7：plumbing index/对象库操纵（事故 6 根因）
        "git read-tree HEAD",
        "git update-index --add foo.py",
        "git write-tree",
        "git hash-object -w foo.py",
    ],
)
def test_git_dangerous_blocked(installed_profile: Path, cmd: str):
    out = _in_shell(installed_profile, cmd)
    assert "BLOCKED" in out, f"未拦截: {cmd}\n{out}"


def test_git_plumbing_serializer_whitelist(installed_profile: Path):
    """66 memo 裁定 7 白名单：ZEPHYR_SERIALIZER_MODE=1 时 plumbing 透传真实 git
    （在系统 TEMP 非 git 目录执行，真 git 报自身错误证明透传发生，绝不应出现 wrapper BLOCKED）。

    警告：本用例绝不可用 pytest tmp_path——本仓 pyproject basetemp 在仓内
    （.runtime/tmp/），仓内透传 read-tree 会真碰主仓 index（66 事故 6 同款风险）。
    """
    import tempfile

    with tempfile.TemporaryDirectory() as outside_repo:
        out = _in_shell(installed_profile, "$env:ZEPHYR_SERIALIZER_MODE='1'; git read-tree HEAD", cwd=Path(outside_repo))
    assert "BLOCKED" not in out, f"白名单误拦: {out}"
    assert "not a git repository" in out or "fatal" in out, f"未透传真实 git: {out}"


@pytest.mark.parametrize(
    "cmd",
    [
        "git clean -n",                # dry-run 放行
        "git stash list",              # 只读放行
        "git push --force-with-lease", # lease 放行
        "git rm --cached foo.py",      # cached 放行
    ],
)
def test_git_safe_allowed_through(installed_profile: Path, cmd: str):
    """放行命令透传真实 git（执行可能报 git 自身错误，但绝不应出现 wrapper BLOCKED）。"""
    out = _in_shell(installed_profile, cmd)
    assert "BLOCKED" not in out, f"误拦: {cmd}\n{out}"


def test_git_status_really_executes(installed_profile: Path, tmp_path: Path):
    """放行链路真执行：初始化临时仓后 git status 有真实输出。"""
    repo = tmp_path / "r"
    repo.mkdir()
    out = _in_shell(installed_profile, "git init -q; git status --short --branch", cwd=repo)
    assert "BLOCKED" not in out
    assert "No commits yet" in out or "##" in out


def test_git_checkout_path_blocked_in_repo(installed_profile: Path, tmp_path: Path):
    """PS 5.1 吞裸 '--'——checkout -- <path> 与 checkout <branch> 同构，wrapper 用 rev-parse 区分：
    现存路径必拦；真实分支名放行。"""
    repo = tmp_path / "r2"
    repo.mkdir()
    _in_shell(installed_profile, "git init -q; git config user.email t@t; git config user.name t", cwd=repo)
    (repo / "foo.py").write_text("x", encoding="utf-8")
    _in_shell(installed_profile, "git add foo.py; git commit -qm init; git branch -qb side", cwd=repo)
    # checkout -- <现存路径> → 拦（PS 吞 -- 后 rev-parse 判定 foo.py 非 ref 且路径存在）
    out = _in_shell(installed_profile, "git checkout -- foo.py", cwd=repo)
    assert "BLOCKED" in out, f"checkout -- path 未拦: {out}"
    # checkout <真实分支> → 放行
    out2 = _in_shell(installed_profile, "git checkout side", cwd=repo)
    assert "BLOCKED" not in out2, f"checkout 分支误拦: {out2}"


def test_git_branch_d_allowed_uppercase_d_blocked(installed_profile: Path, tmp_path: Path):
    """tracker #72：-d/-D 区分——PowerShell -match 大小写不敏感曾把安全删除
    git branch -d 当 -D 误拦；修复后 -d 放行透传、-D 仍拦截、分支名含 -D 子串不误拦。"""
    repo = tmp_path / "r3"
    repo.mkdir()
    _in_shell(installed_profile, "git init -q; git config user.email t@t; git config user.name t", cwd=repo)
    (repo / "foo.py").write_text("x", encoding="utf-8")
    _in_shell(installed_profile, "git add foo.py; git commit -qm init; git branch merged", cwd=repo)
    # ① git branch -d <已合并分支> → 放行且真透传删除（tracker #72 核心断言）
    out = _in_shell(installed_profile, "git branch -d merged", cwd=repo)
    assert "BLOCKED" not in out, f"git branch -d 误拦（tracker #72）: {out}"
    out_list = _in_shell(installed_profile, "git branch --list merged", cwd=repo)
    assert "merged" not in out_list, f"-d 未透传真实 git 删除: {out_list}"
    # ② git branch -D → 仍拦截（与上方 parametrize 用例互补的显式回归）
    out_d = _in_shell(installed_profile, "git branch -D feature", cwd=repo)
    assert "BLOCKED" in out_d, f"git branch -D 未拦截: {out_d}"
    # ③ 分支名含 -D 子串（my-D-branch）→ -d 删除不误拦（边界锚定防子串误报）
    out_sub = _in_shell(installed_profile, "git branch my-D-branch; git branch -d my-D-branch", cwd=repo)
    assert "BLOCKED" not in out_sub, f"分支名含 -D 子串误拦: {out_sub}"


# ------------------------------------------------------- 原生删除类拦截（§7.1.2 + §7.17.2）


def test_remove_item_recurse_force_blocked(installed_profile: Path):
    """victim 必须在 $env:TEMP 之外（wrapper TEMP 白名单），放仓内 .runtime 临时目录。"""
    import uuid

    victim = REPO_ROOT / ".runtime" / f"wrapper_test_{uuid.uuid4().hex[:12]}" / "victim"
    victim.mkdir(parents=True)
    (victim / "a.txt").write_text("x", encoding="utf-8")
    try:
        out = _in_shell(installed_profile, f"Remove-Item '{victim}' -Recurse -Force")
        assert "BLOCKED" in out
        assert victim.exists(), "被拦目录不应被删"
    finally:
        import shutil

        shutil.rmtree(victim.parent, ignore_errors=True)


def test_remove_item_recurse_force_temp_allowed(installed_profile: Path):
    out = _in_shell(
        installed_profile,
        "$d = Join-Path $env:TEMP ('zephyr_wrapper_test_' + [guid]::NewGuid().ToString('N'));"
        " New-Item -ItemType Directory -Path $d -Force | Out-Null;"
        " Remove-Item $d -Recurse -Force;"
        " if (Test-Path $d) { 'STILL_EXISTS' } else { 'DELETED' }",
    )
    assert "BLOCKED" not in out
    assert "DELETED" in out


def test_remove_item_single_file_allowed(installed_profile: Path, tmp_path: Path):
    f = tmp_path / "one.txt"
    f.write_text("x", encoding="utf-8")
    out = _in_shell(installed_profile, f"Remove-Item '{f}' -Force")
    assert "BLOCKED" not in out
    assert not f.exists()


def test_remove_item_git_dir_hardblocked(installed_profile: Path):
    """§7.17.2：.git 目录写入硬阻断（放仓内路径，避开 TEMP 白名单干扰）。"""
    import shutil
    import uuid

    base = REPO_ROOT / ".runtime" / f"wrapper_test_{uuid.uuid4().hex[:12]}"
    gitdir = base / "repo" / ".git"
    gitdir.mkdir(parents=True)
    (gitdir / "config").write_text("x", encoding="utf-8")
    try:
        out = _in_shell(installed_profile, f"Remove-Item '{gitdir}' -Recurse -Force")
        assert "HARDBLOCKED" in out
        assert gitdir.exists(), ".git 目录不应被动"
    finally:
        shutil.rmtree(base, ignore_errors=True)


@pytest.mark.parametrize("cmd", ["del /s foo", "rd /s foo", "rm -rf foo"])
def test_cmd_native_delete_blocked(installed_profile: Path, cmd: str):
    out = _in_shell(installed_profile, cmd)
    assert "BLOCKED" in out or "HARDBLOCKED" in out, f"未拦截: {cmd}\n{out}"


@pytest.mark.parametrize("cmd", ["format C:", "diskpart", "vssadmin delete shadows /all"])
def test_critical_hardblocked(installed_profile: Path, cmd: str):
    out = _in_shell(installed_profile, cmd)
    assert "HARDBLOCKED" in out, f"未硬阻断: {cmd}\n{out}"
    assert "escape" not in out, "CRITICAL 命令不得提供逃生通道"


# ---------------------------------------------------------------- 审计（§7.10/7.27）


def test_audit_log_written(installed_profile: Path):
    audit_dir = Path(os.environ["USERPROFILE"]) / ".zephyr_audit"
    before = set(audit_dir.glob("audit_*.jsonl")) if audit_dir.exists() else set()
    out = _in_shell(installed_profile, "git clean -fd; git status")
    assert "BLOCKED" in out
    after = set(audit_dir.glob("audit_*.jsonl"))
    candidates = (after - before) or after
    found = {"BLOCKED": False, "ALLOWED": False}
    for fp in candidates:
        for line in fp.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("command") == "git clean -fd" and entry.get("action") == "BLOCKED":
                found["BLOCKED"] = True
            if entry.get("command") == "git status" and entry.get("action") == "ALLOWED":
                found["ALLOWED"] = True
    assert found["BLOCKED"], "审计缺 BLOCKED 记录"
    assert found["ALLOWED"], "审计缺 ALLOWED 记录"


# ---------------------------------------------------------------- Session ID（§7.32）


def test_session_id_injected(installed_profile: Path):
    out = _in_shell(installed_profile, "$env:ZEPHYR_SESSION_ID")
    assert "-" in out.strip() and len(out.strip()) >= 36


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
