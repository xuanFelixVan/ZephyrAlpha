# [BLUEPRINT] SH-GOV-003 | docs/03_modules/_domain_governance/blueprint.md | §dataflowgraph
# [MODULE] scripts.governance.apply_dataflowgraph
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance.dataflowgraph_schema; psycopg2
# [CONSUMERS] (manual CLI, invoked by AI/human for dataflowgraph modifications)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] all writes go through pg_advisory_lock(424243); design_maturity gating enforced
# [MODIFY-GUARD] dataflowgraph_schema.py; 03_create_dataflow_schema.sql
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] raises RuntimeError on connection failure; ValueError on invalid args
# [TESTS] tests/test_apply_dataflowgraph.py
# [A_module] module_id=SH-GOV-003 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-051
# noqa: m11-perm-manual-legitimate  合法 manual CLI 写入工具（ARCH-051 裁定）：人工/AI 按需调用 dataflowgraph 变更入口，对齐 apply_depgraph.py 模式，非永久自动运行器

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
    python scripts/governance/apply_dataflowgraph.py --add-design-job \
        --job-name ingest.minqmt_kline \
        --scope production \
        --source-code-ref src/zephyr/data/implementations/miniqmt_provider.py \
        --trigger-type scheduled

    # 列出所有 Dataset
    python scripts/governance/apply_dataflowgraph.py --list-datasets

    # 转换 build_status
    python scripts/governance/apply_dataflowgraph.py --transition-build-status 1 generated
"""

from __future__ import annotations

__manifest__ = """
args: []
description: apply_dataflowgraph.py — dataflowgraph 变更写入工具（CLI）
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import psycopg2

# 添加项目根到 sys.path（确保 zephyr.* 可导入）
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# 添加 _shared 到 sys.path（确保 _shared.constants 可导入）
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS  # noqa: E402

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
# SQL 集中化常量（§5.160.2 NO-BARE-SQL 治本：禁止 cur.execute 内裸 SQL 字面量）
# 对齐 apply_depgraph.py 的 SQL_* 模块级常量模式。
# ---------------------------------------------------------------------------
SQL_SELECT_JOB_BY_NAME = (
    "SELECT job_id, job_name, module_id, design_maturity, build_status FROM dataflow_jobs WHERE job_name = %s"
)
SQL_SELECT_JOB_BY_MODULE_ID = (
    "SELECT job_id, job_name, module_id, design_maturity, build_status FROM dataflow_jobs WHERE module_id = %s"
)
SQL_DELETE_EDGES_BY_ENTITY = "DELETE FROM dataflow_edges WHERE from_entity_id = %s OR to_entity_id = %s"
SQL_DELETE_JOB_BY_ID = "DELETE FROM dataflow_jobs WHERE job_id = %s"


def _backup_after_write(rc: int) -> None:
    """写操作成功后自动触发架构库备份（trae_054 v1.6.0 STEP0）。失败不阻断主流程。

    v2 扩展（2026-08-03）：backup_pg_architecture 覆盖全景 19 张 DB 真源表
    （depgraph+battle_map+decisiongraph+dataflowgraph），非仅 dataflowgraph。
    """
    if rc == EXIT_PASS:
        try:
            try:
                from scripts.governance.meta.backup_runtime_state import backup_pg_architecture
            except ImportError:
                from meta.backup_runtime_state import backup_pg_architecture
            backup_pg_architecture(throttle_seconds=60)
        except Exception as _e:  # noqa: BLE001
            print(f"[BACKUP-PG] WARNING: 备份失败（不阻断主流程）: {_e}", file=sys.stderr)


# ---------------------------------------------------------------------------
# 命令实现
# ---------------------------------------------------------------------------


def cmd_add_design_dataset(args: argparse.Namespace) -> int:
    """新增设计态 Dataset 节点。"""
    init_dataflow_db()
    conn = get_dataflowgraph_pg_connection(autocommit=False, allow_design_delete=True)  # ARCH-053: 允许设计态写入
    try:
        acquire_dataflow_write_lock(conn)
        with conn.cursor() as cur:
            # 检查 entity_name 是否已存在
            cur.execute("SELECT 1 FROM dataflow_datasets WHERE entity_name = %s", (args.entity_name,))
            if cur.fetchone() is not None:
                print(f"ERROR: Dataset entity_name={args.entity_name!r} 已存在", file=sys.stderr)
                return EXIT_FINDINGS
            extra = _parse_kv_pairs(args.extra)
            cur.execute(
                """
                INSERT INTO dataflow_datasets
                    (entity_name, entity_type, scope, contract_ref, physical_type,
                     produced_by_job, domain_id, design_maturity, build_status,
                     pit_policy, format_summary, valid_since, last_updated)
                VALUES (%s, 'dataset', %s, %s, %s, %s, %s, 'design', 'planned', %s, %s, %s, %s)
                RETURNING dataset_id
            """,
                (
                    args.entity_name,
                    args.scope,
                    args.contract_ref,
                    args.physical_type,
                    args.produced_by_job,
                    args.domain_id,
                    args.pit_policy,
                    args.format_summary,
                    args.valid_since or extra.get("valid_since"),
                    _now(),
                ),
            )
            dataset_id = cur.fetchone()[0]
        conn.commit()
        print(
            f"OK: 新增设计态 Dataset dataset_id={dataset_id} entity_name={args.entity_name!r} (design_maturity=design, build_status=planned)"
        )
        return EXIT_PASS
    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}", file=sys.stderr)
        return EXIT_FINDINGS
    finally:
        try:
            release_dataflow_write_lock(conn)
        except psycopg2.Error as lock_err:
            print(f"WARN: 释放 dataflow 写锁失败（可能遗留 advisory lock）: {lock_err}", file=sys.stderr)
        conn.close()


def cmd_add_design_job(args: argparse.Namespace) -> int:
    """新增设计态 Job 节点。"""
    init_dataflow_db()
    conn = get_dataflowgraph_pg_connection(autocommit=False, allow_design_delete=True)  # ARCH-053: 允许设计态写入
    try:
        acquire_dataflow_write_lock(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM dataflow_jobs WHERE job_name = %s", (args.job_name,))
            if cur.fetchone() is not None:
                print(f"ERROR: Job job_name={args.job_name!r} 已存在", file=sys.stderr)
                return EXIT_FINDINGS
            cur.execute(
                """
                INSERT INTO dataflow_jobs
                    (job_name, entity_type, scope, source_code_ref, trigger_type,
                     run_context, pit_relevance, description, design_maturity,
                     build_status, last_updated)
                VALUES (%s, 'job', %s, %s, %s, %s, %s, %s, 'design', 'planned', %s)
                RETURNING job_id
            """,
                (
                    args.job_name,
                    args.scope,
                    args.source_code_ref,
                    args.trigger_type,
                    args.run_context,
                    args.pit_relevance,
                    args.description,
                    _now(),
                ),
            )
            job_id = cur.fetchone()[0]
        conn.commit()
        print(
            f"OK: 新增设计态 Job job_id={job_id} job_name={args.job_name!r} (design_maturity=design, build_status=planned)"
        )
        return EXIT_PASS
    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}", file=sys.stderr)
        return EXIT_FINDINGS
    finally:
        try:
            release_dataflow_write_lock(conn)
        except psycopg2.Error as lock_err:
            print(f"WARN: 释放 dataflow 写锁失败（可能遗留 advisory lock）: {lock_err}", file=sys.stderr)
        conn.close()


def cmd_add_design_edge(args: argparse.Namespace) -> int:
    """新增设计态数据流边。"""
    init_dataflow_db()
    conn = get_dataflowgraph_pg_connection(autocommit=False, allow_design_delete=True)  # ARCH-053: 允许设计态写入
    try:
        acquire_dataflow_write_lock(conn)
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO dataflow_edges
                    (from_entity_id, to_entity_id, from_entity_type, to_entity_type,
                     edge_type, design_maturity, last_updated)
                VALUES (%s, %s, %s, %s, %s, 'design', %s)
                RETURNING edge_id
            """,
                (
                    args.from_id,
                    args.to_id,
                    args.from_type,
                    args.to_type,
                    args.edge_type,
                    _now(),
                ),
            )
            edge_id = cur.fetchone()[0]
        conn.commit()
        print(
            f"OK: 新增设计态 Edge edge_id={edge_id} {args.from_type}({args.from_id}) --{args.edge_type}--> {args.to_type}({args.to_id})"
        )
        return EXIT_PASS
    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}", file=sys.stderr)
        return EXIT_FINDINGS
    finally:
        try:
            release_dataflow_write_lock(conn)
        except psycopg2.Error as lock_err:
            print(f"WARN: 释放 dataflow 写锁失败（可能遗留 advisory lock）: {lock_err}", file=sys.stderr)
        conn.close()


def cmd_transition_build_status(args: argparse.Namespace) -> int:
    """转换 Dataset/Job 的 build_status。

    用法: --transition-build-status <entity_type> <entity_id|entity_name> <new_status>
      entity_type: dataset | job

    注意：build_status 合法值（planned/generated/testing/stable/deprecated/production，
    B-007 P0 2026-08-26 六态）由 DB CHECK
    约束定义（03_create_dataflow_schema.sql），不在代码中预校验以避免 VOCAB-HARDCODE
    门禁。非法值由 DB CHECK 约束拒绝，错误信息含合法值清单。
    （dataflow 图 stable→production 推进边开放属另案裁定，本命令维持 5 态链语义。）
    """
    init_dataflow_db()
    conn = get_dataflowgraph_pg_connection(autocommit=False, allow_design_delete=True)  # ARCH-053: 允许设计态写入
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
                return EXIT_FINDINGS
        conn.commit()
        print(f"OK: {args.entity_type} {args.entity_ref!r} build_status -> {args.new_status}")
        return EXIT_PASS
    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}", file=sys.stderr)
        return EXIT_FINDINGS
    finally:
        try:
            release_dataflow_write_lock(conn)
        except psycopg2.Error as lock_err:
            print(f"WARN: 释放 dataflow 写锁失败（可能遗留 advisory lock）: {lock_err}", file=sys.stderr)
        conn.close()


def cmd_delete_design_job(args: argparse.Namespace) -> int:
    """删除设计态 Job 节点（含其关联边，仅限 design_maturity=design）。

    用途：清理被弃用/重命名后的孤儿设计态 Job（如 module_id 变更后残留的旧占位节点）。
    安全闸：仅允许删除 design_maturity='design' 的 Job，禁止删除 production 运营态节点。
    定位方式：--job-name（精确名）或 --module-id（按 module_id 匹配，可批量）。

    用法:
        python scripts/governance/apply_dataflowgraph.py --delete-design-job --job-name MOD-XS-EXT-001
        python scripts/governance/apply_dataflowgraph.py --delete-design-job --module-id MOD-XS-EXT-001
    """
    if not args.job_name and not args.module_id:
        print("ERROR: --delete-design-job 需配合 --job-name 或 --module-id", file=sys.stderr)
        return EXIT_FINDINGS

    init_dataflow_db()
    conn = get_dataflowgraph_pg_connection(autocommit=False, allow_design_delete=True)  # ARCH-053: 允许设计态写入
    try:
        acquire_dataflow_write_lock(conn)
        with conn.cursor() as cur:
            if args.job_name:
                cur.execute(SQL_SELECT_JOB_BY_NAME, (args.job_name,))
            else:
                cur.execute(SQL_SELECT_JOB_BY_MODULE_ID, (args.module_id,))
            rows = cur.fetchall()
            if not rows:
                print(f"ERROR: 未找到 Job (job_name={args.job_name!r}, module_id={args.module_id!r})", file=sys.stderr)
                return EXIT_FINDINGS

            # 安全闸：仅允许删除 design 态 Job
            non_design = [r for r in rows if r[3] != "design"]
            if non_design:
                for r in non_design:
                    print(
                        f"ERROR: 拒绝删除非设计态 Job job_id={r[0]} job_name={r[1]!r} "
                        f"(design_maturity={r[3]}, build_status={r[4]})；仅允许删除 design 态节点。",
                        file=sys.stderr,
                    )
                return EXIT_FINDINGS

            deleted = 0
            for r in rows:
                job_id, job_name, module_id, _, _ = r
                # 级联清理关联边（from/to 任一端引用此 job_id）
                cur.execute(SQL_DELETE_EDGES_BY_ENTITY, (job_id, job_id))
                edge_count = cur.rowcount
                cur.execute(SQL_DELETE_JOB_BY_ID, (job_id,))
                deleted += 1
                print(
                    f"OK: 删除设计态 Job job_id={job_id} job_name={job_name!r} module_id={module_id!r} (级联边 {edge_count} 条)"
                )
        conn.commit()
        print(f"共删除 {deleted} 个设计态 Job")
        return EXIT_PASS
    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}", file=sys.stderr)
        return EXIT_FINDINGS
    finally:
        try:
            release_dataflow_write_lock(conn)
        except psycopg2.Error as lock_err:
            print(f"WARN: 释放 dataflow 写锁失败（可能遗留 advisory lock）: {lock_err}", file=sys.stderr)
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
        print(
            f"{'ID':>4}  {'entity_name':40}  {'scope':18}  {'contract':12}  {'domain':14}  {'maturity':10}  {'build':10}"
        )
        print("-" * 130)
        for row in rows:
            print(
                f"{row[0]:>4}  {row[1]:40}  {row[2]:18}  {row[3] or '-'!s:12}  {row[4] or '-'!s:14}  {row[5]:10}  {row[6]:10}"
            )
        print(f"\n共 {len(rows)} 个 Dataset")
        return EXIT_PASS
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
        print(
            f"{'ID':>4}  {'job_name':35}  {'scope':18}  {'source_code_ref':50}  {'trigger':12}  {'maturity':10}  {'build':10}"
        )
        print("-" * 150)
        for row in rows:
            print(
                f"{row[0]:>4}  {row[1]:35}  {row[2]:18}  {row[3] or '-'!s:50}  {row[4] or '-'!s:12}  {row[5]:10}  {row[6]:10}"
            )
        print(f"\n共 {len(rows)} 个 Job")
        return EXIT_PASS
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
    print("  --delete-design-job        删除设计态 Job（仅限 design 态，级联清理边；--job-name 或 --module-id）")
    print()
    print("只读命令：")
    print("  --list-datasets            列出所有 Dataset")
    print("  --list-jobs                列出所有 Job")
    print("  --list-ops                  列出本帮助")
    print()
    print("写入互斥锁 key: %d（与 depgraph 的 424242 互不干扰）" % _DATAFLOW_ADVISORY_LOCK_KEY)
    return EXIT_PASS


# ---------------------------------------------------------------------------
# CLI 定义
# ---------------------------------------------------------------------------


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
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
    parser.add_argument("--delete-design-job", action="store_true", help="删除设计态 Job（仅限 design 态，级联清理边）")
    parser.add_argument(
        "--transition-build-status",
        nargs=3,
        metavar=("ENTITY_TYPE", "ENTITY_REF", "NEW_STATUS"),
        help="转换 build_status: ENTITY_TYPE(dataset|job) ENTITY_REF(id或name) NEW_STATUS",
    )

    # Dataset 参数
    parser.add_argument("--entity-name", type=str, help="Dataset entity_name（如 market_data.tick）")
    parser.add_argument(
        "--scope", type=str, default="production", choices=["production", "backtest_internal"], help="作用域"
    )
    parser.add_argument("--contract-ref", type=str, default=None, help="契约引用（CTR-ID，回测内部为空）")
    parser.add_argument("--physical-type", type=str, default=None, help="物理类型引用")
    parser.add_argument("--produced-by-job", type=str, default=None, help="产出该 Dataset 的 Job 名称")
    parser.add_argument("--domain-id", type=str, default=None, help="所属域 ID")
    parser.add_argument(
        "--pit-policy", type=str, default="strict", choices=["strict", "loose", "none"], help="PIT 策略"
    )
    parser.add_argument("--format-summary", type=str, default=None, help="数据格式摘要")
    parser.add_argument("--valid-since", type=str, default=None, help="数据有效起始日期")

    # Job 参数
    parser.add_argument("--job-name", type=str, help="Job job_name（如 ingest.minqmt_kline）")
    parser.add_argument(
        "--module-id", type=str, default=None, help="module_id（--delete-design-job 按 module_id 定位）"
    )
    parser.add_argument("--source-code-ref", type=str, default=None, help="depgraph 模块 path（跨图关联）")
    parser.add_argument(
        "--trigger-type",
        type=str,
        default=None,
        choices=["event_driven", "scheduled", "manual", "stream"],
        help="触发类型",
    )
    parser.add_argument("--run-context", type=str, default=None, help="运行上下文")
    parser.add_argument(
        "--pit-relevance", type=str, default="strict", choices=["strict", "loose", "none"], help="PIT 相关性"
    )
    parser.add_argument("--description", type=str, default=None, help="作业描述")

    # Edge 参数
    parser.add_argument("--from-id", type=int, help="Edge 起点实体 ID")
    parser.add_argument("--to-id", type=int, help="Edge 终点实体 ID")
    parser.add_argument("--from-type", type=str, choices=["dataset", "job"], help="Edge 起点类型")
    parser.add_argument("--to-type", type=str, choices=["dataset", "job"], help="Edge 终点类型")
    parser.add_argument(
        "--edge-type",
        type=str,
        default="push",
        choices=["push", "pull", "sync", "async", "event_driven"],
        help="边类型",
    )

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
            sys.exit(EXIT_ERROR)
        rc = cmd_add_design_dataset(args)
        _backup_after_write(rc)
        sys.exit(rc)
    if args.add_design_job:
        if not args.job_name:
            print("ERROR: --add-design-job 需要 --job-name", file=sys.stderr)
            sys.exit(EXIT_ERROR)
        rc = cmd_add_design_job(args)
        _backup_after_write(rc)
        sys.exit(rc)
    if args.add_design_edge:
        if not all([args.from_id, args.to_id, args.from_type, args.to_type]):
            print("ERROR: --add-design-edge 需要 --from-id --to-id --from-type --to-type", file=sys.stderr)
            sys.exit(EXIT_ERROR)
        rc = cmd_add_design_edge(args)
        _backup_after_write(rc)
        sys.exit(rc)
    if args.delete_design_job:
        rc = cmd_delete_design_job(args)
        _backup_after_write(rc)
        sys.exit(rc)
    if args.transition_build_status:
        entity_type, entity_ref, new_status = args.transition_build_status
        if entity_type not in ("dataset", "job"):
            print(f"ERROR: ENTITY_TYPE 必须是 dataset 或 job，得到: {entity_type!r}", file=sys.stderr)
            sys.exit(EXIT_ERROR)
        args.entity_type = entity_type
        args.entity_ref = entity_ref
        args.new_status = new_status
        rc = cmd_transition_build_status(args)
        _backup_after_write(rc)
        sys.exit(rc)

    # 无命令时显示帮助
    parser.print_help()
    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    try:
        main()
    finally:
        # 生成器自动重生成（reconcile_generators §双路径调用）：
        # apply 写完 DB → reconcile("dataflowgraph_db") 查注册表调全部 dataflowgraph 读取生成器。
        # 生成失败不阻断 apply（apply 是真源，生成是派生，§2.3 派生关系）。
        # ZEPHYR_SKIP_REGENERATE=1 逃生通道：批量操作时可跳过（boot_hooks 启动兜底）。
        import os as _os
        import sys as _sys

        is_dry_run = "--dry-run" in _sys.argv
        _write_cmds = {
            "--add-design-dataset",
            "--add-design-job",
            "--add-design-edge",
            "--delete-design-job",
            "--transition-build-status",
            "--batch",
        }
        has_write_cmd = any(arg in _write_cmds for arg in _sys.argv)
        if has_write_cmd and not is_dry_run and _os.environ.get("ZEPHYR_SKIP_REGENERATE") != "1":
            try:
                try:
                    from scripts.governance.reconcile_generators import reconcile_async
                except ImportError:
                    from reconcile_generators import reconcile_async
                regen = reconcile_async("dataflowgraph_db")
                if regen.get("status") == "spawned":
                    print(
                        f"[REGENERATE] 🔄 后台启动 PID={regen['pid']} 日志: {regen['log_file']}",
                        file=_sys.stderr,
                    )
                else:
                    print(f"[REGENERATE] WARNING: 后台启动失败（不阻断写入）: {regen.get('error')}", file=_sys.stderr)
            except Exception as _e:  # noqa: BLE001 — 编排器不可用不阻断主流程
                print(f"[REGENERATE] WARNING: 编排器不可用（不阻断写入）: {_e}", file=_sys.stderr)
