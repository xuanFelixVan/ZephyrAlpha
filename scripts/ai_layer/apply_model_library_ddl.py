# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §model_library
# [MODULE] scripts.ai_layer.apply_model_library_ddl
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection)
# [CONSUMERS] CLI python scripts/ai_layer/apply_model_library_ddl.py [--schema ai_layer_model] [--verify] [--drop-test-schema];
#             M2 写入方（模型入库器/评分回写器/牌价时序写入=后续批）；tests/ai_layer/test_model_library_ddl.py
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] DDL-as-Code: ai_layer_model 三表 DDL 真源即本文件（设计真源=docs/_working/ai_layer_vision/OBJ_M_models/DESIGN.md §3.1-§3.2）;
#              全部幂等(CREATE SCHEMA/TABLE/INDEX IF NOT EXISTS); 时间戳一律 TIMESTAMPTZ(RULE-SCHEMA-TZ 同义执行);
#              生熟分离=未过四闸的情报禁入 model_registry（写入方责任，DB 层不做闸判定）;
#              provider 前缀须在 model_routing_policy.yaml 词表内（写入方责任，DB 层不硬编码词表）;
#              墓碑制退役不删: status='tombstone' 是合法终态, registry 禁物理删行; price/promo 两 history 表只增不改(append-only);
#              牌价数值真源=config/model_pricing.yaml, model_registry.input_price 等列只是缓存视图(D-M2-01 SSOT 分界);
#              schema 名必须匹配 ^ai_layer_model(_test_[a-z0-9_]+)?$ (fail-closed, 防 DROP/CREATE 打偏);
#              DROP 仅在 --drop-test-schema 且 schema 以 ai_layer_model_test_ 前缀时允许(测试残留清理专用)
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_M_models/DESIGN.md §3.2（改表结构先改设计稿）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PG 不可达->打印错误+退出码 2; schema 名不合规->ValueError 立即拒跑(不静默改名); DDL 语句失败->回滚+非零退出;
#                  --verify 缺件->退出码 3 并列出缺失清单
# [TESTS] tests/ai_layer/test_model_library_ddl.py（ai_layer_model_test_ 前缀临时 schema 部署+verify+DROP; PG 不可达=skip 而非假绿）
# [TTL] permanent
"""AI 层 OBJ_M M2——模型库三表 DDL 部署器（PostgreSQL depgraph 同实例，schema `ai_layer_model`）。

设计真源：``docs/_working/ai_layer_vision/OBJ_M_models/DESIGN.md`` §3.1-§3.3（三表+双轴打分口径）。
照 ``scripts/ai_layer/apply_ai_intake_ddl.py`` 模式实现（admin 通道 + 幂等 + 角色分级 GRANT）。

表清单::

    model_registry       T1 模型档案+评分主表（生熟分离熟食库：只收过四闸情报）
    model_price_history  T2 牌价时序（只增不改；数值真源=model_pricing.yaml，此为历史留痕）
    model_promo_history  T3 活动史（只增不改；deprecation 事件触发路由表体检）

索引：两 history 表 model_id 各建 btree（model_registry.model_id=主键自带 btree，不建冗余索引）。

用法::

    python scripts/ai_layer/apply_model_library_ddl.py            # 部署 ai_layer_model（幂等）
    python scripts/ai_layer/apply_model_library_ddl.py --verify   # 只核对件数不部署
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path
from typing import Any, Final

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402

log = logging.getLogger("ai_layer_model.ddl")

SCHEMA_RE: Final = re.compile(r"^ai_layer_model(_test_[a-z0-9_]+)?$")
TEST_SCHEMA_PREFIX: Final = "ai_layer_model_test_"
DEFAULT_SCHEMA: Final = "ai_layer_model"

CHANNELS: Final[tuple[str, ...]] = ("api", "local")
TIERS: Final[tuple[str, ...]] = ("premium", "standard", "economy")
STATUSES: Final[tuple[str, ...]] = ("candidate", "active", "retired", "tombstone")
PROMO_TYPES: Final[tuple[str, ...]] = ("price_cut", "free_window", "promo", "deprecation")


def _q_list(values: tuple[str, ...]) -> str:
    """把常量元组渲染成 SQL 单引号列表（值来源全是本模块常量，非外部输入）。"""
    return ", ".join("'" + v.replace("'", "''") + "'" for v in values)


_SQL_MODEL_REGISTRY = """
CREATE TABLE IF NOT EXISTS {s}.model_registry (
    model_id             TEXT PRIMARY KEY,
    provider             TEXT NOT NULL,
    channel              TEXT NOT NULL CHECK (channel IN ({channels})),
    endpoint             TEXT,
    api_version          TEXT,
    alias                TEXT,
    input_price          NUMERIC,
    output_price         NUMERIC,
    peak_off_peak        JSONB,
    cache_price          NUMERIC,
    price_source_url     TEXT,
    price_updated_at     TIMESTAMPTZ,
    context_window       INTEGER,
    max_output_tokens    INTEGER,
    strengths            JSONB,
    weaknesses           JSONB,
    job_matches          JSONB,
    passport_ref         JSONB,
    exam_suite_version   TEXT,
    exam_at              TIMESTAMPTZ,
    arena_rank           INTEGER,
    aa_intelligence      NUMERIC,
    external_snapshot_at TIMESTAMPTZ,
    free_window          JSONB,
    promos               JSONB,
    meas_30d             JSONB,
    perf_p               NUMERIC,
    value_v              NUMERIC,
    score_s              NUMERIC,
    tier                 TEXT CHECK (tier IN ({tiers})),
    score_policy_version TEXT,
    scored_at            TIMESTAMPTZ,
    status               TEXT NOT NULL DEFAULT 'candidate' CHECK (status IN ({statuses})),
    registered_at        TIMESTAMPTZ NOT NULL,
    deprecation_notice   TEXT
)
"""

_SQL_PRICE_HISTORY = """
CREATE TABLE IF NOT EXISTS {s}.model_price_history (
    id            BIGSERIAL PRIMARY KEY,
    model_id      TEXT NOT NULL,
    price_date    TIMESTAMPTZ NOT NULL,
    input_price   NUMERIC,
    output_price  NUMERIC,
    peak_off_peak JSONB,
    source_url    TEXT,
    recorded_at   TIMESTAMPTZ NOT NULL
)
"""

_SQL_PROMO_HISTORY = """
CREATE TABLE IF NOT EXISTS {s}.model_promo_history (
    id         BIGSERIAL PRIMARY KEY,
    model_id   TEXT NOT NULL,
    promo_date TIMESTAMPTZ NOT NULL,
    promo_type TEXT NOT NULL CHECK (promo_type IN ({promo_types})),
    url        TEXT,
    impact     TEXT,
    recorded_at TIMESTAMPTZ NOT NULL
)
"""

_SQL_INDEXES: Final[tuple[str, ...]] = (
    "CREATE INDEX IF NOT EXISTS ix_model_price_history_model_id ON {s}.model_price_history (model_id)",
    "CREATE INDEX IF NOT EXISTS ix_model_promo_history_model_id ON {s}.model_promo_history (model_id)",
)

_SQL_CREATE_SCHEMA: Final[str] = "CREATE SCHEMA IF NOT EXISTS {s}"

_SQL_GRANT_READER_USAGE: Final[str] = "GRANT USAGE ON SCHEMA {s} TO depgraph_reader"
_SQL_GRANT_WRITER_USAGE: Final[str] = "GRANT USAGE ON SCHEMA {s} TO depgraph_writer"
_SQL_GRANT_WRITER_SEQ_PRICE: Final[str] = (
    "GRANT USAGE, SELECT ON SEQUENCE {s}.model_price_history_id_seq TO depgraph_writer"
)
_SQL_GRANT_WRITER_SEQ_PROMO: Final[str] = (
    "GRANT USAGE, SELECT ON SEQUENCE {s}.model_promo_history_id_seq TO depgraph_writer"
)
_SQL_GRANT_READER_TABLE: Final[str] = "GRANT SELECT ON {s}.{t} TO depgraph_reader"
_SQL_GRANT_WRITER_TABLE: Final[str] = (
    "GRANT SELECT, INSERT, UPDATE, DELETE ON {s}.{t} TO depgraph_writer"
)


def _ddl_statements(schema: str) -> list[str]:
    """渲染全部 DDL 语句（幂等；schema 名已由 check_schema_name 白名单校验）。"""
    fmt: dict[str, Any] = {
        "s": schema,
        "channels": _q_list(CHANNELS),
        "tiers": _q_list(TIERS),
        "statuses": _q_list(STATUSES),
        "promo_types": _q_list(PROMO_TYPES),
    }
    out = [_SQL_CREATE_SCHEMA.format(s=schema)]
    out.extend([_SQL_MODEL_REGISTRY.format(**fmt), _SQL_PRICE_HISTORY.format(**fmt), _SQL_PROMO_HISTORY.format(**fmt)])
    out.extend(tpl.format(**fmt) for tpl in _SQL_INDEXES)
    return out


def _grant_statements(schema: str) -> list[str]:
    """角色分级授权（照 intake DDL 惯例：reader 只读 / writer 读写）。"""
    tables = ("model_registry", "model_price_history", "model_promo_history")
    out = [
        _SQL_GRANT_READER_USAGE.format(s=schema),
        _SQL_GRANT_WRITER_USAGE.format(s=schema),
        _SQL_GRANT_WRITER_SEQ_PRICE.format(s=schema),
        _SQL_GRANT_WRITER_SEQ_PROMO.format(s=schema),
    ]
    out.extend(_SQL_GRANT_READER_TABLE.format(s=schema, t=t) for t in tables)
    out.extend(_SQL_GRANT_WRITER_TABLE.format(s=schema, t=t) for t in tables)
    return out


def check_schema_name(schema: str) -> str:
    """schema 名白名单校验（fail-closed：不合规直接 ValueError，绝不静默改名）。"""
    if not SCHEMA_RE.match(schema or ""):
        raise ValueError(
            f"schema 名不合规：{schema!r}（只许 ai_layer_model 或 ai_layer_model_test_<后缀>，"
            "防 DDL/DROP 打偏到他人 schema）"
        )
    return schema


def deploy(schema: str = DEFAULT_SCHEMA, *, conn: Any | None = None) -> dict[str, int]:
    """部署/刷新 schema（幂等）。返回各阶段执行计数。

    :param schema: 目标 schema（白名单校验）
    :param conn: 可选已存在连接（测试注入用）；缺省自建 admin 连接并负责关闭
    """
    check_schema_name(schema)
    own_conn = conn is None
    if own_conn:
        conn = get_depgraph_pg_connection(superuser=True, read_only=False, autocommit=False)
    counts = {"ddl": 0, "grant": 0}
    try:
        cur = conn.cursor()
        for stmt in _ddl_statements(schema):
            cur.execute(stmt)
            counts["ddl"] += 1
        for stmt in _grant_statements(schema):
            # SAVEPOINT 包裹：角色不存在（本地精简实例）时只回滚该条 GRANT，
            # 不能整事务回滚（PG 的 DDL 是事务性的，rollback 会把表一起撤掉）。
            cur.execute("SAVEPOINT sp_grant")
            try:
                cur.execute(stmt)
                counts["grant"] += 1
                cur.execute("RELEASE SAVEPOINT sp_grant")
            except Exception as exc:  # noqa: BLE001——授权失败不阻断 DDL 主体，warning 留痕
                log.warning("GRANT 跳过：%s", exc)
                cur.execute("ROLLBACK TO SAVEPOINT sp_grant")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        if own_conn:
            conn.close()
    return counts


EXPECTED_TABLES: Final[tuple[str, ...]] = (
    "model_registry",
    "model_price_history",
    "model_promo_history",
)
EXPECTED_INDEXES: Final[tuple[str, ...]] = (
    "ix_model_price_history_model_id",
    "ix_model_promo_history_model_id",
)
EXPECTED_SEQUENCES: Final[tuple[str, ...]] = (
    "model_price_history_id_seq",
    "model_promo_history_id_seq",
)
SQL_VERIFY_TABLES = (
    "SELECT table_name FROM information_schema.tables "
    "WHERE table_schema = %s AND table_type = 'BASE TABLE' ORDER BY table_name"
)
SQL_VERIFY_INDEXES = "SELECT indexname FROM pg_indexes WHERE schemaname = %s ORDER BY indexname"
# 序列核对走 pg_sequences（目录表全量可见）；information_schema.sequences 只显示当前角色
# 持权的序列，只读连接角色对序列无授权时会假报缺失。
SQL_VERIFY_SEQUENCES = (
    "SELECT sequencename FROM pg_sequences WHERE schemaname = %s ORDER BY sequencename"
)


def verify(schema: str = DEFAULT_SCHEMA) -> tuple[bool, list[str]]:
    """核对 schema 内三表/索引/序列是否齐全（只读，不部署）。返回 (齐全?, 缺失清单)。"""
    check_schema_name(schema)
    conn = get_depgraph_pg_connection(read_only=True)
    missing: list[str] = []
    try:
        cur = conn.cursor()
        cur.execute(SQL_VERIFY_TABLES, (schema,))
        found = {row[0] for row in cur.fetchall()}
        missing.extend(f"table:{t}" for t in EXPECTED_TABLES if t not in found)
        cur.execute(SQL_VERIFY_INDEXES, (schema,))
        found_idx = {row[0] for row in cur.fetchall()}
        missing.extend(f"index:{i}" for i in EXPECTED_INDEXES if i not in found_idx)
        cur.execute(SQL_VERIFY_SEQUENCES, (schema,))
        found_seq = {row[0] for row in cur.fetchall()}
        missing.extend(f"sequence:{q}" for q in EXPECTED_SEQUENCES if q not in found_seq)
    finally:
        conn.close()
    return (not missing), missing


def drop_test_schema(schema: str) -> None:
    """删除测试残留 schema（仅 ai_layer_model_test_ 前缀允许；生产 schema 永不删）。"""
    if not schema.startswith(TEST_SCHEMA_PREFIX):
        raise ValueError(f"拒删非测试 schema：{schema!r}")
    check_schema_name(schema)
    conn = get_depgraph_pg_connection(superuser=True, read_only=False, autocommit=True)
    try:
        conn.cursor().execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
    finally:
        conn.close()


def main(argv: list[str] | None = None) -> int:
    """CLI 入口：部署或核对 ai_layer_model schema。"""
    parser = argparse.ArgumentParser(description="AI 层 OBJ_M M2 模型库三表 DDL 部署器（幂等）")
    parser.add_argument("--schema", default=DEFAULT_SCHEMA, help="目标 schema（默认 ai_layer_model）")
    parser.add_argument("--verify", action="store_true", help="只核对不部署")
    parser.add_argument(
        "--drop-test-schema",
        action="store_true",
        help="删除测试残留 schema（仅 ai_layer_model_test_ 前缀）",
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
