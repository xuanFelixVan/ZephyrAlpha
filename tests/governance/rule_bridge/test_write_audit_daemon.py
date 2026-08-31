# [BLUEPRINT] MOD-GOV_DRIFT_WATCHDOG | (auto-injected by S4 reconciler) | §
# [A_module] module_id=MOD-GOV_DRIFT_WATCHDOG | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [MODULE] tests.governance.rule_bridge.test_write_audit_daemon
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.write_audit_daemon
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 事件五要素+三层归因正确性；热目录集边界不破；带外写删 5s 内落盘可归因
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest assert
# [TESTS] self
"""test_write_audit_daemon.py — WriteAudit 守护 MVP 单测（#ARCH-279 裁定B1/B2）

覆盖：hash 助手/session 映射/归因匹配/事件落盘全操作族/告警联动查询/单实例锁。
进程快照与注册表读取经 monkeypatch 隔离宿主环境。
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest

from zephyr.gov_enforcement.rule_bridge import write_audit_daemon as wad


@pytest.fixture()
def root(tmp_path: Path) -> Path:
    """仿真仓根：建热目录集+仓根热文件。"""
    (tmp_path / "docs/01_policies_and_standards/_registry/catalogs").mkdir(parents=True)
    (tmp_path / "docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos").mkdir(parents=True)
    (tmp_path / ".runtime/quarantine").mkdir(parents=True)
    (tmp_path / "AGENTS.md").write_text("rules", encoding="utf-8")
    (tmp_path / "docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml").write_text(
        "v: 1", encoding="utf-8"
    )
    return tmp_path


@pytest.fixture()
def handler(root: Path, monkeypatch: pytest.MonkeyPatch) -> wad.WriteAuditHandler:
    """隔离宿主进程/注册表的 handler（快照与归因确定性）。"""
    monkeypatch.setattr(
        wad, "_snapshot_processes", lambda: [{"pid": 4242, "name": "python.exe", "cmdline": "python x"}]
    )
    return wad.WriteAuditHandler(root)


def _write_registry(root: Path, entries: dict) -> None:
    (root / ".runtime").mkdir(parents=True, exist_ok=True)
    (root / ".runtime/session_registry.json").write_text(json.dumps(entries), encoding="utf-8")


class TestHashAndCache:
    def test_sha256_stable_and_missing(self, root: Path) -> None:
        p = root / "AGENTS.md"
        assert wad._sha256_file(p) == wad._sha256_file(p)
        assert wad._sha256_file(root / "nonexistent.md") is None

    def test_prime_cache_covers_watch_specs(self, handler: wad.WriteAuditHandler) -> None:
        """基准扫描覆盖热目录集：注册表目录文件+仓根平铺热文件均入缓存。"""
        assert "docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml" in handler._hash_cache
        assert "AGENTS.md" in handler._hash_cache  # 仓根平铺（非递归）

    def test_rel_posix(self, root: Path) -> None:
        assert wad._rel(root / "docs/x.md", root) == "docs/x.md"


class TestSessionAttribution:
    def test_session_map_pid_hit_and_stale(self, root: Path) -> None:
        now = time.time()
        _write_registry(
            root,
            {
                "sess-live": {"pid": 100, "last_heartbeat": now - 5},
                "sess-stale": {"pid": 200, "last_heartbeat": now - 9999},
                "sess-nopid": {"last_heartbeat": now},
            },
        )
        m = wad._load_session_map(root)
        assert m[100]["session_id"] == "sess-live" and m[100]["stale"] is False
        assert m[200]["stale"] is True
        assert len(m) == 2  # 无 pid 条目被跳过

    def test_session_map_missing_registry(self, root: Path) -> None:
        assert wad._load_session_map(root) == {}

    def test_attribute_sessions_matches(self) -> None:
        snapshot = [{"pid": 100, "name": "python.exe", "cmdline": "a"}, {"pid": 999, "name": "cmd.exe", "cmdline": "b"}]
        smap = {100: {"session_id": "sess-x", "stale": False, "heartbeat_age_s": 3.0}}
        hits = wad._attribute_sessions(snapshot, smap)
        assert len(hits) == 1 and hits[0]["session_id"] == "sess-x"


class TestEventRecording:
    def _read_events(self, root: Path) -> list[dict]:
        audit = root / ".runtime/audit/write_audit.jsonl"
        if not audit.is_file():
            return []
        return [json.loads(ln) for ln in audit.read_text(encoding="utf-8").splitlines() if ln.strip()]

    def test_write_event_five_elements(self, handler: wad.WriteAuditHandler, root: Path, monkeypatch) -> None:
        """写事件：五要素（ts/path/op/前后hash/归因）齐备。"""
        monkeypatch.setattr(
            wad,
            "_load_session_map",
            lambda _r: {4242: {"session_id": "sess-w", "stale": False, "heartbeat_age_s": 1.0}},
        )
        target = root / "docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml"
        target.write_text("v: 2", encoding="utf-8")
        rec = handler.record("write", target)
        assert rec["op"] == "write"
        assert rec["path"].endswith("factor_registry.yaml")
        assert rec["hash_before"] is not None and rec["hash_after"] is not None
        assert rec["hash_before"] != rec["hash_after"]
        assert rec["sessions"][0]["session_id"] == "sess-w"
        assert rec["exact_attribution"] is False
        events = self._read_events(root)
        assert len(events) == 1 and events[0]["path"] == rec["path"]

    def test_create_and_delete_lifecycle(self, handler: wad.WriteAuditHandler, root: Path) -> None:
        """create：hash_before=None；delete：hash_after=None 且缓存清除。"""
        target = root / ".runtime/quarantine/drift_x.json"
        handler.record("create", target)
        target.write_text("snap", encoding="utf-8")
        rec_del = handler.record("delete", target)
        assert rec_del["hash_after"] is None
        assert ".runtime/quarantine/drift_x.json" not in handler._hash_cache

    def test_rename_records_dest(self, handler: wad.WriteAuditHandler, root: Path) -> None:
        src = root / "AGENTS.md"
        dst = root / "AGENTS.bak.md"
        rec = handler.record("rename", src, dest_path=dst)
        assert rec["op"] == "rename" and rec["dest_path"] == "AGENTS.bak.md"
        assert "AGENTS.bak.md" in handler._hash_cache


class TestHashResilience:
    """#ARCH-306（2026-08-31）：_sha256_file 大文件/异常容错（08-31 MemoryError 实证裂缝）。"""

    def test_oversized_file_returns_none_not_crash(self, root: Path) -> None:
        """超过大小上限的文件：跳过 hash 返回 None，不抛异常（防 RDCW 回调线程炸死）。"""
        big = root / "big.bin"
        big.write_bytes(b"x" * 1024)  # 实际内容不重要，monkeypatch 压上限
        monkeypatch_limit = 512  # 压上限模拟"大文件"判定路径
        import zephyr.gov_enforcement.rule_bridge.write_audit_daemon as _wad

        orig = _wad._HASH_MAX_BYTES
        _wad._HASH_MAX_BYTES = monkeypatch_limit
        try:
            oversized = root / "oversized.bin"
            oversized.write_bytes(b"y" * (monkeypatch_limit + 1))
            assert _wad._sha256_file(oversized) is None
            # 上限内文件照常 hash
            small = root / "small.bin"
            small.write_bytes(b"z" * 100)
            assert _wad._sha256_file(small) is not None
        finally:
            _wad._HASH_MAX_BYTES = orig

    def test_read_error_returns_none(self, root: Path) -> None:
        """读取期非 OSError 异常（如 MemoryError）→ None 不炸（fail-open 取证语义）。"""
        import zephyr.gov_enforcement.rule_bridge.write_audit_daemon as _wad

        p = root / "AGENTS.md"
        orig_open = _wad.open if hasattr(_wad, "open") else open

        def _boom(*_a, **_kw):
            raise MemoryError("simulated")

        _wad_open_backup = _wad.__dict__.get("open")
        _wad.open = _boom  # type: ignore[attr-defined]
        try:
            assert _wad._sha256_file(p) is None
        finally:
            if _wad_open_backup is not None:
                _wad.open = _wad_open_backup  # type: ignore[attr-defined]
            else:
                del _wad.open  # type: ignore[attr-defined]
        _ = orig_open


class TestRecentEventsFor:
    def test_filter_by_path_time_limit(self, root: Path) -> None:
        audit_dir = root / ".runtime/audit"
        audit_dir.mkdir(parents=True)
        now = time.time()
        rows = [
            {"ts": now - 300, "path": "a.md", "op": "write"},
            {"ts": now - 5, "path": "a.md", "op": "write", "sessions": [{"session_id": "s1"}]},
            {"ts": now - 2, "path": "b.md", "op": "delete"},
            {"ts": now - 1, "path": "a.md", "op": "delete", "sessions": [{"session_id": "s2"}]},
        ]
        (audit_dir / "write_audit.jsonl").write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
        hits = wad.recent_events_for("a.md", 60, root)
        assert [h["op"] for h in hits] == ["delete", "write"]  # 新→旧
        assert hits[0]["sessions"][0]["session_id"] == "s2"
        limited = wad.recent_events_for("a.md", 60, root, limit=1)
        assert len(limited) == 1

    def test_missing_audit_file(self, root: Path) -> None:
        assert wad.recent_events_for("x.md", 60, root) == []


class TestSuspectSummary:
    """#ARCH-279 裁定B2：告警联动嫌疑摘要（drift watchdog 调用面）。"""

    def _seed(self, root: Path, rows: list[dict]) -> None:
        audit_dir = root / ".runtime/audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        (audit_dir / "write_audit.jsonl").write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")

    def test_session_hit_format(self, root: Path) -> None:
        """有会话命中：`sess(pid,op)` 紧凑格式；stale 带标记。"""
        now = time.time()
        self._seed(
            root,
            [
                {
                    "ts": now - 3,
                    "path": "a.md",
                    "op": "write",
                    "sessions": [{"session_id": "sess-x", "pid": 100, "stale": False}],
                },
                {
                    "ts": now - 1,
                    "path": "a.md",
                    "op": "delete",
                    "sessions": [{"session_id": "sess-y", "pid": 200, "stale": True}],
                },
            ],
        )
        summary = wad.suspect_summary("a.md", root)
        assert "sess-y(pid=200,delete,stale)" in summary
        assert "sess-x(pid=100,write)" in summary

    def test_no_session_but_processes(self, root: Path) -> None:
        """无会话命中→在场进程名清单（带外终端直删场景）。"""
        self._seed(
            root,
            [
                {
                    "ts": time.time() - 1,
                    "path": "a.md",
                    "op": "delete",
                    "sessions": [],
                    "processes": [{"name": "cmd.exe"}, {"name": "python.exe"}],
                }
            ],
        )
        summary = wad.suspect_summary("a.md", root)
        assert "无会话命中" in summary and "cmd.exe" in summary

    def test_no_events_empty(self, root: Path) -> None:
        assert wad.suspect_summary("ghost.md", root) == ""


class TestDaemonGuards:
    def test_single_instance_lock_exclusive(self, root: Path) -> None:
        fh1 = wad._acquire_single_instance_lock(root)
        assert fh1 is not None
        try:
            assert wad._acquire_single_instance_lock(root) is None
        finally:
            fh1.close()

    def test_ensure_daemon_skips_pytest(self, root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("PYTEST_CURRENT_TEST", "x")
        assert wad.ensure_daemon(root) is True
        assert not wad._pid_path(root).exists()

    def test_status_shape(self, root: Path) -> None:
        st = wad._status(root)
        assert set(st) >= {"alive", "pid", "audit_file", "audit_bytes"}
        assert st["alive"] is False
