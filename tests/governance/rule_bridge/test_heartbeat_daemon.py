# [BLUEPRINT] MOD-GOV_HEARTBEAT_DAEMON_TEST | tests/governance/rule_bridge/test_heartbeat_daemon.py | §Ruling-100PCT-AI-GOVERNANCE-P3-1
# [MODULE] tests.governance.rule_bridge.test_heartbeat_daemon
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.heartbeat_daemon; zephyr.gov_enforcement.rule_bridge.emergency_commit; zephyr.gov_enforcement.rule_bridge.session_worktree
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 临时目录隔离测试，不污染主仓库；不依赖真实 DB；不启动真实 daemon 进程
# [MODIFY-GUARD] 测试函数名与 heartbeat_daemon / emergency_commit / session_worktree API 对齐
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败→pytest assert error
# [TESTS] self
# [A_module] module_id=MOD-GOV_HEARTBEAT_DAEMON_TEST | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_heartbeat_daemon.py — heartbeat daemon + 成本递增 smoke test（Ruling:100PCT-AI-GOVERNANCE P3-1）

测试覆盖（P1-1 ~ P1-5）：
  1. heartbeat_file_path 路径格式
  2. cleanup_heartbeat_file 清理（文件存在 / 不存在 / 失败兜底）
  3. _append_heartbeat_log JSONL 追加（多记录）
  4. _session_in_registry 注册表查询（mock SessionRegistry）
  5. _classify_merge_failure 错误分类（deterministic / transient / unknown）
  6. _check_emergency_escalation 成本递增门禁（N<3 / N=3空reason / N>=5）
  7. _increment_emergency_count 计数递增 + block_next_start 阈值
  8. check_start_blocked 多 session 扫描
  9. run_daemon 生命周期 smoke（启动 → 心跳 → session 注销后退出）

测试策略：
  - 每个测试用独立临时目录（tmp_path），不污染主仓库
  - mock SessionRegistry 避免真实 DB 依赖
  - run_daemon 用短 interval（0.1s）+ session 立即注销 避免测试阻塞
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from zephyr.gov_enforcement.rule_bridge.emergency_commit import (
    _check_emergency_escalation,
    _increment_emergency_count,
    _read_emergency_count,
    _write_emergency_count,
    check_start_blocked,
)
from zephyr.gov_enforcement.rule_bridge.heartbeat_daemon import (
    _append_heartbeat_log,
    _session_in_registry,
    cleanup_heartbeat_file,
    heartbeat_file_path,
    run_daemon,
)
from zephyr.gov_enforcement.rule_bridge.session_worktree import _classify_merge_failure

# ---------------------------------------------------------------------------
# P1-1: heartbeat_daemon.py 单元测试
# ---------------------------------------------------------------------------


def test_heartbeat_file_path_format(tmp_path: Path) -> None:
    """heartbeat_file_path 返回正确格式 <root>/.runtime/sessions/<sid>/heartbeat.jsonl。"""
    p = heartbeat_file_path(tmp_path, "sess-test-001")
    assert p == tmp_path / ".runtime" / "sessions" / "sess-test-001" / "heartbeat.jsonl"


def test_cleanup_heartbeat_file_when_exists(tmp_path: Path) -> None:
    """cleanup_heartbeat_file 删除已存在的 heartbeat.jsonl，返回 True。"""
    hb = heartbeat_file_path(tmp_path, "sess-001")
    hb.parent.mkdir(parents=True, exist_ok=True)
    hb.write_text('{"ts":"2026-07-20T00:00:00Z","status":"started"}\n', encoding="utf-8")
    assert hb.exists()
    assert cleanup_heartbeat_file(tmp_path, "sess-001") is True
    assert not hb.exists()


def test_cleanup_heartbeat_file_when_not_exists(tmp_path: Path) -> None:
    """cleanup_heartbeat_file 文件不存在时返回 True（幂等）。"""
    assert cleanup_heartbeat_file(tmp_path, "sess-nonexistent") is True


def test_cleanup_heartbeat_file_preserves_emergency_count(tmp_path: Path) -> None:
    """cleanup_heartbeat_file 只删 heartbeat.jsonl，不删 emergency_count.json。"""
    sid = "sess-preserve-001"
    hb = heartbeat_file_path(tmp_path, sid)
    hb.parent.mkdir(parents=True, exist_ok=True)
    hb.write_text('{"status":"started"}\n', encoding="utf-8")
    emergency_file = hb.parent / "emergency_count.json"
    emergency_file.write_text('{"count":3}', encoding="utf-8")

    assert cleanup_heartbeat_file(tmp_path, sid) is True
    assert not hb.exists()
    assert emergency_file.exists(), "emergency_count.json must NOT be deleted by heartbeat cleanup"


def test_append_heartbeat_log_creates_file(tmp_path: Path) -> None:
    """_append_heartbeat_log 创建文件并写入首条记录。"""
    hb = heartbeat_file_path(tmp_path, "sess-log-001")
    _append_heartbeat_log(hb, "started", {"interval": 30})
    assert hb.exists()
    lines = hb.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert rec["status"] == "started"
    assert rec["interval"] == 30
    assert "ts" in rec and "pid" in rec


def test_append_heartbeat_log_appends_multiple(tmp_path: Path) -> None:
    """_append_heartbeat_log 多次调用追加记录（不覆盖）。"""
    hb = heartbeat_file_path(tmp_path, "sess-log-002")
    _append_heartbeat_log(hb, "started")
    _append_heartbeat_log(hb, "alive")
    _append_heartbeat_log(hb, "alive")
    _append_heartbeat_log(hb, "exited", {"reason": "session not in registry"})

    lines = hb.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 4
    statuses = [json.loads(line)["status"] for line in lines]
    assert statuses == ["started", "alive", "alive", "exited"]


# ---------------------------------------------------------------------------
# P1-1: _session_in_registry（mock SessionRegistry）
# ---------------------------------------------------------------------------


def test_session_in_registry_returns_true_when_present(tmp_path: Path) -> None:
    """session 在 registry 中时返回 True。"""
    class _FakeRegistry:
        def __init__(self, root):
            pass
        def get_session(self, sid):
            return {"session_id": sid}  # 非 None

    with patch(
        "zephyr.security.access_control.session_concurrency.SessionRegistry",
        _FakeRegistry,
    ):
        assert _session_in_registry("sess-001", tmp_path) is True


def test_session_in_registry_returns_false_when_absent(tmp_path: Path) -> None:
    """session 不在 registry 中时返回 False（daemon 应退出）。"""
    class _FakeRegistry:
        def __init__(self, root):
            pass
        def get_session(self, sid):
            return None

    with patch(
        "zephyr.security.access_control.session_concurrency.SessionRegistry",
        _FakeRegistry,
    ):
        assert _session_in_registry("sess-002", tmp_path) is False


def test_session_in_registry_returns_true_on_exception(tmp_path: Path) -> None:
    """registry 查询异常时返回 True（保守不退出，避免误判）。"""
    class _FakeRegistry:
        def __init__(self, root):
            raise RuntimeError("DB down")
        def get_session(self, sid):
            return None

    with patch(
        "zephyr.security.access_control.session_concurrency.SessionRegistry",
        _FakeRegistry,
    ):
        assert _session_in_registry("sess-003", tmp_path) is True


# ---------------------------------------------------------------------------
# P1-1: run_daemon 生命周期 smoke test
# ---------------------------------------------------------------------------


def test_run_daemon_lifecycle_smoke(tmp_path: Path) -> None:
    """run_daemon 生命周期：started → alive → exited（session 注销后退出）。

    用短 interval（0.05s）+ mock registry 立即返回 None，确保 1s 内退出。
    """
    call_count = {"n": 0}

    class _FakeRegistry:
        def __init__(self, root):
            pass
        def get_session(self, sid):
            call_count["n"] += 1
            # 第 1 次查询（_session_in_registry）：返回非 None（alive）
            # 第 2 次开始返回 None，让 daemon 退出
            if call_count["n"] == 1:
                return {"session_id": sid}
            return None
        def heartbeat(self, sid):
            pass

    with patch(
        "zephyr.security.access_control.session_concurrency.SessionRegistry",
        _FakeRegistry,
    ):
        # patch INITIAL_DELAY 和 interval 都缩短到 0.05s
        with patch(
            "zephyr.gov_enforcement.rule_bridge.heartbeat_daemon._INITIAL_DELAY", 0.05
        ), patch(
            "zephyr.gov_enforcement.rule_bridge.heartbeat_daemon._HEARTBEAT_INTERVAL", 0.05
        ):
            rc = run_daemon("sess-life-001", tmp_path, interval=0.05)

    assert rc == 0, "daemon 应正常退出（rc=0）"

    hb = heartbeat_file_path(tmp_path, "sess-life-001")
    assert hb.exists(), "heartbeat.jsonl 应被创建"
    lines = hb.read_text(encoding="utf-8").strip().splitlines()
    statuses = [json.loads(line)["status"] for line in lines]
    assert "started" in statuses, "应有 started 记录"
    assert "exited" in statuses, "应有 exited 记录（session 注销后）"


# ---------------------------------------------------------------------------
# #ARCH-HEARTBEAT-002: idle-timeout 退出（活性反转治本，2026-07-23）
# ---------------------------------------------------------------------------


def test_run_daemon_exits_on_idle_timeout(tmp_path: Path) -> None:
    """last_activity 超 idle 上限时 daemon 自动退出（消除僵尸 daemon 永久保活死 session）。

    场景：chat 异常关闭（未 merge/abort），session 无真实治理操作，last_activity
    停留在 4000s 前。daemon 首次循环即检测 idle > _MAX_IDLE_SECONDS(1800s)，
    停止心跳并退出——registry 条目 90s 后过期，held_files 自动释放。
    """
    class _FakeRegistry:
        def __init__(self, root):
            pass
        def get_session(self, sid):
            return {
                "session_id": sid,
                "last_activity": time.time() - 4000,  # idle 4000s > 1800s
                "start_time": time.time() - 5000,
            }
        def heartbeat(self, sid):
            pass

    with patch(
        "zephyr.security.access_control.session_concurrency.SessionRegistry",
        _FakeRegistry,
    ), patch(
        "zephyr.gov_enforcement.rule_bridge.heartbeat_daemon._INITIAL_DELAY", 0.05
    ), patch(
        "zephyr.gov_enforcement.rule_bridge.heartbeat_daemon._MAX_IDLE_SECONDS", 1800
    ):
        rc = run_daemon("sess-idle-001", tmp_path, interval=0.05)

    assert rc == 0, "daemon 应正常退出（rc=0）"
    hb = heartbeat_file_path(tmp_path, "sess-idle-001")
    recs = [json.loads(line) for line in hb.read_text(encoding="utf-8").strip().splitlines()]
    exited = [r for r in recs if r["status"] == "exited"]
    assert exited, "应有 exited 记录"
    assert exited[0]["reason"] == "idle timeout"
    assert "alive" not in [r["status"] for r in recs], "idle 退出发生在首次心跳前，不得有 alive 记录"


def test_run_daemon_keeps_alive_when_recent_activity(tmp_path: Path) -> None:
    """last_activity 新鲜时 daemon 正常心跳（不误杀活跃 session）。

    last_activity=now 的活跃 session：daemon 照常 heartbeat + alive 记录，
    直到 session 从 registry 注销后才以 "session not in registry" 退出。
    """
    calls = {"get": 0}

    class _FakeRegistry:
        def __init__(self, root):
            pass
        def get_session(self, sid):
            calls["get"] += 1
            # 前 2 次查询返回活跃 session（idle≈0），第 3 次返回 None 让 daemon 退出
            if calls["get"] >= 3:
                return None
            return {"session_id": sid, "last_activity": time.time()}
        def heartbeat(self, sid):
            pass

    with patch(
        "zephyr.security.access_control.session_concurrency.SessionRegistry",
        _FakeRegistry,
    ), patch(
        "zephyr.gov_enforcement.rule_bridge.heartbeat_daemon._INITIAL_DELAY", 0.05
    ):
        rc = run_daemon("sess-active-001", tmp_path, interval=0.05)

    assert rc == 0
    hb = heartbeat_file_path(tmp_path, "sess-active-001")
    recs = [json.loads(line) for line in hb.read_text(encoding="utf-8").strip().splitlines()]
    statuses = [r["status"] for r in recs]
    assert "alive" in statuses, "活跃 session 应有 alive 心跳记录"
    exited = [r for r in recs if r["status"] == "exited"]
    assert exited and exited[0]["reason"] == "session not in registry"


def test_session_idle_seconds_fallback_and_none(tmp_path: Path) -> None:
    """_session_idle_seconds：session 不存在返回 None；缺 last_activity 回退 start_time。"""
    from zephyr.gov_enforcement.rule_bridge.heartbeat_daemon import _session_idle_seconds

    class _NoneRegistry:
        def __init__(self, root):
            pass
        def get_session(self, sid):
            return None

    with patch(
        "zephyr.security.access_control.session_concurrency.SessionRegistry",
        _NoneRegistry,
    ):
        assert _session_idle_seconds("sess-none-001", tmp_path) is None

    class _LegacyRegistry:
        def __init__(self, root):
            pass
        def get_session(self, sid):
            # 修复前旧条目：无 last_activity，仅 start_time（绝不回退 last_heartbeat）
            return {"session_id": sid, "start_time": time.time() - 100}

    with patch(
        "zephyr.security.access_control.session_concurrency.SessionRegistry",
        _LegacyRegistry,
    ):
        idle = _session_idle_seconds("sess-legacy-001", tmp_path)
        assert idle is not None and idle >= 99, f"旧条目应回退 start_time 计算 idle，got {idle}"


# ---------------------------------------------------------------------------
# 真机回归（2026-08-19）：SessionRegistry 真接口 get_session——防 mock 盲区回潮
# （mock 万物皆有 .get，生产 AttributeError 被 except 吞掉致 12 僵尸 daemon 实证）
# ---------------------------------------------------------------------------


def test_session_queries_against_real_registry(tmp_path: Path) -> None:
    """真 SessionRegistry（非 mock）端到端：注册→查询→idle 计算→注销后两态。

    防回归锚点：若 SessionRegistry 接口再改名（get_session→他名），本测试立即红——
    mock 测试抓不到此类漂移（Mock 对任意方法名都返回真值）。
    """
    from zephyr.gov_enforcement.rule_bridge.heartbeat_daemon import (
        _session_idle_seconds,
        _session_in_registry,
    )
    from zephyr.security.access_control.session_concurrency import SessionRegistry

    # 真注册（register 刷新 last_activity=now）
    registry = SessionRegistry(tmp_path)
    registry.register("sess-real-001", pid=0)

    assert _session_in_registry("sess-real-001", tmp_path) is True
    idle = _session_idle_seconds("sess-real-001", tmp_path)
    assert idle is not None, "真 registry 注册后 idle 必须可计算（None=接口断裂回潮）"
    assert idle < 60, f"刚注册的 session idle 应接近 0，got {idle}"

    # 手工把 last_activity 改陈旧（模拟死 session：无治理操作 4000s）
    info = registry.get_session("sess-real-001")
    assert info is not None
    data = registry.load()
    data["sess-real-001"]["last_activity"] = info.start_time - 4000
    registry.save(data)
    idle_stale = _session_idle_seconds("sess-real-001", tmp_path)
    assert idle_stale is not None and idle_stale > 1800, (
        f"陈旧 session idle 应超 _MAX_IDLE_SECONDS(1800)，got {idle_stale}"
    )

    # 注销后两态
    registry.unregister("sess-real-001")
    assert _session_in_registry("sess-real-001", tmp_path) is False
    assert _session_idle_seconds("sess-real-001", tmp_path) is None


# ---------------------------------------------------------------------------
# P1-4: _classify_merge_failure 错误分类
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("error_text,expected", [
    # deterministic（不重试）
    ("automatic merge failed; fix conflicts", "deterministic"),
    ("CONFLICT (content): Merge conflict", "deterministic"),
    ("fatal: not something we can merge", "deterministic"),
    ("worktree 不存在", "deterministic"),
    ("session_id 不能为空", "deterministic"),
    # transient（重试）
    ("fatal: Unable to create index.lock", "transient"),
    ("another git process seems to be running", "transient"),
    ("error: could not lock config file", "transient"),
    ("TimeoutExpired: command timed out", "transient"),
    # unknown
    ("some weird error", "unknown"),
    ("", "unknown"),
    (None, "unknown"),
])
def test_classify_merge_failure(error_text, expected) -> None:
    """_classify_merge_failure 正确分类 deterministic / transient / unknown。"""
    assert _classify_merge_failure(error_text) == expected


# ---------------------------------------------------------------------------
# P1-5: emergency_commit 成本递增
# ---------------------------------------------------------------------------


def test_check_emergency_escalation_allowed_below_threshold(tmp_path: Path) -> None:
    """N<3 时允许提交（无 reason 也允许）。"""
    # 默认 count=0
    allowed, err = _check_emergency_escalation(tmp_path, "sess-ec-001", reason="")
    assert allowed is True
    assert err == ""


def test_check_emergency_escalation_requires_reason_at_threshold(tmp_path: Path) -> None:
    """N>=3 且 reason 为空时拒绝（强制说明原因）。"""
    _write_emergency_count(tmp_path, "sess-ec-002", {"count": 3, "block_next_start": False})
    allowed, err = _check_emergency_escalation(tmp_path, "sess-ec-002", reason="")
    assert allowed is False
    assert "必须提供非空 reason" in err


def test_check_emergency_escalation_allows_with_reason_at_threshold(tmp_path: Path) -> None:
    """N>=3 且 reason 非空时允许。"""
    _write_emergency_count(tmp_path, "sess-ec-003", {"count": 3, "block_next_start": False})
    allowed, err = _check_emergency_escalation(tmp_path, "sess-ec-003", reason="GW 锁死")
    assert allowed is True
    assert err == ""


def test_check_emergency_escalation_blocks_at_block_threshold(tmp_path: Path) -> None:
    """N>=5 时无条件拒绝（必须先调查根因）。"""
    _write_emergency_count(tmp_path, "sess-ec-004", {"count": 5, "block_next_start": True})
    allowed, err = _check_emergency_escalation(tmp_path, "sess-ec-004", reason="GW 锁死")
    assert allowed is False
    assert "阻断本次提交" in err


def test_increment_emergency_count_below_block_threshold(tmp_path: Path) -> None:
    """N+1 < 5 时不设置 block_next_start。"""
    _write_emergency_count(tmp_path, "sess-ec-005", {"count": 2, "block_next_start": False})
    new_count = _increment_emergency_count(tmp_path, "sess-ec-005")
    assert new_count == 3
    data = _read_emergency_count(tmp_path, "sess-ec-005")
    assert data["count"] == 3
    assert data["block_next_start"] is False, "N=3 不应阻断"


def test_increment_emergency_count_sets_block_at_threshold(tmp_path: Path) -> None:
    """N+1 >= 5 时设置 block_next_start=True。"""
    _write_emergency_count(tmp_path, "sess-ec-006", {"count": 4, "block_next_start": False})
    new_count = _increment_emergency_count(tmp_path, "sess-ec-006")
    assert new_count == 5
    data = _read_emergency_count(tmp_path, "sess-ec-006")
    assert data["count"] == 5
    assert data["block_next_start"] is True, "N=5 应阻断下次 session_worktree_start"


def test_increment_emergency_count_starts_from_zero(tmp_path: Path) -> None:
    """文件不存在时从 count=0 开始递增。"""
    new_count = _increment_emergency_count(tmp_path, "sess-ec-007")
    assert new_count == 1
    data = _read_emergency_count(tmp_path, "sess-ec-007")
    assert data["count"] == 1
    assert data["block_next_start"] is False


# ---------------------------------------------------------------------------
# P1-5: check_start_blocked 多 session 扫描
# ---------------------------------------------------------------------------


def test_check_start_blocked_no_sessions_dir(tmp_path: Path) -> None:
    """emergency_counts 目录不存在时返回 (False, '')。"""
    blocked, reason = check_start_blocked(tmp_path)
    assert blocked is False
    assert reason == ""


def test_check_start_blocked_no_block(tmp_path: Path) -> None:
    """所有 agent bucket 都未阻断时返回 (False, '')。"""
    _write_emergency_count(tmp_path, "agent-001", {"count": 2, "block_next_start": False})
    _write_emergency_count(tmp_path, "agent-002", {"count": 4, "block_next_start": False})

    blocked, reason = check_start_blocked(tmp_path)
    assert blocked is False
    assert reason == ""


def test_check_start_blocked_detects_blocked_session(tmp_path: Path) -> None:
    """任一 agent bucket block_next_start=True 时返回 (True, reason)。"""
    _write_emergency_count(tmp_path, "agent-001", {"count": 2, "block_next_start": False})
    _write_emergency_count(tmp_path, "agent-bad", {"count": 5, "block_next_start": True})

    blocked, reason = check_start_blocked(tmp_path)
    assert blocked is True
    assert "agent-bad" in reason
    assert "5" in reason


def test_check_start_blocked_skips_corrupt_json(tmp_path: Path) -> None:
    """损坏的 JSON 文件被跳过（不阻断扫描）。"""
    counts_dir = tmp_path / ".runtime" / "emergency_counts"
    counts_dir.mkdir(parents=True)
    (counts_dir / "agent-corrupt.json").write_text(
        'not valid json {{{', encoding="utf-8"
    )

    blocked, reason = check_start_blocked(tmp_path)
    assert blocked is False
    assert reason == ""


# ---------------------------------------------------------------------------
# P1-3 + P1-5 集成场景：cleanup_heartbeat_file 不影响 check_start_blocked
# ---------------------------------------------------------------------------


def test_cleanup_heartbeat_does_not_clear_block(tmp_path: Path) -> None:
    """cleanup_heartbeat_file 删 heartbeat.jsonl 后，emergency_count.json 仍生效。

    场景：session_worktree_abort 后 heartbeat.jsonl 被清理，
    但 emergency_count.json 保留（计数持久化）。
    若 block_next_start=True，下次 check_start_blocked 仍应阻断。
    """
    sid = "sess-integration-001"
    hb = heartbeat_file_path(tmp_path, sid)
    hb.parent.mkdir(parents=True, exist_ok=True)
    hb.write_text('{"status":"started"}\n', encoding="utf-8")
    _write_emergency_count(tmp_path, sid, {"count": 5, "block_next_start": True})

    # cleanup heartbeat.jsonl
    assert cleanup_heartbeat_file(tmp_path, sid) is True
    assert not hb.exists()

    # emergency_count.json 仍存在并阻断
    blocked, reason = check_start_blocked(tmp_path)
    assert blocked is True
    assert sid in reason


# ---------------------------------------------------------------------------
# CAND-DAEMON-001: worktree 失锚自退（2026-08-17，根治孤儿 daemon 假活性）
# ---------------------------------------------------------------------------


def test_worktree_anchor_alive_semantics(tmp_path: Path) -> None:
    """_worktree_anchor_alive：None/空串=未配置锚保守存活；存在目录=True；消失=False。"""
    from zephyr.gov_enforcement.rule_bridge.heartbeat_daemon import _worktree_anchor_alive

    assert _worktree_anchor_alive(None) is True, "未配置锚（旧 spawn 兼容）应保守存活"
    assert _worktree_anchor_alive("") is True, "空串锚应保守存活"
    assert _worktree_anchor_alive(tmp_path) is True, "存在目录应存活"
    assert _worktree_anchor_alive(tmp_path / "gone") is False, "消失目录应失锚"


def test_run_daemon_exits_on_worktree_anchor_lost(tmp_path: Path) -> None:
    """worktree 锚点目录不存在时 daemon 失锚自退（reason=worktree anchor lost）。

    场景（#99 族实证）：session registry 条目残留（2 个两天残留 daemon），
    但所属 worktree 早已退役删除——daemon 空转制造假活性。
    失锚自退：首次循环即检测锚点缺失，停止心跳并退出。
    """
    class _FakeRegistry:
        def __init__(self, root):
            pass
        def get_session(self, sid):
            # registry 条目残留且活性新鲜——若无锚点检查 daemon 会永久空转
            return {"session_id": sid, "last_activity": time.time()}
        def heartbeat(self, sid):
            pass

    missing_wt = tmp_path / "retired_worktree"  # 从不创建=已退役删除
    with patch(
        "zephyr.security.access_control.session_concurrency.SessionRegistry",
        _FakeRegistry,
    ), patch(
        "zephyr.gov_enforcement.rule_bridge.heartbeat_daemon._INITIAL_DELAY", 0.05
    ):
        rc = run_daemon(
            "sess-anchor-001", tmp_path, interval=0.05, worktree_path=missing_wt,
        )

    assert rc == 0, "daemon 应正常退出（rc=0）"
    hb = heartbeat_file_path(tmp_path, "sess-anchor-001")
    recs = [json.loads(line) for line in hb.read_text(encoding="utf-8").strip().splitlines()]
    exited = [r for r in recs if r["status"] == "exited"]
    assert exited, "应有 exited 记录"
    assert exited[0]["reason"] == "worktree anchor lost"
    assert exited[0]["worktree_path"] == str(missing_wt)
    assert "alive" not in [r["status"] for r in recs], "失锚退出发生在首次心跳前，不得有 alive 记录"


def test_run_daemon_anchor_present_no_false_exit(tmp_path: Path) -> None:
    """锚点目录存活时 daemon 不误退出（活跃 session 正常心跳直至 registry 注销）。

    红队反向验证：失锚检查不得误杀锚点存活的活跃 session——alive 心跳照常，
    最终退出原因必须是 registry 注销而非 anchor lost。
    """
    calls = {"get": 0}

    class _FakeRegistry:
        def __init__(self, root):
            pass
        def get_session(self, sid):
            calls["get"] += 1
            if calls["get"] >= 3:
                return None
            return {"session_id": sid, "last_activity": time.time()}
        def heartbeat(self, sid):
            pass

    alive_wt = tmp_path / "active_worktree"
    alive_wt.mkdir()  # 锚点存活
    with patch(
        "zephyr.security.access_control.session_concurrency.SessionRegistry",
        _FakeRegistry,
    ), patch(
        "zephyr.gov_enforcement.rule_bridge.heartbeat_daemon._INITIAL_DELAY", 0.05
    ):
        rc = run_daemon(
            "sess-anchor-002", tmp_path, interval=0.05, worktree_path=alive_wt,
        )

    assert rc == 0
    hb = heartbeat_file_path(tmp_path, "sess-anchor-002")
    recs = [json.loads(line) for line in hb.read_text(encoding="utf-8").strip().splitlines()]
    statuses = [r["status"] for r in recs]
    assert "alive" in statuses, "锚点存活的活跃 session 应有 alive 心跳记录"
    exited = [r for r in recs if r["status"] == "exited"]
    assert exited and exited[0]["reason"] == "session not in registry", \
        "退出原因必须是 registry 注销，不得是 worktree anchor lost"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
