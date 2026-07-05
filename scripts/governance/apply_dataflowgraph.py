# [BLUEPRINT] SH-GOV-003 | docs/03_modules/_domain-governance/blueprint.md | §dataflowgraph
# [MODULE] scripts.governance.apply_dataflowgraph
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.dataflowgraph_schema; psycopg2
# [CONSUMERS] (manual CLI, invoked by AI/human for dataflowgraph modifications)
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] all writes go through pg_advisory_lock(424243); design_maturity gating enforced
# [MODIFY-GUARD] dataflowgraph_schema.py; 03_create_dataflow_schema.sql
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] raises RuntimeError on connection failure; ValueError on invalid args
# [TESTS] tests/test_apply_dataflowgraph.py
# [TTL] permanent
# [ARCH-REF] #ARCH-051

"""
apply_dataflowgraph.py — dataflowgraph 变更写入工具（CLI）
============================================================
依据：ARCH-051 裁定（2026-07-06）

功能：
  - 新增设计态 Dataset / Job / Edge
  - 转换 build_status（planned → generated → testing → stable）
  - 列出所有 Dataset / Job（只读查询）
  - 所有写入操作通过 pg_advisory_lock(424243) 互斥（与 depgraph 的 424242 互不干扰）

设计态门闸（对齐 depgraph 模式）：
  - --add-design-dataset 默认 design_maturity=design, build_status=planned
  - --transition-build-status 用于将设计态推进到运营态（planned → generated）

用法
----
    # 新增设计态 Dataset
    python scripts/governance/apply_dataflowgraph.py --add-design-dataset \\
        --entity-name market_data.tick \\
        --scope production \\
        --contract-ref CTR-001 \\
        --physical-type "src/zephyr/shared/contracts/market_data.py::NormalizedMarketData" \\
        --domain-id D_MKT_DATA

    # 新增设计态 Job
    python scripts/governance/apply_dataflowgraph.py --add-design-job \\
        --job-name ingest.ifind_kline \\
        --scope production \\
        --source-code-ref src/zephyr/data/ingest_ifind.py \\
        --trigger-type scheduled

    # 列出所有 Dataset
    python scripts/governance/apply_dataflowgraph.py --list-datasets

    # 转换 build_status
    python scripts/governance/apply_dataflowgraph.py --transition-build-status 1 generated
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from typing import Any

# 添加项目根到 sys.path（确保 zephyr.* 可导入）
from pathlib import Path
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from zephyr.governance.persistence.dataflowgraph_schema import (  # noqa: E402
    _DATAFLOW_ADVISORY_LOCK_KEY,
    acquire_dataflow_write_lock,
    get_dataflowgraph_pg_connection,
    init_dataflow_db,
    release_dataflow_write_lock,
)


def _now() -> str:
    """返回当前 UTC 时间 ISO 字符串。"""
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _parse_kv_pairs(pairs: list[str] | None) -> dict[str, str]:
    """解析 KEY=VALUE 列表为字典。"""
    result: dict[str, str] = {}
    if not pairs:
        return result
    for pair in pairs:
        if "=" not in pair:
            raise ValueError(f"无效的 KEY=VALUE 参数: {pair}（缺少 =）")
        key, _, value = pair.partition("=")
        result[key.strip()] = value.strip()
    return result


# ---------------------------------------------------------------------------
# 命令实现
# ---------------------------------------------------------------------------

def cmd_add_design_dataset(args: argparse.Namespace) -> int:
    """新增设计态 Dataset 节点。"""
    init_dataflow_db()
    conn = get_dataflowgraph_pg_connection(autocommit=False)
    try:
        acquire_dataflow_write_lock(conn)
        with conn.cursor() as cur:
            # 检查 entity_name 是否已存在
            cur.execute("SELECT 1 FROM dataflow_datasets WHERE entity_name = %s", (args.entity_name,))
            if cur.fetchone() is not None:
                print(f"ERROR: Dataset entity_name={args.entity_name!r} 已存在", file=sys.stderr)
                return 1

            extra = _parse_kv_pairs(args.extra)
            cur.execute("""
                INSERT INTO dataflow_datasets
                    (entity_name, entity_type, scope, contract_ref, physical_type,
                     produced_by_job, domain_id, design_maturity, build_status,
                     pit_policy, format_summary, valid_since, last_updated)
                VALUES (%s, 'dataset', %s, %s, %s, %s, %s, 'design', 'planned', %s, %s, %s, %s)
                RETURNING dataset_id
            """, (
                args.entity_name, args.scope, args.contract_ref, args.physical_type,
                args.produced_by_job, args.domain_id,
                args.pit_policy, args.format_summary, args.valid_since or extra.get("valid_since"),
                _now(),
            ))
            dataset_id = cur.fetchone()[0]
        conn.commit()
        print(f"OK: 新增设计态 Dataset dataset_id={dataset_id} entity_name={args.entity_name!r} (design_maturity=design, build_status=planned)")
        return 0
    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    finally:
        try:
            release_dataflow_write_lock(conn)
        except Exception:
            pass
        conn.close()


def cmd_add_design_job(args: argparse.Namespace) -> int:
    """新增设计态 Job 节点。"""
    init_dataflow_db()
    conn = get_dataflowgraph_pg_connection(autocommit=False)
    try:
        acquire_dataflow_write_lock(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM dataflow_jobs WHERE job_name = %s", (args.job_name,))
            if cur.fetchone() is not None:
                print(f"ERROR: Job job_name={args.job_name!r} 已存在", file=sys.stderr)
                return 1

            cur.execute("""
                INSERT INTO dataflow_jobs
                    (job_name, entity_type, scope, source_code_ref, trigger_type,
                     run_context, pit_relevance, description, design_maturity,
                     build_status, last_updated)
                VALUES (%s, 'job', %s, %s, %s, %s, %s, %s, 'design', 'planned', %s)
                RETURNING job_id
            """, (
                args.job_name, args.scope, args.source_code_ref, args.trigger_type,
                args.run_context, args.pit_relevance, args.description, _now(),
            ))
            job_id = cur.fetchone()[0]
        conn.commit()
        print(f"OK: 新增设计态 Job job_id={job_id} job_name={args.job_name!r} (design_maturity=design, build_status=planned)")
        return 0
    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    finally:
        try:
            release_dataflow_write_lock(conn)
        except Exception:
            pass
        conn.close()


def cmd_add_design_edge(args: argparse.Namespace) -> int:
    """新增设计态数据流边。"""
    init_dataflow_db()
    conn = get_dataflowgraph_pg_connection(autocommit=False)
    try:
        acquire_dataflow_write_lock(conn)
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO dataflow_edges
                    (from_entity_id, to_entity_id, from_entity_type, to_entity_type,
                     edge_type, design_maturity, last_updated)
                VALUES (%s, %s, %s, %s, %s, 'design', %s)
                RETURNING edge_id
            """, (
                args.from_id, args.to_id, args.from_type, args.to_type,
                args.edge_type, _now(),
            ))
            edge_id = cur.fetchone()[0]
        conn.commit()
        print(f"OK: 新增设计态 Edge edge_id={edge_id} {args.from_type}({args.from_id}) --{args.edge_type}--> {args.to_type}({args.to_id})")
        return 0
    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    finally:
        try:
            release_dataflow_write_lock(conn)
        except Exception:
            pass
        conn.close()


def cmd_transition_build_status(args: argparse.Namespace) -> int:
    """转换 Dataset/Job 的 build_status。

    用法: --transition-build-status <entity_type> <entity_id|entity_name> <new_status>
      entity_type: dataset | job

    注意：build_status 合法值（planned/generated/testing/stable/deprecated）由 DB CHECK
    约束定义（03_create_dataflow_schema.sql），不在代码中预校验以避免 VOCAB-HARDCODE
    门禁。非法值由 DB CHECK 约束拒绝，错误信息含合法值清单。
    """
    init_dataflow_db()
    conn = get_dataflowgraph_pg_connection(autocommit=False)
    try:
        acquire_dataflow_write_lock(conn)
        with conn.cursor() as cur:
            table = "dataflow_datasets" if args.entity_type == "dataset" else "dataflow_jobs"
            id_col = "dataset_id" if args.entity_type == "dataset" else "job_id"
            name_col = "entity_name" if args.entity_type == "dataset" else "job_name"

            # 支持数字 ID 或名称
            entity_ref: Any
            if args.entity_ref.isdigit():
                entity_ref = int(args.entity_ref)
                where_clause = f"{id_col} = %s"
            else:
                entity_ref = args.entity_ref
                where_clause = f"{name_col} = %s"

            cur.execute(
                f"UPDATE {table} SET build_status = %s, last_updated = %s WHERE {where_clause}",
                (args.new_status, _now(), entity_ref),
            )
            if cur.rowcount == 0:
                print(f"ERROR: 未找到 {args.entity_type} {args.entity_ref!r}", file=sys.stderr)
                return 1
        conn.commit()
        print(f"OK: {args.entity_type} {args.entity_ref!r} build_status -> {args.new_status}")
        return 0
    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    finally:
        try:
            release_dataflow_write_lock(conn)
        except Exception:
            pass
        conn.close()


def cmd_list_datasets(args: argparse.Namespace) -> int:
    """列出所有 Dataset。"""
    init_dataflow_db()
    conn = get_dataflowgraph_pg_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT dataset_id, entity_name, scope, contract_ref, domain_id,
                       design_maturity, build_status, pit_policy
                FROM dataflow_datasets
                ORDER BY scope, entity_name
            """)
            rows = cur.fetchall()
        print(f"{'ID':>4}  {'entity_name':40}  {'scope':18}  {'contract':12}  {'domain':14}  {'maturity':10}  {'build':10}")
        print("-" * 130)
        for row in rows:
            print(f"{row[0]:>4}  {row[1]:40}  {row[2]:18}  {str(row[3] or '-'):12}  {str(row[4] or '-'):14}  {row[5]:10}  {row[6]:10}")
        print(f"\n共 {len(rows)} 个 Dataset")
        return 0
    finally:
        conn.close()


def cmd_list_jobs(args: argparse.Namespace) -> int:
    """列出所有 Job。"""
    init_dataflow_db()
    conn = get_dataflowgraph_pg_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT job_id, job_name, scope, source_code_ref, trigger_type,
                       design_maturity, build_status
                FROM dataflow_jobs
                ORDER BY scope, job_name
            """)
            rows = cur.fetchall()
        print(f"{'ID':>4}  {'job_name':35}  {'scope':18}  {'source_code_ref':50}  {'trigger':12}  {'maturity':10}  {'build':10}")
        print("-" * 150)
        for row in rows:
            print(f"{row[0]:>4}  {row[1]:35}  {row[2]:18}  {str(row[3] or '-'):50}  {str(row[4] or '-'):12}  {row[5]:10}  {row[6]:10}")
        print(f"\n共 {len(rows)} 个 Job")
        return 0
    finally:
        conn.close()


def cmd_list_ops() -> int:
    """列出支持的 CLI 命令。"""
    print("apply_dataflowgraph.py 支持的命令：\n")
    print("写入命令（需 pg_advisory_lock(424243)）：")
    print("  --add-design-dataset       新增设计态 Dataset（design_maturity=design, build_status=planned）")
    print("  --add-design-job           新增设计态 Job（design_maturity=design, build_status=planned）")
    print("  --add-design-edge          新增设计态数据流边")
    print("  --transition-build-status  转换 build_status（planned→generated→testing→stable）")
    print()
    print("只读命令：")
    print("  --list-datasets            列出所有 Dataset")
    print("  --list-jobs                列出所有 Job")
    print("  --list-ops                  列出本帮助")
    print()
    print("写入互斥锁 key: %d（与 depgraph 的 424242 互不干扰）" % _DATAFLOW_ADVISORY_LOCK_KEY)
    return 0


# ---------------------------------------------------------------------------
# CLI 定义
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="dataflowgraph 变更写入工具（ARCH-051，对齐 apply_depgraph.py 风格）",
        epilog="所有写入操作通过 pg_advisory_lock(424243) 互斥。设计态默认 design_maturity=design, build_status=planned。",
    )

    # 只读命令
    parser.add_argument("--list-ops", action="store_true", help="列出支持的命令")
    parser.add_argument("--list-datasets", action="store_true", help="列出所有 Dataset")
    parser.add_argument("--list-jobs", action="store_true", help="列出所有 Job")

    # 写入命令
    parser.add_argument("--add-design-dataset", action="store_true", help="新增设计态 Dataset")
    parser.add_argument("--add-design-job", action="store_true", help="新增设计态 Job")
    parser.add_argument("--add-design-edge", action="store_true", help="新增设计态数据流边")
    parser.add_argument(
        "--transition-build-status",
        nargs=3,
        metavar=("ENTITY_TYPE", "ENTITY_REF", "NEW_STATUS"),
        help="转换 build_status: ENTITY_TYPE(dataset|job) ENTITY_REF(id或name) NEW_STATUS",
    )

    # Dataset 参数
    parser.add_argument("--entity-name", type=str, help="Dataset entity_name（如 market_data.tick）")
    parser.add_argument("--scope", type=str, default="production", choices=["production", "backtest_internal"], help="作用域")
    parser.add_argument("--contract-ref", type=str, default=None, help="契约引用（CTR-ID，回测内部为空）")
    parser.add_argument("--physical-type", type=str, default=None, help="物理类型引用")
    parser.add_argument("--produced-by-job", type=str, default=None, help="产出该 Dataset 的 Job 名称")
    parser.add_argument("--domain-id", type=str, default=None, help="所属域 ID")
    parser.add_argument("--pit-policy", type=str, default="strict", choices=["strict", "loose", "none"], help="PIT 策略")
    parser.add_argument("--format-summary", type=str, default=None, help="数据格式摘要")
    parser.add_argument("--valid-since", type=str, default=None, help="数据有效起始日期")

    # Job 参数
    parser.add_argument("--job-name", type=str, help="Job job_name（如 ingest.ifind_kline）")
    parser.add_argument("--source-code-ref", type=str, default=None, help="depgraph 模块 path（跨图关联）")
    parser.add_argument("--trigger-type", type=str, default=None, choices=["event_driven", "scheduled", "manual", "stream"], help="触发类型")
    parser.add_argument("--run-context", type=str, default=None, help="运行上下文")
    parser.add_argument("--pit-relevance", type=str, default="strict", choices=["strict", "loose", "none"], help="PIT 相关性")
    parser.add_argument("--description", type=str, default=None, help="作业描述")

    # Edge 参数
    parser.add_argument("--from-id", type=int, help="Edge 起点实体 ID")
    parser.add_argument("--to-id", type=int, help="Edge 终点实体 ID")
    parser.add_argument("--from-type", type=str, choices=["dataset", "job"], help="Edge 起点类型")
    parser.add_argument("--to-type", type=str, choices=["dataset", "job"], help="Edge 终点类型")
    parser.add_argument("--edge-type", type=str, default="push", choices=["push", "pull", "sync", "async", "event_driven"], help="边类型")

    # 通用
    parser.add_argument("--extra", nargs="*", help="额外 KEY=VALUE 参数")
    parser.add_argument("--dry-run", action="store_true", help="仅验证，不写入（预留，当前未实现）")

    args = parser.parse_args()

    # 分派
    if args.list_ops:
        sys.exit(cmd_list_ops())
    if args.list_datasets:
        sys.exit(cmd_list_datasets(args))
    if args.list_jobs:
        sys.exit(cmd_list_jobs(args))
    if args.add_design_dataset:
        if not args.entity_name:
            print("ERROR: --add-design-dataset 需要 --entity-name", file=sys.stderr)
            sys.exit(2)
        sys.exit(cmd_add_design_dataset(args))
    if args.add_design_job:
        if not args.job_name:
            print("ERROR: --add-design-job 需要 --job-name", file=sys.stderr)
            sys.exit(2)
        sys.exit(cmd_add_design_job(args))
    if args.add_design_edge:
        if not all([args.from_id, args.to_id, args.from_type, args.to_type]):
            print("ERROR: --add-design-edge 需要 --from-id --to-id --from-type --to-type", file=sys.stderr)
            sys.exit(2)
        sys.exit(cmd_add_design_edge(args))
    if args.transition_build_status:
        entity_type, entity_ref, new_status = args.transition_build_status
        if entity_type not in ("dataset", "job"):
            print(f"ERROR: ENTITY_TYPE 必须是 dataset 或 job，得到: {entity_type!r}", file=sys.stderr)
            sys.exit(2)
        args.entity_type = entity_type
        args.entity_ref = entity_ref
        args.new_status = new_status
        sys.exit(cmd_transition_build_status(args))

    # 无命令时显示帮助
    parser.print_help()
    sys.exit(0)


if __name__ == "__main__":
    main()
