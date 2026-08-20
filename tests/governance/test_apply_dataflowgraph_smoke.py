# [A_test] module_id: MOD-GOV_apply_dataflowgraph_smoke | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-279 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_apply_dataflowgraph_smoke
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module; DB 不可达->skip_test
# [TESTS] tests/governance/test_apply_dataflowgraph_smoke.py
# [A_module] module_id=MOD-TEST-279 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_apply_dataflowgraph_smoke.py — apply_dataflowgraph.py end-to-end smoke test

Ruling:100PCT-AI-GOVERNANCE P1-6 治本：核心治理工具必须有 e2e smoke test。

对标 test_apply_depgraph_smoke.py 模式，检测以下 bug 类型：
1. **NameError（import 缺失）**：模块加载时 import 语句缺失导致 NameError
2. **CLI 不可运行**：argparse 配置错误、main() 入口损坏
3. **DB 连接失败**：PostgreSQL 配置漂移、角色权限问题
4. **函数签名漂移**：参数重命名/删除导致调用失败

设计原则（与 apply_depgraph_smoke 一致）：
1. 真实 import + 真实调用（不 mock 整个模块，只 mock DB 写入）
2. 真实 DB 连接（@pytest.mark.e2e）
3. 不写入生产 dataflowgraph（mock conn + 早期校验失败路径）
4. 每个测试独立检测 NameError
5. @pytest.mark.smoke：快速运行（<5s），可纳入 AI session 启动健康度检查

Usage::

    py -3.12 -m pytest tests/governance/test_apply_dataflowgraph_smoke.py -v
    py -3.12 -m pytest tests/governance/test_apply_dataflowgraph_smoke.py -k "not e2e"
"""

from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT_PATH = _REPO_ROOT / "scripts" / "governance" / "apply_dataflowgraph.py"


@pytest.fixture(scope="module")
def adf():
    """动态加载 apply_dataflowgraph.py（避免 __init__.py 依赖问题）。

    真实执行模块级代码（含 import 语句）——若 import 缺失会立即抛 ImportError/NameError。
    """
    spec = importlib.util.spec_from_file_location("apply_dataflowgraph_smoke_under_test", _SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_mock_conn(fetchone_result=None, fetchall_result=None):
    """构造 mock dataflowgraph 连接（避免写入生产 DB）。"""
    conn = MagicMock()
    cursor = MagicMock()
    cursor.fetchone.return_value = fetchone_result
    cursor.fetchall.return_value = fetchall_result or []
    conn.execute.return_value = cursor
    conn.cursor.return_value.__enter__.return_value = cursor
    conn.cursor.return_value = cursor
    return conn


# ============================================================================
# Test 1: Import smoke —— 检测 NameError（import 缺失）
# ============================================================================


class TestImportSmoke:
    """验证 apply_dataflowgraph.py 模块能正常 import。"""

    def test_module_loads_without_name_error(self, adf):
        """模块能加载且无 NameError。"""
        assert adf is not None, "apply_dataflowgraph 模块加载失败"

    def test_get_dataflowgraph_pg_connection_symbol_exists(self, adf):
        """get_dataflowgraph_pg_connection 符号存在。"""
        assert hasattr(adf, "get_dataflowgraph_pg_connection"), (
            "get_dataflowgraph_pg_connection 不在模块命名空间——NameError 隐患"
        )

    def test_exit_constants_exist(self, adf):
        """EXIT_* 常量存在（从 _shared.constants 导入）。"""
        assert hasattr(adf, "EXIT_PASS"), "EXIT_PASS 常量缺失"
        assert hasattr(adf, "EXIT_ERROR"), "EXIT_ERROR 常量缺失"
        assert hasattr(adf, "EXIT_FINDINGS"), "EXIT_FINDINGS 常量缺失"

    def test_core_functions_exist(self, adf):
        """核心 cmd_* 函数存在（签名漂移检测）。"""
        for func_name in [
            "cmd_add_design_dataset",
            "cmd_add_design_job",
            "cmd_add_design_edge",
            "cmd_transition_build_status",
            "cmd_list_datasets",
            "cmd_list_jobs",
            "cmd_list_ops",
        ]:
            assert hasattr(adf, func_name), f"核心函数 {func_name} 缺失"

    def test_lock_constants_exist(self, adf):
        """锁常量/函数存在。"""
        assert hasattr(adf, "_DATAFLOW_ADVISORY_LOCK_KEY"), "_DATAFLOW_ADVISORY_LOCK_KEY 缺失"
        assert hasattr(adf, "acquire_dataflow_write_lock"), "acquire_dataflow_write_lock 缺失"
        assert hasattr(adf, "release_dataflow_write_lock"), "release_dataflow_write_lock 缺失"


# ============================================================================
# Test 2: CLI smoke —— 检测 CLI 入口可运行
# ============================================================================


class TestCLISmoke:
    """验证 apply_dataflowgraph.py CLI 入口可运行。"""

    def test_list_ops_cli_runs(self):
        """--list-ops CLI 命令能正常运行（returncode=0）。"""
        result = subprocess.run(
            [sys.executable, str(_SCRIPT_PATH), "--list-ops"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            cwd=str(_REPO_ROOT),
        )
        assert result.returncode == 0, (
            f"--list-ops CLI 失败 rc={result.returncode}\nstdout: {result.stdout[:500]}\nstderr: {result.stderr[:500]}"
        )
        # --list-ops 输出应包含命令说明
        assert "list" in result.stdout.lower() or "dataset" in result.stdout.lower(), (
            f"--list-ops 输出格式异常\nstdout: {result.stdout[:500]}"
        )

    def test_no_args_prints_help(self):
        """无参数调用打印 help（非崩溃退出）。"""
        result = subprocess.run(
            [sys.executable, str(_SCRIPT_PATH)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            cwd=str(_REPO_ROOT),
        )
        combined = result.stdout + result.stderr
        assert "usage:" in combined, "help 输出缺少 usage 行"


# ============================================================================
# Test 3: DB connection smoke —— 真实连接 PostgreSQL（@pytest.mark.e2e）
# ============================================================================


@pytest.mark.e2e
class TestDBConnectionSmoke:
    """验证 get_dataflowgraph_pg_connection 能真实连接 PostgreSQL dataflowgraph。

    @pytest.mark.e2e：真实 DB 连接，检测配置漂移、角色权限问题。
    跳过条件：PostgreSQL 不可达（CI 环境无 DB 时 skip）。
    """

    def test_read_only_connection_works(self, adf):
        """只读角色能连接并执行 SELECT 1。"""
        try:
            conn = adf.get_dataflowgraph_pg_connection(read_only=True)
        except Exception as e:
            pytest.skip(f"PostgreSQL dataflowgraph 不可达（CI 环境？）: {e}")
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 AS smoke_test")
                row = cur.fetchone()
                assert row is not None, "SELECT 1 返回空"
        finally:
            conn.close()

    def test_dataflow_datasets_table_accessible(self, adf):
        """dataflow_datasets 表可读（验证 schema 健康度）。"""
        try:
            conn = adf.get_dataflowgraph_pg_connection(read_only=True)
        except Exception as e:
            pytest.skip(f"PostgreSQL dataflowgraph 不可达: {e}")
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) AS n FROM dataflow_datasets")
                row = cur.fetchone()
                assert row is not None, "SELECT COUNT 返回空"
        finally:
            conn.close()


# ============================================================================
# Test 4: Function callable smoke —— mock DB，真实调用函数逻辑
# ============================================================================


class TestFunctionCallableSmoke:
    """验证核心 cmd_* 函数能被调用（mock DB，检测 NameError/签名漂移）。

    mock 策略：替换 get_dataflowgraph_pg_connection 返回 mock conn，
    避免写入生产 dataflowgraph。函数逻辑真实执行。
    """

    def test_cmd_add_design_dataset_callable_with_mock_db(self, adf, monkeypatch):
        """cmd_add_design_dataset 能被调用（mock DB，检测 NameError）。

        场景：args.namespace 构造最小参数，mock DB 返回空 → 函数早期校验失败或返回非零。
        验证：①函数可调用 ②get_dataflowgraph_pg_connection 调用正常 ③无 NameError。
        """
        mock_conn = _make_mock_conn(fetchone_result=None)
        monkeypatch.setattr(adf, "init_dataflow_db", lambda *a, **kw: None)  # cmd_* 首行 init 会自建真实连接，一并 mock
        monkeypatch.setattr(adf, "get_dataflowgraph_pg_connection", lambda **kw: mock_conn)
        monkeypatch.setattr(adf, "acquire_dataflow_write_lock", lambda conn: None)
        monkeypatch.setattr(adf, "release_dataflow_write_lock", lambda conn: None)

        args = argparse.Namespace(
            add_design_dataset=True,
            entity_name="smoke_test.nonexist",
            scope="production",
            contract_ref=None,
            physical_type=None,
            produced_by_job=None,
            domain_id="D-SMOKE-NONEXIST",
            pit_policy="strict",
            format_summary=None,
            valid_since=None,
        )
        # 调用 cmd_add_design_dataset（mock DB，domain 不存在 → 返回非零）
        result = adf.cmd_add_design_dataset(args)
        # mock DB 下应返回非零（写入失败或校验失败），但不抛 NameError
        assert isinstance(result, int), f"cmd_add_design_dataset 应返回 int，实际 {type(result)}"

    def test_cmd_list_ops_callable(self, adf):
        """cmd_list_ops 能被调用（无需 DB，检测 NameError）。"""
        result = adf.cmd_list_ops()
        # cmd_list_ops 返回 EXIT_PASS=0
        assert result == 0, f"cmd_list_ops 应返回 0，实际 {result}"

    def test_cmd_list_datasets_callable_with_mock_db(self, adf, monkeypatch):
        """cmd_list_datasets 能被调用（mock DB，检测 NameError）。"""
        mock_conn = _make_mock_conn(fetchall_result=[])
        monkeypatch.setattr(adf, "init_dataflow_db", lambda *a, **kw: None)  # cmd_* 首行 init 会自建真实连接，一并 mock
        monkeypatch.setattr(adf, "get_dataflowgraph_pg_connection", lambda **kw: mock_conn)

        args = argparse.Namespace(list_datasets=True)
        result = adf.cmd_list_datasets(args)
        # mock DB 下应返回 0（空列表查询成功）
        assert result == 0, f"cmd_list_datasets 应返回 0，实际 {result}"
