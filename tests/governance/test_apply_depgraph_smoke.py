# [A_test] module_id: MOD-GOV_apply_depgraph_smoke | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-277 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_apply_depgraph_smoke
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module; DB 不可达->skip_test
# [TESTS] tests/governance/test_apply_depgraph_smoke.py
# [TTL] permanent
"""test_apply_depgraph_smoke.py — apply_depgraph.py end-to-end smoke test

#ARCH-TOOL-HEALTH-V1 Phase 4 治本：核心治理工具必须有 e2e smoke test。

病根（第一性原理）
-----------------
commit deb695006f 批量重构 sys.exit→EXIT_* 时误删 get_depgraph_pg_connection
的 import 语句，导致 56 处调用保留但未导入。5 层防线（pre-commit hook、
GitCommitGateway、测试等）全部失效，NameError 在生产中静默累积。

根因：apply_depgraph.py 是 L1 铁律执行工具（apply_depgraph.py 直接写 depgraph
PostgreSQL），但只有 mock-based 单测（test_apply_depgraph_transition_sync.py），
mock 路径下 NameError 永远不暴露——mock 替换了 get_depgraph_pg_connection，
即使 import 缺失，mock 也能"工作"。

治本方案
--------
本 smoke test 真实调用 apply_depgraph.py 的核心函数 + 真实 DB 连接，
检测以下 bug 类型：
1. **NameError（Phase 1 类型）**：import 缺失导致运行时 NameError
2. **CLI 不可运行**：argparse 配置错误、main() 入口损坏
3. **DB 连接失败**：PostgreSQL 配置漂移、角色权限问题
4. **函数签名漂移**：参数重命名/删除导致调用失败

设计原则
--------
1. **真实 import + 真实调用**：不 mock 整个模块，只 mock DB 写入（避免污染生产库）
2. **真实 DB 连接**：test_db_connection_smoke 真实连接 PostgreSQL（@pytest.mark.e2e）
3. **不写入生产 depgraph**：硬约束"禁止测试域插入生产 depgraph"——所有写入测试
   用 mock conn + rollback，验证函数逻辑而非 DB 持久化
4. **每个 test 独立检测 NameError**：即使某个函数 import 缺失，其他 test 仍能运行
5. **@pytest.mark.smoke**：快速运行（<5s），可纳入 AI session 启动健康度检查

Usage::

    py -3.12 -m pytest tests/governance/test_apply_depgraph_smoke.py -v
    py -3.12 -m pytest tests/governance/test_apply_depgraph_smoke.py -k "not e2e"  # 跳过 DB 连接
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT_PATH = _REPO_ROOT / "scripts" / "governance" / "apply_depgraph.py"


@pytest.fixture(scope="module")
def adg():
    """动态加载 apply_depgraph.py（避免 __init__.py 依赖问题）。

    真实执行模块级代码（含 import 语句）——若 import 缺失会立即抛 ImportError/NameError，
    这正是 Phase 1 类 bug 的检测点。
    """
    spec = importlib.util.spec_from_file_location(
        "apply_depgraph_smoke_under_test", _SCRIPT_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_mock_conn(fetchone_result=None, fetchall_result=None):
    """构造 mock depgraph 连接（避免写入生产 DB）。

    mock 策略：
    - execute() 返回 cursor 自身（链式调用）
    - fetchone() 返回 fetchone_result（dict 形式，对标 psycopg2 RealDictCursor）
    - fetchall() 返回 fetchall_result
    - commit()/rollback()/close() 无操作
    """
    conn = MagicMock()
    cursor = MagicMock()
    cursor.fetchone.return_value = fetchone_result
    cursor.fetchall.return_value = fetchall_result or []
    conn.execute.return_value = cursor
    conn.cursor.return_value.__enter__.return_value = cursor
    conn.cursor.return_value = cursor  # 兼容 conn.cursor() 直接调用
    return conn


# ============================================================================
# Test 1: Import smoke —— 检测 Phase 1 类 NameError（import 缺失）
# ============================================================================

class TestImportSmoke:
    """验证 apply_depgraph.py 模块能正常 import（所有依赖符号可用）。

    这是 Phase 1 NameError bug 的第一道检测——commit deb695006f 误删
    get_depgraph_pg_connection import 时，模块 import 会失败。
    """

    def test_module_loads_without_name_error(self, adg):
        """模块能加载且无 NameError。"""
        assert adg is not None, "apply_depgraph 模块加载失败"

    def test_get_depgraph_pg_connection_symbol_exists(self, adg):
        """get_depgraph_pg_connection 符号存在（Phase 1 误删的就是这个 import）。"""
        assert hasattr(adg, "get_depgraph_pg_connection"), (
            "get_depgraph_pg_connection 不在模块命名空间——Phase 1 NameError 复发"
        )

    def test_exit_constants_exist(self, adg):
        """EXIT_* 常量存在（commit deb695006f 引入的 sys.exit→EXIT_* 重构）。

        apply_depgraph.py 从 _shared.exit_codes 导入 EXIT_PASS/EXIT_ERROR/EXIT_FINDINGS，
        Phase 1 误删 import 时这组常量会整体缺失（NameError 命中点）。
        """
        assert hasattr(adg, "EXIT_PASS"), "EXIT_PASS 常量缺失"
        assert hasattr(adg, "EXIT_ERROR"), "EXIT_ERROR 常量缺失"
        assert hasattr(adg, "EXIT_FINDINGS"), "EXIT_FINDINGS 常量缺失"

    def test_core_functions_exist(self, adg):
        """核心公开函数存在（签名漂移检测）。"""
        for func_name in [
            "add_design_node",
            "add_design_edge",
            "add_file_node",
            "transition_build_status",
            "transition_design_maturity",
            "remove_design_node",
            "deprecate_node",
            "delete_design_edge",
            "cmd_insert_domain",
        ]:
            assert hasattr(adg, func_name), f"核心函数 {func_name} 缺失"


# ============================================================================
# Test 2: CLI smoke —— 检测 CLI 入口可运行（argparse 配置错误）
# ============================================================================

class TestCLISmoke:
    """验证 apply_depgraph.py CLI 入口可运行。

    调用 --list-ops（只读命令），验证 returncode=0 且输出含 "cmd_batch 支持的 op"。
    检测 argparse 配置错误、main() 入口损坏。
    """

    def test_list_ops_cli_runs(self):
        """--list-ops CLI 命令能正常运行（returncode=0）。"""
        result = subprocess.run(
            [sys.executable, str(_SCRIPT_PATH), "--list-ops"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=30, cwd=str(_REPO_ROOT),
        )
        assert result.returncode == 0, (
            f"--list-ops CLI 失败 rc={result.returncode}\n"
            f"stdout: {result.stdout[:500]}\nstderr: {result.stderr[:500]}"
        )
        assert "cmd_batch 支持的 op" in result.stdout, (
            f"--list-ops 输出格式异常，缺少 'cmd_batch 支持的 op'\n"
            f"stdout: {result.stdout[:500]}"
        )

    def test_no_args_prints_help(self):
        """无参数调用打印 help（returncode=3，非崩溃）。"""
        result = subprocess.run(
            [sys.executable, str(_SCRIPT_PATH)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=30, cwd=str(_REPO_ROOT),
        )
        # 无参数时 parser.print_help() + sys.exit(3)
        assert result.returncode == 3, (
            f"无参数调用应返回 rc=3（print_help+exit），实际 rc={result.returncode}"
        )
        assert "usage:" in result.stdout, "help 输出缺少 usage 行"


# ============================================================================
# Test 3: DB connection smoke —— 真实连接 PostgreSQL（@pytest.mark.e2e）
# ============================================================================

@pytest.mark.e2e
class TestDBConnectionSmoke:
    """验证 get_depgraph_pg_connection 能真实连接 PostgreSQL depgraph。

    @pytest.mark.e2e：真实 DB 连接，检测配置漂移、角色权限问题。
    跳过条件：PostgreSQL 不可达（CI 环境无 DB 时 skip）。
    """

    def test_read_only_connection_works(self, adg):
        """只读角色能连接并执行 SELECT 1。"""
        try:
            conn = adg.get_depgraph_pg_connection(read_only=True)
        except Exception as e:
            pytest.skip(f"PostgreSQL depgraph 不可达（CI 环境？）: {e}")
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 AS smoke_test")
                row = cur.fetchone()
                assert row is not None, "SELECT 1 返回空"
        finally:
            conn.close()

    def test_depgraph_nodes_table_accessible(self, adg):
        """nodes 表可读（验证 schema 健康度）。"""
        try:
            conn = adg.get_depgraph_pg_connection(read_only=True)
        except Exception as e:
            pytest.skip(f"PostgreSQL depgraph 不可达: {e}")
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) AS n FROM nodes")
                row = cur.fetchone()
                assert row is not None, "SELECT COUNT 返回空"
                # depgraph 应有节点（非空库）
                count = row["n"] if isinstance(row, dict) else row[0]
                assert count > 0, f"depgraph nodes 表为空（n={count}），schema 未初始化？"
        finally:
            conn.close()


# ============================================================================
# Test 4: Function callable smoke —— mock DB，真实调用函数逻辑
# ============================================================================

class TestFunctionCallableSmoke:
    """验证核心函数能被调用（mock DB，检测 NameError/签名漂移）。

    mock 策略：替换 get_depgraph_pg_connection 返回 mock conn，
    避免写入生产 depgraph（硬约束）。函数逻辑真实执行——若内部引用了
    未导入的符号（Phase 1 NameError），会立即抛 NameError。
    """

    def test_add_design_node_callable_with_mock_db(self, adg, monkeypatch):
        """add_design_node 能被调用（mock DB，检测 NameError）。

        场景：domain_id 不存在 → 函数返回 -1（早期校验失败）。
        这验证了：①函数可调用 ②get_depgraph_pg_connection 调用正常
        ③SQL_SELECT_DOMAIN_ID_BY_DOMAIN_ID 符号存在 ④无 NameError。
        """
        mock_conn = _make_mock_conn(fetchone_result=None)  # domain 不存在
        monkeypatch.setattr(adg, "get_depgraph_pg_connection", lambda **kw: mock_conn)
        # mock _db_write_lock 避免 lock_conn 调用
        from contextlib import contextmanager

        @contextmanager
        def _mock_lock(*args, **kwargs):
            yield mock_conn

        monkeypatch.setattr(adg, "_db_write_lock", _mock_lock)

        # 调用 add_design_node（domain_id='D-SMOKE-NONEXIST' 不存在 → 返回 -1）
        result = adg.add_design_node(
            path="src/smoke_test/",
            blueprint_id="",
            domain_id="D-SMOKE-NONEXIST",
            build_status="planned",
            granularity="directory",
        )
        # domain 不存在时返回 -1（早期校验失败，未写入）
        assert result == -1, f"add_design_node 应返回 -1（domain 不存在），实际 {result}"

    def test_add_design_edge_callable_with_mock_db(self, adg, monkeypatch):
        """add_design_edge 能被调用（mock DB，检测 NameError）。

        场景：节点不存在 → 函数返回 -1。
        验证：①函数可调用 ②SQL 常量存在 ③无 NameError。
        """
        mock_conn = _make_mock_conn(fetchone_result=None)  # 节点不存在
        monkeypatch.setattr(adg, "get_depgraph_pg_connection", lambda **kw: mock_conn)
        from contextlib import contextmanager

        @contextmanager
        def _mock_lock(*args, **kwargs):
            yield mock_conn

        monkeypatch.setattr(adg, "_db_write_lock", _mock_lock)

        result = adg.add_design_edge(from_node_id=999999, to_node_id=999998)
        # 节点不存在时返回 -1
        assert result == -1, f"add_design_edge 应返回 -1（节点不存在），实际 {result}"

    def test_transition_build_status_callable_with_mock_db(self, adg, monkeypatch):
        """transition_build_status 能被调用（mock DB，检测 NameError）。

        场景：node_id 不存在 → 函数返回 False。
        验证：①函数可调用 ②状态机校验逻辑正常 ③无 NameError。
        """
        mock_conn = _make_mock_conn(fetchone_result=None)  # node 不存在
        monkeypatch.setattr(adg, "get_depgraph_pg_connection", lambda **kw: mock_conn)

        result = adg.transition_build_status(node_id=999999, to="stable")
        # node 不存在或状态转换无效时返回 False
        assert result is False, (
            f"transition_build_status 应返回 False（node 不存在），实际 {result}"
        )

    def test_remove_design_node_callable_with_mock_db(self, adg, monkeypatch):
        """remove_design_node 能被调用（mock DB，检测 NameError）。"""
        mock_conn = _make_mock_conn(fetchone_result=None)
        monkeypatch.setattr(adg, "get_depgraph_pg_connection", lambda **kw: mock_conn)

        result = adg.remove_design_node(node_id=999999)
        # node 不存在时返回 False
        assert result is False, (
            f"remove_design_node 应返回 False（node 不存在），实际 {result}"
        )


# ============================================================================
# Test 5: 真实 DB 只读查询 smoke —— 验证函数与真实 schema 对齐
# ============================================================================

@pytest.mark.e2e
class TestRealDBReadOnlySmoke:
    """真实 DB 只读查询，验证函数引用的 SQL/表名与真实 schema 对齐。

    @pytest.mark.e2e：真实 DB 连接，但只读 SELECT，不写入。
    检测 schema 漂移（如表名/列名变更后函数 SQL 失效）。
    """

    def test_nodes_table_schema_matches_function_expectations(self, adg):
        """nodes 表包含 add_design_node 写入的列（schema 对齐）。"""
        try:
            conn = adg.get_depgraph_pg_connection(read_only=True)
        except Exception as e:
            pytest.skip(f"PostgreSQL depgraph 不可达: {e}")
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'nodes'
                    ORDER BY column_name
                """)
                columns = {row["column_name"] for row in cur.fetchall()}
            # add_design_node 写入的列必须存在
            required_cols = {
                "path", "blueprint_id", "domain_id", "build_status",
                "design_maturity", "granularity", "node_type", "blueprint_path",
            }
            missing = required_cols - columns
            assert not missing, (
                f"nodes 表缺少 add_design_node 期望的列: {missing}。"
                f"schema 漂移——apply_depgraph.py SQL 与 DB schema 不一致"
            )
        finally:
            conn.close()

    def test_domains_table_has_test_isolation_domain(self, adg):
        """domains 表可读（FK 完整性基础）。"""
        try:
            conn = adg.get_depgraph_pg_connection(read_only=True)
        except Exception as e:
            pytest.skip(f"PostgreSQL depgraph 不可达: {e}")
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) AS n FROM domains")
                row = cur.fetchone()
                count = row["n"] if isinstance(row, dict) else row[0]
                assert count > 0, "domains 表为空，depgraph 未初始化"
        finally:
            conn.close()


# ============================================================================
# Test 6: ARCH-MM-001 gate smoke —— [MATURITY] header 校验门禁
# ============================================================================

class TestMaturityHeaderGateSmoke:
    """验证 transition_design_maturity 的 [MATURITY] header 校验门禁。

    ARCH-MM-001 裁定（2026-07-22 治本）：
    - [MATURITY] 文件头是"声明"，depgraph DB 是"验证"
    - transition_design_maturity 手动提升时 MUST 确保 header == TO_MATURITY
    - --force 逃生通道跳过 header 校验（warn 但不阻断）

    mock 策略：替换 get_depgraph_pg_connection 返回 mock conn，
    避免写入生产 depgraph。真实读取文件头 [MATURITY] 值。
    """

    def test_read_maturity_header_returns_value(self, adg):
        """_read_maturity_header 能从真实文件读取 [MATURITY] 值。"""
        header_val = adg._read_maturity_header(_SCRIPT_PATH)
        assert header_val is not None, (
            f"_read_maturity_header 返回 None——{_SCRIPT_PATH} 应有 [MATURITY] header"
        )
        assert header_val in ("design", "prototype", "production"), (
            f"[MATURITY] 值 '{header_val}' 不在合法枚举 design/prototype/production 中"
        )

    def test_gate_blocks_when_header_mismatches(self, adg, monkeypatch):
        """gate 硬阻断：header=prototype 但 TO_MATURITY=production → 返回 False。"""
        mock_conn = _make_mock_conn(
            fetchone_result={"design_maturity": "prototype", "path": str(_SCRIPT_PATH.relative_to(_REPO_ROOT)).replace("\\", "/")}
        )
        monkeypatch.setattr(adg, "get_depgraph_pg_connection", lambda **kw: mock_conn)
        from contextlib import contextmanager

        @contextmanager
        def _mock_lock(*args, **kwargs):
            yield mock_conn

        monkeypatch.setattr(adg, "_db_write_lock", _mock_lock)

        result = adg.transition_design_maturity(node_id=999999, to="production")
        assert result is False, (
            "gate 应阻断 header=prototype != TO=production 的 transition，"
            "但返回了 True——ARCH-MM-001 门禁失效"
        )

    def test_gate_allows_when_header_matches(self, adg, monkeypatch):
        """gate 放行：header==TO_MATURITY → 返回 True。"""
        mock_conn = _make_mock_conn(
            fetchone_result={"design_maturity": "design", "path": str(_SCRIPT_PATH.relative_to(_REPO_ROOT)).replace("\\", "/")}
        )
        monkeypatch.setattr(adg, "get_depgraph_pg_connection", lambda **kw: mock_conn)
        from contextlib import contextmanager

        @contextmanager
        def _mock_lock(*args, **kwargs):
            yield mock_conn

        monkeypatch.setattr(adg, "_db_write_lock", _mock_lock)
        # mock _read_maturity_header 返回 "prototype"（模拟 header==TO_MATURITY）
        monkeypatch.setattr(adg, "_read_maturity_header", lambda fpath: "prototype")

        # design→prototype 是合法转换，header=prototype==TO=prototype → 放行
        result = adg.transition_design_maturity(node_id=999999, to="prototype")
        assert result is True, (
            "gate 应放行 header=prototype == TO=prototype 的 transition，"
            "但返回了 False——门禁误判"
        )

    def test_force_bypasses_gate_with_warning(self, adg, monkeypatch, capsys):
        """--force 逃生通道：header != TO 但 force=True → 放行 + stderr 警告。"""
        mock_conn = _make_mock_conn(
            fetchone_result={"design_maturity": "prototype", "path": str(_SCRIPT_PATH.relative_to(_REPO_ROOT)).replace("\\", "/")}
        )
        monkeypatch.setattr(adg, "get_depgraph_pg_connection", lambda **kw: mock_conn)
        from contextlib import contextmanager

        @contextmanager
        def _mock_lock(*args, **kwargs):
            yield mock_conn

        monkeypatch.setattr(adg, "_db_write_lock", _mock_lock)

        # apply_depgraph.py [MATURITY]=prototype, TO=production, header != TO
        # force=True → 应放行 + stderr 含 WARNING
        result = adg.transition_design_maturity(node_id=999999, to="production", force=True)
        assert result is True, (
            "--force 应放行 header mismatch 的 transition，但返回了 False"
        )
        captured = capsys.readouterr()
        assert "WARNING" in captured.err or "--force" in captured.err, (
            f"--force 放行时应在 stderr 输出 WARNING，实际 stderr: {captured.err[:200]}"
        )

    def test_gate_no_block_when_file_missing(self, adg, monkeypatch):
        """gate 不阻断：文件不存在 → 无法校验 → 放行。"""
        mock_conn = _make_mock_conn(
            fetchone_result={"design_maturity": "prototype", "path": "nonexistent/file.py"}
        )
        monkeypatch.setattr(adg, "get_depgraph_pg_connection", lambda **kw: mock_conn)
        from contextlib import contextmanager

        @contextmanager
        def _mock_lock(*args, **kwargs):
            yield mock_conn

        monkeypatch.setattr(adg, "_db_write_lock", _mock_lock)

        # 文件不存在 → _read_maturity_header 返回 None → gate 不阻断
        # prototype→production 是合法转换
        result = adg.transition_design_maturity(node_id=999999, to="production")
        assert result is True, (
            "文件不存在时 gate 不应阻断（无法校验），但返回了 False"
        )
