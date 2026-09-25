# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_scheduling
# [MODULE] scripts.ai_layer.apply_ai_layer_scheduling_ddl
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection)
# [CONSUMERS] CLI python scripts/ai_layer/apply_ai_layer_scheduling_ddl.py [--schema ai_scheduling] [--verify];
#             zephyr.ai_layer.scheduling.order_daemon（工单持久化 sink 的表结构真源）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] DDL-as-Code: L5 工单库表 DDL 真源即本文件（设计真源=docs/_working/ai_layer_vision/
#              L5_schedule_gate/DESIGN.md §2 C2）; PG 同实例独立 schema `ai_scheduling`，与 L2 ai_intake
#              schema 隔离（生熟分离产线禁读界不破）; 全部幂等(SCHEMA/TABLE/INDEX IF NOT EXISTS);
#              时间戳一律 TIMESTAMPTZ(RULE-SCHEMA-TZ); 状态机 CHECK 七态枚举（§2.7，与 policy
#              order_states 同表驱动）; audit_log 追加only（触发器前缀校验：可追加禁改禁删）;
#              schema 名白名单 ^ai_scheduling(_test_...)?$ fail-closed（防 DDL/DROP 打偏）;
#              DROP 仅 ai_scheduling_test_ 前缀允许
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L5_schedule_gate/DESIGN.md §2.7（状态机变更先改设计稿）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PG 不可达->打印错误+退出码 2; schema 名不合规->ValueError 立即拒跑; DDL 失败->
#                  回滚+非零退出; --verify 缺件->退出码 3 并列缺失清单
# [TESTS] tests/ai_layer/scheduling/test_scheduling_ddl.py（schema 名白名单/DDL 渲染含七态 CHECK/
#         审计守卫触发器在册/--verify 缺件路径；PG 部署为 opt-in 不进默认测试）
# [TTL] permanent
"""AI 层 L5 排产段——工单库 DDL 部署器（PG depgraph 同实例，独立 schema `ai_scheduling`）。

设计真源：``docs/_working/ai_layer_vision/L5_schedule_gate/DESIGN.md`` §2 C2（B9 修复：独立
schema 与 L2 ai_intake 隔离）。照 ``scripts/ai_layer/apply_ai_intake_ddl.py`` 母版同模式实现
（admin 通道 + 幂等 + 角色分级 GRANT）。

表清单::

    ai_scheduling.ai_work_order  进化施工工单主表（任务书附录 A schema v0 十三字段+状态机+审计）

用法::

    python scripts/ai_layer/apply_ai_layer_scheduling_ddl.py            # 部署 ai_scheduling（幂等）
    python scripts/ai_layer/apply_ai_layer_scheduling_ddl.py --verify   # 只核对不部署
"""

from __future__ import annotations

import argparse
import functools
import logging
import re
import sys
from pathlib import Path
from typing import Any, Final

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402
from zephyr.governance.depgraph_schema import (  # noqa: E402
    deploy_schema as _deploy_schema_engine,
    drop_test_schema as _drop_test_schema_engine,
    q_list as _q_list,
)

log = logging.getLogger("ai_scheduling.ddl")

SCHEMA_RE: Final = re.compile(r"^ai_scheduling(_test_[a-z0-9_]+)?$")
TEST_SCHEMA_PREFIX: Final = "ai_scheduling_test_"


# FUNCTION-DUP 治本（2026-09-24）：deploy/drop 引擎唯一实现收敛 depgraph_schema，本模块按自身 DDL/GRANT/种子源绑定
deploy = functools.partial(
    _deploy_schema_engine,
    ddl_statements_fn=lambda schema: _ddl_statements(schema),
    grant_statements_fn=lambda schema: _grant_statements(schema),
)
drop_test_schema = functools.partial(_drop_test_schema_engine, test_schema_prefix=TEST_SCHEMA_PREFIX)
DEFAULT_SCHEMA: Final = "ai_scheduling"

# 工单状态机七态（DESIGN §2.7；与 config/schedule_gate_policy.yaml order_states 同表驱动）
ORDER_STATES: Final[tuple[str, ...]] = (
    "pending",
    "held_maturity",
    "held_incomplete",
    "dispatched",
    "deferred",
    "done",
    "dead",
)

_SQL_WORK_ORDER = """
CREATE TABLE IF NOT EXISTS {s}.ai_work_order (
    order_id            TEXT PRIMARY KEY,
    schema_version      TEXT NOT NULL DEFAULT '0.1',
    title               TEXT NOT NULL CHECK (length(btrim(title)) > 0),
    domain_id           TEXT NOT NULL,
    contractor          JSONB NOT NULL DEFAULT '{{}}'::jsonb,
    objective           TEXT NOT NULL CHECK (length(btrim(objective)) > 0),
    definition_of_done  JSONB NOT NULL DEFAULT '{{}}'::jsonb,
    red_lines           JSONB NOT NULL DEFAULT '{{}}'::jsonb,
    budget              JSONB NOT NULL DEFAULT '{{}}'::jsonb,
    pre_rulings         JSONB NOT NULL DEFAULT '[]'::jsonb,
    acceptance          JSONB NOT NULL DEFAULT '{{}}'::jsonb,
    rollback_plan       JSONB NOT NULL DEFAULT '{{}}'::jsonb,
    constitution_discipline JSONB NOT NULL DEFAULT '{{}}'::jsonb,
    honesty_clause      JSONB NOT NULL DEFAULT '{{}}'::jsonb,
    experiment_id       TEXT,
    criteria_hash       TEXT,
    significance        TEXT,
    labor_killed        TEXT,
    starred             BOOLEAN NOT NULL DEFAULT false,
    owner_gate          BOOLEAN NOT NULL DEFAULT false,
    priority_score      REAL,
    state               TEXT NOT NULL DEFAULT 'pending' CHECK (state IN ({states})),
    held_reason         TEXT,
    defer_count         SMALLINT NOT NULL DEFAULT 0,
    dispatch_fail_count SMALLINT NOT NULL DEFAULT 0,
    mech_check_fail_count SMALLINT NOT NULL DEFAULT 0,
    audit_log           JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
)
"""

# 追加only 审计守卫：audit_log 只许前缀追加（改/删/重排一律拒绝），DESIGN C2 "append-only 审计字段"
_SQL_AUDIT_GUARD_FN = """
CREATE OR REPLACE FUNCTION {s}._ai_work_order_audit_guard() RETURNS trigger AS $fn$
BEGIN
    IF OLD.audit_log IS DISTINCT FROM NEW.audit_log
       AND left(NEW.audit_log::text, length(OLD.audit_log::text)) IS DISTINCT FROM OLD.audit_log::text THEN
        RAISE EXCEPTION 'append-only violation: ai_work_order.audit_log 前缀被改写';
    END IF;
    NEW.updated_at := now();
    RETURN NEW;
END;
$fn$ LANGUAGE plpgsql
"""

_SQL_AUDIT_TRIGGER = """
DROP TRIGGER IF EXISTS trg_ai_work_order_audit ON {s}.ai_work_order
"""

_SQL_AUDIT_TRIGGER_CREATE = """
CREATE TRIGGER trg_ai_work_order_audit
BEFORE UPDATE ON {s}.ai_work_order
FOR EACH ROW EXECUTE FUNCTION {s}._ai_work_order_audit_guard()
"""

_SQL_INDEXES: Final[tuple[str, ...]] = (
    "CREATE INDEX IF NOT EXISTS ix_work_order_state ON {s}.ai_work_order (state, priority_score)",
    "CREATE INDEX IF NOT EXISTS ix_work_order_domain ON {s}.ai_work_order (domain_id, state)",
    "CREATE INDEX IF NOT EXISTS ix_work_order_experiment ON {s}.ai_work_order (experiment_id)",
)


def _ddl_statements(schema: str) -> list[str]:
    """渲染全部 DDL 语句（幂等；schema 名已由 check_schema_name 白名单校验）。"""
    fmt: dict[str, Any] = {"s": schema, "states": _q_list(ORDER_STATES)}
    out = [
        f"CREATE SCHEMA IF NOT EXISTS {schema}",
        _SQL_WORK_ORDER.format(**fmt),
        _SQL_AUDIT_GUARD_FN.format(**fmt),
        _SQL_AUDIT_TRIGGER.format(**fmt),
        _SQL_AUDIT_TRIGGER_CREATE.format(**fmt),
    ]
    out.extend(tpl.format(**fmt) for tpl in _SQL_INDEXES)
    return out


def _grant_statements(schema: str) -> list[str]:
    """角色分级授权（照 apply_ai_intake_ddl 母版惯例：reader 只读 / writer 读写）。"""
    out = [
        f"GRANT USAGE ON SCHEMA {schema} TO depgraph_reader",
        f"GRANT USAGE ON SCHEMA {schema} TO depgraph_writer",
    ]
    out.append(f"GRANT SELECT ON {schema}.ai_work_order TO depgraph_reader")
    out.append(
        f"GRANT SELECT, INSERT, UPDATE, DELETE ON {schema}.ai_work_order TO depgraph_writer"
    )
    return out


def check_schema_name(schema: str) -> str:
    """schema 名白名单校验（fail-closed：不合规直接 ValueError，绝不静默改名）。"""
    if not SCHEMA_RE.match(schema or ""):
        raise ValueError(
            f"schema 名不合规：{schema!r}（只许 ai_scheduling 或 ai_scheduling_test_<后缀>，"
            "防 DDL/DROP 打偏到他人 schema——与 L2 ai_intake schema 隔离边界）"
        )
    return schema


EXPECTED_TABLES: Final[tuple[str, ...]] = ("ai_work_order",)
SQL_VERIFY_RELATIONS = (
    "SELECT table_name, table_type FROM information_schema.tables "
    "WHERE table_schema = %s ORDER BY table_name"
)
SQL_VERIFY_CHECK_STATES = (
    "SELECT pg_get_constraintdef(c.oid) FROM pg_constraint c "
    "JOIN pg_class t ON c.conrelid = t.oid "
    "JOIN pg_namespace n ON t.relnamespace = n.oid "
    "WHERE n.nspname = %s AND t.relname = 'ai_work_order' AND c.contype = 'c'"
)


def verify(schema: str = DEFAULT_SCHEMA, *, conn: Any | None = None) -> tuple[bool, list[str]]:
    """核对表/状态机 CHECK/审计守卫触发器是否齐全（只读，不部署）。返回 (齐全?, 缺失清单)。"""
    check_schema_name(schema)
    own_conn = conn is None
    if own_conn:
        conn = get_depgraph_pg_connection(read_only=True)
    missing: list[str] = []
    try:
        cur = conn.cursor()
        cur.execute(SQL_VERIFY_RELATIONS, (schema,))
        found = {row[0] for row in cur.fetchall()}
        for t in EXPECTED_TABLES:
            if t not in found:
                missing.append(f"table:{t}")
        cur.execute(SQL_VERIFY_CHECK_STATES, (schema,))
        check_defs = " ".join(str(row[0]) for row in cur.fetchall())
        for st in ORDER_STATES:
            if f"'{st}'" not in check_defs:
                missing.append(f"check_state:{st}")
        cur.execute(
            "SELECT tgname FROM pg_trigger t "  # noqa: bare-sql  bare-sql豁免: P1存量伪新增,域内SQL集中通道,§5.160.2专项另列
            "JOIN pg_class c ON t.tgrelid = c.oid "
            "JOIN pg_namespace n ON c.relnamespace = n.oid "
            "WHERE n.nspname = %s AND c.relname = 'ai_work_order' AND NOT t.tgisinternal",
            (schema,),
        )
        triggers = {str(row[0]) for row in cur.fetchall()}
        if "trg_ai_work_order_audit" not in triggers:
            missing.append("trigger:trg_ai_work_order_audit")
    finally:
        if own_conn:
            conn.close()
    return (not missing), missing


def main(argv: list[str] | None = None) -> int:
    """CLI 入口：部署或核对 ai_scheduling schema。"""
    parser = argparse.ArgumentParser(description="AI 层 L5 排产段工单库 DDL 部署器（幂等）")
    parser.add_argument("--schema", default=DEFAULT_SCHEMA, help="目标 schema（默认 ai_scheduling）")
    parser.add_argument("--verify", action="store_true", help="只核对不部署")
    parser.add_argument(
        "--drop-test-schema",
        action="store_true",
        help="删除测试残留 schema（仅 ai_scheduling_test_ 前缀）",
    )
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        if args.drop_test_schema:
            drop_test_schema(args.schema)
            print(f"DROPPED test schema {args.schema}")
            return 0
        if args.verify:
            ok, missing = verify(args.schema)
            print(f"VERIFY {args.schema}: {'OK' if ok else 'MISSING ' + ','.join(missing)}")
            return 0 if ok else 3
        counts = deploy(args.schema)
        ok, missing = verify(args.schema)
        print(f"DEPLOYED {args.schema} {counts} verify={'OK' if ok else missing}")
        return 0 if ok else 3
    except ValueError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001——CLI 边界统一转退出码 2（PG 不可达/权限不足等）
        print(f"DDL FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: DDL 部署器属人工运维入口，非自动常驻任务
    sys.exit(main())
