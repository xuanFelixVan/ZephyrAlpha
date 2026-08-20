# [A_test] module_id: MOD-GOV_new_file_depgraph_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_new_file_depgraph_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_new_file_depgraph_gate.py — NEW-FILE-DEPGRAPH-ENFORCEMENT 门禁单测

权威依据：new_file_depgraph_gate.py（make_new_file_depgraph_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestIsInScope: _is_in_scope 范围判断
  - src/zephyr/ 下 .py → True
  - scripts/ 下 .py → True
  - tests/ 下 .py → False
  - 其他路径 → False
- TestGetStagedNewPyFiles: _get_staged_new_py_files 解析逻辑
  - 正常新增 .py 文件 → 返回列表
  - 非 .py 文件跳过
  - tests/ 豁免
  - 其他目录跳过
  - git diff 失败 → None (fail-open)
  - git diff 异常 → None (fail-open)
- TestCheckDepgraphHasFile: _check_depgraph_has_file DB 查询
  - depgraph 有记录 → True
  - depgraph 无记录 → False
  - DB 异常 → None (fail-open)
- TestGatewayIntegration: mock gateway + monkeypatch DB
  - 无新增 .py → 放行
  - 新增 .py 已登记 depgraph → 放行
  - 新增 .py 未登记 depgraph → 阻断
  - DB 不可达 → fail-open 放行
  - git diff 失败 → fail-open 放行
  - 非 Zephyr 项目 → skip
  - commit_files 过滤：staged 区含非 commit files → 只检测 commit files

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

from zephyr.gov_enforcement.commit_gates.new_file_depgraph_gate import (  # noqa: E402
    _check_depgraph_has_file,
    _format_violation_detail,
    _get_staged_new_py_files,
    _is_in_scope,
    make_new_file_depgraph_gate,
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
        gate = make_new_file_depgraph_gate()
        assert gate.gate_id == "NEW-FILE-DEPGRAPH-ENFORCEMENT"

    def test_priority(self) -> None:
        gate = make_new_file_depgraph_gate()
        assert gate.priority == 58

    def test_is_gate_spec(self) -> None:
        gate = make_new_file_depgraph_gate()
        assert isinstance(gate, GateSpec)


# ---------------------------------------------------------------------------
# TestIsInScope
# ---------------------------------------------------------------------------


class TestIsInScope:
    """_is_in_scope 范围判断。"""

    def test_src_zephyr_in_scope(self) -> None:
        assert _is_in_scope("src/zephyr/governance/audit/foo.py") is True

    def test_scripts_in_scope(self) -> None:
        assert _is_in_scope("scripts/governance/foo.py") is True

    def test_tests_exempt(self) -> None:
        assert _is_in_scope("tests/governance/test_foo.py") is False

    def test_other_path_out_of_scope(self) -> None:
        assert _is_in_scope("docs/foo.py") is False

    def test_root_level_out_of_scope(self) -> None:
        assert _is_in_scope("foo.py") is False


# ---------------------------------------------------------------------------
# TestGetStagedNewPyFiles
# ---------------------------------------------------------------------------


class TestGetStagedNewPyFiles:
    """_get_staged_new_py_files 解析逻辑。"""

    def test_normal_new_py_file(self) -> None:
        """正常新增 .py 文件 → 返回列表。"""
        gw = MagicMock()
        gw.run_git = MagicMock(return_value=_MockResult(0, "src/zephyr/governance/audit/new_module.py\n"))
        result = _get_staged_new_py_files(gw)
        assert result == ["src/zephyr/governance/audit/new_module.py"]

    def test_multiple_new_py_files(self) -> None:
        """多个新增 .py 文件 → 全部返回。"""
        gw = MagicMock()
        gw.run_git = MagicMock(return_value=_MockResult(0, "src/zephyr/foo.py\nscripts/governance/bar.py\n"))
        result = _get_staged_new_py_files(gw)
        assert result == ["src/zephyr/foo.py", "scripts/governance/bar.py"]

    def test_non_py_file_skipped(self) -> None:
        """非 .py 文件跳过。"""
        gw = MagicMock()
        gw.run_git = MagicMock(
            return_value=_MockResult(0, "src/zephyr/foo.py\nsrc/zephyr/bar.md\nsrc/zephyr/baz.yaml\n")
        )
        result = _get_staged_new_py_files(gw)
        assert result == ["src/zephyr/foo.py"]

    def test_tests_exempt(self) -> None:
        """tests/ 下 .py 文件豁免。"""
        gw = MagicMock()
        gw.run_git = MagicMock(return_value=_MockResult(0, "tests/governance/test_foo.py\nsrc/zephyr/foo.py\n"))
        result = _get_staged_new_py_files(gw)
        assert result == ["src/zephyr/foo.py"]

    def test_out_of_scope_skipped(self) -> None:
        """其他目录跳过（docs/ / 根级）。"""
        gw = MagicMock()
        gw.run_git = MagicMock(return_value=_MockResult(0, "docs/foo.py\nfoo.py\nsrc/zephyr/bar.py\n"))
        result = _get_staged_new_py_files(gw)
        assert result == ["src/zephyr/bar.py"]

    def test_git_diff_fail_returns_none(self) -> None:
        """git diff 失败 → None (fail-open)。"""
        gw = MagicMock()
        gw.run_git = MagicMock(return_value=_MockResult(1, ""))
        result = _get_staged_new_py_files(gw)
        assert result is None

    def test_git_diff_exception_returns_none(self) -> None:
        """git diff 异常 → None (fail-open)。"""
        gw = MagicMock()
        gw.run_git = MagicMock(side_effect=RuntimeError("git broken"))
        result = _get_staged_new_py_files(gw)
        assert result is None

    def test_empty_staged_returns_empty(self) -> None:
        """无 staged 文件 → 空列表。"""
        gw = MagicMock()
        gw.run_git = MagicMock(return_value=_MockResult(0, ""))
        result = _get_staged_new_py_files(gw)
        assert result == []

    def test_windows_path_normalized(self) -> None:
        """Windows 反斜杠路径归一化为正斜杠。"""
        gw = MagicMock()
        gw.run_git = MagicMock(return_value=_MockResult(0, "src\\zephyr\\foo.py\n"))
        result = _get_staged_new_py_files(gw)
        assert result == ["src/zephyr/foo.py"]


# ---------------------------------------------------------------------------
# TestCheckDepgraphHasFile
# ---------------------------------------------------------------------------


class TestCheckDepgraphHasFile:
    """_check_depgraph_has_file DB 查询。"""

    def test_file_exists_in_depgraph(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """depgraph 有记录 → True。"""
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = (1,)
        mock_conn.cursor.return_value = mock_cur

        def _mock_get_conn(**kwargs):
            return mock_conn

        import zephyr.governance.depgraph_schema as schema_mod

        monkeypatch.setattr(schema_mod, "get_depgraph_pg_connection", _mock_get_conn)
        result = _check_depgraph_has_file("src/zephyr/foo.py")
        assert result is True

    def test_file_not_in_depgraph(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """depgraph 无记录 → False。"""
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = None
        mock_conn.cursor.return_value = mock_cur

        def _mock_get_conn(**kwargs):
            return mock_conn

        import zephyr.governance.depgraph_schema as schema_mod

        monkeypatch.setattr(schema_mod, "get_depgraph_pg_connection", _mock_get_conn)
        result = _check_depgraph_has_file("src/zephyr/foo.py")
        assert result is False

    def test_db_exception_returns_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """DB 异常 → None (fail-open)。"""

        def _mock_get_conn(**kwargs):
            raise RuntimeError("DB connection failed")

        import zephyr.governance.depgraph_schema as schema_mod

        monkeypatch.setattr(schema_mod, "get_depgraph_pg_connection", _mock_get_conn)
        result = _check_depgraph_has_file("src/zephyr/foo.py")
        assert result is None


# ---------------------------------------------------------------------------
# TestGatewayIntegration
# ---------------------------------------------------------------------------


class TestGatewayIntegration:
    """mock gateway + monkeypatch DB 的集成测试。"""

    def _make_gateway(self, tmp_path: Path, diff_stdout: str = "", diff_rc: int = 0) -> MagicMock:
        """构造 mock gateway，模拟 _run_git 返回 diff 结果。"""
        gw = MagicMock()
        gw.project_root = tmp_path
        gw.run_git = MagicMock(return_value=_MockResult(diff_rc, diff_stdout))
        # 模拟非 Zephyr 项目检测：d1_structure 目录存在
        (tmp_path / "scripts" / "governance" / "d1_structure").mkdir(parents=True, exist_ok=True)
        return gw

    def test_no_new_py_files_passes(self, tmp_path: Path) -> None:
        """无新增 .py → 放行。"""
        gw = self._make_gateway(tmp_path, diff_stdout="")
        gate = make_new_file_depgraph_gate()
        passed, msg = gate.check(gw, files=[])
        assert passed is True

    def test_new_py_registered_in_depgraph_passes(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """新增 .py 已登记 depgraph → 放行。"""
        gw = self._make_gateway(
            tmp_path,
            diff_stdout="src/zephyr/new_module.py\n",
        )
        # mock DB 查询返回 True（已登记）
        import zephyr.gov_enforcement.commit_gates.new_file_depgraph_gate as gate_mod

        monkeypatch.setattr(gate_mod, "_check_depgraph_has_file", lambda f: True)

        gate = make_new_file_depgraph_gate()
        # files 参数需包含 commit_files_rel
        files = [str(tmp_path / "src/zephyr/new_module.py")]
        passed, msg = gate.check(gw, files=files)
        assert passed is True

    def test_new_py_not_in_depgraph_blocks(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """新增 .py 未登记 depgraph → 阻断。"""
        gw = self._make_gateway(
            tmp_path,
            diff_stdout="src/zephyr/new_module.py\n",
        )
        # mock DB 查询返回 False（未登记）
        import zephyr.gov_enforcement.commit_gates.new_file_depgraph_gate as gate_mod

        monkeypatch.setattr(gate_mod, "_check_depgraph_has_file", lambda f: False)

        gate = make_new_file_depgraph_gate()
        files = [str(tmp_path / "src/zephyr/new_module.py")]
        passed, msg = gate.check(gw, files=files)
        assert passed is False
        assert "NEW-FILE-DEPGRAPH-ENFORCEMENT" in msg
        assert "src/zephyr/new_module.py" in msg
        assert "apply_depgraph.py" in msg or "generate_project_depgraph.py" in msg

    def test_db_unreachable_fail_open(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """DB 不可达 → fail-open 放行。"""
        gw = self._make_gateway(
            tmp_path,
            diff_stdout="src/zephyr/new_module.py\n",
        )
        # mock DB 查询返回 None（DB 不可达）
        import zephyr.gov_enforcement.commit_gates.new_file_depgraph_gate as gate_mod

        monkeypatch.setattr(gate_mod, "_check_depgraph_has_file", lambda f: None)

        gate = make_new_file_depgraph_gate()
        files = [str(tmp_path / "src/zephyr/new_module.py")]
        passed, msg = gate.check(gw, files=files)
        assert passed is True

    def test_git_diff_fail_fail_open(self, tmp_path: Path) -> None:
        """git diff 失败 → fail-open 放行。"""
        gw = self._make_gateway(tmp_path, diff_stdout="", diff_rc=1)
        gate = make_new_file_depgraph_gate()
        passed, msg = gate.check(gw, files=[])
        assert passed is True

    def test_db_offline_failopen_persists(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """tracker #116 B1/B2：探针证实 PG 离线 + DB 查询失败 → 放行 +
        critical_warn 落盘（DB 离线降级，含受影响文件清单）。"""
        import json as _json
        import sqlite3 as _sqlite3
        from datetime import datetime
        from datetime import timezone as _tz

        # 植入探针状态：离线
        _state = {
            "reachable": False,
            "checked_at": datetime.now(_tz.utc).isoformat(),
            "host": "localhost",
            "port": 5432,
            "error": "refused",
            "last_reachable_at": None,
            "first_offline_at": datetime.now(_tz.utc).isoformat(),
        }
        _sp = tmp_path / ".runtime" / "pg_probe_state.json"
        _sp.parent.mkdir(parents=True, exist_ok=True)
        _sp.write_text(_json.dumps(_state), encoding="utf-8")

        gw = self._make_gateway(tmp_path, diff_stdout="src/zephyr/new_module.py\n")
        import zephyr.gov_enforcement.commit_gates.new_file_depgraph_gate as gate_mod

        monkeypatch.setattr(gate_mod, "_check_depgraph_has_file", lambda f: None)

        gate = make_new_file_depgraph_gate()
        files = [str(tmp_path / "src/zephyr/new_module.py")]
        passed, msg = gate.check(gw, files=files, session_id="sess-t")
        assert passed is True

        db_path = tmp_path / "data" / "databases" / "governance.db"
        assert db_path.is_file()
        conn = _sqlite3.connect(str(db_path))
        try:
            rows = conn.execute("SELECT gate_id, action, detail FROM reconcile_execution_log").fetchall()
        finally:
            conn.close()
        assert len(rows) == 1
        assert rows[0][0] == "NEW-FILE-DEPGRAPH-ENFORCEMENT"
        assert rows[0][1] == "critical_warn"
        assert "DB 离线降级" in rows[0][2]
        assert "src/zephyr/new_module.py" in rows[0][2]

    def test_non_zephyr_project_skips(self, tmp_path: Path) -> None:
        """非 Zephyr 项目（无 d1_structure 目录）→ skip。"""
        gw = MagicMock()
        gw.project_root = tmp_path
        gw.run_git = MagicMock(return_value=_MockResult(0, "src/zephyr/foo.py\n"))
        # 不创建 d1_structure 目录（非 Zephyr 项目）
        gate = make_new_file_depgraph_gate()
        passed, msg = gate.check(gw, files=[])
        assert passed is True
        assert "non-Zephyr project" in msg

    def test_commit_files_filter(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """staged 区含非 commit files → 只检测 commit files（gateway 选择性提交）。"""
        gw = self._make_gateway(
            tmp_path,
            # staged 区有 2 个新文件
            diff_stdout="src/zephyr/a.py\nsrc/zephyr/b.py\n",
        )
        import zephyr.gov_enforcement.commit_gates.new_file_depgraph_gate as gate_mod

        # mock DB: a.py 未登记（False），b.py 已登记（True）
        monkeypatch.setattr(
            gate_mod,
            "_check_depgraph_has_file",
            lambda f: not f.endswith("a.py"),
        )

        gate = make_new_file_depgraph_gate()
        # files 只含 a.py（gateway 选择性提交）
        files = [str(tmp_path / "src/zephyr/a.py")]
        passed, msg = gate.check(gw, files=files)
        # a.py 未登记 → 阻断
        assert passed is False
        assert "src/zephyr/a.py" in msg
        assert "b.py" not in msg

    def test_mixed_registered_and_unregistered_blocks(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """混合新增：部分已登记部分未登记 → 阻断并显示未登记文件。"""
        gw = self._make_gateway(
            tmp_path,
            diff_stdout="src/zephyr/registered.py\nsrc/zephyr/unregistered.py\n",
        )
        import zephyr.gov_enforcement.commit_gates.new_file_depgraph_gate as gate_mod

        # 精确路径匹配：registered.py 已登记，unregistered.py 未登记
        # （不能用 "registered" 子串，否则 "unregistered" 也匹配）
        _registered = {"src/zephyr/registered.py"}
        monkeypatch.setattr(
            gate_mod,
            "_check_depgraph_has_file",
            lambda f: f in _registered,
        )

        gate = make_new_file_depgraph_gate()
        files = [
            str(tmp_path / "src/zephyr/registered.py"),
            str(tmp_path / "src/zephyr/unregistered.py"),
        ]
        passed, msg = gate.check(gw, files=files)
        assert passed is False
        assert "unregistered.py" in msg
        # missing 详情只含未登记文件（断言 "详情:" 后的部分精确等于 unregistered.py）
        detail_part = msg.split("详情:")[1] if "详情:" in msg else msg
        assert detail_part.strip() == "src/zephyr/unregistered.py"


# ---------------------------------------------------------------------------
# TestFormatViolationDetail
# ---------------------------------------------------------------------------


class TestFormatViolationDetail:
    """_format_violation_detail 格式化。"""

    def test_single_file(self) -> None:
        result = _format_violation_detail(["src/zephyr/foo.py"])
        assert result == "src/zephyr/foo.py"

    def test_multiple_files(self) -> None:
        files = ["a.py", "b.py", "c.py"]
        result = _format_violation_detail(files)
        assert "a.py" in result
        assert "b.py" in result
        assert "c.py" in result

    def test_more_than_five_files_truncated(self) -> None:
        files = [f"file{i}.py" for i in range(7)]
        result = _format_violation_detail(files)
        assert "还有 2 个" in result
        assert "file0.py" in result
        assert "file4.py" in result

    def test_exactly_five_files_no_truncation(self) -> None:
        files = [f"file{i}.py" for i in range(5)]
        result = _format_violation_detail(files)
        assert "还有" not in result
