# [A_test] module_id: MOD-GOV_generate_project_depgraph_smoke | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-281 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_generate_project_depgraph_smoke
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module; DB 不可达->skip_test
# [TESTS] tests/governance/test_generate_project_depgraph_smoke.py
# [A_module] module_id=MOD-TEST-281 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_generate_project_depgraph_smoke.py — generate_project_depgraph.py e2e smoke test

Ruling:100PCT-AI-GOVERNANCE P1-6 治本：核心治理工具必须有 e2e smoke test。
+ 问题B治本验证（rebuild 时 design↔production 边被 FK CASCADE 丢失）。

generate_project_depgraph.py 是 L2 铁律执行工具（depgraph rebuild），但此前无 smoke test。
本次补齐并覆盖问题B（apply_depgraph 登记的 design↔production 边跨 rebuild 丢失）。

对标 test_sync_yaml_to_depgraph_smoke.py 模式：
1. Import smoke（无 DB）：模块加载无 NameError、关键函数存在、CLI --help 可运行
2. DesignEdgeSurvivesRebuild（@pytest.mark.e2e，真实 DB + 事务回滚）：
   验证 _snapshot_apply_depgraph_design_edges + _restore_apply_depgraph_design_edges_by_path
   协作使 design↔production 边跨 rebuild 存活。零持久副作用（conn.rollback()）。

设计原则：
1. 真实 import + 真实调用（不 mock 整个模块）
2. 真实 DB 连接（@pytest.mark.e2e）+ 事务回滚（不写生产 DB）
3. 不运行 --force 全量 rebuild（会写生产 DB、破坏其他会话）——改为在可回滚事务内直接验证 helper 协作

Usage::

    python -m pytest tests/governance/test_generate_project_depgraph_smoke.py -v
    python -m pytest tests/governance/test_generate_project_depgraph_smoke.py -k "not e2e"
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT_PATH = _REPO_ROOT / "scripts" / "governance" / "generate_project_depgraph.py"


@pytest.fixture(scope="module")
def gpd():
    """动态加载 generate_project_depgraph.py（避免 __init__.py 依赖问题）。

    真实执行模块级代码（含 import 语句）——若 import 缺失会立即抛 ImportError/NameError。
    """
    spec = importlib.util.spec_from_file_location("generate_project_depgraph_smoke_under_test", _SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ============================================================================
# Test 1: Import smoke —— 检测 NameError（import 缺失）/ 函数签名漂移
# ============================================================================


class TestImportSmoke:
    """验证 generate_project_depgraph.py 模块能正常 import 且关键函数存在。"""

    def test_module_loads_without_name_error(self, gpd):
        """模块能加载且无 NameError。"""
        assert gpd is not None, "generate_project_depgraph 模块加载失败"

    def test_main_function_exists(self, gpd):
        """main() 函数存在（CLI 入口）。"""
        assert hasattr(gpd, "main"), "main 函数缺失"

    def test_write_depgraph_to_db_exists(self, gpd):
        """write_depgraph_to_db() 函数存在（核心 rebuild 入口）。"""
        assert hasattr(gpd, "write_depgraph_to_db"), "write_depgraph_to_db 缺失"

    def test_snapshot_helper_exists(self, gpd):
        """问题B快照函数存在（治本改动生效校验）。"""
        assert hasattr(gpd, "_snapshot_apply_depgraph_design_edges"), (
            "_snapshot_apply_depgraph_design_edges 缺失（问题B治本未生效？）"
        )

    def test_restore_helper_exists(self, gpd):
        """问题B重插函数存在（治本改动生效校验）。"""
        assert hasattr(gpd, "_restore_apply_depgraph_design_edges_by_path"), (
            "_restore_apply_depgraph_design_edges_by_path 缺失（问题B治本未生效？）"
        )


# ============================================================================
# Test 2: CLI smoke —— --help 可运行（只读，不写 DB）
# ============================================================================


class TestCLISmoke:
    """验证 generate_project_depgraph.py CLI 入口可运行。"""

    def test_help_runs(self):
        """--help CLI 命令能正常运行（returncode=0）。

        --help 是 argparse 内置只读命令，不扫描代码、不写 DB，不需要 DB 连接。
        """
        result = subprocess.run(
            [sys.executable, str(_SCRIPT_PATH), "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            cwd=str(_REPO_ROOT),
        )
        assert result.returncode == 0, (
            f"--help CLI 失败 rc={result.returncode}\nstdout: {result.stdout[:500]}\nstderr: {result.stderr[:500]}"
        )


# ============================================================================
# Test 3: DesignEdgeSurvivesRebuild —— 问题B治本逻辑 e2e 验证（事务回滚）
# ============================================================================


@pytest.mark.e2e
class TestDesignEdgeSurvivesRebuild:
    """验证 snapshot→CASCADE删除→按path重插 链路使 design↔production 边跨 rebuild 存活。

    问题B根因：rebuild 删 production 节点时 FK ON DELETE CASCADE 删除引用它的 design 边
    （apply_depgraph 登记的，valid_since IS NULL）。design↔design 边因两端 design 节点
    不被删而存活。治本：删前快照（含端点 path），rebuild 后按 path 重插。

    本测试在可回滚事务内直接验证两个 helper 协作，不运行 --force 全量 rebuild
    （会写生产 DB、破坏其他会话）。conn.rollback() 保证零持久副作用。
    用与 write_depgraph_to_db 相同的 DictCursor 连接（gpd.get_pg_conn_with_dict_cursor）。
    """

    def _get_conn(self, gpd):
        try:
            return gpd.get_pg_conn_with_dict_cursor(autocommit=False)
        except Exception as e:
            pytest.skip(f"PostgreSQL depgraph 不可达（CI 环境？）: {e}")

    def test_design_edge_survives_via_path_remap(self, gpd):
        """design↔production 边：删 production 端→CASCADE删边→重建production端→按path重插→边存活。"""
        if not hasattr(gpd, "_snapshot_apply_depgraph_design_edges"):
            pytest.skip("问题B快照函数不存在（治本改动未生效？）")
        if not hasattr(gpd, "_restore_apply_depgraph_design_edges_by_path"):
            pytest.skip("问题B重插函数不存在（治本改动未生效？）")

        conn = self._get_conn(gpd)
        # path 用唯一前缀避免与真实/其他测试数据冲突；blueprint_id=NULL（触发器放行）
        design_path = "__smoke_test_b__design_node__"
        prod_path = "__smoke_test_b__prod_node__"
        try:
            with conn.cursor() as cur:
                # 允许 CASCADE 删除 design 边（模拟 rebuild 的 GUC 设置；SET LOCAL 事务级，rollback 自动还原）
                cur.execute("SET LOCAL app.allow_delete_apply_depgraph_edges = on")

                # 插入测试节点（design 端 + production 端）
                cur.execute(
                    "INSERT INTO nodes (path, design_maturity) VALUES (%s, 'design')",
                    (design_path,),
                )
                cur.execute("SELECT node_id FROM nodes WHERE path = %s", (design_path,))
                design_node_id = cur.fetchone()["node_id"]

                cur.execute(
                    "INSERT INTO nodes (path, design_maturity) VALUES (%s, 'production')",
                    (prod_path,),
                )
                cur.execute("SELECT node_id FROM nodes WHERE path = %s", (prod_path,))
                prod_node_id_old = cur.fetchone()["node_id"]

                # 插入 design 边（apply_depgraph 风格：dep_maturity='design', valid_since IS NULL）
                cur.execute(
                    "INSERT INTO edges (from_node_id, to_node_id, dep_maturity, valid_since, dep_type) "
                    "VALUES (%s, %s, 'design', NULL, 'import')",
                    (design_node_id, prod_node_id_old),
                )

                # 步骤1：快照应含测试边（from_path/to_path 正确）
                snapshot = gpd.snapshot_apply_depgraph_design_edges(cur)
                test_snaps = [r for r in snapshot if r["from_path"] == design_path and r["to_path"] == prod_path]
                assert len(test_snaps) == 1, f"快照应含测试边（design_path→prod_path），实际命中 {len(test_snaps)} 条"

                # 步骤2：删 production 节点 → FK CASCADE 删 design 边
                cur.execute("DELETE FROM nodes WHERE path = %s", (prod_path,))
                cur.execute(
                    "SELECT 1 FROM edges WHERE from_node_id = %s AND to_node_id = %s "
                    "AND dep_maturity = 'design' AND valid_since IS NULL",
                    (design_node_id, prod_node_id_old),
                )
                assert cur.fetchone() is None, "CASCADE 删除后测试边应不存在"

                # 步骤3：重建 production 节点（同 path，新 node_id，模拟 rebuild 端点漂移）
                cur.execute(
                    "INSERT INTO nodes (path, design_maturity) VALUES (%s, 'production')",
                    (prod_path,),
                )
                cur.execute("SELECT node_id FROM nodes WHERE path = %s", (prod_path,))
                prod_node_id_new = cur.fetchone()["node_id"]
                assert prod_node_id_new != prod_node_id_old, "重建后 node_id 应漂移（rebuild 语义）"

                # 构建最小 path→node_id 映射（仅测试 path；真实边路径不在其中→被跳过，零副作用）
                path_to_db_node_id = {design_path: design_node_id, prod_path: prod_node_id_new}

                # 步骤4：按 path 重插
                gpd.restore_apply_depgraph_design_edges_by_path(cur, snapshot, path_to_db_node_id)

                # 步骤5：断言测试边按 path 重映射后存活（from=design_node_id 不变，to=prod_node_id_new 已重映射）
                cur.execute(
                    "SELECT 1 FROM edges WHERE from_node_id = %s AND to_node_id = %s "
                    "AND dep_maturity = 'design' AND valid_since IS NULL",
                    (design_node_id, prod_node_id_new),
                )
                assert cur.fetchone() is not None, (
                    "重插后测试边应存活（from=design_node_id 不变，to=prod_node_id_new 已按 path 重映射）"
                )
        finally:
            conn.rollback()
            conn.close()
