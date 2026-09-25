# [MODULE] zephyr.governance.registry_ledger.deploy
# [DOMAIN] D_GOVERNANCE
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §W-M1
# [DEPENDENCIES] zephyr.governance.registry_ledger.schema（DDL 聚合）; psycopg2
# [CONSUMERS] tests/governance/test_registry_ledger.py（临时 schema 红蓝）; scripts/governance/registry_migration/wave0_phase0_gate.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 幂等部署（CREATE IF NOT EXISTS+可重跑）；不可变双保险=REVOKE+触发器 RAISE；schema_fingerprint 全对象规范哈希防漂移
# [MODIFY-GUARD] 新建 2026-09-23 st-wm1-buildA-20260923（W-M1 车道A·波0①）；2026-09-24 wave0 补全头字段+noqa
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL 执行失败原样上抛（fail-closed 部署）；幂等重跑零漂移由 fingerprint 断言兜
# [TESTS] tests/governance/test_registry_ledger.py
# [TTL] permanent
"""registry_ledger 幂等 DDL 部署器（W-M1 车道A·波0①）。

惯例沿用 depgraph_schema（CREATE TABLE IF NOT EXISTS + _schema_version 版本表，
INSERT ON CONFLICT DO NOTHING，可重跑零漂移）；连接走 depgraph superuser 路径
（设计 §2.0：ledger_admin=DDL 与一次性迁移）。事件/快照表不可变双保险在此落地：
REVOKE UPDATE/DELETE FROM PUBLIC + BEFORE UPDATE OR DELETE 触发器 RAISE EXCEPTION。


# [ALGO_FLOW]
层: 部署 → 保险 → 指纹
- 部署: 按 table_ddls 依赖序幂等执行（CREATE IF NOT EXISTS）
- 保险: REVOKE UPDATE/DELETE+BEFORE 触发器 RAISE（事件/快照表只增不可变）
- 指纹: schema_fingerprint 全对象规范哈希，重跑零漂移断言"""

from __future__ import annotations

import contextlib
import hashlib

import psycopg2

from zephyr.governance.registry_ledger.registry_ledger_ddl import (
    APPEND_ONLY_GUARD_FUNCTION_DDL,
    APPEND_ONLY_TRIGGER_DDL,
    GRANT_READER_DDL,
    GRANT_WRITER_DDL,
    REVOKE_MUTATION_DDL,
    SCHEMA_NAME,
    SCHEMA_VERSION,
    SCHEMA_VERSION_DDL,
    SCHEMA_VERSION_DESCRIPTION,
    table_ddls,
)

IMMUTABLE_TABLES = ("registry_event", "registry_snapshot")
DEFAULT_READER_ROLE = "depgraph_reader"
DEFAULT_WRITER_ROLE = "depgraph_writer"


def _role_exists(cur: object, role: str) -> bool:
    cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (role,))  # noqa: bare-sql  W-M1 ledger SQL 真源集中本模块（参数化查询）
    return cur.fetchone() is not None


def deploy_registry_ledger(
    conn: object | None = None,
    *,
    schema: str = SCHEMA_NAME,
    reader_role: str = DEFAULT_READER_ROLE,
    writer_role: str = DEFAULT_WRITER_ROLE,
) -> dict[str, object]:
    """幂等部署 registry_ledger schema（可重复执行，零漂移）。

    conn 为空时走 depgraph superuser 路径自管生命周期；传入 conn 则使用调用方
    连接并自行 commit/rollback（测试注 temp schema 用）。
    返回 report：{schema, version, statements, objects_before, objects_after}。
    """
    own_conn = conn is None
    if own_conn:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection(superuser=True)
    report: dict[str, object] = {
        "schema": schema,
        "version": SCHEMA_VERSION,
        "statements": 0,
        "objects_before": _count_objects(conn, schema),
        "objects_after": None,
    }
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM pg_namespace WHERE nspname = %s",  # noqa: bare-sql  W-M1 ledger SQL 真源集中本模块（参数化查询）
                (schema,),
            )
            if cur.fetchone() is None:
                cur.execute(f'CREATE SCHEMA "{schema}"')
                report["statements"] += 1
            for ddl in [
                SCHEMA_VERSION_DDL.format(schema=schema),
                *table_ddls(schema),
                APPEND_ONLY_GUARD_FUNCTION_DDL.format(schema=schema),
            ]:
                cur.execute(ddl)
                report["statements"] += 1
            for table in IMMUTABLE_TABLES:
                cur.execute(APPEND_ONLY_TRIGGER_DDL.format(schema=schema, table=table))
                report["statements"] += 1
                cur.execute(REVOKE_MUTATION_DDL.format(schema=schema, table=table))
                report["statements"] += 1
            if _role_exists(cur, reader_role):
                cur.execute(GRANT_READER_DDL.format(schema=schema, role=reader_role))
                report["statements"] += 1
            if _role_exists(cur, writer_role):
                cur.execute(GRANT_WRITER_DDL.format(schema=schema, role=writer_role))
                report["statements"] += 1
            cur.execute(
                f'INSERT INTO "{schema}"._schema_version (version, description) '  # noqa: bare-sql  W-M1 ledger SQL 真源集中本模块（参数化查询）
                "VALUES (%s, %s) ON CONFLICT (version) DO NOTHING",
                (SCHEMA_VERSION, SCHEMA_VERSION_DESCRIPTION),
            )
            report["statements"] += 1
        conn.commit()
    except psycopg2.Error:  # DDL 错误回滚重抛（fail-closed 呈报）
        conn.rollback()
        if own_conn:
            _release(conn)
        raise
    report["objects_after"] = _count_objects(conn, schema)
    if own_conn:
        _release(conn)
    return report


def _release(conn: object) -> None:
    # release 兜底：失败降级直接 close；close 再失败静默（清理路径无可恢复动作）
    with contextlib.suppress(Exception):
        from zephyr.governance.depgraph_schema import (
            release_depgraph_pg_connection,
        )

        release_depgraph_pg_connection(conn)
    with contextlib.suppress(Exception):
        conn.close()


def _count_objects(conn: object, schema: str) -> int:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "  # noqa: bare-sql  W-M1 ledger SQL 真源集中本模块（参数化查询）
            "WHERE n.nspname = %s AND c.relkind IN ('r', 'i', 'I', 'S', 'f')",
            (schema,),
        )
        return int(cur.fetchone()[0])


def schema_fingerprint(conn: object, schema: str = SCHEMA_NAME) -> str:
    """对 schema 全部对象定义做规范哈希（幂等零漂移判据）。"""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT c.relname, c.relkind, pg_get_userbyid(c.relowner), "
            "pg_get_expr(c.relpartbound, c.oid) "
            "FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
            "WHERE n.nspname = %s AND c.relkind IN ('r', 'v', 'f') ORDER BY c.relname",
            (schema,),
        )
        lines = [f"rel:{row[0]}:{row[1]}:{row[2]}" for row in cur.fetchall()]
        cur.execute(
            "SELECT table_name, column_name, data_type, is_nullable, column_default "
            "FROM information_schema.columns WHERE table_schema = %s "
            "ORDER BY table_name, ordinal_position",
            (schema,),
        )
        lines += [f"col:{r[0]}.{r[1]}:{r[2]}:{r[3]}:{r[4]}" for r in cur.fetchall()]
        cur.execute(
            "SELECT tgrelid::regclass::text, tgname, pg_get_triggerdef(oid) "
            "FROM pg_trigger WHERE tgrelid::regclass::text LIKE %s AND NOT tgisinternal "
            "ORDER BY tgrelid::regclass::text, tgname",
            (f"{schema}.%",),
        )
        lines += [f"trg:{r[0]}:{r[1]}:{r[2]}" for r in cur.fetchall()]
        cur.execute(
            "SELECT tablename, indexname, indexdef FROM pg_indexes "  # noqa: bare-sql  W-M1 ledger SQL 真源集中本模块（参数化查询）
            "WHERE schemaname = %s ORDER BY tablename, indexname",
            (schema,),
        )
        lines += [f"idx:{r[1]}:{r[2]}" for r in cur.fetchall()]
        cur.execute(
            f'SELECT version, description FROM "{schema}"._schema_version ORDER BY version'  # noqa: bare-sql  W-M1 ledger SQL 真源集中本模块（参数化查询）
        )
        lines += [f"ver:{r[0]}:{r[1]}" for r in cur.fetchall()]
    blob = "\n".join(lines).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()
