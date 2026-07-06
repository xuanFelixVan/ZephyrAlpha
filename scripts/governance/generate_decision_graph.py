# [BLUEPRINT] MOD-GOV-SCRIPTS | docs/03_modules/_domain_governance/blueprint.md | §decisiongraph
# [MODULE] scripts.governance.generate_decision_graph
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.__init__; zephyr.governance.persistence.decisiongraph_schema (get_decisiongraph_pg_connection); architecture_model/domain/decision_graph_model.yaml (YAML 真源)
# [CONSUMERS] AI 同步 YAML→DB 时调用
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] YAML 是唯一真源; DB 为只读缓存; 同步单向 YAML→DB; 不变量校验前置
# [MODIFY-GUARD] 对标 scripts/governance/generate_project_depgraph.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] YAML 缺失→exit 1; 解析失败→exit 2; DB 写入失败→exit 4
# [TESTS] tests/test_generate_decision_graph.py
# [TTL] task_bound
"""
[BLUEPRINT] | scripts/governance/generate_decision_graph.py | §decisiongraph
[MODULE] scripts.governance.generate_decision_graph
[INVARIANTS] YAML 是唯一真源; DB 为只读缓存; 同步单向 YAML→DB; 不变量校验前置
[MODIFY-GUARD] 对标 scripts/governance/generate_project_depgraph.py
[CONSUMERS] AI 同步 YAML→DB 时调用
[STABILITY] stable
[SAFETY] M
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] YAML 缺失→exit 1; 解析失败→exit 2; DB 写入失败→exit 4
[TESTS] 无

generate_decision_graph.py — 决策流图 YAML→DB 同步生成器

对标 generate_project_depgraph.py，但更简单：
  - depgraph 用 AST 扫描代码（复杂）
  - decisiongraph 从 YAML 真源加载（业务流无法从代码扫描）

YAML 真源：architecture_model/domain/decision_graph_model.yaml
  定义：4轨 + 10层 + 6节点类型 + 4边类型 + 5不变量
  存储：4张表（decision_layers/decision_nodes/decision_edges/decision_tracks）

同步策略：
  - tracks（4轨）：全量覆盖（YAML 是真源，DB 跟随）
  - layers（10层）：全量覆盖
  - nodes/edges：本脚本不同步（由 apply_decisiongraph.py 手动写入，
    或由 A1 设计文档导入脚本在 Phase 5 写入）

用法:
  python scripts/governance/generate_decision_graph.py
      # 默认：增量同步（YAML 有变更的记录才更新）

  python scripts/governance/generate_decision_graph.py --dry-run
      # 预演：只打印将要执行的 SQL，不写入 DB

  python scripts/governance/generate_decision_graph.py --force
      # 破坏性重建：清空 tracks+layers 后全量重写（危险！保留 nodes/edges）

  python scripts/governance/generate_decision_graph.py --validate-only
      # 仅校验 YAML 不变量，不写 DB

pg_advisory_lock key：
  depgraph       = 424242
  dataflowgraph  = 424243
  decisiongraph = 424244  ← 本脚本使用
"""

from __future__ import annotations

__manifest__ = """
args: []
description: decisiongraph YAML→DB 同步生成器（对标 generate_project_depgraph.py）
dimensions:
- D1
priority: P2
timeout_seconds: 120
warn_only: false
"""

import argparse
import contextlib
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import yaml
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
    load_track_ids,
)

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

# YAML 真源路径（architecture_model/domain/decision_graph_model.yaml）
_YAML_PATH = REPO_ROOT / "architecture_model" / "domain" / "decision_graph_model.yaml"

# pg_advisory_lock key（depgraph=424242, dataflowgraph=424243, decisiongraph=424244）
_DECISIONGRAPH_LOCK_KEY = 424244

# build_status 5态机（单调推进）—— 从 YAML 真源动态加载（VOCAB-HARDCODE 治本）
_BUILD_STATUS_ORDER = load_build_status_order()

# 合法 track_id —— 从 YAML 真源动态加载
_VALID_TRACK_IDS = load_track_ids()

# 合法 node_type —— 从 YAML 真源动态加载
_VALID_NODE_TYPES = load_node_type_values()

# 合法 edge_type（DEC-INV-003）—— 从词表 YAML 动态加载
_VALID_EDGE_TYPES = load_edge_type_values()


# ---------------------------------------------------------------------------
# YAML 加载与校验
# ---------------------------------------------------------------------------


def _load_yaml(yaml_path: Path) -> dict:
    """加载 YAML 真源。"""
    if not yaml_path.is_file():
        print(f"ERROR: YAML truth source not found: {yaml_path}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"ERROR: YAML parse failed: {e}", file=sys.stderr)
        sys.exit(2)
    if not isinstance(data, dict):
        print(f"ERROR: YAML root must be a mapping, got {type(data).__name__}", file=sys.stderr)
        sys.exit(2)
    return data


def _validate_yaml(data: dict) -> list[str]:
    """校验 YAML 不变量，返回错误列表（空列表=通过）。

    校验内容：
    - schema_version 存在
    - tracks 列表非空且 track_id 合法
    - layers 列表非空且 layer_id 合法、track 字段引用合法 track_id
    - build_status 取值合法
    """
    errors: list[str] = []

    if not data.get("schema_version"):
        errors.append("schema_version missing")

    tracks = data.get("tracks", [])
    if not isinstance(tracks, list) or not tracks:
        errors.append("tracks must be a non-empty list")
    else:
        track_ids = set()
        for t in tracks:
            tid = t.get("track_id")
            if not tid:
                errors.append(f"track missing track_id: {t}")
            elif tid not in _VALID_TRACK_IDS:
                errors.append(f"track_id '{tid}' not in valid set {_VALID_TRACK_IDS}")
            else:
                track_ids.add(tid)
            if not t.get("track_name"):
                errors.append(f"track {tid} missing track_name")
            if not t.get("track_name_en"):
                errors.append(f"track {tid} missing track_name_en")
            if "priority" not in t:
                errors.append(f"track {tid} missing priority")

    layers = data.get("layers", [])
    if not isinstance(layers, list) or not layers:
        errors.append("layers must be a non-empty list")
    else:
        layer_ids = set()
        for L in layers:
            lid = L.get("layer_id")
            if not lid:
                errors.append(f"layer missing layer_id: {L}")
            else:
                layer_ids.add(lid)
            if not L.get("layer_name"):
                errors.append(f"layer {lid} missing layer_name")
            if not L.get("layer_name_en"):
                errors.append(f"layer {lid} missing layer_name_en")
            track = L.get("track")
            if track and track not in _VALID_TRACK_IDS:
                errors.append(
                    f"layer {lid} track '{track}' not in valid set {_VALID_TRACK_IDS}"
                )
            bs = L.get("build_status")
            if bs and bs not in _BUILD_STATUS_ORDER:
                errors.append(
                    f"layer {lid} build_status '{bs}' not in valid set {_BUILD_STATUS_ORDER}"
                )
            dm = L.get("design_maturity")
            if dm and dm not in ("design", "production", "prototype"):
                errors.append(
                    f"layer {lid} design_maturity '{dm}' not in valid set"
                )

    return errors


# ---------------------------------------------------------------------------
# DB 写入（YAML→DB 同步）
# ---------------------------------------------------------------------------


@contextlib.contextmanager
def _decision_sync_lock(conn):
    """获取 decisiongraph pg_advisory_lock（generate 专用，避免与 apply_decisiongraph.py 重名）。"""
    with conn.cursor() as cur:
        cur.execute("SELECT pg_advisory_lock(%s)", (_DECISIONGRAPH_LOCK_KEY,))
    try:
        yield
    finally:
        with conn.cursor() as cur:
            cur.execute("SELECT pg_advisory_unlock(%s)", (_DECISIONGRAPH_LOCK_KEY,))


def _sync_tracks(conn, tracks: list[dict], dry_run: bool = False) -> dict:
    """同步 tracks 表（全量覆盖）。"""
    stats = {"inserted": 0, "updated": 0, "unchanged": 0}
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        for t in tracks:
            cur.execute(
                "SELECT * FROM decision_tracks WHERE track_id = %s",
                (t["track_id"],),
            )
            existing = cur.fetchone()
            row = {
                "track_id": t["track_id"],
                "track_name": t["track_name"],
                "track_name_en": t["track_name_en"],
                "description": t.get("description", ""),
                "priority": t["priority"],
                "activation_condition": t.get("activation_condition", ""),
            }
            if existing is None:
                if dry_run:
                    print(f"[DRY-RUN] INSERT track {t['track_id']}")
                else:
                    cur.execute(
                        """
                        INSERT INTO decision_tracks
                            (track_id, track_name, track_name_en, description, priority, activation_condition)
                        VALUES (%(track_id)s, %(track_name)s, %(track_name_en)s,
                                %(description)s, %(priority)s, %(activation_condition)s)
                        """,
                        row,
                    )
                stats["inserted"] += 1
            else:
                # 对比关键字段，决定 update/unchanged
                needs_update = any(
                    existing.get(k) != v for k, v in row.items() if k != "track_id"
                )
                if needs_update:
                    if dry_run:
                        print(f"[DRY-RUN] UPDATE track {t['track_id']}")
                    else:
                        cur.execute(
                            """
                            UPDATE decision_tracks SET
                                track_name = %(track_name)s,
                                track_name_en = %(track_name_en)s,
                                description = %(description)s,
                                priority = %(priority)s,
                                activation_condition = %(activation_condition)s
                            WHERE track_id = %(track_id)s
                            """,
                            row,
                        )
                    stats["updated"] += 1
                else:
                    stats["unchanged"] += 1
    return stats


def _sync_layers(conn, layers: list[dict], dry_run: bool = False) -> dict:
    """同步 layers 表（全量覆盖）。"""
    stats = {"inserted": 0, "updated": 0, "unchanged": 0}
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        for L in layers:
            cur.execute(
                "SELECT * FROM decision_layers WHERE layer_id = %s",
                (L["layer_id"],),
            )
            existing = cur.fetchone()
            # module_id / source_code_ref 可为空字符串或 null，统一处理为 None
            mid = L.get("module_id") or None
            scr = L.get("source_code_ref") or None
            row = {
                "layer_id": L["layer_id"],
                "layer_name": L["layer_name"],
                "layer_name_en": L["layer_name_en"],
                "track": L["track"],
                "description": L.get("description", ""),
                "decision_frequency": L.get("decision_frequency", ""),
                "design_maturity": L.get("design_maturity", "production"),
                "build_status": L.get("build_status", "generated"),
                "module_id": mid,
                "source_code_ref": scr,
            }
            if existing is None:
                if dry_run:
                    print(f"[DRY-RUN] INSERT layer {L['layer_id']}")
                else:
                    cur.execute(
                        """
                        INSERT INTO decision_layers
                            (layer_id, layer_name, layer_name_en, track, description,
                             decision_frequency, design_maturity, build_status,
                             module_id, source_code_ref)
                        VALUES (%(layer_id)s, %(layer_name)s, %(layer_name_en)s, %(track)s,
                                %(description)s, %(decision_frequency)s,
                                %(design_maturity)s, %(build_status)s,
                                %(module_id)s, %(source_code_ref)s)
                        """,
                        row,
                    )
                stats["inserted"] += 1
            else:
                needs_update = any(
                    existing.get(k) != v for k, v in row.items() if k != "layer_id"
                )
                if needs_update:
                    if dry_run:
                        print(f"[DRY-RUN] UPDATE layer {L['layer_id']}")
                    else:
                        cur.execute(
                            """
                            UPDATE decision_layers SET
                                layer_name = %(layer_name)s,
                                layer_name_en = %(layer_name_en)s,
                                track = %(track)s,
                                description = %(description)s,
                                decision_frequency = %(decision_frequency)s,
                                design_maturity = %(design_maturity)s,
                                build_status = %(build_status)s,
                                module_id = %(module_id)s,
                                source_code_ref = %(source_code_ref)s
                            WHERE layer_id = %(layer_id)s
                            """,
                            row,
                        )
                    stats["updated"] += 1
                else:
                    stats["unchanged"] += 1
    return stats


def _force_rebuild_tracks_layers(conn, dry_run: bool = False) -> None:
    """破坏性重建：清空 tracks+layers 后全量重写（--force 模式）。

    安全约束：不删除 decision_nodes/decision_edges（业务数据）。
    """
    if dry_run:
        print("[DRY-RUN] DELETE FROM decision_layers")
        print("[DRY-RUN] DELETE FROM decision_tracks")
        return
    with conn.cursor() as cur:
        # 先清空 layers（tracks 被 layers FK 引用，需先删 layers）
        cur.execute("DELETE FROM decision_layers")
        cur.execute("DELETE FROM decision_tracks")


def sync_decision_graph(
    yaml_path: Path = _YAML_PATH,
    dry_run: bool = False,
    force: bool = False,
    validate_only: bool = False,
) -> dict:
    """主入口：YAML→DB 同步。

    Args:
        yaml_path: YAML 真源路径
        dry_run: True 时只打印 SQL 不写入
        force: True 时破坏性重建（清空 tracks+layers 后重写）
        validate_only: True 时只校验 YAML 不变量不写 DB

    Returns:
        同步统计 dict
    """
    data = _load_yaml(yaml_path)

    errors = _validate_yaml(data)
    if errors:
        print("ERROR: YAML invariant violations:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(2)

    if validate_only:
        print("[validate-only] YAML invariants passed:")
        print(f"  tracks: {len(data.get('tracks', []))}")
        print(f"  layers: {len(data.get('layers', []))}")
        print(f"  node_types: {len(data.get('node_types', []))}")
        print(f"  edge_types: {len(data.get('edge_types', []))}")
        print(f"  invariants: {len(data.get('invariants', []))}")
        return {"validate_only": True}

    tracks = data.get("tracks", [])
    layers = data.get("layers", [])

    conn = get_decisiongraph_pg_connection(autocommit=False)
    try:
        with _decision_sync_lock(conn):
            if force:
                _force_rebuild_tracks_layers(conn, dry_run=dry_run)

            track_stats = _sync_tracks(conn, tracks, dry_run=dry_run)
            layer_stats = _sync_layers(conn, layers, dry_run=dry_run)

        if dry_run:
            conn.rollback()
            print("[DRY-RUN] Transaction rolled back (no writes)")
        else:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return {
        "tracks": track_stats,
        "layers": layer_stats,
        "dry_run": dry_run,
        "force": force,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="decisiongraph YAML→DB 同步生成器（对标 generate_project_depgraph.py）",
        epilog="""YAML 真源：architecture_model/domain/decision_graph_model.yaml
DB 目标：PostgreSQL decision_layers + decision_tracks 表
节点/边：本脚本不同步（由 apply_decisiongraph.py 写入）

与 depgraph 的差异：
  - depgraph 用 AST 扫描代码生成 nodes/edges
  - decisiongraph 从 YAML 真源加载（业务流无法从代码扫描）
  - YAML 只定义骨架（tracks+layers），节点/边由后续脚本/导入补充""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="预演：只打印 SQL 不写入 DB")
    parser.add_argument("--force", action="store_true",
                        help="破坏性重建：清空 tracks+layers 后重写（保留 nodes/edges）")
    parser.add_argument("--validate-only", action="store_true",
                        help="仅校验 YAML 不变量，不写 DB")
    parser.add_argument("--yaml-path", type=str, default=str(_YAML_PATH),
                        help=f"YAML 真源路径（默认 {_YAML_PATH}）")
    args = parser.parse_args()

    yaml_path = Path(args.yaml_path)
    stats = sync_decision_graph(
        yaml_path=yaml_path,
        dry_run=args.dry_run,
        force=args.force,
        validate_only=args.validate_only,
    )
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
