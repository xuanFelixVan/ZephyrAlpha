# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_depgraph_freshness_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_depgraph_freshness_gate.py — DEPGRAPH-FRESHNESS 门禁单测

权威依据：depgraph_freshness_gate.py
（make_depgraph_freshness_gate，#ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 3.1）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestParseSavedAt: ISO 时间戳解析（带时区/无时区/空值/非法值）
- TestCheckDualThreshold: mock gateway + tmp .runtime/depgraph_scan_cache.json
  - cache 缺失 → 放行（fail-open）
  - JSON 解析失败 → 放行（fail-open）
  - _meta.saved_at 缺失 → 放行（fail-open）
  - saved_at 不可解析 → 放行（fail-open）
  - fresh（< 30min）→ 放行
  - WARN（30min ~ 24h）→ 放行 + warning
  - BLOCK（> 24h）→ 阻断
  - saved_at 在未来（时钟漂移）→ 放行
- TestLinkedWorktreeAuthoritativeCache: linked worktree 内锚定态权威副本解析（#ARCH-324 实证③）
  - wt 副本陈旧 + 主树新鲜 → 放行（落地面假红治本）
  - 主树陈旧 + wt 植入新鲜副本 → 阻断（禁逃逸）
  - 主树副本缺失 → 回落本地副本（既有 fail-open 面不放松）
  - gitdir 相对 / 非法 / 无 .git 祖先 → 不误指他处

测试隔离：tmp_path fixture 提供 project_root，每个测试独立 .runtime/ 目录。
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates.depgraph_freshness_gate import (  # noqa: E402
    _main_worktree_root,
    _parse_saved_at,
    _resolve_cache_path,
    make_depgraph_freshness_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


def _make_gateway(project_root: Path) -> MagicMock:
    """构造 mock gateway：仅暴露 project_root 属性（depgraph_freshness_gate 不调用 _run_git）。"""
    gw = MagicMock()
    gw.project_root = project_root
    return gw


def _write_cache(project_root: Path, saved_at: str | None) -> None:
    """写入 .runtime/depgraph_scan_cache.json，含 _meta.saved_at。"""
    cache_dir = project_root / ".runtime"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / "depgraph_scan_cache.json"
    data = {"_meta": {}} if saved_at is None else {"_meta": {"saved_at": saved_at}}
    cache_path.write_text(json.dumps(data), encoding="utf-8")


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------


class TestGateSpecFields:
    """gate_id / priority / isinstance(GateSpec)。"""

    def test_gate_id(self) -> None:
        gate = make_depgraph_freshness_gate()
        assert gate.gate_id == "DEPGRAPH-FRESHNESS"

    def test_priority(self) -> None:
        gate = make_depgraph_freshness_gate()
        assert gate.priority == 67

    def test_is_gate_spec(self) -> None:
        gate = make_depgraph_freshness_gate()
        assert isinstance(gate, GateSpec)


# ---------------------------------------------------------------------------
# TestParseSavedAt
# ---------------------------------------------------------------------------


class TestParseSavedAt:
    """_parse_saved_at ISO 时间戳解析。"""

    def test_with_timezone(self) -> None:
        dt = _parse_saved_at("2026-07-18T12:00:00+00:00")
        assert dt is not None
        assert dt.tzinfo == timezone.utc

    def test_without_timezone(self) -> None:
        """无时区 ISO 时间戳——按本地时间解析后转 UTC。"""
        dt = _parse_saved_at("2026-07-18T12:00:00")
        assert dt is not None
        assert dt.tzinfo == timezone.utc

    def test_empty_string(self) -> None:
        assert _parse_saved_at("") is None

    def test_none_like(self) -> None:
        assert _parse_saved_at(None) is None  # type: ignore[arg-type]

    def test_unparseable(self) -> None:
        assert _parse_saved_at("not-a-timestamp") is None


# ---------------------------------------------------------------------------
# TestCheckDualThreshold
# ---------------------------------------------------------------------------


class TestCheckDualThreshold:
    """_check 闭包 dual-threshold 检测逻辑（mock gateway + tmp cache）。"""

    def test_cache_missing_passes(self, tmp_path: Path) -> None:
        """cache 文件缺失 → 放行（fail-open，首次启动/新环境）。"""
        gw = _make_gateway(tmp_path)
        gate = make_depgraph_freshness_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True
        assert "not found" in detail or "skip" in detail.lower()

    def test_json_parse_error_passes(self, tmp_path: Path) -> None:
        """JSON 解析失败 → 放行（fail-open）。"""
        cache_dir = tmp_path / ".runtime"
        cache_dir.mkdir(parents=True)
        (cache_dir / "depgraph_scan_cache.json").write_text("{invalid json", encoding="utf-8")
        gw = _make_gateway(tmp_path)
        gate = make_depgraph_freshness_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True
        assert "parse failed" in detail.lower() or "skip" in detail.lower()

    def test_saved_at_missing_passes(self, tmp_path: Path) -> None:
        """_meta.saved_at 缺失 → 放行（fail-open）。"""
        _write_cache(tmp_path, saved_at=None)
        gw = _make_gateway(tmp_path)
        gate = make_depgraph_freshness_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True
        assert "saved_at" in detail or "skip" in detail.lower()

    def test_saved_at_unparseable_passes(self, tmp_path: Path) -> None:
        """saved_at 不可解析 → 放行（fail-open）。"""
        _write_cache(tmp_path, saved_at="not-a-timestamp")
        gw = _make_gateway(tmp_path)
        gate = make_depgraph_freshness_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True
        assert "unparseable" in detail.lower() or "skip" in detail.lower()

    def test_fresh_passes(self, tmp_path: Path) -> None:
        """fresh（< 30min）→ 放行。"""
        recent = (datetime.now(timezone.utc) - timedelta(seconds=60)).isoformat()
        _write_cache(tmp_path, saved_at=recent)
        gw = _make_gateway(tmp_path)
        gate = make_depgraph_freshness_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True
        assert "fresh" in detail.lower()

    def test_warn_passes_with_warning(self, tmp_path: Path) -> None:
        """WARN（30min ~ 24h）→ 放行 + warning。"""
        recent = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        _write_cache(tmp_path, saved_at=recent)
        gw = _make_gateway(tmp_path)
        gate = make_depgraph_freshness_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True
        assert "WARN" in detail or "warn" in detail.lower()

    def test_block_blocks(self, tmp_path: Path) -> None:
        """BLOCK（> 24h）→ 阻断。"""
        stale = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
        _write_cache(tmp_path, saved_at=stale)
        gw = _make_gateway(tmp_path)
        gate = make_depgraph_freshness_gate()
        passed, detail = gate.check(gw, [])
        assert passed is False
        assert "24h" in detail or "stale" in detail.lower()

    def test_future_timestamp_passes(self, tmp_path: Path) -> None:
        """saved_at 在未来（时钟漂移）→ 放行。"""
        future = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        _write_cache(tmp_path, saved_at=future)
        gw = _make_gateway(tmp_path)
        gate = make_depgraph_freshness_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True
        assert "future" in detail.lower() or "fresh" in detail.lower()


# ---------------------------------------------------------------------------
# TestPgOfflineExemption（tracker #116 B2，#ARCH-119，报告 §1.3 联动修复）
# ---------------------------------------------------------------------------


def _write_probe_state(project_root: Path, *, offline_hours: float | None) -> None:
    """写入探针状态文件。offline_hours=None 表示在线；否则离线时长（小时）。"""
    now = datetime.now(timezone.utc)
    if offline_hours is None:
        state = {
            "reachable": True,
            "checked_at": now.isoformat(),
            "host": "localhost",
            "port": 5432,
            "error": "",
            "last_reachable_at": now.isoformat(),
            "first_offline_at": None,
        }
    else:
        state = {
            "reachable": False,
            "checked_at": now.isoformat(),
            "host": "localhost",
            "port": 5432,
            "error": "refused",
            "last_reachable_at": None,
            "first_offline_at": (now - timedelta(hours=offline_hours)).isoformat(),
        }
    path = project_root / ".runtime" / "pg_probe_state.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state), encoding="utf-8")


def _read_log_rows(project_root: Path) -> list[tuple]:
    import sqlite3 as _sqlite3

    db_path = project_root / "data" / "databases" / "governance.db"
    if not db_path.is_file():
        return []
    conn = _sqlite3.connect(str(db_path))
    try:
        return conn.execute("SELECT gate_id, action, detail FROM reconcile_execution_log").fetchall()
    finally:
        conn.close()


class TestPgOfflineExemption:
    """探针证实 PG 离线超 24h → saved_at 停更豁免阻断 + 留痕。"""

    def test_offline_over_24h_exempts_block(self, tmp_path: Path) -> None:
        """saved_at 停更 48h + 探针离线 30h → 豁免阻断（放行）+ critical_warn 落盘。"""
        stale = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
        _write_cache(tmp_path, saved_at=stale)
        _write_probe_state(tmp_path, offline_hours=30)
        gw = _make_gateway(tmp_path)
        gate = make_depgraph_freshness_gate()
        passed, detail = gate.check(gw, [], session_id="sess-t")
        assert passed is True
        assert "exempted" in detail
        rows = _read_log_rows(tmp_path)
        assert len(rows) == 1
        assert rows[0][0] == "DEPGRAPH-FRESHNESS"
        assert rows[0][1] == "critical_warn"
        assert "DB 离线降级" in rows[0][2]

    def test_offline_under_24h_still_blocks(self, tmp_path: Path) -> None:
        """saved_at 停更 48h + 探针离线仅 1h（<24h）→ 不豁免，维持阻断。"""
        stale = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
        _write_cache(tmp_path, saved_at=stale)
        _write_probe_state(tmp_path, offline_hours=1)
        gw = _make_gateway(tmp_path)
        gate = make_depgraph_freshness_gate()
        passed, detail = gate.check(gw, [])
        assert passed is False
        assert "24h" in detail or "stale" in detail.lower()

    def test_probe_online_still_blocks(self, tmp_path: Path) -> None:
        """saved_at 停更 48h + 探针在线 → 不豁免，维持阻断。"""
        stale = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
        _write_cache(tmp_path, saved_at=stale)
        _write_probe_state(tmp_path, offline_hours=None)
        gw = _make_gateway(tmp_path)
        gate = make_depgraph_freshness_gate()
        passed, detail = gate.check(gw, [])
        assert passed is False

    def test_probe_missing_still_blocks(self, tmp_path: Path) -> None:
        """saved_at 停更 48h + 无探针状态 → 不豁免，维持阻断。"""
        stale = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
        _write_cache(tmp_path, saved_at=stale)
        gw = _make_gateway(tmp_path)
        gate = make_depgraph_freshness_gate()
        passed, detail = gate.check(gw, [])
        assert passed is False


# ---------------------------------------------------------------------------
# TestLinkedWorktreeAuthoritativeCache（#ARCH-324 实证③：落地面锚定态被 worktree 钉死）
# ---------------------------------------------------------------------------


def _make_linked_worktree(tmp_path: Path) -> tuple[Path, Path]:
    """构造 主工作树 + linked worktree（.git 为 gitdir 指针文件）。"""
    main = tmp_path / "main"
    (main / ".git" / "worktrees" / "wt").mkdir(parents=True)
    wt = tmp_path / "wt"
    (wt / ".runtime").mkdir(parents=True, exist_ok=True)
    (wt / ".git").write_text(
        f"gitdir: {main / '.git' / 'worktrees' / 'wt'}\n", encoding="utf-8"
    )
    return main, wt


def _fresh_ts() -> str:
    return (datetime.now(timezone.utc) - timedelta(seconds=60)).isoformat()


def _stale_ts() -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()


class TestLinkedWorktreeAuthoritativeCache:
    """linked worktree 内以主工作树副本为权威：假红治本 + 逃逸封堵 + fail-open 面不放松。"""

    def test_main_worktree_root_resolved(self, tmp_path: Path) -> None:
        """linked worktree → 主树根；主树自身（.git 是目录）→ None。"""
        main, wt = _make_linked_worktree(tmp_path)
        assert _main_worktree_root(wt) == main
        assert _main_worktree_root(main) is None

    def test_stale_local_fresh_main_passes(self, tmp_path: Path) -> None:
        """落地 worktree 副本停更 48h、主树新鲜 → 放行（假红治本，实证 33 件死信）。"""
        main, wt = _make_linked_worktree(tmp_path)
        _write_cache(main, saved_at=_fresh_ts())
        _write_cache(wt, saved_at=_stale_ts())
        path, src = _resolve_cache_path(wt)
        assert src == "main-worktree"
        assert path == main / ".runtime" / "depgraph_scan_cache.json"
        gate = make_depgraph_freshness_gate()
        passed, detail = gate.check(_make_gateway(wt), [])
        assert passed is True, detail
        assert "source=main-worktree" in detail

    def test_fresh_local_stale_main_blocks(self, tmp_path: Path) -> None:
        """红蓝钉·禁逃逸：worktree 内植入新鲜副本、主树停更 → 仍阻断。"""
        main, wt = _make_linked_worktree(tmp_path)
        _write_cache(main, saved_at=_stale_ts())
        _write_cache(wt, saved_at=_fresh_ts())
        gate = make_depgraph_freshness_gate()
        passed, detail = gate.check(_make_gateway(wt), [])
        assert passed is False
        assert "source=main-worktree" in detail

    def test_main_cache_missing_falls_back_local(self, tmp_path: Path) -> None:
        """主树副本缺失 → 回落本地副本；本地陈旧仍阻断（fail-open 面不放松）。"""
        main, wt = _make_linked_worktree(tmp_path)
        _write_cache(wt, saved_at=_stale_ts())
        path, src = _resolve_cache_path(wt)
        assert src == "local"
        assert path == wt / ".runtime" / "depgraph_scan_cache.json"
        gate = make_depgraph_freshness_gate()
        passed, detail = gate.check(_make_gateway(wt), [])
        assert passed is False
        assert "source=local" in detail

    def test_relative_gitdir_resolved(self, tmp_path: Path) -> None:
        """gitdir 为相对路径 → 仍解析到主树并以主树副本判定。"""
        main, wt = _make_linked_worktree(tmp_path)
        (wt / ".git").write_text(
            "gitdir: ../main/.git/worktrees/wt\n", encoding="utf-8"
        )
        _write_cache(main, saved_at=_fresh_ts())
        _write_cache(wt, saved_at=_stale_ts())
        assert _main_worktree_root(wt) == main
        gate = make_depgraph_freshness_gate()
        passed, detail = gate.check(_make_gateway(wt), [])
        assert passed is True, detail

    def test_malformed_git_file_no_crash(self, tmp_path: Path) -> None:
        """.git 文件内容非法 → 不抛异常、回落本地副本判定。"""
        main, wt = _make_linked_worktree(tmp_path)
        (wt / ".git").write_text("garbage-without-gitdir\n", encoding="utf-8")
        _write_cache(wt, saved_at=_stale_ts())
        assert _main_worktree_root(wt) is None
        path, src = _resolve_cache_path(wt)
        assert src == "local(no-main-root)"
        assert path == wt / ".runtime" / "depgraph_scan_cache.json"
        gate = make_depgraph_freshness_gate()
        passed, detail = gate.check(_make_gateway(wt), [])
        assert passed is False

    def test_gitdir_pointing_outside_no_ancestor(self, tmp_path: Path) -> None:
        """gitdir 路径无 .git 祖先（异常布局）→ 回落本地，不误指他处。"""
        main, wt = _make_linked_worktree(tmp_path)
        (wt / ".git").write_text(
            f"gitdir: {tmp_path / 'elsewhere' / 'meta'}\n", encoding="utf-8"
        )
        _write_cache(main, saved_at=_fresh_ts())
        _write_cache(wt, saved_at=_stale_ts())
        assert _main_worktree_root(wt) is None
        gate = make_depgraph_freshness_gate()
        passed, _ = gate.check(_make_gateway(wt), [])
        assert passed is False
