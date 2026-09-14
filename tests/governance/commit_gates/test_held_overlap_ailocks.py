# -*- coding: utf-8 -*-
# [A_test] module_id: MOD-GOV_held_overlap_ailocks | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_held_overlap_ailocks
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_held_overlap_ailocks — .ailocks 双轨搭便车防护单测（红蓝 v4 F2 治本）

覆盖：
- 他会话 .ailocks 活跃锁命中目标文件 → 阻断（含持有者与文件名）
- 本会话自己的锁 → 放行
- 过期锁（ts 超过 TTL）→ 放行
- 无 .ailocks 目录 / 无命中锁 → 放行
- allow_overlap=True 逃生通道仍放行
- held_files 既有路径（other_held_files）不受影响
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from types import SimpleNamespace

from zephyr.gov_enforcement.commit_gates.held_overlap_gate import (
    _ailocks_other_holders,
    make_held_overlap_gate,
)

FILE_A = "tests/xt4tmp/some_file.py"


class _FakeRegistry:
    def __init__(self, other_held=None):
        self._other = other_held or set()

    def other_held_files(self, session_id):
        return self._other


class _FakeGateway:
    def __init__(self, project_root: str, other_held=None):
        self.project_root = project_root
        self._registry = _FakeRegistry(other_held)


def _write_lock(
    root: Path,
    rel: str,
    owner: str,
    *,
    ts_offset: float = 0.0,
    ttl_s: float = 1800.0,
    pid: int = 999999,
    session_id: str = "",
) -> None:
    """模拟 lock_files 的磁盘锁（_sanitize_path 同款目录名 + owner.json 格式）。

    裁定#252：session_id 非空时写入 owner.json（锁存活=会话存活语义）。
    """
    normalized = str(Path(root) / rel)
    lock_dir = _fake_lock_dir(normalized, root)
    lock_dir.mkdir(parents=True, exist_ok=True)
    owner_file = lock_dir / "owner.json"
    now = time.time()
    payload = {
        "owner_id": owner,
        "pid": pid,
        "timestamp": now - ts_offset,
        "ttl_s": ttl_s,
        "expires_at": now - ts_offset + ttl_s,
    }
    if session_id:
        payload["session_id"] = session_id
    owner_file.write_text(json.dumps(payload), encoding="utf-8")


def _fake_lock_dir(normalized: str, root: Path) -> Path:
    """与 scripts/lock_files.py _sanitize_path 同款算法（root 锚定版）。"""
    rel = Path(normalized)
    try:
        rel = rel.relative_to(root)
    except ValueError:
        pass
    sanitized = str(rel).replace("\\", ".").replace("/", ".").replace("..", "_dotdot_")
    sanitized = "".join(c for c in sanitized if c.isalnum() or c in "._-")
    return root / ".ailocks" / (sanitized.lower()[:120] + ".lock")


def _run(tmp_path, files, session_id="xt4-attacker", other_held=None, allow_overlap=False):
    gate = make_held_overlap_gate()
    return gate.check(
        _FakeGateway(str(tmp_path), other_held),
        files,
        session_id=session_id,
        allow_overlap=allow_overlap,
    )


def test_ailocks_active_lock_blocks(tmp_path):
    _write_lock(tmp_path, FILE_A, "xt4-victim")
    ok, msg = _run(tmp_path, [FILE_A])
    assert not ok, "他会话 .ailocks 活跃锁必须阻断"
    assert "xt4-victim" in msg
    assert FILE_A in msg


def test_own_lock_passes(tmp_path):
    _write_lock(tmp_path, FILE_A, "xt4-attacker")
    ok, msg = _run(tmp_path, [FILE_A])
    assert ok, msg


def test_expired_lock_passes(tmp_path):
    _write_lock(tmp_path, FILE_A, "xt4-victim", ts_offset=1900.0, ttl_s=1800.0)
    ok, msg = _run(tmp_path, [FILE_A])
    assert ok, msg


def test_no_ailocks_dir_passes(tmp_path):
    ok, msg = _run(tmp_path, [FILE_A])
    assert ok, msg


def test_unrelated_lock_passes(tmp_path):
    _write_lock(tmp_path, "docs/other_file.py", "xt4-victim")
    ok, msg = _run(tmp_path, [FILE_A])
    assert ok, msg


def test_allow_overlap_still_escapes(tmp_path):
    _write_lock(tmp_path, FILE_A, "xt4-victim")
    gate = make_held_overlap_gate()
    ok, msg = gate.check(
        _FakeGateway(str(tmp_path)),
        [FILE_A],
        session_id="xt4-attacker",
        allow_overlap=True,
    )
    assert ok, msg


def test_held_files_path_still_blocks(tmp_path):
    # 既有第一轨不受影响：other_held_files 命中 → 阻断
    # （生产契约：files 恒为绝对路径——测试同步用绝对路径，与 resolve() 比对对齐）
    import os

    abs_file = os.path.abspath(Path(tmp_path) / FILE_A)
    ok, msg = _run(tmp_path, [abs_file], other_held={abs_file})
    assert not ok, "held_files 第一轨必须保持"
    assert "HELD_OVERLAP_VIOLATION" in msg


def test_helper_returns_holders_and_hits(tmp_path):
    _write_lock(tmp_path, FILE_A, "xt4-victim")
    holders, hits = _ailocks_other_holders(_FakeGateway(str(tmp_path)), [FILE_A], "xt4-attacker")
    assert holders == ["xt4-victim"]
    assert len(hits) == 1


# ── 裁定#252 语义：锁存活=会话存活 ───────────────────────


def test_session_bound_lock_alive_session_blocks(tmp_path, monkeypatch):
    """锁绑会话+会话存活（pid=0 心跳新鲜）→ 即使领取进程 PID 已死仍阻断（本 bug 回归测试）。"""
    import sys

    _write_lock(tmp_path, FILE_A, "xt4-victim", pid=111111, session_id="xt4-victim-sess")

    alive_info = SimpleNamespace(pid=0, last_heartbeat=time.time())

    class _FakeSessReg:
        def __init__(self, root):
            pass

        def get_session(self, sid):
            return alive_info if sid == "xt4-victim-sess" else None

    import zephyr.security.access_control.session_concurrency as sc_mod

    monkeypatch.setattr(sc_mod.SessionRegistry, "get_session", lambda self, sid: _FakeSessReg(str(tmp_path)).get_session(sid))
    holders, hits = _ailocks_other_holders(_FakeGateway(str(tmp_path)), [FILE_A], "xt4-attacker")
    assert holders == ["xt4-victim"], "瞬时 PID 死亡但会话存活 → 锁必须仍有效（裁定#252 核心）"
    assert len(hits) == 1


def test_session_bound_lock_dead_session_passes(tmp_path, monkeypatch):
    """锁绑会话+会话已死（心跳过期 90s+）→ 锁废，放行。"""
    _write_lock(tmp_path, FILE_A, "xt4-victim", pid=111111, session_id="xt4-dead-sess")

    dead_info = SimpleNamespace(pid=0, last_heartbeat=time.time() - 300)

    import zephyr.security.access_control.session_concurrency as sc_mod

    monkeypatch.setattr(sc_mod.SessionRegistry, "get_session", lambda self, sid: dead_info if sid == "xt4-dead-sess" else None)
    holders, hits = _ailocks_other_holders(_FakeGateway(str(tmp_path)), [FILE_A], "xt4-attacker")
    assert holders == [], "会话已死 → 锁必须作废"


# 裁定#252：_is_session_alive 判活真源——pid>0 双判活 / pid=0 心跳 90s
_is_session_alive = None
