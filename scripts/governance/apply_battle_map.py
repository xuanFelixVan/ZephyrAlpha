# [BLUEPRINT] MOD-GOV_SCRIPTS | docs/02_enterprise_architecture/04_architecture_principles_decisions/panorama/battle_map_positioning.md | §battlemap
# [MODULE] scripts.governance.apply_battle_map
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__; zephyr.governance.persistence.battlemap_schema (get_battle_map_pg_connection); zephyr.governance.persistence.battle_map_reader (BattleMapReader)
# [CONSUMERS] AI 写入 battlemap 环节/锚点/边时调用
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] pg_advisory_lock 写锁; BM-INV-001~002 校验; 事务回滚
# [MODIFY-GUARD] 对标 scripts/governance/apply_decisiongraph.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 违反不变量→exit 1; DB 写入失败→exit 4
# [TESTS] tests/test_apply_battle_map.py
# [A_module] module_id=MOD-GOV_SCRIPTS | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
[BLUEPRINT] | scripts/governance/apply_battle_map.py | §battlemap
[MODULE] scripts.governance.apply_battle_map
[INVARIANTS] pg_advisory_lock 写锁; BM-INV-001~002 校验; 事务回滚
[MODIFY-GUARD] 对标 scripts/governance/apply_decisiongraph.py
[CONSUMERS] AI 写入 battlemap 环节/锚点/边时调用
[STABILITY] evolving
[SAFETY] M
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] 违反不变量→exit 1; DB 写入失败→exit 4
[TESTS] 无

apply_battle_map.py — 作战地图写入入口（对标 apply_decisiongraph.py）

提供 battle_map_steps/battle_map_anchors/battle_map_edges 的写入操作。
  - 环节操作：add_step / update_step / remove_step
  - 锚点操作：add_anchor / remove_anchor
  - 边操作：add_edge / remove_edge
  - 批量操作：--batch（JSON 数组）

四条承重墙不变量（BM-INV-001~004）在写入时校验：
  - BM-INV-001: 环节无锚点=悬空决策（君子协定，align_battle_map.py 告警，写入时不阻断）
  - BM-INV-002: 锚点 target_id 必须能在 target_graph 找到（add_anchor 时可选校验，--strict-target-check）

pg_advisory_lock key：
  depgraph       = 424242
  dataflowgraph  = 424243
  decisiongraph = 424244
  battlemap      = 424245  ← 本脚本使用

用法:
  # 添加作战环节
  python scripts/governance/apply_battle_map.py \\
      --add-step \\
      --step-id BM-BUY-03 --step-name "四轨融合" \\
      --flow-stage buy_flow --layer L2A --sort-order 30 \\
      --narrative-ref BM-BUY-03 \\
      --indicators-json '{"trigger":{"condition":"满足2/3"}}'

  # 添加锚点（环节↔模块双向关联）
  python scripts/governance/apply_battle_map.py \\
      --add-anchor --step-id BM-BUY-03 \\
      --target-graph depgraph --target-id MOD-L05-001 \\
      --target-role primary --status-snapshot planned

  # 添加流转边
  python scripts/governance/apply_battle_map.py \\
      --add-edge --from-step-id BM-BUY-03 --to-step-id BM-POS-01 \\
      --edge-type data_flow --label "portfolio_target"

  # 批量操作（JSON 数组，用于草图迁移批量登记）
  python scripts/governance/apply_battle_map.py --batch ops.json --dry-run

  # 查询支持的 op 列表
  python scripts/governance/apply_battle_map.py --list-ops
"""

from __future__ import annotations

__manifest__ = """
args: []
description: battlemap 作战地图写入入口（对标 apply_decisiongraph.py）
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""

import argparse
import contextlib
import json
import os
import sys
from pathlib import Path
from typing import Any

from psycopg2.extras import RealDictCursor

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

from _shared.constants import EXIT_FINDINGS

from zephyr.governance.persistence.battlemap_schema import (
    _DESIGN_MATURITIES,
    _EDGE_TYPES,
    _FLOW_STAGES,
    _TARGET_GRAPHS,
    _TARGET_ROLES,
    get_battle_map_pg_connection,
)

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

# pg_advisory_lock key（depgraph=424242, dataflowgraph=424243, decisiongraph=424244, battlemap=424245）
_BATTLEMAP_LOCK_KEY = 424245

# 受控词表（从 battlemap_schema 导入，SSoT）
_VALID_FLOW_STAGES = set(_FLOW_STAGES)
_VALID_TARGET_GRAPHS = set(_TARGET_GRAPHS)
_VALID_TARGET_ROLES = set(_TARGET_ROLES)
_VALID_EDGE_TYPES = set(_EDGE_TYPES)
_VALID_DESIGN_MATURITIES = set(_DESIGN_MATURITIES)

# 支持的 op 列表
_STEP_OPS = frozenset({"add_step", "update_step", "remove_step"})
_ANCHOR_OPS = frozenset({"add_anchor", "remove_anchor"})
_EDGE_OPS = frozenset({"add_edge", "remove_edge"})
_ALL_OPS = _STEP_OPS | _ANCHOR_OPS | _EDGE_OPS

# update_step 允许更新的字段白名单（安全约束：禁止改 step_id）
_STEP_UPDATABLE_FIELDS = {
    "step_name", "flow_stage", "layer", "sort_order",
    "narrative_ref", "indicators", "source_ref",
    "parent_step_id", "depth", "design_maturity",
}
_STEP_JSONB_FIELDS = {"indicators"}


def _get_supported_ops() -> set[str]:
    """返回支持的 op 集合（对标 apply_decisiongraph.py _get_supported_ops）。"""
    return _ALL_OPS


# ---------------------------------------------------------------------------
# 写锁
# ---------------------------------------------------------------------------


@contextlib.contextmanager
def _db_write_lock(conn):
    """获取 battlemap pg_advisory_lock（对标 apply_decisiongraph.py _db_write_lock）。"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT pg_advisory_lock(%s)", (_BATTLEMAP_LOCK_KEY,))
    try:
        yield
    finally:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT pg_advisory_unlock(%s)", (_BATTLEMAP_LOCK_KEY,))


# ---------------------------------------------------------------------------
# 环节操作（battle_map_steps）
# ---------------------------------------------------------------------------


def op_add_step(
    conn,
    *,
    step_id: str,
    step_name: str,
    flow_stage: str,
    layer: str | None = None,
    sort_order: int = 0,
    narrative_ref: str | None = None,
    indicators: dict | None = None,
    source_ref: str | None = None,
    parent_step_id: str | None = None,
    depth: int = 0,
    design_maturity: str = "production",
    dry_run: bool = False,
) -> dict:
    """添加作战环节。

    step_id 格式：BM-<阶段缩写>-<序号>，如 BM-BUY-03。
    indicators 是 6 件套结构化数据（trigger/consumes/params/data_flow/code_mapping/degradation）。
    """
    if flow_stage not in _VALID_FLOW_STAGES:
        raise ValueError(
            f"flow_stage '{flow_stage}' 不合法，合法值: {sorted(_VALID_FLOW_STAGES)}"
        )
    if design_maturity not in _VALID_DESIGN_MATURITIES:
        raise ValueError(
            f"design_maturity '{design_maturity}' 不合法，合法值: {sorted(_VALID_DESIGN_MATURITIES)}"
        )
    if not step_id or not step_name:
        raise ValueError("step_id 和 step_name 必填")

    row = {
        "step_id": step_id,
        "step_name": step_name,
        "flow_stage": flow_stage,
        "layer": layer,
        "sort_order": sort_order,
        "narrative_ref": narrative_ref or step_id,
        "indicators": json.dumps(indicators, ensure_ascii=False) if indicators else None,
        "source_ref": source_ref,
        "parent_step_id": parent_step_id,
        "depth": depth,
        "design_maturity": design_maturity,
    }

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT 1 FROM battle_map_steps WHERE step_id = %s", (step_id,))
        if cur.fetchone() is not None:
            raise ValueError(f"step_id '{step_id}' 已存在（PK 约束）")

        # BM-INV-006: 校验父环节存在 + flow_stage 一致（若指定 parent_step_id）
        if parent_step_id is not None:
            cur.execute(
                "SELECT flow_stage FROM battle_map_steps WHERE step_id = %s",
                (parent_step_id,),
            )
            parent_row = cur.fetchone()
            if parent_row is None:
                raise ValueError(
                    f"parent_step_id '{parent_step_id}' 不存在（BM-INV-006）"
                )
            if parent_row["flow_stage"] != flow_stage:
                raise ValueError(
                    f"子环节 flow_stage '{flow_stage}' 与父 '{parent_row['flow_stage']}' "
                    f"不一致（BM-INV-006 防跨阶段嵌套）"
                )

        # BM-INV-006: depth 上限校验（根→子→孙→曾孙，上限3）
        if depth is not None and depth > 3:
            raise ValueError(
                f"depth={depth} > 3（上限根→子→孙→曾孙，BM-INV-006）"
            )

        if dry_run:
            print(f"[DRY-RUN] INSERT step {step_id} ({step_name})")
        else:
            cur.execute(
                """
                INSERT INTO battle_map_steps
                    (step_id, step_name, flow_stage, layer, sort_order,
                     narrative_ref, indicators, source_ref, parent_step_id, depth,
                     design_maturity)
                VALUES (%(step_id)s, %(step_name)s, %(flow_stage)s, %(layer)s, %(sort_order)s,
                        %(narrative_ref)s, %(indicators)s, %(source_ref)s,
                        %(parent_step_id)s, %(depth)s, %(design_maturity)s)
                RETURNING step_id
                """,
                row,
            )
            new_id = cur.fetchone()["step_id"]
            return {"op": "add_step", "step_id": new_id}

    return {"op": "add_step", "dry_run": True, "step_id": step_id}


def op_update_step(
    conn, *, step_id: str, field: str, value: Any, dry_run: bool = False
) -> dict:
    """更新环节字段（仅允许白名单字段，禁止改 step_id）。"""
    if field not in _STEP_UPDATABLE_FIELDS:
        raise ValueError(
            f"field '{field}' 不在允许列表 {_STEP_UPDATABLE_FIELDS}"
        )
    if field == "flow_stage" and value not in _VALID_FLOW_STAGES:
        raise ValueError(f"flow_stage '{value}' 不合法")
    if field == "design_maturity" and value not in _VALID_DESIGN_MATURITIES:
        raise ValueError(f"design_maturity '{value}' 不合法")

    db_value = json.dumps(value, ensure_ascii=False) if field in _STEP_JSONB_FIELDS else value

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT 1 FROM battle_map_steps WHERE step_id = %s", (step_id,))
        if cur.fetchone() is None:
            raise ValueError(f"step_id '{step_id}' 不存在")

        if dry_run:
            print(f"[DRY-RUN] UPDATE step {step_id} {field} = {value!r}")
        else:
            cur.execute(
                f"UPDATE battle_map_steps SET {field} = %s WHERE step_id = %s",  # noqa: S608
                (db_value, step_id),
            )
            return {"op": "update_step", "step_id": step_id, "field": field}

    return {"op": "update_step", "dry_run": True, "step_id": step_id}


def op_remove_step(conn, *, step_id: str, dry_run: bool = False) -> dict:
    """删除环节（ON DELETE CASCADE 级联删除其 anchors 和 edges）。"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT step_name FROM battle_map_steps WHERE step_id = %s", (step_id,)
        )
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"step_id '{step_id}' 不存在")

        if dry_run:
            print(f"[DRY-RUN] DELETE step {step_id} ({row['step_name']}) + 级联 anchors/edges")
        else:
            cur.execute("DELETE FROM battle_map_steps WHERE step_id = %s", (step_id,))
            return {"op": "remove_step", "step_id": step_id}

    return {"op": "remove_step", "dry_run": True, "step_id": step_id}


# ---------------------------------------------------------------------------
# 锚点操作（battle_map_anchors）—— 双向查找真源
# ---------------------------------------------------------------------------


def op_add_anchor(
    conn,
    *,
    step_id: str,
    target_graph: str,
    target_id: str,
    target_role: str = "primary",
    status_snapshot: str | None = None,
    dry_run: bool = False,
) -> dict:
    """添加锚点（环节↔模块/候选/蓝图双向关联）。

    BM-INV-001: 环节无锚点=悬空决策（君子协定，align_battle_map.py 告警）。
    BM-INV-002: target_id 存在性校验由 align_battle_map.py 批量做（跨图校验，apply 不阻断）。
    """
    if target_graph not in _VALID_TARGET_GRAPHS:
        raise ValueError(
            f"target_graph '{target_graph}' 不合法，合法值: {sorted(_VALID_TARGET_GRAPHS)}"
        )
    if target_role not in _VALID_TARGET_ROLES:
        raise ValueError(
            f"target_role '{target_role}' 不合法，合法值: {sorted(_VALID_TARGET_ROLES)}"
        )
    if not target_id:
        raise ValueError("target_id 必填")

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # 校验 step_id 存在
        cur.execute("SELECT 1 FROM battle_map_steps WHERE step_id = %s", (step_id,))
        if cur.fetchone() is None:
            raise ValueError(f"step_id '{step_id}' 不存在（无法挂锚点）")

        # 校验 UNIQUE (step_id, target_graph, target_id)
        cur.execute(
            "SELECT 1 FROM battle_map_anchors WHERE step_id = %s AND target_graph = %s AND target_id = %s",
            (step_id, target_graph, target_id),
        )
        if cur.fetchone() is not None:
            raise ValueError(
                f"锚点已存在: step_id={step_id} target_graph={target_graph} target_id={target_id}"
            )

        if dry_run:
            print(f"[DRY-RUN] INSERT anchor {step_id} → {target_graph}:{target_id} ({target_role})")
        else:
            cur.execute(
                """
                INSERT INTO battle_map_anchors
                    (step_id, target_graph, target_id, target_role, status_snapshot)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING anchor_id
                """,
                (step_id, target_graph, target_id, target_role, status_snapshot),
            )
            new_id = cur.fetchone()["anchor_id"]
            return {"op": "add_anchor", "anchor_id": new_id}

    return {"op": "add_anchor", "dry_run": True, "step_id": step_id}


def op_remove_anchor(conn, *, anchor_id: int, dry_run: bool = False) -> dict:
    """删除锚点。"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT 1 FROM battle_map_anchors WHERE anchor_id = %s", (anchor_id,))
        if cur.fetchone() is None:
            raise ValueError(f"anchor_id {anchor_id} 不存在")

        if dry_run:
            print(f"[DRY-RUN] DELETE anchor {anchor_id}")
        else:
            cur.execute("DELETE FROM battle_map_anchors WHERE anchor_id = %s", (anchor_id,))
            return {"op": "remove_anchor", "anchor_id": anchor_id}

    return {"op": "remove_anchor", "dry_run": True, "anchor_id": anchor_id}


# ---------------------------------------------------------------------------
# 边操作（battle_map_edges）
# ---------------------------------------------------------------------------


def op_add_edge(
    conn,
    *,
    from_step_id: str,
    to_step_id: str,
    edge_type: str,
    label: str | None = None,
    dry_run: bool = False,
) -> dict:
    """添加环节流转边。"""
    if edge_type not in _VALID_EDGE_TYPES:
        raise ValueError(
            f"edge_type '{edge_type}' 不合法，合法值: {sorted(_VALID_EDGE_TYPES)}"
        )
    if from_step_id == to_step_id:
        raise ValueError("from_step_id 不能等于 to_step_id（自环禁止）")

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT 1 FROM battle_map_steps WHERE step_id = %s", (from_step_id,))
        if cur.fetchone() is None:
            raise ValueError(f"from_step_id '{from_step_id}' 不存在")
        cur.execute("SELECT 1 FROM battle_map_steps WHERE step_id = %s", (to_step_id,))
        if cur.fetchone() is None:
            raise ValueError(f"to_step_id '{to_step_id}' 不存在")

        if dry_run:
            print(f"[DRY-RUN] INSERT edge {from_step_id} →{edge_type}→ {to_step_id}")
        else:
            cur.execute(
                """
                INSERT INTO battle_map_edges (from_step_id, to_step_id, edge_type, label)
                VALUES (%s, %s, %s, %s)
                RETURNING edge_id
                """,
                (from_step_id, to_step_id, edge_type, label),
            )
            new_id = cur.fetchone()["edge_id"]
            return {"op": "add_edge", "edge_id": new_id}

    return {"op": "add_edge", "dry_run": True, "from_step_id": from_step_id}


def op_remove_edge(conn, *, edge_id: int, dry_run: bool = False) -> dict:
    """删除流转边。"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT 1 FROM battle_map_edges WHERE edge_id = %s", (edge_id,))
        if cur.fetchone() is None:
            raise ValueError(f"edge_id {edge_id} 不存在")

        if dry_run:
            print(f"[DRY-RUN] DELETE edge {edge_id}")
        else:
            cur.execute("DELETE FROM battle_map_edges WHERE edge_id = %s", (edge_id,))
            return {"op": "remove_edge", "edge_id": edge_id}

    return {"op": "remove_edge", "dry_run": True, "edge_id": edge_id}


# ---------------------------------------------------------------------------
# op 分发表
# ---------------------------------------------------------------------------

_OP_DISPATCH = {
    "add_step": op_add_step,
    "update_step": op_update_step,
    "remove_step": op_remove_step,
    "add_anchor": op_add_anchor,
    "remove_anchor": op_remove_anchor,
    "add_edge": op_add_edge,
    "remove_edge": op_remove_edge,
}


# ---------------------------------------------------------------------------
# 批量操作
# ---------------------------------------------------------------------------


def _run_batch(conn, ops: list[dict], dry_run: bool = False) -> list[dict]:
    """执行批量 op（JSON 数组，对标 apply_decisiongraph.py --batch）。

    每个 op 是 {"op": "add_step", "step_id": ..., ...}。
    任一 op 失败则回滚整个批次（事务原子性）。
    """
    results: list[dict] = []
    for i, op_spec in enumerate(ops):
        if not isinstance(op_spec, dict) or "op" not in op_spec:
            raise ValueError(f"batch[{i}] 格式错误：缺少 'op' 字段")
        op_name = op_spec["op"]
        if op_name not in _OP_DISPATCH:
            raise ValueError(f"batch[{i}] op '{op_name}' 不支持，合法: {sorted(_ALL_OPS)}")
        kwargs = {k: v for k, v in op_spec.items() if k != "op"}
        kwargs["dry_run"] = dry_run
        result = _OP_DISPATCH[op_name](conn, **kwargs)
        results.append(result)
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_argparser() -> argparse.ArgumentParser:
    """_build_argparser implementation."""
    p = argparse.ArgumentParser(
        description="battlemap 作战地图写入入口（对标 apply_decisiongraph.py）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--list-ops", action="store_true", help="列出支持的 op")
    p.add_argument("--dry-run", action="store_true", help="只打印不写入")

    # 环节操作
    p.add_argument("--add-step", action="store_true", help="添加作战环节")
    p.add_argument("--update-step", action="store_true", help="更新环节字段")
    p.add_argument("--remove-step", action="store_true", help="删除环节（级联删 anchors/edges）")
    p.add_argument("--step-id", help="环节 ID（如 BM-BUY-03）")
    p.add_argument("--step-name", help="环节中文名")
    p.add_argument("--flow-stage", help="阶段（stock_selection/buy_flow/.../reconciliation）")
    p.add_argument("--layer", help="映射层（L0/L1/L2A/.../横切）")
    p.add_argument("--sort-order", type=int, default=0, help="环节顺序")
    p.add_argument("--narrative-ref", help="翻译真源 step_id（默认等于 step_id）")
    p.add_argument("--indicators-json", help="indicators 6件套 JSON 字符串")
    p.add_argument("--indicators-file", help="indicators 6件套 JSON 文件路径")
    p.add_argument("--source-ref", help="出处（草图§x / 代码路径）")
    p.add_argument("--design-maturity", default="production", help="design/production")

    # 锚点操作
    p.add_argument("--add-anchor", action="store_true", help="添加锚点（环节↔模块）")
    p.add_argument("--remove-anchor", action="store_true", help="删除锚点")
    p.add_argument("--anchor-id", type=int, help="锚点 ID")
    p.add_argument("--target-graph", help="目标图（depgraph/dataflowgraph/decisiongraph/candidate/blueprint）")
    p.add_argument("--target-id", help="目标节点 ID")
    p.add_argument("--target-role", default="primary", help="角色（primary/supplement/degradation）")
    p.add_argument("--status-snapshot", help="状态快照（production/planned/deprecated）")

    # 边操作
    p.add_argument("--add-edge", action="store_true", help="添加流转边")
    p.add_argument("--remove-edge", action="store_true", help="删除流转边")
    p.add_argument("--edge-id", type=int, help="边 ID")
    p.add_argument("--from-step-id", help="上游环节 ID")
    p.add_argument("--to-step-id", help="下游环节 ID")
    p.add_argument("--edge-type", help="边类型（data_flow/trigger/degradation）")
    p.add_argument("--label", help="边标签")

    # update_step 专用
    p.add_argument("--field", help="update_step 的字段名")
    p.add_argument("--value", help="update_step 的字段值")

    # 批量
    p.add_argument("--batch", help="批量操作 JSON 文件路径")

    return p


def main(argv: list[str] | None = None) -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = _build_argparser()
    args = parser.parse_args(argv)

    if args.list_ops:
        print("支持的 op:")
        for op in sorted(_ALL_OPS):
            print(f"  - {op}")
        return 0

    # 解析 indicators
    indicators = None
    if args.indicators_json:
        indicators = json.loads(args.indicators_json)
    elif args.indicators_file:
        indicators = json.loads(Path(args.indicators_file).read_text(encoding="utf-8"))

    # 构造单 op（若指定了任一操作标志）
    single_op: dict | None = None
    if args.add_step:
        single_op = {"op": "add_step", "step_id": args.step_id, "step_name": args.step_name,
                     "flow_stage": args.flow_stage, "layer": args.layer,
                     "sort_order": args.sort_order, "narrative_ref": args.narrative_ref,
                     "indicators": indicators, "source_ref": args.source_ref,
                     "design_maturity": args.design_maturity}
    elif args.update_step:
        val: Any = args.value
        if args.field in _STEP_JSONB_FIELDS and args.value:
            val = json.loads(args.value)
        single_op = {"op": "update_step", "step_id": args.step_id,
                     "field": args.field, "value": val}
    elif args.remove_step:
        single_op = {"op": "remove_step", "step_id": args.step_id}
    elif args.add_anchor:
        single_op = {"op": "add_anchor", "step_id": args.step_id,
                     "target_graph": args.target_graph, "target_id": args.target_id,
                     "target_role": args.target_role, "status_snapshot": args.status_snapshot}
    elif args.remove_anchor:
        single_op = {"op": "remove_anchor", "anchor_id": args.anchor_id}
    elif args.add_edge:
        single_op = {"op": "add_edge", "from_step_id": args.from_step_id,
                     "to_step_id": args.to_step_id, "edge_type": args.edge_type, "label": args.label}
    elif args.remove_edge:
        single_op = {"op": "remove_edge", "edge_id": args.edge_id}
    elif args.batch:
        ops = json.loads(Path(args.batch).read_text(encoding="utf-8"))
        if not isinstance(ops, list):
            print("ERROR: --batch 文件必须是 JSON 数组", file=sys.stderr)
            return 1
        return _execute_ops(ops, dry_run=args.dry_run)
    else:
        parser.print_help()
        return 0

    return _execute_ops([single_op], dry_run=args.dry_run)


def _execute_ops(ops: list[dict], dry_run: bool = False) -> int:
    """执行 op 列表（带写锁 + 事务，原子提交/回滚）。

    裁定#ARCH-DEPGRAPH_ACCESS_CONTROL: apply_battle_map.py 是 battlemap 写入唯一合法 CLI
    （白名单脚本），使用 read_only=False 升级到 depgraph_writer 角色。
    DEPGRAPH-WRITE-PATH gate 白名单已收录本脚本（扩展三步 a/b/c）。
    """
    conn = get_battle_map_pg_connection(autocommit=False, read_only=False)
    try:
        with _db_write_lock(conn):
            results = _run_batch(conn, ops, dry_run=dry_run)
            if dry_run:
                print(f"[DRY-RUN] {len(results)} ops（未提交）")
            else:
                conn.commit()
                print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
                # trae_054 v1.6.0 STEP0: 写入后自动 PG 备份（backup_pg_architecture 事件触发）
                try:
                    try:
                        from scripts.governance.meta.backup_runtime_state import backup_pg_architecture
                    except ImportError:
                        from meta.backup_runtime_state import backup_pg_architecture
                    backup_pg_architecture(throttle_seconds=60)
                except Exception as _e:  # noqa: BLE001
                    print(f"[BACKUP-PG] WARNING: 备份失败（不阻断主流程）: {_e}", file=sys.stderr)
                # 真源写入成功 → 自动派生重生成（编排器查 generator_registry.yaml，§2.3 派生关系）
                # 生成失败不阻断 apply（apply 是真源，生成是派生）
                # 生成器自动重生成（reconcile_generators §reconcile_async 非阻塞）：
                # apply 写完 DB → reconcile_async("battle_map_db") 后台 spawn 生成器子进程。
                # 异步非阻塞——与 apply_depgraph/dataflowgraph/decisiongraph 一致（治本缺口#1）。
                # 失败不丢失：boot_hooks 启动时 reconcile_stale() 兜底重跑（生成器幂等）。
                # ZEPHYR_SKIP_REGENERATE=1 逃生通道：批量操作时可跳过。
                if os.environ.get("ZEPHYR_SKIP_REGENERATE") != "1":
                    try:
                        try:
                            from scripts.governance.reconcile_generators import reconcile_async
                        except ImportError:
                            from reconcile_generators import reconcile_async
                        regen = reconcile_async("battle_map_db")
                        if regen.get("status") == "spawned":
                            print(
                                f"[REGENERATE] 🔄 后台启动 PID={regen['pid']} "
                                f"日志: {regen['log_file']}",
                                file=sys.stderr,
                            )
                        else:
                            print(f"[REGENERATE] WARNING: 后台启动失败（不阻断写入）: {regen.get('error')}", file=sys.stderr)
                    except Exception as e:  # noqa: BLE001 — 编排器不可用不阻断主流程
                        print(f"  ⚠ 编排器不可用（不阻断写入）: {e}", file=sys.stderr)
        return 0
    except (ValueError, KeyError) as e:
        conn.rollback()
        print(f"ERROR: {e}", file=sys.stderr)
        return EXIT_FINDINGS
    except Exception as e:
        conn.rollback()
        print(f"ERROR (DB): {e}", file=sys.stderr)
        return 4
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
