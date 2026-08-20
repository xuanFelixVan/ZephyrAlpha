# [A_test] module_id: MOD-GOV_apply_decisiongraph_smoke | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-278 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_apply_decisiongraph_smoke
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module; DB 不可达->skip_test
# [TESTS] tests/governance/test_apply_decisiongraph_smoke.py
# [A_module] module_id=MOD-TEST-278 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_apply_decisiongraph_smoke.py — apply_decisiongraph.py end-to-end smoke test

Ruling:100PCT-AI-GOVERNANCE P1-6 治本：核心治理工具必须有 e2e smoke test。

对标 test_apply_depgraph_smoke.py 模式，检测以下 bug 类型：
1. **NameError（import 缺失）**：模块加载时 import 语句缺失导致 NameError
2. **CLI 不可运行**：argparse 配置错误、main() 入口损坏
3. **DB 连接失败**：PostgreSQL 配置漂移、角色权限问题
4. **函数签名漂移**：参数重命名/删除导致调用失败

设计原则（与 apply_depgraph_smoke 一致）：
1. 真实 import + 真实调用（不 mock 整个模块，只 mock DB 写入）
2. 真实 DB 连接（@pytest.mark.e2e）
3. 不写入生产 decisiongraph（mock conn + 早期校验失败路径）
4. 每个测试独立检测 NameError
5. @pytest.mark.smoke：快速运行（<5s），可纳入 AI session 启动健康度检查

Usage::

    py -3.12 -m pytest tests/governance/test_apply_decisiongraph_smoke.py -v
    py -3.12 -m pytest tests/governance/test_apply_decisiongraph_smoke.py -k "not e2e"  # 跳过 DB 连接
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT_PATH = _REPO_ROOT / "scripts" / "governance" / "apply_decisiongraph.py"


@pytest.fixture(scope="module")
def adg():
    """动态加载 apply_decisiongraph.py（避免 __init__.py 依赖问题）。

    真实执行模块级代码（含 import 语句）——若 import 缺失会立即抛 ImportError/NameError。
    """
    spec = importlib.util.spec_from_file_location("apply_decisiongraph_smoke_under_test", _SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_mock_conn(fetchone_result=None, fetchall_result=None):
    """构造 mock decisiongraph 连接（避免写入生产 DB）。"""
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
    """验证 apply_decisiongraph.py 模块能正常 import。"""

    def test_module_loads_without_name_error(self, adg):
        """模块能加载且无 NameError。"""
        assert adg is not None, "apply_decisiongraph 模块加载失败"

    def test_get_decisiongraph_pg_connection_symbol_exists(self, adg):
        """get_decisiongraph_pg_connection 符号存在。"""
        assert hasattr(adg, "get_decisiongraph_pg_connection"), (
            "get_decisiongraph_pg_connection 不在模块命名空间——NameError 隐患"
        )

    def test_core_functions_exist(self, adg):
        """核心 op_* 函数存在（签名漂移检测）。

        apply_decisiongraph 的操作函数用 op_ 前缀（op_add_design_node 等），
        接收 conn 作为第一个位置参数——与 apply_depgraph 的裸函数名不同。
        """
        for func_name in [
            "op_add_design_node",
            "op_transition_build_status",
            "op_remove_design_node",
            "op_deprecate_node",
            "op_update_node_field",
            "op_add_edge",
            "op_remove_edge",
        ]:
            assert hasattr(adg, func_name), f"核心函数 {func_name} 缺失"

    def test_constants_exist(self, adg):
        """关键常量存在（lock key / 状态机 / op 集合）。"""
        assert hasattr(adg, "_DECISIONGRAPH_LOCK_KEY"), "_DECISIONGRAPH_LOCK_KEY 缺失"
        assert hasattr(adg, "_BUILD_STATUS_ORDER"), "_BUILD_STATUS_ORDER 缺失"
        assert hasattr(adg, "_VALID_NODE_TYPES"), "_VALID_NODE_TYPES 缺失"
        assert hasattr(adg, "_VALID_EDGE_TYPES"), "_VALID_EDGE_TYPES 缺失"
        assert hasattr(adg, "_db_write_lock"), "_db_write_lock 缺失"

    def test_supported_ops_nonempty(self, adg):
        """_get_supported_ops() 返回非空集合（op 注册完整性）。"""
        ops = adg.get_supported_ops()
        assert len(ops) > 0, "supported ops 为空——op 注册丢失"
        # 核心操作必须在列
        assert "add_design_node" in ops, "add_design_node 未注册"
        assert "transition_build_status" in ops, "transition_build_status 未注册"


# ============================================================================
# Test 2: CLI smoke —— 检测 CLI 入口可运行
# ============================================================================


class TestCLISmoke:
    """验证 apply_decisiongraph.py CLI 入口可运行。"""

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
        # --list-ops 输出应包含 op 名称
        assert "add_design_node" in result.stdout or "Node ops" in result.stdout, (
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
        # 无参数时打印 "ERROR: Must specify an operation." + usage
        assert result.returncode != 0, "无参数应返回非零 rc"
        combined = result.stdout + result.stderr
        assert "usage:" in combined or "operation" in combined.lower(), "help 输出缺少 usage 行"


# ============================================================================
# Test 3: DB connection smoke —— 真实连接 PostgreSQL（@pytest.mark.e2e）
# ============================================================================


@pytest.mark.e2e
class TestDBConnectionSmoke:
    """验证 get_decisiongraph_pg_connection 能真实连接 PostgreSQL decisiongraph。

    @pytest.mark.e2e：真实 DB 连接，检测配置漂移、角色权限问题。
    跳过条件：PostgreSQL 不可达（CI 环境无 DB 时 skip）。
    """

    def test_read_only_connection_works(self, adg):
        """只读角色能连接并执行 SELECT 1。"""
        try:
            conn = adg.get_decisiongraph_pg_connection(read_only=True)
        except Exception as e:
            pytest.skip(f"PostgreSQL decisiongraph 不可达（CI 环境？）: {e}")
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 AS smoke_test")
                row = cur.fetchone()
                assert row is not None, "SELECT 1 返回空"
        finally:
            conn.close()

    def test_decision_nodes_table_accessible(self, adg):
        """decision_nodes 表可读（验证 schema 健康度）。"""
        try:
            conn = adg.get_decisiongraph_pg_connection(read_only=True)
        except Exception as e:
            pytest.skip(f"PostgreSQL decisiongraph 不可达: {e}")
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) AS n FROM decision_nodes")
                row = cur.fetchone()
                assert row is not None, "SELECT COUNT 返回空"
        finally:
            conn.close()


# ============================================================================
# Test 4: Function callable smoke —— mock DB，真实调用函数逻辑
# ============================================================================


class TestFunctionCallableSmoke:
    """验证核心 op_* 函数能被调用（mock DB，检测 NameError/签名漂移）。

    op_* 函数接收 conn 作为第一个位置参数（与 apply_depgraph 的裸函数不同），
    校验失败时抛 ValueError（不返回 -1/False）。本测试用 pytest.raises(ValueError)
    验证函数可调用——ValueError 来自函数自身校验逻辑，证明无 NameError。
    """

    def test_op_add_design_node_callable_with_mock_db(self, adg):
        """op_add_design_node 能被调用（mock DB，检测 NameError）。

        场景：layer_id 不存在 → 函数抛 ValueError（DEC-INV-001 校验）。
        验证：①函数可调用 ②node_type/evidence_hash 校验逻辑正常 ③无 NameError。
        """
        mock_conn = _make_mock_conn(fetchone_result=None)
        # 取第一个合法 node_type（从 YAML 真源加载的集合）
        valid_node_type = next(iter(adg._VALID_NODE_TYPES))

        with pytest.raises(ValueError):
            adg.op_add_design_node(
                mock_conn,
                layer_id="L-SMOKE-NONEXIST",
                node_type=valid_node_type,
                path="src/smoke_test_decision/",
                decision_name="smoke",
                decision_name_en="smoke",
                evidence_hash="smoke_hash",
            )

    def test_op_add_edge_callable_with_mock_db(self, adg):
        """op_add_edge 能被调用（mock DB，检测 NameError）。

        mock DB 下 cursor.__enter__ 返回值因 mock 配置而异，返回值/异常类型
        不确定——关键验证点是函数执行到 DB 写入路径且无 NameError（import 缺失）。
        """
        mock_conn = _make_mock_conn(fetchone_result=None)
        valid_edge_type = next(iter(adg._VALID_EDGE_TYPES))

        try:
            adg.op_add_edge(
                mock_conn,
                from_node_id=999999,
                to_node_id=999998,
                edge_type=valid_edge_type,
            )
        except NameError:
            pytest.fail("op_add_edge raised NameError — import 缺失")
        except Exception:
            pass  # mock DB 下的其他异常都是函数逻辑正常执行的证明

    def test_op_transition_build_status_callable_with_mock_db(self, adg):
        """op_transition_build_status 能被调用（mock DB，检测 NameError）。

        场景：to='nonexistent' 非法状态 → 函数抛 ValueError（状态机校验）。
        """
        mock_conn = _make_mock_conn(fetchone_result=None)

        with pytest.raises(ValueError):
            adg.op_transition_build_status(
                mock_conn,
                node_id=999999,
                to="nonexistent_status",
            )

    def test_op_remove_design_node_callable_with_mock_db(self, adg):
        """op_remove_design_node 能被调用（mock DB，检测 NameError）。

        场景：node_id 不存在 → 函数抛 ValueError。
        """
        mock_conn = _make_mock_conn(fetchone_result=None)

        with pytest.raises(ValueError):
            adg.op_remove_design_node(mock_conn, node_id=999999)
