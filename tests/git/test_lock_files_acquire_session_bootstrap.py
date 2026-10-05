# [A_test] test_id=ARCH-AICOLLAB-001-58 | module=scripts/lock_files.py | gate=pytest
# [BLUEPRINT] MOD-INF-005 | scripts/lock_files.py | §7.28+C9 会话存活兜底
# [TESTS] tests/git/test_lock_files_acquire_session_bootstrap.py
# [TTL] task_bound
"""lock_files acquire --session 会话存活兜底测试（修3，st-sQ-infra-20261005）。

C9 同款兜底（参照 scripts/git_commit.py enqueue 段）：裁定#252 绑定锁的判活锚
=SessionRegistry——会话未注册/已过期时 acquire 自动调用 session_worktree_start
幂等重注册（allow_duplicate+allow_workspace_drift，含心跳 daemon 拉起）后再继续
claim；已注册且存活=零额外操作。任何失败不阻断 claim（fail-open）。

断言矩阵：
1. 未注册会话 acquire → 触发幂等重注册（参数契约：allow_duplicate/allow_workspace_drift）且 claim 成功
2. 已注册且存活会话 acquire → 不触发重注册（零额外操作），claim 成功
3. 已过期（心跳超窗 90s 判死，get_session 返回 None）会话 acquire → 触发重注册
"""

from __future__ import annotations

import contextlib
import io
import json
import sys
import time
from pathlib import Path

import pytest

# 确保 scripts/ 在 sys.path（与 test_lock_files_ttl_mutex.py 同口径）
SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import lock_files  # noqa: E402

_SID = "sess-bootstrap-probe"
_PROBE = "docs/bootstrap_probe.md"


@pytest.fixture
def isolated_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """锁根/registry/REPO_ROOT 全部隔离到 tmp——判活分片与 guide 留痕均落 tmp。

    _GUIDE_READS_DIR/_LOOKUP_AUDIT_DIR 是 import 期自真 REPO_ROOT 派生的模块
    常量（monkeypatch REPO_ROOT 不重算），须一并打到 tmp（测试禁写生产 .runtime）。
    """
    lock_root = tmp_path / ".ailocks"
    monkeypatch.setattr(lock_files, "LOCK_ROOT", lock_root)
    monkeypatch.setattr(lock_files, "REGISTRY_PATH", lock_root / "registry.json")
    monkeypatch.setattr(lock_files, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(lock_files, "_GUIDE_READS_DIR", tmp_path / ".runtime" / "guide_reads")
    monkeypatch.setattr(lock_files, "_LOOKUP_AUDIT_DIR", tmp_path / ".runtime" / "lookup_audit")
    return tmp_path


def _write_shard(root: Path, *, last_heartbeat: float) -> None:
    """直写会话分片（S4-D 片存储格式，与主仓 .runtime/session_registry 同构）。"""
    shard_dir = root / ".runtime" / "session_registry"
    shard_dir.mkdir(parents=True, exist_ok=True)
    now = time.time()
    (shard_dir / f"{_SID}.json").write_text(
        json.dumps(
            {
                "session_id": _SID,
                "pid": 0,
                "start_time": now,
                "held_files": [],
                "last_heartbeat": last_heartbeat,
                "last_activity": now,
            }
        ),
        encoding="utf-8",
    )


def _install_fake_start(monkeypatch: pytest.MonkeyPatch) -> list[dict]:
    """桩掉 session_worktree_start（helper 惰性导入，打模块属性即生效），记录调用。"""
    calls: list[dict] = []

    def _fake_start(session_id=None, project_root=None, **kwargs):
        calls.append({"session_id": session_id, **kwargs})
        return {"ok": True, "session_id": session_id}

    import zephyr.gov_enforcement.rule_bridge.session_worktree as sw_mod

    monkeypatch.setattr(sw_mod, "session_worktree_start", _fake_start)
    return calls


def _run_acquire(monkeypatch: pytest.MonkeyPatch) -> tuple[int, str]:
    monkeypatch.setattr(
        sys,
        "argv",
        ["lock_files.py", "acquire", _PROBE, _SID, "--session", _SID, "--skip-naming-check"],
    )
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = lock_files.main()
    return rc, buf.getvalue()


def test_acquire_auto_registers_unregistered_session(isolated_env: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """未注册会话 acquire → 自动幂等重注册（参数契约断言）后再 claim。"""
    calls = _install_fake_start(monkeypatch)
    rc, out = _run_acquire(monkeypatch)
    assert rc == 0, out
    assert "ACQUIRED" in out
    assert len(calls) == 1, f"应恰好重注册一次，实得 {calls}"
    assert calls[0]["session_id"] == _SID
    assert calls[0]["allow_duplicate"] is True
    assert calls[0]["allow_workspace_drift"] is True


def test_acquire_registered_session_zero_extra_ops(isolated_env: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """已注册且存活（pid=0+心跳新鲜）会话 acquire → 零额外操作（不调重注册）。"""
    _write_shard(isolated_env, last_heartbeat=time.time())
    calls = _install_fake_start(monkeypatch)
    rc, out = _run_acquire(monkeypatch)
    assert rc == 0, out
    assert "ACQUIRED" in out
    assert calls == [], f"存活会话不得触发重注册，实得 {calls}"


def test_acquire_expired_session_triggers_reregister(isolated_env: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """已过期（心跳超窗 90s 判死）会话 acquire → get_session 返回 None → 触发重注册。"""
    _write_shard(isolated_env, last_heartbeat=time.time() - 10_000.0)
    calls = _install_fake_start(monkeypatch)
    rc, out = _run_acquire(monkeypatch)
    assert rc == 0, out
    assert "ACQUIRED" in out
    assert len(calls) == 1 and calls[0]["session_id"] == _SID
