# [BLUEPRINT] SH-DB-003 | docs/02_enterprise_architecture/04_architecture_principles_decisions/panorama/battle_map_positioning.md | §battlemap
# [MODULE] zephyr.governance.persistence.battle_map_reader
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.persistence.battlemap_schema (get_battle_map_pg_connection); zephyr.governance.persistence.pg_wrapper (_PgConnExecuteWrapper)
# [CONSUMERS] scripts/governance/apply_battle_map.py; scripts/governance/align_battle_map.py; scripts/governance/generate_battle_map_diagram.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只读查询; 参数化防注入; 懒加载连接; 与 depgraph 共享 PG 实例（不同表）; 双向查询是核心
# [MODIFY-GUARD] 修改需同步更新 tests/test_battle_map_reader.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 连接失败抛 RuntimeError; 查询失败抛 psycopg2.Error
# [TESTS] tests/test_battle_map_reader.py
# [TTL] permanent
"""
battle_map_reader.py — 作战地图数据库只读查询工具模块

[BLUEPRINT] SH-DB-003 | battle_map_positioning.md | §battlemap
[MODULE] zephyr.governance.persistence.battle_map_reader
[INVARIANTS] 只读查询; 参数化防注入; 懒加载连接; JSONB 字段自动解析; 双向查询
[CONSUMERS] apply_battle_map.py; align_battle_map.py; generate_battle_map_diagram.py
[STABILITY] evolving
[SAFETY] M
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] 连接失败抛 RuntimeError; 查询失败抛 psycopg2.Error

提供从 battlemap (PostgreSQL) 读取作战地图数据的统一接口，
替代直接查询 3 张 battle_map_* 表的方式。

3 张表：
  - battle_map_steps    — 作战环节（11列，JSONB indicators 6件套）
  - battle_map_anchors  — 双向锚点（7列，环节↔各图模块/候选/蓝图）
  - battle_map_edges    — 环节流转（6列，data_flow/trigger/degradation）

双向查询（本模块灵魂，battle_map_positioning.md §七）：
  - 方向A（环节→模块）：get_anchors_by_step(step_id) — 写决策时查环节落地
  - 方向B（模块→环节）：get_steps_by_target(target_graph, target_id) — 看模块时查作战位置

与 DecisionGraphReader 的关系：
  - 复用同一 PostgreSQL 实例（不同表前缀 battle_map_*）
  - 连接由 battlemap_schema.get_battle_map_pg_connection() 派生
  - 设计模式与 DecisionGraphReader 完全一致（_PgConnExecuteWrapper + 懒加载）

使用方式：
    from zephyr.governance.persistence.battle_map_reader import BattleMapReader
    reader = BattleMapReader()
    steps = reader.get_steps_by_flow_stage('buy_flow')
    anchors = reader.get_anchors_by_step('BM-BUY-03')           # 方向A
    steps = reader.get_steps_by_target('depgraph', 'MOD-xxx')   # 方向B
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from zephyr.governance.persistence.battlemap_schema import (
    get_battle_map_pg_connection,
)
from zephyr.governance.persistence.pg_wrapper import _PgConnExecuteWrapper

# JSONB 字段名（自动解析为 dict/list）
_JSONB_STEP_FIELDS = ("indicators",)


def _parse_jsonb(row: dict, fields: tuple[str, ...]) -> dict:
    """将 JSONB 字段从字符串解析为 Python 对象（原地修改 row）。"""
    for f in fields:
        v = row.get(f)
        if isinstance(v, str) and v:
            try:
                row[f] = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                pass  # 保留原字符串
    return row


class BattleMapReader:
    """作战地图数据库只读读取器。

    懒加载连接，可作 context manager 使用：
        with BattleMapReader() as reader:
            steps = reader.get_all_steps()
    """

    def __init__(self, db_path: str | Path | None = None) -> None:
        # db_path 保留向后兼容（PG 模式下由 battlemap_schema 管理连接配置）
        self._conn: _PgConnExecuteWrapper | None = None

    def _get_conn(self) -> _PgConnExecuteWrapper:
        if self._conn is None:
            self._conn = _PgConnExecuteWrapper(
                get_battle_map_pg_connection(autocommit=True)
            )
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> BattleMapReader:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    # ── 环节查询（battle_map_steps）──────────────────────────────

    def get_all_steps(self) -> list[dict[str, Any]]:
        """获取所有作战环节（按 flow_stage, sort_order 排序，自动解析 indicators JSONB）。"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM battle_map_steps ORDER BY flow_stage, sort_order"
        )
        return [_parse_jsonb(dict(row), _JSONB_STEP_FIELDS) for row in cursor.fetchall()]

    def get_step_by_id(self, step_id: str) -> dict[str, Any] | None:
        """按 step_id 精确查询环节（自动解析 indicators JSONB）。"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM battle_map_steps WHERE step_id = %s", (step_id,)
        )
        row = cursor.fetchone()
        return _parse_jsonb(dict(row), _JSONB_STEP_FIELDS) if row else None

    def get_steps_by_flow_stage(self, flow_stage: str) -> list[dict[str, Any]]:
        """按 flow_stage（stock_selection/buy_flow/.../reconciliation）查询环节。

        生成器 generate_battle_map_diagram.py 按阶段生成 07_ battle_map 视图用。
        """
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM battle_map_steps WHERE flow_stage = %s ORDER BY sort_order",
            (flow_stage,),
        )
        return [_parse_jsonb(dict(row), _JSONB_STEP_FIELDS) for row in cursor.fetchall()]

    def get_steps_by_design_maturity(self, design_maturity: str) -> list[dict[str, Any]]:
        """按 design_maturity（design/production）查询环节。"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM battle_map_steps WHERE design_maturity = %s ORDER BY flow_stage, sort_order",
            (design_maturity,),
        )
        return [_parse_jsonb(dict(row), _JSONB_STEP_FIELDS) for row in cursor.fetchall()]

    # ── 锚点查询（battle_map_anchors）—— 双向查找核心 ─────────────

    def get_all_anchors(self) -> list[dict[str, Any]]:
        """获取所有锚点（按 step_id 排序）。"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM battle_map_anchors ORDER BY step_id, anchor_id"
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_anchor_by_id(self, anchor_id: int) -> dict[str, Any] | None:
        """按 anchor_id 精确查询锚点。"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM battle_map_anchors WHERE anchor_id = %s", (anchor_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_anchors_by_step(self, step_id: str) -> list[dict[str, Any]]:
        """【方向A：环节→模块】查询环节的所有锚点（写决策时查环节落地）。

        返回该环节挂载的所有模块/候选/蓝图/决策节点/数据流节点。
        每个 anchor 带 target_graph/target_id/target_role/status_snapshot。
        """
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM battle_map_anchors WHERE step_id = %s ORDER BY target_role, anchor_id",
            (step_id,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_steps_by_target(self, target_graph: str, target_id: str) -> list[dict[str, Any]]:
        """【方向B：模块→环节】查询目标模块对应的作战环节（看模块时查作战位置）。

        返回该模块（depgraph/candidate/.../节点）服务的所有作战环节。
        每个 step 带完整环节信息（含 indicators JSONB）。

        :param target_graph: depgraph/dataflowgraph/decisiongraph/candidate/blueprint
        :param target_id: 目标图里的节点 id（module_id/candidate_id/...）
        """
        conn = self._get_conn()
        cursor = conn.execute(
            """
            SELECT s.* FROM battle_map_steps s
            JOIN battle_map_anchors a ON s.step_id = a.step_id
            WHERE a.target_graph = %s AND a.target_id = %s
            ORDER BY s.flow_stage, s.sort_order
            """,
            (target_graph, target_id),
        )
        return [_parse_jsonb(dict(row), _JSONB_STEP_FIELDS) for row in cursor.fetchall()]

    def get_anchors_by_target(self, target_graph: str, target_id: str) -> list[dict[str, Any]]:
        """查询指向特定目标的所有锚点（含所属 step 信息）。"""
        conn = self._get_conn()
        cursor = conn.execute(
            """
            SELECT a.*, s.step_name, s.flow_stage
            FROM battle_map_anchors a
            JOIN battle_map_steps s ON a.step_id = s.step_id
            WHERE a.target_graph = %s AND a.target_id = %s
            ORDER BY s.flow_stage, s.sort_order
            """,
            (target_graph, target_id),
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_steps_with_anchors(self, flow_stage: str | None = None) -> list[dict[str, Any]]:
        """获取环节 + 其所有锚点（生成器批量渲染用）。

        返回 [{step字段..., anchors: [anchor字段...]}]。
        :param flow_stage: 可选，按阶段过滤
        """
        conn = self._get_conn()
        if flow_stage is None:
            cursor = conn.execute(
                "SELECT * FROM battle_map_steps ORDER BY flow_stage, sort_order"
            )
        else:
            cursor = conn.execute(
                "SELECT * FROM battle_map_steps WHERE flow_stage = %s ORDER BY sort_order",
                (flow_stage,),
            )
        steps = [_parse_jsonb(dict(row), _JSONB_STEP_FIELDS) for row in cursor.fetchall()]
        # 批量查询锚点，避免 N+1
        if steps:
            step_ids = [s["step_id"] for s in steps]
            placeholders = ", ".join(["%s"] * len(step_ids))
            cursor = conn.execute(
                f"SELECT * FROM battle_map_anchors WHERE step_id IN ({placeholders}) ORDER BY step_id, target_role",  # noqa: S608
                step_ids,
            )
            anchors_by_step: dict[str, list[dict[str, Any]]] = {}
            for row in cursor.fetchall():
                r = dict(row)
                anchors_by_step.setdefault(r["step_id"], []).append(r)
            for s in steps:
                s["anchors"] = anchors_by_step.get(s["step_id"], [])
        return steps

    # ── 边查询（battle_map_edges）─────────────────────────────────

    def get_all_edges(self) -> list[dict[str, Any]]:
        """获取所有环节流转边（按 edge_id 排序）。"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM battle_map_edges ORDER BY edge_id")
        return [dict(row) for row in cursor.fetchall()]

    def get_edges_from_step(self, from_step_id: str) -> list[dict[str, Any]]:
        """查询从指定环节出发的所有流转边。"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM battle_map_edges WHERE from_step_id = %s ORDER BY edge_id",
            (from_step_id,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_edges_to_step(self, to_step_id: str) -> list[dict[str, Any]]:
        """查询指向指定环节的所有流转边。"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM battle_map_edges WHERE to_step_id = %s ORDER BY edge_id",
            (to_step_id,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_edges_by_type(self, edge_type: str) -> list[dict[str, Any]]:
        """按 edge_type（data_flow/trigger/degradation）查询边。"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM battle_map_edges WHERE edge_type = %s ORDER BY edge_id",
            (edge_type,),
        )
        return [dict(row) for row in cursor.fetchall()]

    # ── 图拓扑查询 ──────────────────────────────────────────────

    def get_adjacency_forward(self) -> dict[str, list[str]]:
        """构建前向邻接表 {from_step_id: [to_step_id, ...]}。"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT from_step_id, to_step_id FROM battle_map_edges ORDER BY from_step_id"
        )
        adj: dict[str, list[str]] = {}
        for row in cursor.fetchall():
            r = dict(row)
            adj.setdefault(r["from_step_id"], []).append(r["to_step_id"])
        return adj

    def get_adjacency_reverse(self) -> dict[str, list[str]]:
        """构建反向邻接表 {to_step_id: [from_step_id, ...]}。"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT from_step_id, to_step_id FROM battle_map_edges ORDER BY to_step_id"
        )
        adj: dict[str, list[str]] = {}
        for row in cursor.fetchall():
            r = dict(row)
            adj.setdefault(r["to_step_id"], []).append(r["from_step_id"])
        return adj

    def get_full_battle_map(self) -> dict[str, Any]:
        """导出完整作战地图（steps + anchors + edges）。

        用于生成器、对齐校验、外部可视化工具。
        """
        return {
            "steps": self.get_all_steps(),
            "anchors": self.get_all_anchors(),
            "edges": self.get_all_edges(),
        }

    # ── 统计查询 ──────────────────────────────────────────────

    def get_step_count(self) -> int:
        """获取作战环节总数。"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT COUNT(*) AS cnt FROM battle_map_steps")
        return cursor.fetchone()["cnt"]

    def get_anchor_count(self) -> int:
        """获取锚点总数。"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT COUNT(*) AS cnt FROM battle_map_anchors")
        return cursor.fetchone()["cnt"]

    def get_edge_count(self) -> int:
        """获取流转边总数。"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT COUNT(*) AS cnt FROM battle_map_edges")
        return cursor.fetchone()["cnt"]

    def get_step_count_by_flow_stage(self) -> dict[str, int]:
        """按 flow_stage 分组统计环节数。"""
        conn = self._get_conn()
        cursor = conn.execute(
            """
            SELECT flow_stage, COUNT(*) AS cnt
            FROM battle_map_steps
            GROUP BY flow_stage
            ORDER BY flow_stage
            """
        )
        return {row["flow_stage"]: row["cnt"] for row in cursor.fetchall()}

    # ── 不变量校验查询（BM-INV-001~002）────────────────────────

    def find_steps_without_anchors(self) -> list[dict[str, Any]]:
        """查找违反 BM-INV-001（环节至少一个锚点）的环节。

        环节无锚点=悬空决策=幻觉风险。返回无锚点的 steps 列表。
        align_battle_map.py 君子协定告警用。

        V0.4.0 父子嵌套豁免：子环节（parent_step_id 非空）若父环节有锚点，
        则不算孤儿——锚点通过父环节间接覆盖。只有"自身无锚点 AND 父环节也无锚点"
        的子环节才报孤儿（父子全悬空）。
        """
        conn = self._get_conn()
        cursor = conn.execute(
            """
            SELECT s.* FROM battle_map_steps s
            WHERE NOT EXISTS (
                SELECT 1 FROM battle_map_anchors a WHERE a.step_id = s.step_id
            )
            AND NOT EXISTS (
                -- V0.4.0 子环节豁免：父环节有锚点则子环节不算孤儿
                SELECT 1 FROM battle_map_anchors a2
                WHERE a2.step_id = s.parent_step_id
            )
            ORDER BY s.flow_stage, s.sort_order
            """
        )
        return [_parse_jsonb(dict(row), _JSONB_STEP_FIELDS) for row in cursor.fetchall()]

    def find_orphan_anchors_by_graph(self, target_graph: str, valid_ids: set[str]) -> list[dict[str, Any]]:
        """查找违反 BM-INV-002（锚点 target_id 必须存在）的幽灵锚点。

        :param target_graph: 要校验的图（如 'depgraph'）
        :param valid_ids: 该图所有合法 id 集合（调用方从对应图/仓库查得）
        :return: target_id 不在 valid_ids 中的锚点列表
        """
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM battle_map_anchors WHERE target_graph = %s ORDER BY anchor_id",
            (target_graph,),
        )
        return [
            dict(row) for row in cursor.fetchall()
            if dict(row)["target_id"] not in valid_ids
        ]


if __name__ == "__main__":
    # CLI 入口：python -m zephyr.governance.persistence.battle_map_reader
    # 打印作战地图摘要（用于快速健康检查）
    reader = BattleMapReader()
    try:
        print(f"steps:   {reader.get_step_count()}")
        print(f"anchors: {reader.get_anchor_count()}")
        print(f"edges:   {reader.get_edge_count()}")
        by_stage = reader.get_step_count_by_flow_stage()
        if by_stage:
            print("steps per flow_stage:")
            for stage, cnt in by_stage.items():
                print(f"  {stage}: {cnt}")
        orphans = reader.find_steps_without_anchors()
        if orphans:
            print(f"⚠️ BM-INV-001 违反: {len(orphans)} 个环节无锚点（悬空决策）:")
            for s in orphans:
                print(f"  - {s['step_id']}: {s['step_name']}")
    finally:
        reader.close()
