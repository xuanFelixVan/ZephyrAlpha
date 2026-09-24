# [TTL] permanent
# [MODULE] tests.governance.test_w4_env_no_residual
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.git_commit_gateway
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 测试隔离——桩掉真 commit / git 子进程，仅用 tmp_path，禁污染生产 data/ 与 depgraph/governance.db
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
"""test_w4_env_no_residual.py — W4（`_commit_auto` 永久留授权旗）止血红测（D2 §6 R-D2-b）

病根（`git_commit_gateway.py` `_commit_auto`）：两条 `os.environ[_GATEWAY_ENV] = "1"`
（正常支 + fail-open 降级支）置位后，函数唯一 finally 只删 pathspec 临时文件、不还原旗
⇒ 任何一次 auto-commit 之后本进程永久持 "1" ⇒ 后续非 commit 子进程 / in-process 护栏
（`git_guard` 认旗放行 reset --hard/clean/stash）被过授权。

本测桩掉真 commit（不触真 git / 真 gate），调 `_commit_auto` 形态路径一次，断言返回后
`os.environ` 无残留 "1"（并测前值还原）。对未打补丁网关 MUST 红、打补丁后 MUST 绿。
tests/ 目录 CREATE-GUARD 豁免（免 creation_token）。
"""

from __future__ import annotations

import os
import subprocess
import types
from pathlib import Path

import pytest

# 真源名（对外别名 GATEWAY_ENV）——直接钉死字面量，独立于导入符号，防别名漂移掩红
GATEWAY_ENV_NAME = "ZEPHYR_COMMIT_GATEWAY"

import zephyr.gov_enforcement.rule_bridge.git_commit_gateway as gw_mod  # noqa: E402
from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (  # noqa: E402
    CommitStatus,
    GitCommitGateway,
)


# ---------------------------------------------------------------------------
# 桩 harness：只让 _commit_auto 走到 os.environ[_GATEWAY_ENV]="1" 那一行，
# 不触任何真 git / 真 gate（真 commit 已被桩掉）
# ---------------------------------------------------------------------------
def _init_git_repo(repo_dir: Path) -> None:
    repo_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(
        GIT_AUTHOR_NAME="T",
        GIT_AUTHOR_EMAIL="t@t.com",
        GIT_COMMITTER_NAME="T",
        GIT_COMMITTER_EMAIL="t@t.com",
    )
    subprocess.run(["git", "init", "-q"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(
        ["git", "config", "user.email", "t@t.com"], cwd=str(repo_dir), capture_output=True, env=env, check=True
    )
    readme = repo_dir / "README.md"
    readme.write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(
        ["git", "commit", "-qm", "init", "--no-verify"], cwd=str(repo_dir), capture_output=True, env=env, check=True
    )


class _NoopLock:
    """桩 _GlobalCommitLock：空临界区，不触文件锁设施。"""

    def __init__(self, *a, **k) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _stub_commit_auto(gw, tmp_path: Path) -> str:
    """把 _commit_auto 直提路径上所有真 git / 真 gate 站点桩掉，返回一个既有文件路径。"""
    tracked = tmp_path / "work.txt"
    tracked.write_text("hello\n", encoding="utf-8")

    # 批器关闭（否则 _commit_auto 缓冲后早返回，走不到置位行）
    gw._batcher.is_enabled = lambda: False  # type: ignore[assignment]
    # 队列改道关闭 → 走现行直提
    gw._is_merge_in_progress = lambda: False  # type: ignore[assignment]
    gw._resolve_auto_commit_files = lambda files: [str(tracked)]  # type: ignore[assignment]
    # 所有 auto-commit gate（DIRECTORY-CONTRACT/TTL/FILE-PLACEMENT-TTL）判通过
    gw._run_auto_commit_gate = lambda *a, **k: None  # type: ignore[assignment]
    # pathspec 临时文件走 tmp_path（finally 的 os.remove 即便不存在也被吞）
    gw._write_pathspec_file = lambda existing: str(tmp_path / "gw_pathspec_stub.txt")  # type: ignore[assignment]
    # git add 成功（返回 None=无 fail）
    gw._git_add_with_index_lock_retry = lambda *a, **k: None  # type: ignore[assignment]
    # git diff --cached --quiet 返回码非 0 → 有 staged 变更，继续 commit
    gw.run_git = lambda cmd: types.SimpleNamespace(returncode=1, stdout=b"", stderr=b"")  # type: ignore[assignment]
    # 真 commit 桩：返回假 hash，无错误
    gw._commit_with_file_message = lambda *a, **k: ("deadbeefcafebabe", None)  # type: ignore[assignment]
    return str(tracked)


def _make_gateway(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> GitCommitGateway:
    repo = tmp_path / "repo"
    _init_git_repo(repo)
    monkeypatch.setattr(gw_mod, "_commit_queue_serializer_enabled", lambda: False)
    monkeypatch.setattr(gw_mod, "_GlobalCommitLock", _NoopLock)
    monkeypatch.setattr(gw_mod, "record_derived_write", lambda *a, **k: None)
    return GitCommitGateway(project_root=repo)


# ---------------------------------------------------------------------------
# 证尺有牙：确认被导入的网关模块就是这块 worktree 的 src（防 conftest 把主区插 sys.path[0] 假绿/假红）
# ---------------------------------------------------------------------------
def _assert_module_is_from_this_worktree() -> None:
    here = Path(__file__).resolve()
    mod_file = Path(gw_mod.__file__).resolve()
    # 测试文件与网关模块必须同属一个 worktree 根（parents[2] of tests/governance/x.py）
    root = here.parents[2]
    assert str(mod_file).startswith(str(root)), (
        f"证尺失真：网关模块解析到 {mod_file}，不在本 worktree {root}——"
        f"疑似 conftest 把主区 _PROJECT_ROOT 插到 sys.path[0]（假测）"
    )


def test_commit_auto_leaves_no_gateway_env_residual(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """R-D2-b 核心：_commit_auto 返回后进程不得残留 ZEPHYR_COMMIT_GATEWAY="1"。"""
    _assert_module_is_from_this_worktree()
    # 干净起点：显式清旗，坐实 "1" 只可能来自被测函数
    monkeypatch.delenv(GATEWAY_ENV_NAME, raising=False)
    gw = _make_gateway(tmp_path, monkeypatch)
    target = _stub_commit_auto(gw, tmp_path)

    result = gw._commit_auto("s-w4", [target], "chore: w4 residual probe")
    assert result.status is CommitStatus.OK, f"直提桩路径应 OK，实得 {result.status}: {result.message}"

    residual = os.environ.get(GATEWAY_ENV_NAME)
    assert residual != "1", (
        "W4 泄漏未止血：_commit_auto 返回后进程仍持授权旗 ZEPHYR_COMMIT_GATEWAY='1'"
        "（过授权方向——后续非 commit 子进程 / git_guard 将被蒙蔽放行破坏性操作）"
    )
    assert GATEWAY_ENV_NAME not in os.environ, f"返回后应彻底无残留，实得 {residual!r}"


def test_commit_auto_restores_prior_gateway_env_value(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """prev-snapshot 分支：函数置位前已有的前值必须在返回后被原样还原（非 pop 掉、也非留 '1'）。"""
    _assert_module_is_from_this_worktree()
    sentinel = "caller-owned-prev"
    monkeypatch.setenv(GATEWAY_ENV_NAME, sentinel)
    gw = _make_gateway(tmp_path, monkeypatch)
    target = _stub_commit_auto(gw, tmp_path)

    result = gw._commit_auto("s-w4", [target], "chore: w4 prev-value probe")
    assert result.status is CommitStatus.OK

    after = os.environ.get(GATEWAY_ENV_NAME)
    assert after != "1", f"W4 泄漏：置位覆盖了调用方前值且未还原，返回后仍为 {after!r}"
    assert after == sentinel, f"前值应被还原为 {sentinel!r}，实得 {after!r}（还原逻辑 prev is None 分支误 pop？）"
