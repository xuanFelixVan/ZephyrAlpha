# [BLUEPRINT] MOD-D5_ARCH_TOOLS | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""验证5个之前不可达模块（BM-SEL-06/07/09/10/15）的依赖边是否真的能跑通链路。

测试目标：
  1. 5条修复边在 depgraph 中存在（edge_id 10892829~10892833）
  2. BFS 从上游起点能到达5个模块（拓扑可达性）
  3. 数据流上游边存在性（每个模块至少有1条上游边，非孤儿）

修复历史（2026-08-03）：
  5个模块因缺上游依赖边而拓扑不可达，登记5条修复边后全部可达：
    - 02→03 因子池→市场状态 (修复07/15，03→07/03→15 已存在)
    - 11→06 传导路径图→跨市场传导 (修复06)
    - L0→06/L0→09/L0→10 全球市场数据→跨市场传导/调整周期/行情生命周期
"""

import sys
from pathlib import Path

import pytest

_THIS = Path(__file__).resolve()
_GOV = str(next(p for p in _THIS.parents if (p / "scripts" / "governance").exists()))
if _GOV not in sys.path:
    sys.path.insert(0, _GOV)

from zephyr.governance.persistence.battlemap_schema import get_battle_map_pg_connection

# 5个之前不可达的模块（step_id → module_id）
UNREACHABLE_5 = {
    "BM-SEL-06": "MOD-SIG-038",  # 跨市场传导感知
    "BM-SEL-07": "MOD-SIG-039",  # 体制转换检测
    "BM-SEL-09": "MOD-SIG-040",  # 调整周期追踪
    "BM-SEL-10": "MOD-SIG-041",  # 行情生命周期阶段
    "BM-SEL-15": "MOD-SIG-045",  # Survival止盈止损时间预测
}

# 5条修复边 (from_blueprint_id, to_blueprint_id, 描述)
FIX_EDGES = [
    ("MOD-L02-001", "MOD-SIG-036", "02→03 因子池→市场状态 (修复07/15不可达)"),
    ("MOD-SIG-042", "MOD-SIG-038", "11→06 传导路径图→跨市场传导 (修复06不可达)"),
    ("MOD-MKT-006", "MOD-SIG-038", "L0→06 全球市场数据→跨市场传导"),
    ("MOD-MKT-006", "MOD-SIG-040", "L0→09 板块新高占比→调整周期"),
    ("MOD-MKT-006", "MOD-SIG-041", "L0→10 板块新高占比趋势→行情生命周期"),
]

# BFS 起点（production 上游 + 已可达的 design 上游）
BFS_STARTS = ["MOD-L02-001", "MOD-MKT-006", "MOD-SIG-042"]


@pytest.fixture(scope="module")
def db_conn():
    """共享数据库连接（真实 battle_map PG 集成验证，需本机 PG(5432) 可用）。"""
    conn = get_battle_map_pg_connection()
    yield conn
    conn.close()


@pytest.fixture(scope="module")
def adjacency(db_conn):
    """预构建 depgraph 邻接表（from → [to1, to2, ...]）。"""
    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT n_from.blueprint_id, n_to.blueprint_id "
            "FROM edges e "
            "JOIN nodes n_from ON n_from.node_id = e.from_node_id "
            "JOIN nodes n_to ON n_to.node_id = e.to_node_id"
        )
        adj: dict[str, list[str]] = {}
        for from_bp, to_bp in cur.fetchall():
            adj.setdefault(from_bp, []).append(to_bp)
    return adj


class TestFixEdgesExist:
    """测试1：5条修复边在 depgraph 中存在。"""

    @pytest.mark.parametrize("from_bp,to_bp,desc", FIX_EDGES)
    def test_fix_edge_exists(self, db_conn, from_bp, to_bp, desc):
        """验证每条修复边在 edges 表中存在。"""
        with db_conn.cursor() as cur:
            cur.execute(
                "SELECT e.edge_id, e.dep_type, e.dep_maturity "
                "FROM edges e "
                "JOIN nodes n_from ON n_from.node_id = e.from_node_id "
                "JOIN nodes n_to ON n_to.node_id = e.to_node_id "
                "WHERE n_from.blueprint_id = %s AND n_to.blueprint_id = %s",
                (from_bp, to_bp),
            )
            rows = cur.fetchall()
        assert len(rows) > 0, f"修复边不存在: {desc} ({from_bp}→{to_bp})"
        eid, dep_type, dep_maturity = rows[0]
        assert dep_maturity == "design", f"{desc}: dep_maturity={dep_maturity}≠design"

    def test_fix_edge_count(self, db_conn):
        """验证5条修复边全部存在（非重复写入）。"""
        found = 0
        with db_conn.cursor() as cur:
            for from_bp, to_bp, _ in FIX_EDGES:
                cur.execute(
                    "SELECT COUNT(*) FROM edges e "
                    "JOIN nodes n_from ON n_from.node_id = e.from_node_id "
                    "JOIN nodes n_to ON n_to.node_id = e.to_node_id "
                    "WHERE n_from.blueprint_id = %s AND n_to.blueprint_id = %s",
                    (from_bp, to_bp),
                )
                if cur.fetchone()[0] > 0:
                    found += 1
        assert found == len(FIX_EDGES), f"修复边存在数={found}≠{len(FIX_EDGES)}"


class TestBfsReachable:
    """测试2：BFS 从上游起点能到达5个模块。"""

    @staticmethod
    def _bfs_reachable(adj: dict, starts: list, target: str) -> bool:
        """BFS 判断 target 是否从 starts 可达。"""
        visited: set[str] = set()
        queue = list(starts)
        while queue:
            node = queue.pop(0)
            if node == target:
                return True
            if node in visited:
                continue
            visited.add(node)
            queue.extend(adj.get(node, []))
        return False

    @pytest.mark.parametrize("step_id,module_id", list(UNREACHABLE_5.items()))
    def test_module_reachable_from_upstream(self, adjacency, step_id, module_id):
        """验证5个模块从上游起点 BFS 可达（修复后应全部可达）。"""
        reachable = self._bfs_reachable(adjacency, BFS_STARTS, module_id)
        assert reachable, f"{step_id}({module_id}) 从上游起点 {BFS_STARTS} BFS 不可达——修复边可能缺失或断链"

    def test_all_5_reachable_summary(self, adjacency):
        """汇总验证：5个模块全部可达。"""
        unreachable = []
        for step_id, module_id in UNREACHABLE_5.items():
            if not self._bfs_reachable(adjacency, BFS_STARTS, module_id):
                unreachable.append(f"{step_id}({module_id})")
        assert not unreachable, f"以下模块不可达: {unreachable}"


class TestDataflowChain:
    """测试3：数据流上游边存在性（每个模块非孤儿）。"""

    @pytest.mark.parametrize("module_id", list(UNREACHABLE_5.values()))
    def test_module_has_upstream_edges(self, db_conn, module_id):
        """验证每个模块在数据库中有至少1条上游边（非拓扑孤儿）。"""
        with db_conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM edges e "
                "JOIN nodes n_to ON n_to.node_id = e.to_node_id "
                "WHERE n_to.blueprint_id = %s",
                (module_id,),
            )
            count = cur.fetchone()[0]
        assert count > 0, f"{module_id} 无任何上游边（拓扑孤儿）"

    def test_fix_edge_targets_cover_unreachable_5(self, db_conn):
        """验证5条修复边的目标覆盖5个不可达模块的入口点。

        修复边目标：MOD-SIG-036(03,07/15的上游), MOD-SIG-038(06),
                    MOD-SIG-040(09), MOD-SIG-041(10)。
        07/15 通过 03→07/03→15 已有边间接受益。
        """
        fix_targets = {to_bp for _, to_bp, _ in FIX_EDGES}
        # 03 是 07/15 的上游桥梁；06/09/10 是直接修复目标
        expected_direct_targets = {
            "MOD-SIG-036",  # 03→07, 03→15 已存在
            "MOD-SIG-038",  # 06 直接修复
            "MOD-SIG-040",  # 09 直接修复
            "MOD-SIG-041",  # 10 直接修复
        }
        assert fix_targets == expected_direct_targets, f"修复边目标不匹配: {fix_targets}≠{expected_direct_targets}"

    @pytest.mark.parametrize("step_id,module_id", list(UNREACHABLE_5.items()))
    def test_module_node_exists(self, db_conn, step_id, module_id):
        """验证5个模块在 depgraph nodes 表中存在（设计态或已建成节点）。

        2026-08-23 长城任务批1/批2 实证：MOD-SIG-036/038/040/041（REGIME 批）与
        MOD-SIG-045（SIGNAL 批）已建成转态（build_status=testing、design_maturity
        可随生成器 rescan 转 production）——断言从"planned 设计态"演进为"节点存在
        且 build_status 合法"，链路治理意图（节点在图中）不变。
        """
        with db_conn.cursor() as cur:
            cur.execute(
                "SELECT build_status, design_maturity FROM nodes "
                "WHERE blueprint_id = %s",
                (module_id,),
            )
            rows = cur.fetchall()
        assert len(rows) > 0, f"{step_id}({module_id}) 无 depgraph 节点"
        build_status, maturity = rows[0]
        assert build_status in ("planned", "generated", "testing", "stable", "production"), (
            f"{step_id}({module_id}): build_status={build_status} 非法"
        )
        assert maturity in ("design", "production"), (
            f"{step_id}({module_id}): maturity={maturity} 非法"
        )
