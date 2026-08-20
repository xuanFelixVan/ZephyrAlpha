# [A_test] module_id: MOD-GOV_rename_depgraph_sync_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_RENAME_DEPGRAPH_SYNC_GATE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_rename_depgraph_sync_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_RENAME_DEPGRAPH_SYNC_GATE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_rename_depgraph_sync_gate.py — RENAME-DEPGRAPH-SYNC 门禁单测

权威依据：rename_depgraph_sync_gate.py（make_rename_depgraph_sync_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestGetStagedRenames: _get_staged_renamed_py_files 解析逻辑
  - 正常重命名 .py 文件 → 返回 (old, new) 列表
  - 非 .py 文件跳过
  - tests/ 豁免
  - git diff 失败 → None (fail-open)
  - git diff 异常 → None (fail-open)
- TestCheckDepgraphHasFile: _check_depgraph_has_file DB 查询
  - depgraph 有记录 → True
  - depgraph 无记录 → False
  - DB 异常 → None (fail-open)
- TestGatewayIntegration: mock gateway + monkeypatch DB
  - 无重命名 → 放行
  - 重命名已同步 depgraph → 放行
  - 重命名未同步 depgraph → 阻断
  - DB 不可达 → fail-open 放行
  - git diff 失败 → fail-open 放行

测试隔离：MagicMock 模拟 gateway.run_git；monkeypatch 模拟 DB 查询。
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates.rename_depgraph_sync_gate import (  # noqa: E402
    _check_depgraph_has_file,
    _format_violation_detail,
    _get_staged_renamed_py_files,
    make_rename_depgraph_sync_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------


class TestGateSpecFields:
    """gate_id / priority / isinstance(GateSpec)。"""

    def test_gate_id(self) -> None:
        gate = make_rename_depgraph_sync_gate()
        assert gate.gate_id == "RENAME-DEPGRAPH-SYNC"

    def test_priority(self) -> None:
        gate = make_rename_depgraph_sync_gate()
        assert gate.priority == 39

    def test_is_gate_spec(self) -> None:
        gate = make_rename_depgraph_sync_gate()
        assert isinstance(gate, GateSpec)


# ---------------------------------------------------------------------------
# TestGetStagedRenames
# ---------------------------------------------------------------------------


class TestGetStagedRenames:
    """_get_staged_renamed_py_files 解析逻辑。"""

    def test_normal_rename(self, tmp_path: Path) -> None:
        """正常 .py 重命名 → 返回 (old, new) 列表。"""
        gw = MagicMock()
        gw.run_git = MagicMock(return_value=_MockResult(0, "R100\told_module.py\tnew_module.py\n"))
        result = _get_staged_renamed_py_files(gw)
        assert result == [("old_module.py", "new_module.py")]

    def test_multiple_renames(self, tmp_path: Path) -> None:
        """多个重命名 → 全部返回。"""
        gw = MagicMock()
        gw.run_git = MagicMock(return_value=_MockResult(0, "R100\ta/old.py\ta/new.py\nR080\tb/old.py\tb/new.py\n"))
        result = _get_staged_renamed_py_files(gw)
        assert len(result) == 2
        assert result[0] == ("a/old.py", "a/new.py")
        assert result[1] == ("b/old.py", "b/new.py")

    def test_non_py_skipped(self) -> None:
        """非 .py 文件跳过。"""
        gw = MagicMock()
        gw.run_git = MagicMock(return_value=_MockResult(0, "R100\told.md\tnew.md\nR100\told.py\tnew.py\n"))
        result = _get_staged_renamed_py_files(gw)
        assert result == [("old.py", "new.py")]

    def test_tests_exempt(self) -> None:
        """tests/ 路径豁免。"""
        gw = MagicMock()
        gw.run_git = MagicMock(
            return_value=_MockResult(0, "R100\ttests/test_old.py\ttests/test_new.py\nR100\tsrc/old.py\tsrc/new.py\n")
        )
        result = _get_staged_renamed_py_files(gw)
        assert result == [("src/old.py", "src/new.py")]

    def test_no_renames(self) -> None:
        """无重命名 → 空列表。"""
        gw = MagicMock()
        gw.run_git = MagicMock(return_value=_MockResult(0, ""))
        result = _get_staged_renamed_py_files(gw)
        assert result == []

    def test_diff_fails_returns_none(self) -> None:
        """git diff 失败 → None (fail-open)。"""
        gw = MagicMock()
        gw.run_git = MagicMock(return_value=_MockResult(1, ""))
        result = _get_staged_renamed_py_files(gw)
        assert result is None

    def test_diff_raises_returns_none(self) -> None:
        """git diff 异常 → None (fail-open)。"""
        gw = MagicMock()
        gw.run_git = MagicMock(side_effect=RuntimeError("git not found"))
        result = _get_staged_renamed_py_files(gw)
        assert result is None


# ---------------------------------------------------------------------------
# TestCheckDepgraphHasFile
# ---------------------------------------------------------------------------


class TestCheckDepgraphHasFile:
    """_check_depgraph_has_file DB 查询逻辑。"""

    def test_file_exists(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """depgraph 有记录 → True。"""

        class _FakeCursor:
            def execute(self, sql, params):
                pass

            def fetchone(self):
                return (1,)

        class _FakeConn:
            def cursor(self):
                return _FakeCursor()

            def close(self):
                pass

        def _fake_conn(*a, **k):
            return _FakeConn()

        monkeypatch.setattr(
            "zephyr.governance.depgraph_schema.get_depgraph_pg_connection",
            _fake_conn,
        )
        assert _check_depgraph_has_file("src/zephyr/module.py") is True

    def test_file_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """depgraph 无记录 → False。"""

        class _FakeCursor:
            def execute(self, sql, params):
                pass

            def fetchone(self):
                return None

        class _FakeConn:
            def cursor(self):
                return _FakeCursor()

            def close(self):
                pass

        monkeypatch.setattr(
            "zephyr.governance.depgraph_schema.get_depgraph_pg_connection",
            lambda *a, **k: _FakeConn(),
        )
        assert _check_depgraph_has_file("src/zephyr/nonexistent.py") is False

    def test_db_error_returns_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """DB 异常 → None (fail-open)。"""

        def _fake_conn(*a, **k):
            raise ConnectionError("DB unreachable")

        monkeypatch.setattr(
            "zephyr.governance.depgraph_schema.get_depgraph_pg_connection",
            _fake_conn,
        )
        assert _check_depgraph_has_file("src/zephyr/module.py") is None


# ---------------------------------------------------------------------------
# TestFormatViolationDetail
# ---------------------------------------------------------------------------


class TestFormatViolationDetail:
    """_format_violation_detail 格式化。"""

    def test_single(self) -> None:
        result = _format_violation_detail([("a.py", "b.py")])
        assert "a.py -> b.py" in result

    def test_truncation(self) -> None:
        """超过5个时截断显示。"""
        missing = [(f"old{i}.py", f"new{i}.py") for i in range(10)]
        result = _format_violation_detail(missing)
        assert "还有 5 个" in result


# ---------------------------------------------------------------------------
# TestGatewayIntegration
# ---------------------------------------------------------------------------


class TestGatewayIntegration:
    """mock gateway + monkeypatch DB 的完整流程测试。"""

    def test_no_rename_passes(self) -> None:
        """无重命名 → 放行。"""
        gw = MagicMock()
        gw.run_git = MagicMock(return_value=_MockResult(0, ""))
        gate = make_rename_depgraph_sync_gate()
        passed, msg = gate.check(gw, [])
        assert passed is True
        assert msg == ""

    def test_synced_rename_passes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """重命名已同步 depgraph → 放行。"""
        gw = MagicMock()
        gw.run_git = MagicMock(return_value=_MockResult(0, "R100\told.py\tnew.py\n"))

        class _FakeCursor:
            def execute(self, sql, params):
                pass

            def fetchone(self):
                return (1,)

        class _FakeConn:
            def cursor(self):
                return _FakeCursor()

            def close(self):
                pass

        monkeypatch.setattr(
            "zephyr.governance.depgraph_schema.get_depgraph_pg_connection",
            lambda *a, **k: _FakeConn(),
        )
        gate = make_rename_depgraph_sync_gate()
        passed, msg = gate.check(gw, ["new.py"])
        assert passed is True

    def test_unsynced_rename_blocks(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """重命名未同步 depgraph → 阻断。"""
        gw = MagicMock()
        gw.run_git = MagicMock(return_value=_MockResult(0, "R100\tsrc/old.py\tsrc/new.py\n"))

        class _FakeCursor:
            def execute(self, sql, params):
                pass

            def fetchone(self):
                return None  # depgraph 无记录

        class _FakeConn:
            def cursor(self):
                return _FakeCursor()

            def close(self):
                pass

        monkeypatch.setattr(
            "zephyr.governance.depgraph_schema.get_depgraph_pg_connection",
            lambda *a, **k: _FakeConn(),
        )
        gate = make_rename_depgraph_sync_gate()
        passed, msg = gate.check(gw, ["src/new.py"])
        assert passed is False
        assert "RENAME-DEPGRAPH-SYNC" in msg
        assert "generate_project_depgraph.py" in msg
        assert "src/old.py -> src/new.py" in msg

    def test_db_unreachable_fail_open(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """DB 不可达 → fail-open 放行。"""
        gw = MagicMock()
        gw.run_git = MagicMock(return_value=_MockResult(0, "R100\told.py\tnew.py\n"))
        monkeypatch.setattr(
            "zephyr.governance.depgraph_schema.get_depgraph_pg_connection",
            lambda *a, **k: (_ for _ in ()).throw(ConnectionError("DB down")),
        )
        gate = make_rename_depgraph_sync_gate()
        passed, msg = gate.check(gw, ["new.py"])
        assert passed is True

    def test_diff_fails_fail_open(self) -> None:
        """git diff 失败 → fail-open 放行。"""
        gw = MagicMock()
        gw.run_git = MagicMock(return_value=_MockResult(1, ""))
        gate = make_rename_depgraph_sync_gate()
        passed, msg = gate.check(gw, ["new.py"])
        assert passed is True


# ---------------------------------------------------------------------------
# TestFailopenPersistence（tracker #116 B1/B2，#ARCH-119）
# ---------------------------------------------------------------------------


def _plant_probe_state(project_root: Path, *, reachable: bool) -> None:
    """写入探针状态文件（模拟网关前置探针结果）。"""
    import json as _json
    from datetime import datetime
    from datetime import timezone as _tz

    state = {
        "reachable": reachable,
        "checked_at": datetime.now(_tz.utc).isoformat(),
        "host": "localhost",
        "port": 5432,
        "error": "" if reachable else "refused",
        "last_reachable_at": datetime.now(_tz.utc).isoformat() if reachable else None,
        "first_offline_at": None if reachable else datetime.now(_tz.utc).isoformat(),
    }
    path = project_root / ".runtime" / "pg_probe_state.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_json.dumps(state), encoding="utf-8")


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


def _raise_conn(*a, **k):
    raise ConnectionError("DB down")


class TestFailopenPersistence:
    """DB 离线 → 放行 + log_gate_failure 落盘可断言（tracker #116 B1/B2）。"""

    def _make_gateway(self, tmp_path: Path) -> MagicMock:
        gw = MagicMock()
        gw.project_root = tmp_path
        gw.run_git = MagicMock(return_value=_MockResult(0, "R100\tsrc/old.py\tsrc/new.py\n"))
        return gw

    def test_db_offline_passes_and_persists(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """探针证实离线 + DB 连接失败 → 放行 + critical_warn 落盘（DB_OFFLINE）。"""
        _plant_probe_state(tmp_path, reachable=False)
        monkeypatch.setattr(
            "zephyr.governance.depgraph_schema.get_depgraph_pg_connection",
            _raise_conn,
        )
        gw = self._make_gateway(tmp_path)
        gate = make_rename_depgraph_sync_gate()
        passed, _msg = gate.check(gw, ["src/new.py"], session_id="sess-t")
        assert passed is True
        rows = _read_log_rows(tmp_path)
        assert len(rows) == 1
        gate_id, action, detail = rows[0]
        assert gate_id == "RENAME-DEPGRAPH-SYNC"
        assert action == "critical_warn"
        assert "DB 离线降级" in detail
        assert "src/old.py -> src/new.py" in detail

    def test_db_offline_dedup_same_day(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """探针离线——同签名当日去重（两次 check 只落一条）。"""
        _plant_probe_state(tmp_path, reachable=False)
        monkeypatch.setattr(
            "zephyr.governance.depgraph_schema.get_depgraph_pg_connection",
            _raise_conn,
        )
        gw = self._make_gateway(tmp_path)
        gate = make_rename_depgraph_sync_gate()
        for _ in range(2):
            passed, _msg = gate.check(gw, ["src/new.py"])
            assert passed is True
        assert len(_read_log_rows(tmp_path)) == 1

    def test_probe_online_real_error_not_silent(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """探针在线而 gate 连接失败=真实错误 → 逐次留痕（不静默，不去重）。"""
        _plant_probe_state(tmp_path, reachable=True)
        monkeypatch.setattr(
            "zephyr.governance.depgraph_schema.get_depgraph_pg_connection",
            _raise_conn,
        )
        gw = self._make_gateway(tmp_path)
        gate = make_rename_depgraph_sync_gate()
        for _ in range(2):
            passed, _msg = gate.check(gw, ["src/new.py"])
            assert passed is True
        rows = _read_log_rows(tmp_path)
        assert len(rows) == 2
        assert all("真实错误" in r[2] for r in rows)
