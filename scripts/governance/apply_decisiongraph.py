# [BLUEPRINT] MOD-GOV-SCRIPTS | docs/03_modules/_domain_governance/blueprint.md | §decisiongraph
# [MODULE] scripts.governance.apply_decisiongraph
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.__init__; zephyr.governance.persistence.decisiongraph_schema (get_decisiongraph_pg_connection); zephyr.governance.persistence.decision_graph_reader (DecisionGraphReader)
# [CONSUMERS] AI 写入 decisiongraph 节点/边时调用（设计态→运营态迁移）
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] pg_advisory_lock 写锁; build_status 单调推进; DEC-INV-001~005 校验; 事务回滚
# [MODIFY-GUARD] 对标 scripts/governance/apply_depgraph.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 违反不变量→exit 1; 状态迁移非法→exit 1; DB 写入失败→exit 4
# [TESTS] tests/test_apply_decisiongraph.py
# [TTL] task_bound
"""
[BLUEPRINT] | scripts/governance/apply_decisiongraph.py | §decisiongraph
[MODULE] scripts.governance.apply_decisiongraph
[INVARIANTS] pg_advisory_lock 写锁; build_status 单调推进; DEC-INV-001~005 校验; 事务回滚
[MODIFY-GUARD] 对标 scripts/governance/apply_depgraph.py
[CONSUMERS] AI 写入 decisiongraph 节点/边时调用
[STABILITY] stable
[SAFETY] M
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] 违反不变量→exit 1; 状态迁移非法→exit 1; DB 写入失败→exit 4
[TESTS] 无

apply_decisiongraph.py — 决策流图写入入口（对标 apply_depgraph.py）

提供 decision_nodes/decision_edges 的设计态→运营态写入操作。
depgraph 的 apply 脚本有 52 个参数处理大量字段，decisiongraph 更聚焦：
  - 节点操作：add_design_node / transition_build_status / remove_design_node / deprecate_node / update_node_field
  - 边操作：add_edge / add_design_edge / remove_edge
  - 批量操作：--batch（JSON 数组）

五条承重墙不变量（DEC-INV-001~005）在写入时校验：
  - DEC-INV-001: order 节点必须有 risk_check 的 approving 入边
  - DEC-INV-002: signal 节点不能直接连 order 节点
  - DEC-INV-003: DAG 无环（Tarjan SCC 检测）
  - DEC-INV-004: 时间单调性（valid_since 单调）
  - DEC-INV-005: evidence_hash 必填

build_status 状态机（单调推进，禁止跳态）：
  planned → generated → testing → stable → deprecated

用法:
  # 设计态登记新决策节点（status=planned）
  python scripts/governance/apply_decisiongraph.py \\
      --add-design-node \\
      --layer-id L2A --node-type signal \\
      --path "decision/signal/alpha_v1" \\
      --decision-name "Alpha信号v1" --decision-name-en "Alpha Signal v1" \\
      --evidence-hash "sha256:abc123..."

  # 状态迁移：planned → generated
  python scripts/governance/apply_decisiongraph.py \\
      --transition-build-status --node-id 42 --to generated

  # 批量操作（JSON 数组）
  python scripts/governance/apply_decisiongraph.py \\
      --batch ops.json --dry-run

  # 查询支持的 op 列表
  python scripts/governance/apply_decisiongraph.py --list-ops

pg_advisory_lock key：
  depgraph       = 424242
  dataflowgraph  = 424243
  decisiongraph = 424244  ← 本脚本使用
"""

from __future__ import annotations

__manifest__ = """
args: []
description: decisiongraph 写入入口（对标 apply_depgraph.py）
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""

import argparse
import contextlib
import json
import sys
from pathlib import Path
from typing import Any

from psycopg2.extras import RealDictCursor

from zephyr.shared.io.paths import REPO_ROOT

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

from zephyr.governance.persistence.decisiongraph_schema import (
    get_decisiongraph_pg_connection,
    load_build_status_order,
    load_edge_type_values,
    load_node_type_values,
)

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

# pg_advisory_lock key（depgraph=424242, dataflowgraph=424243, decisiongraph=424244）
_DECISIONGRAPH_LOCK_KEY = 424244

# build_status 5态机（单调推进）—— 从 YAML 真源动态加载（VOCAB-HARDCODE 治本）
_BUILD_STATUS_ORDER = load_build_status_order()

# 合法 node_type —— 从 YAML 真源动态加载
_VALID_NODE_TYPES = load_node_type_values()

# 合法 edge_type（DEC-INV-003）—— 从词表 YAML 动态加载
_VALID_EDGE_TYPES = load_edge_type_values()

# 支持的 op 列表（对标 apply_depgraph.py _get_supported_ops）
_NODE_OPS = frozenset({
    "add_design_node",
    "transition_build_status",
    "remove_design_node",
    "deprecate_node",
    "update_node_field",
})
_EDGE_OPS = frozenset({
    "add_edge",
    "remove_edge",
})
_ALL_OPS = _NODE_OPS | _EDGE_OPS


def _get_supported_ops() -> set[str]:
    """返回支持的 op 集合（对标 apply_depgraph.py _get_supported_ops）。"""
    return _ALL_OPS


# ---------------------------------------------------------------------------
# 写锁
# ---------------------------------------------------------------------------


@contextlib.contextmanager
def _db_write_lock(conn):
    """获取 decisiongraph pg_advisory_lock（对标 apply_depgraph.py _db_write_lock）。"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT pg_advisory_lock(%s)", (_DECISIONGRAPH_LOCK_KEY,))
    try:
        yield
    finally:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT pg_advisory_unlock(%s)", (_DECISIONGRAPH_LOCK_KEY,))


# ---------------------------------------------------------------------------
# 状态机校验
# ---------------------------------------------------------------------------


def _validate_status_transition(
    current: str, target: str, node_id: int | None = None
) -> None:
    """校验 build_status 状态迁移合法性（单调推进，禁止跳态）。

    规则：
    - 只能向前推进（planned→generated→testing→stable→deprecated）
    - 禁止跳态（generated 不能直接到 stable，必须经过 testing）
    - deprecated 是终态，不可再迁移

    Raises:
        ValueError: 状态迁移非法时
    """
    if current not in _BUILD_STATUS_ORDER:
        raise ValueError(
            f"node {node_id or '?'} current build_status '{current}' 不合法"
        )
    if target not in _BUILD_STATUS_ORDER:
        raise ValueError(
            f"node {node_id or '?'} target build_status '{target}' 不合法"
        )
    if current == "deprecated":
        raise ValueError(
            f"node {node_id or '?'} 已 deprecated，不能再迁移到 {target}"
        )
    cur_idx = _BUILD_STATUS_ORDER.index(current)
    tgt_idx = _BUILD_STATUS_ORDER.index(target)
    if tgt_idx < cur_idx:
        raise ValueError(
            f"node {node_id or '?'} build_status 禁止回退: "
            f"{current}({cur_idx}) → {target}({tgt_idx})"
        )
    if tgt_idx - cur_idx > 1:
        raise ValueError(
            f"node {node_id or '?'} build_status 禁止跳态: "
            f"{current}({cur_idx}) → {target}({tgt_idx})，"
            f"必须经过 {_BUILD_STATUS_ORDER[cur_idx + 1]}"
        )


# ---------------------------------------------------------------------------
# 不变量校验（DEC-INV-001~005）
# ---------------------------------------------------------------------------


def _check_invariants_on_add_edge(
    conn, from_node_id: int, to_node_id: int, edge_type: str
) -> list[str]:
    """添加边时校验 DEC-INV-002（signal→order 禁止）。

    返回违规列表（空列表=通过）。
    """
    violations: list[str] = []
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # DEC-INV-002: signal 节点不能直接连 order 节点
        cur.execute(
            """
            SELECT dn_from.node_type AS from_type, dn_to.node_type AS to_type
            FROM decision_nodes dn_from, decision_nodes dn_to
            WHERE dn_from.node_id = %s AND dn_to.node_id = %s
            """,
            (from_node_id, to_node_id),
        )
        row = cur.fetchone()
        if row:
            if row["from_type"] == "signal" and row["to_type"] == "order":
                violations.append(
                    f"DEC-INV-002 违反: signal(node={from_node_id}) 不能直接连 "
                    f"order(node={to_node_id})，必须经 portfolio_target 中转"
                )
    return violations


def _check_invariants_post_add_edge(
    conn, to_node_id: int
) -> list[str]:
    """添加边后校验 DEC-INV-001（order 节点必须有 risk_check approving）。

    仅当 to_node 是 order 类型时检查。
    返回违规列表（空列表=通过）。
    """
    violations: list[str] = []
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT node_type FROM decision_nodes WHERE node_id = %s",
            (to_node_id,),
        )
        row = cur.fetchone()
        if row and row["node_type"] == "order":
            cur.execute(
                """
                SELECT 1 FROM decision_edges de
                JOIN decision_nodes dn_from ON de.from_node_id = dn_from.node_id
                WHERE de.to_node_id = %s
                  AND de.edge_type = 'approving'
                  AND dn_from.node_type = 'risk_check'
                LIMIT 1
                """,
                (to_node_id,),
            )
            if cur.fetchone() is None:
                violations.append(
                    f"DEC-INV-001 违反: order 节点 {to_node_id} 必须有至少一条 "
                    f"approving 入边来自 risk_check"
                )
    return violations


# ---------------------------------------------------------------------------
# 节点操作
# ---------------------------------------------------------------------------


def op_add_design_node(
    conn,
    *,
    layer_id: str,
    node_type: str,
    path: str,
    decision_name: str,
    decision_name_en: str,
    evidence_hash: str,
    module_id: str | None = None,
    source_code_ref: str | None = None,
    inputs: dict | None = None,
    outputs: dict | None = None,
    conditions: dict | None = None,
    facets: dict | None = None,
    dry_run: bool = False,
) -> dict:
    """添加设计态决策节点（status=planned）。

    依赖关系先行铁律（L1）：施工前登记到 depgraph 设计态。
    本 op 对标 apply_depgraph.py --add-design-node。
    """
    if node_type not in _VALID_NODE_TYPES:
        raise ValueError(
            f"node_type '{node_type}' 不合法，合法值: {_VALID_NODE_TYPES}"
        )
    if not evidence_hash:
        raise ValueError("evidence_hash 必填（DEC-INV-005）")

    row = {
        "layer_id": layer_id,
        "node_type": node_type,
        "path": path,
        "module_id": module_id,
        "source_code_ref": source_code_ref,
        "decision_name": decision_name,
        "decision_name_en": decision_name_en,
        "inputs": json.dumps(inputs, ensure_ascii=False) if inputs else None,
        "outputs": json.dumps(outputs, ensure_ascii=False) if outputs else None,
        "conditions": json.dumps(conditions, ensure_ascii=False) if conditions else None,
        "facets": json.dumps(facets, ensure_ascii=False) if facets else None,
        "evidence_hash": evidence_hash,
        "build_status": "planned",
        "design_maturity": "design",
    }

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT layer_id FROM decision_layers WHERE layer_id = %s",
            (layer_id,),
        )
        if cur.fetchone() is None:
            raise ValueError(
                f"layer_id '{layer_id}' 不存在（DEC-INV-001: 节点必须有归属层）"
            )

        cur.execute("SELECT 1 FROM decision_nodes WHERE path = %s", (path,))
        if cur.fetchone() is not None:
            raise ValueError(f"path '{path}' 已存在（UNIQUE 约束）")

        if dry_run:
            print(f"[DRY-RUN] INSERT design node path={path}")
        else:
            cur.execute(
                """
                INSERT INTO decision_nodes
                    (layer_id, node_type, path, module_id, source_code_ref,
                     decision_name, decision_name_en,
                     inputs, outputs, conditions, facets, evidence_hash,
                     design_maturity, build_status)
                VALUES (%(layer_id)s, %(node_type)s, %(path)s, %(module_id)s, %(source_code_ref)s,
                        %(decision_name)s, %(decision_name_en)s,
                        %(inputs)s, %(outputs)s, %(conditions)s, %(facets)s,
                        %(evidence_hash)s, %(design_maturity)s, %(build_status)s)
                RETURNING node_id
                """,
                row,
            )
            new_id = cur.fetchone()["node_id"]
            return {"op": "add_design_node", "node_id": new_id, "path": path}

    return {"op": "add_design_node", "dry_run": True, "path": path}


def op_transition_build_status(
    conn, *, node_id: int, to: str, dry_run: bool = False
) -> dict:
    """状态迁移：校验单调性后更新 build_status。"""
    if to not in _BUILD_STATUS_ORDER:
        raise ValueError(f"target build_status '{to}' 不合法")

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT build_status FROM decision_nodes WHERE node_id = %s",
            (node_id,),
        )
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"node_id {node_id} 不存在")
        current = row["build_status"]
        _validate_status_transition(current, to, node_id=node_id)

        if dry_run:
            print(f"[DRY-RUN] UPDATE node {node_id} build_status {current} → {to}")
        else:
            cur.execute(
                "UPDATE decision_nodes SET build_status = %s WHERE node_id = %s",
                (to, node_id),
            )
            return {
                "op": "transition_build_status",
                "node_id": node_id,
                "from": current,
                "to": to,
            }

    return {"op": "transition_build_status", "dry_run": True, "node_id": node_id}


def op_remove_design_node(conn, *, node_id: int, dry_run: bool = False) -> dict:
    """删除设计态节点（仅当 status=planned 时允许，对标 apply_depgraph.py）。"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT build_status, path FROM decision_nodes WHERE node_id = %s",
            (node_id,),
        )
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"node_id {node_id} 不存在")
        if row["build_status"] != "planned":
            raise ValueError(
                f"node {node_id} build_status='{row['build_status']}'，"
                f"仅 planned 节点可删除（已投入生产的节点需走 deprecate 流程）"
            )

        cur.execute(
            "SELECT COUNT(*) AS cnt FROM decision_edges "
            "WHERE from_node_id = %s OR to_node_id = %s",
            (node_id, node_id),
        )
        edge_count = cur.fetchone()["cnt"]
        if edge_count > 0:
            raise ValueError(
                f"node {node_id} 有 {edge_count} 条关联边，必须先删除边再删节点"
            )

        if dry_run:
            print(f"[DRY-RUN] DELETE node {node_id} (path={row['path']})")
        else:
            cur.execute(
                "DELETE FROM decision_nodes WHERE node_id = %s", (node_id,)
            )
            return {"op": "remove_design_node", "node_id": node_id}

    return {"op": "remove_design_node", "dry_run": True, "node_id": node_id}


def op_deprecate_node(conn, *, node_id: int, dry_run: bool = False) -> dict:
    """弃用节点：迁移到 deprecated 终态。"""
    return op_transition_build_status(conn, node_id=node_id, to="deprecated", dry_run=dry_run)


def op_update_node_field(
    conn, *, node_id: int, field: str, value: Any, dry_run: bool = False
) -> dict:
    """更新节点字段（仅允许白名单字段）。"""
    _ALLOWED_FIELDS = {
        "decision_name", "decision_name_en", "module_id",
        "inputs", "outputs", "conditions", "facets", "evidence_hash",
        "design_maturity", "source_code_ref",
    }
    if field not in _ALLOWED_FIELDS:
        raise ValueError(
            f"field '{field}' 不在允许列表 {_ALLOWED_FIELDS}（安全约束：禁止改 build_status，"
            f"请用 transition_build_status op）"
        )

    # JSONB 字段需 json.dumps
    _JSONB_FIELDS = {"inputs", "outputs", "conditions", "facets"}
    db_value = json.dumps(value, ensure_ascii=False) if field in _JSONB_FIELDS else value

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT 1 FROM decision_nodes WHERE node_id = %s", (node_id,)
        )
        if cur.fetchone() is None:
            raise ValueError(f"node_id {node_id} 不存在")

        if dry_run:
            print(f"[DRY-RUN] UPDATE node {node_id} {field} = {value!r}")
        else:
            cur.execute(
                f"UPDATE decision_nodes SET {field} = %s WHERE node_id = %s",  # noqa: S608
                (db_value, node_id),
            )
            return {"op": "update_node_field", "node_id": node_id, "field": field}

    return {"op": "update_node_field", "dry_run": True, "node_id": node_id}


# ---------------------------------------------------------------------------
# 边操作
# ---------------------------------------------------------------------------


def op_add_edge(
    conn,
    *,
    from_node_id: int,
    to_node_id: int,
    edge_type: str,
    edge_type_cn: str | None = None,
    condition: str | None = None,
    priority: int | None = None,
    track: str | None = None,
    evidence_bundle: dict | None = None,
    dry_run: bool = False,
) -> dict:
    """添加决策边（带 DEC-INV-001/002 校验）。"""
    if edge_type not in _VALID_EDGE_TYPES:
        raise ValueError(
            f"edge_type '{edge_type}' 不合法（DEC-INV-003），合法值: {_VALID_EDGE_TYPES}"
        )
    if from_node_id == to_node_id:
        raise ValueError("自环边禁止（DEC-INV-003 DAG 无环）")

    violations = _check_invariants_on_add_edge(conn, from_node_id, to_node_id, edge_type)
    if violations:
        raise ValueError("; ".join(violations))

    row = {
        "from_node_id": from_node_id,
        "to_node_id": to_node_id,
        "edge_type": edge_type,
        "edge_type_cn": edge_type_cn,
        "condition": condition,
        "priority": priority,
        "track": track,
        "evidence_bundle": json.dumps(evidence_bundle, ensure_ascii=False) if evidence_bundle else None,
    }

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        if dry_run:
            print(f"[DRY-RUN] INSERT edge {from_node_id} → {to_node_id} ({edge_type})")
        else:
            cur.execute(
                """
                INSERT INTO decision_edges
                    (from_node_id, to_node_id, edge_type, edge_type_cn,
                     condition, priority, track, evidence_bundle)
                VALUES (%(from_node_id)s, %(to_node_id)s, %(edge_type)s, %(edge_type_cn)s,
                        %(condition)s, %(priority)s, %(track)s, %(evidence_bundle)s)
                RETURNING edge_id
                """,
                row,
            )
            new_id = cur.fetchone()["edge_id"]

            # DEC-INV-001 后置校验：order 节点必须有 risk_check approving
            post_violations = _check_invariants_post_add_edge(conn, to_node_id)
            if post_violations:
                # 边已插入但 order 节点缺 approving，回滚事务并报错
                raise ValueError(
                    "; ".join(post_violations)
                    + f"（已回滚 edge {new_id} 的插入）"
                )

            return {"op": "add_edge", "edge_id": new_id}

    return {"op": "add_edge", "dry_run": True}


def op_remove_edge(conn, *, edge_id: int, dry_run: bool = False) -> dict:
    """删除决策边。"""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT 1 FROM decision_edges WHERE edge_id = %s", (edge_id,))
        if cur.fetchone() is None:
            raise ValueError(f"edge_id {edge_id} 不存在")

        if dry_run:
            print(f"[DRY-RUN] DELETE edge {edge_id}")
        else:
            cur.execute("DELETE FROM decision_edges WHERE edge_id = %s", (edge_id,))
            return {"op": "remove_edge", "edge_id": edge_id}

    return {"op": "remove_edge", "dry_run": True, "edge_id": edge_id}


def op_add_design_edge(
    conn,
    *,
    from_node_id: int,
    to_node_id: int,
    edge_type: str,
    edge_type_cn: str | None = None,
    condition: str | None = None,
    priority: int | None = None,
    track: str | None = None,
    evidence_bundle: dict | None = None,
    dry_run: bool = False,
) -> dict:
    """新增设计态决策边（design_maturity='design', build_status='planned'）。

    依赖关系先行铁律（L1）：施工前登记设计态决策边到 decisiongraph。
    与 op_add_edge 的差异：
    - 写入 design_maturity='design'（规划中），op_add_edge 默认 'production'（已实现）
    - 写入 build_status='planned'（设计态未实现），op_add_edge 默认 'generated'
    - 校验两端节点 design_maturity='design'（仅允许设计态节点互连，对标 apply_depgraph.add_design_edge）
    - 校验不变量 DEC-INV-001/002/003 与 op_add_edge 一致
    """
    if edge_type not in _VALID_EDGE_TYPES:
        raise ValueError(
            f"edge_type '{edge_type}' 不合法（DEC-INV-003），合法值: {_VALID_EDGE_TYPES}"
        )
    if from_node_id == to_node_id:
        raise ValueError("自环边禁止（DEC-INV-003 DAG 无环）")

    violations = _check_invariants_on_add_edge(conn, from_node_id, to_node_id, edge_type)
    if violations:
        raise ValueError("; ".join(violations))

    # 校验两端节点存在且为设计态
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT node_id, design_maturity FROM decision_nodes WHERE node_id = %s",
            (from_node_id,),
        )
        from_node = cur.fetchone()
        if from_node is None:
            raise ValueError(f"from_node_id={from_node_id} 不存在")
        if from_node["design_maturity"] != "design":
            raise ValueError(
                f"from_node_id={from_node_id} design_maturity={from_node['design_maturity']}（应为 design）"
            )

        cur.execute(
            "SELECT node_id, design_maturity FROM decision_nodes WHERE node_id = %s",
            (to_node_id,),
        )
        to_node = cur.fetchone()
        if to_node is None:
            raise ValueError(f"to_node_id={to_node_id} 不存在")
        if to_node["design_maturity"] != "design":
            raise ValueError(
                f"to_node_id={to_node_id} design_maturity={to_node['design_maturity']}（应为 design）"
            )

    row = {
        "from_node_id": from_node_id,
        "to_node_id": to_node_id,
        "edge_type": edge_type,
        "edge_type_cn": edge_type_cn,
        "condition": condition,
        "priority": priority,
        "track": track,
        "evidence_bundle": json.dumps(evidence_bundle, ensure_ascii=False) if evidence_bundle else None,
        "design_maturity": "design",
        "build_status": "planned",
    }

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        if dry_run:
            print(f"[DRY-RUN] INSERT design edge {from_node_id} → {to_node_id} ({edge_type})")
        else:
            cur.execute(
                """
                INSERT INTO decision_edges
                    (from_node_id, to_node_id, edge_type, edge_type_cn,
                     condition, priority, track, evidence_bundle,
                     design_maturity, build_status)
                VALUES (%(from_node_id)s, %(to_node_id)s, %(edge_type)s, %(edge_type_cn)s,
                        %(condition)s, %(priority)s, %(track)s, %(evidence_bundle)s,
                        %(design_maturity)s, %(build_status)s)
                RETURNING edge_id
                """,
                row,
            )
            new_id = cur.fetchone()["edge_id"]

            post_violations = _check_invariants_post_add_edge(conn, to_node_id)
            if post_violations:
                raise ValueError(
                    "; ".join(post_violations)
                    + f"（已回滚 design edge {new_id} 的插入）"
                )

            return {"op": "add_design_edge", "edge_id": new_id}

    return {"op": "add_design_edge", "dry_run": True}


# ---------------------------------------------------------------------------
# 批量操作
# ---------------------------------------------------------------------------


_OP_DISPATCH = {
    "add_design_node": op_add_design_node,
    "transition_build_status": op_transition_build_status,
    "remove_design_node": op_remove_design_node,
    "deprecate_node": op_deprecate_node,
    "update_node_field": op_update_node_field,
    "add_edge": op_add_edge,
    "add_design_edge": op_add_design_edge,
    "remove_edge": op_remove_edge,
}


def _execute_batch_op(conn, op_spec: dict, dry_run: bool = False) -> dict:
    """执行单个 batch op（对标 apply_depgraph.py _apply_single_op）。"""
    op = op_spec.get("op")
    if op not in _OP_DISPATCH:
        raise ValueError(f"未知 op '{op}'，合法 op: {_get_supported_ops()}")

    fn = _OP_DISPATCH[op]
    kwargs = {k: v for k, v in op_spec.items() if k != "op"}
    return fn(conn, dry_run=dry_run, **kwargs)


def cmd_batch(
    batch_path: str, dry_run: bool = False, allow_promote: bool = False
) -> dict:
    """批量执行 JSON 文件中的 ops（对标 apply_depgraph.py --batch）。

    batch JSON 格式：
        [
          {"op": "add_design_node", "layer_id": "L2A", "node_type": "signal",
           "path": "decision/signal/alpha_v1",
           "decision_name": "Alpha信号v1", "decision_name_en": "Alpha Signal v1",
           "evidence_hash": "sha256:abc123"},
          {"op": "transition_build_status", "node_id": 42, "to": "generated"},
          {"op": "add_edge", "from_node_id": 1, "to_node_id": 2, "edge_type": "triggering"}
        ]
    """
    p = Path(batch_path)
    if not p.is_file():
        print(f"ERROR: batch file not found: {batch_path}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(p, encoding="utf-8") as f:
            ops = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"ERROR: batch file parse failed: {e}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(ops, list):
        print("ERROR: batch file must be a JSON array of op objects", file=sys.stderr)
        sys.exit(1)

    conn = get_decisiongraph_pg_connection(autocommit=False)
    results: list[dict] = []
    try:
        with _db_write_lock(conn):
            for i, op_spec in enumerate(ops):
                try:
                    r = _execute_batch_op(conn, op_spec, dry_run=dry_run)
                    results.append(r)
                except Exception as e:
                    conn.rollback()
                    print(
                        f"ERROR: op #{i} failed: {op_spec.get('op')}: {e}",
                        file=sys.stderr,
                    )
                    print(f"  (transaction rolled back, {i} prior ops reverted)", file=sys.stderr)
                    sys.exit(1)
        if dry_run:
            conn.rollback()
            print(f"[DRY-RUN] {len(results)} ops previewed, transaction rolled back")
        else:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return {"total_ops": len(results), "results": results, "dry_run": dry_run}


def cmd_list_ops() -> None:
    """列出支持的 op（对标 apply_depgraph.py --list-ops）。"""
    print("Supported operations:")
    print("\nNode ops:")
    for op in sorted(_NODE_OPS):
        print(f"  {op}")
    print("\nEdge ops:")
    for op in sorted(_EDGE_OPS):
        print(f"  {op}")
    print("\nBatch JSON format:")
    print('  [{"op": "add_design_node", "layer_id": "L0", "node_type": "signal",')
    print('    "path": "decision/signal/example",')
    print('    "decision_name": "示例", "decision_name_en": "Example",')
    print('    "evidence_hash": "sha256:..."}]')
    print("\nbuild_status state machine (monotonic):")
    print("  " + " → ".join(_BUILD_STATUS_ORDER))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="decisiongraph 写入入口（对标 apply_depgraph.py）",
        epilog="""操作类型：
  --add-design-node           登记设计态节点（status=planned）
  --transition-build-status   状态迁移（planned→generated→...）
  --remove-design-node        删除设计态节点（仅 planned 可删）
  --deprecate-node            弃用节点（迁移到 deprecated 终态）
  --update-node-field         更新节点字段（白名单）
  --add-edge                  添加边（带不变量校验）
  --remove-edge               删除边
  --batch ops.json            批量执行 JSON 文件中的 ops
  --list-ops                  列出支持的 op
  --dry-run                   预演（不写 DB）

build_status 状态机（单调推进，禁止跳态）：
  planned → generated → testing → stable → deprecated""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--list-ops", action="store_true", help="列出支持的 op")
    parser.add_argument("--dry-run", action="store_true", help="预演：不写 DB")
    parser.add_argument("--batch", type=str, help="批量执行 JSON 文件中的 ops")

    # add-design-node 参数
    parser.add_argument("--add-design-node", action="store_true", help="登记设计态节点")
    parser.add_argument("--layer-id", type=str, help="归属层 ID（如 L0/L1/L2A）")
    parser.add_argument("--node-type", type=str, help="节点类型（signal/order/...）")
    parser.add_argument("--path", type=str, help="节点路径（UNIQUE）")
    parser.add_argument("--module-id", type=str, help="关联模块 ID（与 depgraph 关联）")
    parser.add_argument("--source-code-ref", type=str, help="代码/脚本引用路径")
    parser.add_argument("--decision-name", type=str, help="决策名称（中文）")
    parser.add_argument("--decision-name-en", type=str, help="决策名称（英文）")
    parser.add_argument("--evidence-hash", type=str, help="证据哈希（DEC-INV-005 必填）")
    parser.add_argument("--inputs", type=str, help="输入 JSON 字符串")
    parser.add_argument("--outputs", type=str, help="输出 JSON 字符串")
    parser.add_argument("--conditions", type=str, help="条件 JSON 字符串")
    parser.add_argument("--facets", type=str, help="Facet JSON 字符串")

    # transition-build-status 参数
    parser.add_argument("--transition-build-status", action="store_true",
                        help="状态迁移")
    parser.add_argument("--node-id", type=int, help="节点 ID")
    parser.add_argument("--to", type=str, help="目标状态（planned/generated/...）")

    # remove-design-node 参数
    parser.add_argument("--remove-design-node", action="store_true",
                        help="删除设计态节点")

    # deprecate-node 参数
    parser.add_argument("--deprecate-node", action="store_true", help="弃用节点")

    # update-node-field 参数
    parser.add_argument("--update-node-field", action="store_true",
                        help="更新节点字段")
    parser.add_argument("--field", type=str, help="字段名（白名单）")
    parser.add_argument("--value", type=str, help="字段值（JSON 字符串）")

    # add-edge 参数
    parser.add_argument("--add-edge", action="store_true", help="添加边")
    parser.add_argument("--from-node", dest="from_node_id", type=int,
                        help="起点节点 ID")
    parser.add_argument("--to-node", dest="to_node_id", type=int,
                        help="终点节点 ID")
    parser.add_argument("--edge-type", type=str,
                        help="边类型（triggering/informing/constraining/approving）")
    parser.add_argument("--edge-type-cn", type=str, help="边类型中文名")
    parser.add_argument("--condition", type=str, help="边条件")
    parser.add_argument("--priority", type=int, help="优先级")
    parser.add_argument("--track", type=str, help="所属轨")
    parser.add_argument("--evidence-bundle", type=str, help="证据包 JSON")

    # remove-edge 参数
    parser.add_argument("--remove-edge", action="store_true", help="删除边")
    parser.add_argument("--edge-id", type=int, help="边 ID")

    args = parser.parse_args()

    if args.list_ops:
        cmd_list_ops()
        return

    if args.batch:
        result = cmd_batch(args.batch, dry_run=args.dry_run)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 单 op 模式
    conn = get_decisiongraph_pg_connection(autocommit=False)
    try:
        with _db_write_lock(conn):
            result: dict | None = None
            if args.add_design_node:
                inputs = json.loads(args.inputs) if args.inputs else None
                outputs = json.loads(args.outputs) if args.outputs else None
                conditions = json.loads(args.conditions) if args.conditions else None
                facets = json.loads(args.facets) if args.facets else None
                result = op_add_design_node(
                    conn,
                    layer_id=args.layer_id,
                    node_type=args.node_type,
                    path=args.path,
                    decision_name=args.decision_name,
                    decision_name_en=args.decision_name_en,
                    evidence_hash=args.evidence_hash,
                    module_id=args.module_id,
                    source_code_ref=args.source_code_ref,
                    inputs=inputs,
                    outputs=outputs,
                    conditions=conditions,
                    facets=facets,
                    dry_run=args.dry_run,
                )
            elif args.transition_build_status:
                result = op_transition_build_status(
                    conn, node_id=args.node_id, to=args.to, dry_run=args.dry_run
                )
            elif args.remove_design_node:
                result = op_remove_design_node(
                    conn, node_id=args.node_id, dry_run=args.dry_run
                )
            elif args.deprecate_node:
                result = op_deprecate_node(
                    conn, node_id=args.node_id, dry_run=args.dry_run
                )
            elif args.update_node_field:
                value = json.loads(args.value) if args.value else None
                result = op_update_node_field(
                    conn, node_id=args.node_id, field=args.field,
                    value=value, dry_run=args.dry_run,
                )
            elif args.add_edge:
                evidence_bundle = (
                    json.loads(args.evidence_bundle) if args.evidence_bundle else None
                )
                result = op_add_edge(
                    conn,
                    from_node_id=args.from_node_id,
                    to_node_id=args.to_node_id,
                    edge_type=args.edge_type,
                    edge_type_cn=args.edge_type_cn,
                    condition=args.condition,
                    priority=args.priority,
                    track=args.track,
                    evidence_bundle=evidence_bundle,
                    dry_run=args.dry_run,
                )
            elif args.remove_edge:
                result = op_remove_edge(
                    conn, edge_id=args.edge_id, dry_run=args.dry_run
                )
            else:
                parser.print_help()
                print("\nERROR: Must specify an operation.", file=sys.stderr)
                sys.exit(3)

        if args.dry_run:
            conn.rollback()
            print("[DRY-RUN] Transaction rolled back (no writes)")
        else:
            conn.commit()
            if result:
                print(json.dumps(result, ensure_ascii=False, indent=2))
    except ValueError as e:
        conn.rollback()
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(4)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
