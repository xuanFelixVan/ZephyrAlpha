# [A_test] module_id: MOD-GOV_depgraph_pre_registration_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_depgraph_pre_registration_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_depgraph_pre_registration_gate.py — DEPGRAPH-PRE-REGISTRATION gate 测试

权威依据：depgraph_pre_registration_gate.py（make_depgraph_pre_registration_gate）

裁定 #ARCH-DEP-PREMERGE-ENFORCE：L1 铁律"施工完成转 production"从君子协定
升级为技术强制。本 gate 检测 staged src/zephyr/**/*.py 文件中 [TTL]=permanent
且 depgraph build_status=planned 且实质行数 > 50 的违规。

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestExtractTtl: [TTL] 头部提取
- TestCountImplLines: 实质行数统计
- TestCheckClosure: mock gateway + monkeypatch DB
  - 无 staged .py → 放行
  - TTL 非 permanent → 放行
  - build_status 非 planned → 放行
  - planned + 行数 <= 50 → 放行（骨架/桩代码）
  - planned + 行数 > 50 → 阻断
  - DB 不可达 → fail-open 放行
  - git diff 失败 → fail-open 放行
  - tests/ 豁免

测试隔离：MagicMock 模拟 gateway.run_git；monkeypatch 模拟 DB 查询 + 文件读取。
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates.depgraph_pre_registration_gate import (  # noqa: E402
    _count_impl_lines,
    _extract_ttl,
    make_depgraph_pre_registration_gate,
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
        gate = make_depgraph_pre_registration_gate()
        assert gate.gate_id == "DEPGRAPH-PRE-REGISTRATION"

    def test_priority(self) -> None:
        gate = make_depgraph_pre_registration_gate()
        assert gate.priority == 113

    def test_isinstance(self) -> None:
        gate = make_depgraph_pre_registration_gate()
        assert isinstance(gate, GateSpec)

    def test_check_callable(self) -> None:
        gate = make_depgraph_pre_registration_gate()
        assert callable(gate.check)


# ---------------------------------------------------------------------------
# TestExtractTtl
# ---------------------------------------------------------------------------

class TestExtractTtl:
    """_extract_ttl [TTL] 头部提取。"""

    def test_permanent(self, tmp_path: Path) -> None:
        f = tmp_path / "mod.py"
        f.write_text("# [BLUEPRINT] MOD-XXX\n# [TTL] permanent\nprint('hi')\n", encoding="utf-8")
        assert _extract_ttl(str(f)) == "permanent"

    def test_task_bound(self, tmp_path: Path) -> None:
        f = tmp_path / "mod.py"
        f.write_text("# [TTL] task_bound\n", encoding="utf-8")
        assert _extract_ttl(str(f)) == "task_bound"

    def test_missing_ttl(self, tmp_path: Path) -> None:
        f = tmp_path / "mod.py"
        f.write_text("# [BLUEPRINT] MOD-XXX\nprint('hi')\n", encoding="utf-8")
        assert _extract_ttl(str(f)) is None

    def test_file_not_found(self) -> None:
        assert _extract_ttl("nonexistent_file_xyz.py") is None


# ---------------------------------------------------------------------------
# TestCountImplLines
# ---------------------------------------------------------------------------

class TestCountImplLines:
    """_count_impl_lines 实质行数统计。"""

    def test_counts_code_lines(self, tmp_path: Path) -> None:
        f = tmp_path / "mod.py"
        f.write_text(
            "# comment line\n"
            "\n"
            "x = 1\n"
            "y = 2\n"
            "# another comment\n"
            "z = 3\n",
            encoding="utf-8",
        )
        assert _count_impl_lines(str(f)) == 3

    def test_empty_file(self, tmp_path: Path) -> None:
        f = tmp_path / "mod.py"
        f.write_text("", encoding="utf-8")
        assert _count_impl_lines(str(f)) == 0

    def test_only_comments(self, tmp_path: Path) -> None:
        f = tmp_path / "mod.py"
        f.write_text("# line1\n# line2\n\n", encoding="utf-8")
        assert _count_impl_lines(str(f)) == 0

    def test_file_not_found(self) -> None:
        assert _count_impl_lines("nonexistent_file_xyz.py") == 0


# ---------------------------------------------------------------------------
# TestCheckClosure
# ---------------------------------------------------------------------------

class TestCheckClosure:
    """_check 闭包测试（mock gateway + monkeypatch DB）。"""

    def _make_mock_gateway(
        self,
        git_diff_output: str = "",
        project_root: Path | None = None,
    ) -> MagicMock:
        """构造 mock gateway。"""
        gw = MagicMock()
        gw.project_root = project_root or Path(_PROJECT_ROOT)

        def _run_git(cmd):
            if "diff" in cmd and "--cached" in cmd:
                return _MockResult(returncode=0, stdout=git_diff_output)
            return _MockResult(returncode=0, stdout="")

        gw.run_git = _run_git
        return gw

    def test_no_staged_py_passes(self) -> None:
        """无 staged .py → 放行。"""
        gw = self._make_mock_gateway(git_diff_output="")
        gate = make_depgraph_pre_registration_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True

    def test_git_diff_fail_open(self) -> None:
        """git diff 失败 → fail-open 放行。"""
        gw = MagicMock()
        gw.project_root = Path(_PROJECT_ROOT)
        gw.run_git = lambda cmd: _MockResult(returncode=1, stdout="")
        gate = make_depgraph_pre_registration_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True

    def test_git_diff_exception_fail_open(self) -> None:
        """git diff 异常 → fail-open 放行。"""
        gw = MagicMock()
        gw.project_root = Path(_PROJECT_ROOT)

        def _raise(_cmd):
            raise RuntimeError("boom")

        gw.run_git = _raise
        gate = make_depgraph_pre_registration_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True

    def test_non_src_zephyr_skipped(self) -> None:
        """非 src/zephyr/ 下的 .py → 跳过。"""
        gw = self._make_mock_gateway(
            git_diff_output="scripts/foo.py\n"
        )
        gate = make_depgraph_pre_registration_gate()
        passed, detail = gate.check(gw, ["scripts/foo.py"])
        assert passed is True

    def test_tests_exempt(self) -> None:
        """tests/ 下的 .py → 豁免。"""
        gw = self._make_mock_gateway(
            git_diff_output="src/zephyr/foo.py\ntests/test_foo.py\n"
        )
        # Mock TTL extraction + DB to ensure tests/ is not checked
        gate = make_depgraph_pre_registration_gate()
        # Even with mocked DB returning planned, tests/ should be exempt
        with (
            patch("zephyr.gov_enforcement.commit_gates.depgraph_pre_registration_gate._extract_ttl", return_value="permanent"),
            patch("zephyr.gov_enforcement.commit_gates.depgraph_pre_registration_gate.query_build_status", return_value="planned"),
            patch("zephyr.gov_enforcement.commit_gates.depgraph_pre_registration_gate.count_impl_lines", return_value=100),
        ):
            passed, detail = gate.check(gw, ["src/zephyr/foo.py", "tests/test_foo.py"])
        # src/zephyr/foo.py would block (planned + 100 lines), but tests/ exempt
        assert passed is False

    def test_planned_with_many_lines_blocks(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """planned + 行数 > 50 → 阻断。"""
        # Create file at the path git diff reports (src/zephyr/mod.py under project_root)
        src_dir = tmp_path / "src" / "zephyr"
        src_dir.mkdir(parents=True, exist_ok=True)
        mod_file = src_dir / "mod.py"
        mod_file.write_text(
            "# [TTL] permanent\n" + "\n".join(f"x{i} = {i}" for i in range(60)) + "\n",
            encoding="utf-8",
        )

        gw = self._make_mock_gateway(
            git_diff_output="src/zephyr/mod.py\n",
            project_root=tmp_path,
        )

        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.depgraph_pre_registration_gate.query_build_status",
            lambda _fp: "planned",
        )

        gate = make_depgraph_pre_registration_gate()
        passed, detail = gate.check(gw, ["src/zephyr/mod.py"])
        assert passed is False
        assert "planned" in detail
        assert "production" in detail

    def test_planned_with_few_lines_passes(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """planned + 行数 <= 50 → 放行（骨架/桩代码）。"""
        src_dir = tmp_path / "src" / "zephyr"
        src_dir.mkdir(parents=True, exist_ok=True)
        mod_file = src_dir / "mod.py"
        mod_file.write_text(
            "# [TTL] permanent\nx = 1\ny = 2\n", encoding="utf-8"
        )

        gw = self._make_mock_gateway(
            git_diff_output="src/zephyr/mod.py\n",
            project_root=tmp_path,
        )

        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.depgraph_pre_registration_gate.query_build_status",
            lambda _fp: "planned",
        )

        gate = make_depgraph_pre_registration_gate()
        passed, detail = gate.check(gw, ["src/zephyr/mod.py"])
        assert passed is True

    def test_non_planned_passes(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """build_status 非 planned（如 stable/generated）→ 放行。"""
        src_dir = tmp_path / "src" / "zephyr"
        src_dir.mkdir(parents=True, exist_ok=True)
        mod_file = src_dir / "mod.py"
        mod_file.write_text(
            "# [TTL] permanent\n" + "\n".join(f"x{i} = {i}" for i in range(60)) + "\n",
            encoding="utf-8",
        )

        gw = self._make_mock_gateway(
            git_diff_output="src/zephyr/mod.py\n",
            project_root=tmp_path,
        )

        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.depgraph_pre_registration_gate.query_build_status",
            lambda _fp: "stable",
        )

        gate = make_depgraph_pre_registration_gate()
        passed, detail = gate.check(gw, ["src/zephyr/mod.py"])
        assert passed is True

    def test_non_permanent_ttl_passes(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """[TTL] 非 permanent（如 task_bound）→ 放行。"""
        src_dir = tmp_path / "src" / "zephyr"
        src_dir.mkdir(parents=True, exist_ok=True)
        mod_file = src_dir / "mod.py"
        mod_file.write_text(
            "# [TTL] task_bound\n" + "\n".join(f"x{i} = {i}" for i in range(60)) + "\n",
            encoding="utf-8",
        )

        gw = self._make_mock_gateway(
            git_diff_output="src/zephyr/mod.py\n",
            project_root=tmp_path,
        )

        gate = make_depgraph_pre_registration_gate()
        passed, detail = gate.check(gw, ["src/zephyr/mod.py"])
        assert passed is True

    def test_db_unreachable_fail_open(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """DB 查询失败 → fail-open 放行。"""
        src_dir = tmp_path / "src" / "zephyr"
        src_dir.mkdir(parents=True, exist_ok=True)
        mod_file = src_dir / "mod.py"
        mod_file.write_text(
            "# [TTL] permanent\n" + "\n".join(f"x{i} = {i}" for i in range(60)) + "\n",
            encoding="utf-8",
        )

        gw = self._make_mock_gateway(
            git_diff_output="src/zephyr/mod.py\n",
            project_root=tmp_path,
        )

        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.depgraph_pre_registration_gate.query_build_status",
            lambda _fp: None,  # DB 不可达
        )

        gate = make_depgraph_pre_registration_gate()
        passed, detail = gate.check(gw, ["src/zephyr/mod.py"])
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
        "host": "localhost", "port": 5432, "error": "" if reachable else "refused",
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
        return conn.execute(
            "SELECT gate_id, action, detail FROM reconcile_execution_log"
        ).fetchall()
    finally:
        conn.close()


class TestFailopenPersistence:
    """build_status 查询 None（DB 失败）降级 → 留痕可断言（tracker #116 B1/B2）。"""

    def _setup_permanent_file(self, tmp_path: Path) -> MagicMock:
        src_dir = tmp_path / "src" / "zephyr"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "mod.py").write_text(
            "# [TTL] permanent\n" + "\n".join(f"x{i} = {i}" for i in range(60)) + "\n",
            encoding="utf-8",
        )
        gw = MagicMock()
        gw.project_root = tmp_path
        gw.run_git = lambda cmd: _MockResult(returncode=0, stdout="src/zephyr/mod.py\n")
        return gw

    def test_probe_offline_none_status_logs_db_offline(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """探针证实离线 + query None → 放行 + DB_OFFLINE critical_warn 落盘。"""
        _plant_probe_state(tmp_path, reachable=False)
        gw = self._setup_permanent_file(tmp_path)
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.depgraph_pre_registration_gate.query_build_status",
            lambda _fp: None,
        )
        gate = make_depgraph_pre_registration_gate()
        passed, _detail = gate.check(gw, ["src/zephyr/mod.py"], session_id="sess-t")
        assert passed is True
        rows = _read_log_rows(tmp_path)
        assert len(rows) == 1
        gate_id, action, detail = rows[0]
        assert gate_id == "DEPGRAPH-PRE-REGISTRATION"
        assert action == "critical_warn"
        assert "DB 离线降级" in detail
        assert "src/zephyr/mod.py" in detail

    def test_probe_online_conn_failure_logs_real_error(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """探针在线而单发连接失败=真实错误 → REAL_ERROR 留痕（不静默）。"""
        _plant_probe_state(tmp_path, reachable=True)
        gw = self._setup_permanent_file(tmp_path)
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.depgraph_pre_registration_gate.query_build_status",
            lambda _fp: None,
        )
        def _raise_conn(*a, **k):
            raise ConnectionError("auth failed")
        monkeypatch.setattr(
            "zephyr.governance.depgraph_schema.get_depgraph_pg_connection",
            _raise_conn,
        )
        gate = make_depgraph_pre_registration_gate()
        passed, _detail = gate.check(gw, ["src/zephyr/mod.py"])
        assert passed is True
        rows = _read_log_rows(tmp_path)
        assert len(rows) == 1
        assert "真实错误" in rows[0][2]
        assert "REAL_ERROR" in rows[0][2]

    def test_probe_unknown_conn_ok_no_log(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """探针状态未知 + 单发连接成功 → None 属「无记录」正常语义，不留痕。"""
        gw = self._setup_permanent_file(tmp_path)
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.depgraph_pre_registration_gate.query_build_status",
            lambda _fp: None,
        )
        class _FakeConn:
            def close(self): pass
        monkeypatch.setattr(
            "zephyr.governance.depgraph_schema.get_depgraph_pg_connection",
            lambda *a, **k: _FakeConn(),
        )
        gate = make_depgraph_pre_registration_gate()
        passed, _detail = gate.check(gw, ["src/zephyr/mod.py"])
        assert passed is True
        assert _read_log_rows(tmp_path) == []
