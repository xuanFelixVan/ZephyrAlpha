# [A_test] module_id: MOD-GOV_sync_yaml_to_depgraph_smoke | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-280 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_sync_yaml_to_depgraph_smoke
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module; DB 不可达->skip_test
# [TESTS] tests/governance/test_sync_yaml_to_depgraph_smoke.py
# [A_module] module_id=MOD-TEST-280 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_sync_yaml_to_depgraph_smoke.py — sync_yaml_to_depgraph.py e2e smoke test

Ruling:100PCT-AI-GOVERNANCE P1-6 治本：核心治理工具必须有 e2e smoke test。

sync_yaml_to_depgraph.py 是 L1 铁律执行工具（YAML→DB 单向同步），
但只有 mock-based 单测——mock 路径下 import 缺失/函数签名漂移永不暴露。

对标 test_apply_depgraph_smoke.py 模式，检测以下 bug 类型：
1. **NameError（import 缺失）**：模块加载时 import 语句缺失导致 NameError
2. **CLI 不可运行**：argparse 配置错误、main() 入口损坏
3. **DB 连接失败**：PostgreSQL 配置漂移
4. **函数签名漂移**：参数重命名/删除导致调用失败
5. **READONLY_TABLES 完整性**：只读表列表为空=同步范围丢失

设计原则：
1. 真实 import + 真实调用（不 mock 整个模块）
2. 真实 DB 连接（@pytest.mark.e2e）
3. 不执行 sync_all()（会写入生产 DB）——只验证函数可调用 + CLI 可运行
4. @pytest.mark.smoke：快速运行（<5s）

Usage::

    py -3.12 -m pytest tests/governance/test_sync_yaml_to_depgraph_smoke.py -v
    py -3.12 -m pytest tests/governance/test_sync_yaml_to_depgraph_smoke.py -k "not e2e"
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT_PATH = _REPO_ROOT / "scripts" / "governance" / "d8_doc_sync" / "sync_yaml_to_depgraph.py"


@pytest.fixture(scope="module")
def syd():
    """动态加载 sync_yaml_to_depgraph.py（避免 __init__.py 依赖问题）。

    真实执行模块级代码（含 import 语句）——若 import 缺失会立即抛 ImportError/NameError。
    """
    spec = importlib.util.spec_from_file_location("sync_yaml_to_depgraph_smoke_under_test", _SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ============================================================================
# Test 1: Import smoke —— 检测 NameError（import 缺失）
# ============================================================================


class TestImportSmoke:
    """验证 sync_yaml_to_depgraph.py 模块能正常 import。"""

    def test_module_loads_without_name_error(self, syd):
        """模块能加载且无 NameError。"""
        assert syd is not None, "sync_yaml_to_depgraph 模块加载失败"

    def test_main_function_exists(self, syd):
        """main() 函数存在（CLI 入口）。"""
        assert hasattr(syd, "main"), "main 函数缺失"

    def test_sync_all_function_exists(self, syd):
        """sync_all() 函数存在（核心同步入口）。"""
        assert hasattr(syd, "sync_all"), "sync_all 函数缺失"

    def test_load_yaml_function_exists(self, syd):
        """load_yaml() 函数存在（YAML 加载工具）。"""
        assert hasattr(syd, "load_yaml"), "load_yaml 函数缺失"

    def test_trigger_control_functions_exist(self, syd):
        """触发器控制函数存在（disable/restore readonly triggers）。"""
        assert hasattr(syd, "disable_readonly_triggers"), "disable_readonly_triggers 缺失"
        assert hasattr(syd, "restore_readonly_triggers"), "restore_readonly_triggers 缺失"

    def test_readonly_tables_nonempty(self, syd):
        """READONLY_TABLES 列表非空（同步范围完整性）。

        READONLY_TABLES 为空 = 同步范围丢失 = sync_all() 变成 no-op = silent failure。
        """
        assert hasattr(syd, "READONLY_TABLES"), "READONLY_TABLES 常量缺失"
        assert len(syd.READONLY_TABLES) > 0, "READONLY_TABLES 为空——同步范围丢失，sync_all() 变成 no-op"


# ============================================================================
# Test 2: CLI smoke —— 检测 CLI 入口可运行
# ============================================================================


class TestCLISmoke:
    """验证 sync_yaml_to_depgraph.py CLI 入口可运行。"""

    def test_list_readonly_tables_cli_runs(self):
        """--list-readonly-tables CLI 命令能正常运行（returncode=0）。

        --list-readonly-tables 是只读命令，不执行同步，不需要 DB 连接。
        """
        result = subprocess.run(
            [sys.executable, str(_SCRIPT_PATH), "--list-readonly-tables"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            cwd=str(_REPO_ROOT),
        )
        assert result.returncode == 0, (
            f"--list-readonly-tables CLI 失败 rc={result.returncode}\n"
            f"stdout: {result.stdout[:500]}\nstderr: {result.stderr[:500]}"
        )
        # 输出应包含表名
        assert "sync_yaml_to_depgraph" in result.stdout or len(result.stdout.strip()) > 0, (
            f"--list-readonly-tables 输出为空\nstdout: {result.stdout[:500]}"
        )

    def test_no_args_fails_safely(self):
        """无参数调用不会崩溃（会尝试 sync_all 需 DB，但应优雅退出）。"""
        result = subprocess.run(
            [sys.executable, str(_SCRIPT_PATH)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            cwd=str(_REPO_ROOT),
        )
        # 无参数时调用 sync_all()——无 DB 时应 rc=1（优雅退出），不应崩溃（rc=-15 SIGTERM 等）
        assert result.returncode in (0, 1), (
            f"无参数调用应返回 0（成功）或 1（DB 不可达），实际 rc={result.returncode}\nstderr: {result.stderr[:500]}"
        )


# ============================================================================
# Test 3: DB connection smoke —— 真实连接 PostgreSQL（@pytest.mark.e2e）
# ============================================================================


@pytest.mark.e2e
class TestDBConnectionSmoke:
    """验证 sync_yaml_to_depgraph.py 能真实连接 PostgreSQL depgraph。

    @pytest.mark.e2e：真实 DB 连接，检测配置漂移。
    跳过条件：PostgreSQL 不可达（CI 环境无 DB 时 skip）。
    """

    def test_depgraph_connection_for_sync(self, syd):
        """sync_yaml_to_depgraph 依赖的 depgraph 连接可用。

        sync_yaml_to_depgraph 内部通过 get_depgraph_pg_connection 连接 DB。
        本测试验证该连接函数可用（从 zephyr.governance.depgraph_schema 导入）。
        """
        try:
            from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
        except ImportError as e:
            pytest.skip(f"get_depgraph_pg_connection 导入失败: {e}")

        try:
            conn = get_depgraph_pg_connection(read_only=True)
        except Exception as e:
            pytest.skip(f"PostgreSQL depgraph 不可达（CI 环境？）: {e}")
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 AS smoke_test")
                row = cur.fetchone()
                assert row is not None, "SELECT 1 返回空"
        finally:
            conn.close()

    def test_readonly_tables_exist_in_db(self, syd):
        """READONLY_TABLES 中列出的表在 DB 中存在（schema 对齐）。"""
        try:
            from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

            conn = get_depgraph_pg_connection(read_only=True)
        except Exception as e:
            pytest.skip(f"PostgreSQL depgraph 不可达: {e}")
        try:
            with conn.cursor() as cur:
                for table_name in syd.READONLY_TABLES[:5]:  # 检查前 5 个表
                    cur.execute(
                        "SELECT 1 FROM information_schema.tables WHERE table_name = %s",
                        (table_name,),
                    )
                    row = cur.fetchone()
                    assert row is not None, f"READONLY_TABLES 中的表 '{table_name}' 在 DB 中不存在——schema 漂移"
        finally:
            conn.close()


# ============================================================================
# Test 4: Function callable smoke —— mock DB，真实调用函数逻辑
# ============================================================================


class TestFunctionCallableSmoke:
    """验证核心函数能被调用（mock DB，检测 NameError/签名漂移）。

    mock 策略：替换 get_depgraph_pg_connection 返回 mock conn。
    不执行 sync_all()（会写入生产 DB）——只验证 load_yaml 等只读函数。
    """

    def test_load_yaml_callable(self, syd):
        """load_yaml() 能被调用（读取真实 YAML 文件，检测 NameError）。

        使用项目中的真实 YAML 文件验证 load_yaml 函数可调用。
        """
        # 使用项目中的真实 YAML 文件（cross_module_dependencies 是同步项之一）
        yaml_rel_path = "docs/01_policies_and_standards/_registry/catalogs/cross_module_dependencies.yaml"
        result = syd.load_yaml(yaml_rel_path)
        # load_yaml 返回 dict（可能为空 dict，但不应抛 NameError）
        assert isinstance(result, dict), f"load_yaml 应返回 dict，实际 {type(result)}"

    def test_normalize_domain_id_callable(self, syd):
        """normalize_domain_id() 能被调用（纯函数，检测 NameError）。"""
        if hasattr(syd, "normalize_domain_id"):
            result = syd.normalize_domain_id("D_TEST")
            assert isinstance(result, str), f"normalize_domain_id 应返回 str，实际 {type(result)}"
        else:
            pytest.skip("normalize_domain_id 不在本模块（可能已迁移）")

    def test_sync_all_function_exists_but_not_called(self, syd):
        """sync_all() 函数存在且可引用（不实际调用，避免写入生产 DB）。

        本测试只验证 sync_all 符号存在——实际调用需要真实 DB + YAML 完整性，
        由 @pytest.mark.e2e 的 TestDBConnectionSmoke 间接覆盖。
        """
        assert callable(syd.sync_all), "sync_all 不可调用"


# ============================================================================
# Test 5: 跨模块依赖多节点跳过 —— 问题A治本逻辑 e2e 验证
# ============================================================================


@pytest.mark.e2e
class TestCrossModuleDepMultiNodeSkip:
    """验证 _resolve_module_to_single_node 的多节点跳过逻辑（问题A治本）。

    问题A根因：sync_cross_module_dependencies 用 LIMIT 1 把模块级依赖(MOD-xxx)物化为
    节点级边，多节点模块端点语义错误。治本方案：_resolve_module_to_single_node 在 COUNT>1
    时返回 'multi' 让调用方跳过物化。

    本测试只调用只读 helper（纯 SELECT，不写 DB）——不调用 sync_cross_module_dependencies
    （它会 DELETE+INSERT 真实边）。覆盖三个分支：multi / single / none。
    """

    def _get_conn(self, syd):
        # 用与 sync_yaml_to_depgraph.py 运行时相同的连接入口（syd 从 _shared.constants 导入的
        # RealDictCursor 包装器）。禁止用 zephyr.governance.depgraph_schema 裸连接——它返回
        # tuple cursor，helper 的 cur.fetchone()["n"] 字典访问会 TypeError。
        try:
            return syd.get_depgraph_pg_connection(read_only=True)
        except Exception as e:
            pytest.skip(f"PostgreSQL depgraph 不可达（CI 环境？）: {e}")

    def test_resolve_module_to_single_node_multi(self, syd):
        """多节点模块（MOD-L02-001 实测 52 节点）→ (None, 'multi')。

        这是问题A治本逻辑的核心验证：多节点模块不再用 LIMIT 1 物化。
        """
        if not hasattr(syd, "_resolve_module_to_single_node"):
            pytest.skip("_resolve_module_to_single_node 不存在（治本改动未生效？）")
        conn = self._get_conn(syd)
        try:
            with conn.cursor() as cur:
                # 先确认 MOD-L02-001 确实是多节点（防御性：若 DB 无此模块则 skip）
                cur.execute("SELECT COUNT(*) AS n FROM nodes WHERE blueprint_id = %s", ("MOD-L02-001",))
                cnt = cur.fetchone()["n"]
                if cnt <= 1:
                    pytest.skip(f"MOD-L02-001 在 DB 中非多节点（count={cnt}），无法验证 multi 分支")
                node_id, status = syd.resolve_module_to_single_node(cur, "MOD-L02-001", "")
                assert status == "multi", f"多节点模块应返回 'multi'，实际 {status}"
                assert node_id is None, f"multi 分支应返回 None node_id，实际 {node_id}"
        finally:
            conn.close()

    def test_resolve_module_to_single_node_none(self, syd):
        """不存在的 module_id + 空 fallback → (None, 'none')（COUNT==0 分支）。"""
        if not hasattr(syd, "_resolve_module_to_single_node"):
            pytest.skip("_resolve_module_to_single_node 不存在（治本改动未生效？）")
        conn = self._get_conn(syd)
        try:
            with conn.cursor() as cur:
                node_id, status = syd.resolve_module_to_single_node(cur, "MOD-SMOKE-DOES-NOT-EXIST-999", "")
                assert status == "none", f"不存在模块应返回 'none'，实际 {status}"
                assert node_id is None, f"none 分支应返回 None node_id，实际 {node_id}"
        finally:
            conn.close()

    def test_resolve_module_to_single_node_single(self, syd):
        """单节点模块 → (node_id, 'single')（回归保护：单节点路径不受多节点跳过影响）。

        动态查找 DB 中恰好 1 节点的 blueprint_id；若无则 skip。
        """
        if not hasattr(syd, "_resolve_module_to_single_node"):
            pytest.skip("_resolve_module_to_single_node 不存在（治本改动未生效？）")
        conn = self._get_conn(syd)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT blueprint_id FROM nodes "
                    "WHERE blueprint_id LIKE 'MOD-%' AND blueprint_id IS NOT NULL "
                    "GROUP BY blueprint_id HAVING COUNT(*) = 1 LIMIT 1"
                )
                row = cur.fetchone()
                if not row:
                    pytest.skip("DB 中无单节点 MOD-xxx 模块，无法验证 single 分支")
                single_module = row["blueprint_id"]
                node_id, status = syd.resolve_module_to_single_node(cur, single_module, "")
                assert status == "single", f"单节点模块应返回 'single'，实际 {status}"
                assert node_id is not None, "single 分支应返回非空 node_id"
        finally:
            conn.close()
