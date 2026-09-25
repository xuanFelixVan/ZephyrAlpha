# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_tools
# [MODULE] zephyr.ai_layer.tools.usage_stats
# [DOMAIN] D_GOVERNANCE
# [TESTS] tests/ai_layer/（对应段测试目录）
# [TTL] permanent
# [DEPENDENCIES] zephyr.ai_layer.tools (STAT_SOURCES/ToolBenchError);
#                zephyr.infrastructure.database_service (get_db_service);
#                zephyr.governance.depgraph_schema (get_depgraph_pg_connection);
#                zephyr.shared.utils.time_utils (now_utc/parse_iso); zephyr.shared.io.paths (REPO_ROOT)
# [CONSUMERS] config/tool_inventory.yaml 运营态回填（inventory_generator 产出表恒 null，本件是数据真源）;
#             CLI python -m zephyr.ai_layer.tools.usage_stats [--schema ai_tools] [--verify|--deploy];
#             L5 工具切换工单/出卷（成功率底表，设计预留）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] DDL-as-Code：ai_tools.tool_usage_stats DDL 真源即本文件（experiment_store 同模式，
#              OBJ_T DESIGN §2.2 运营态=架构数据入 DB）；独立 schema `ai_tools` 与 ai_intake/ai_compare
#              隔离（产线禁读界不破），schema 名白名单 ^ai_tools(_test_[a-z0-9_]*)?$ fail-closed；
#              时间戳一律 TIMESTAMPTZ 显式时区（RULE-SCHEMA-TZ；now_utc/parse_iso，禁 datetime.now）；
#              stat_source 词表含 manual_v0 兜底（计量缺口显式暴露不许藏，DESIGN §1⑥）；
#              failures 口径=alerter ERROR+ 落盘字段（task_id/source/error/level/timestamp），
#              分母缺失时 failure_rate 恒 null（禁聚合数硬造比率，RULE-DATA-OPS）;
#              采集纯函数（路径/记录→行 dict）与 SQL 分离，可离线单测；as_of 可注入；
#              telemetry 查询面=调用方注入记录可迭代（本件零真实外呼，单测零网络）;
#              本班零生产 DDL 部署（P1 §1.4：施工批 PG 只读+test_schema 临时面）——
#              生产 deploy=后续授权运维批，CLI 幂等件已备
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_T_tools/DESIGN.md §2.2（改表结构先改设计稿，走 OBJ_R）
# [STABILITY] new
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] schema 名不合规→ValueError 立即拒跑（不静默改名）；stats 源缺文件→StatsError
#                  （fail-closed）；jsonl 坏行→跳过+计数留痕（fail-open）；failures level 非 ERROR+
#                  →该文件不进窗（口径=alerter 落盘约定）；PG 不可达（CLI）→打印错误+退出码 2
# [TESTS] tests/ai_layer/tools/test_usage_stats.py（三源纯函数/坏行跳过/level 口径/分母缺失禁造率/
#         词表外 stat_source 拒/DDL 断言/FakeConn upsert/PG opt-in 临时 schema）
"""usage_stats — T1 运营态计量：`ai_tools.tool_usage_stats` DDL 登记器 + 三源采集接线（C2）。

设计真源：``docs/_working/ai_layer_vision/OBJ_T_tools/DESIGN.md`` §2.1 运营态字段表+
§2.2 真源裁定（运营态=架构数据入 DB，YAML 盘点表恒 null 不虚构）。

三源接线（DESIGN §1⑥ 数据源裁定）::

    audit_jsonl   .runtime/audit/gate_execution_stats.jsonl（gate 触发计数先例）
                  → tool_id=gate:<gate_id>，usage=审计行数，failure=failed 列表命中数
    failures_dir  data/failures/*.json（alerter ERROR+ 落盘=故障率主源）
                  → tool_id=task:<task_id>，failure=窗内落盘件数；分母缺席→failure_rate=null
    telemetry     MOD-INF-015 telemetry_server（查询面=调用方注入记录，本件不外呼）
                  → usage/latency p50/failed 计数
    manual_v0     无计量工具的显式兜底行（缺口诚实暴露）

CLI 用法::

    python -m zephyr.ai_layer.tools.usage_stats --verify          # 只核对不部署
    python -m zephyr.ai_layer.tools.usage_stats --deploy          # 幂等部署（授权运维批）
"""

from __future__ import annotations

import json
import logging
import re
import sys
from datetime import timedelta
from pathlib import Path
from typing import Any, Final, Iterable, Mapping

from zephyr.ai_layer.tools import STAT_SOURCES, ToolBenchError
from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
from zephyr.infrastructure.database_service import get_db_service
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc, parse_iso

logger = logging.getLogger(__name__)

__all__: Final = [
    "StatsError",
    "SCHEMA_RE",
    "DEFAULT_SCHEMA",
    "AUDIT_JSONL_PATH",
    "FAILURES_DIR",
    "WINDOW_DAYS",
    "rows_from_audit_jsonl",
    "rows_from_failures_dir",
    "rows_from_telemetry",
    "manual_row",
    "ToolUsageStore",
    "deploy",
    "verify",
    "main",
]

SCHEMA_RE: Final = re.compile(r"^ai_tools(_test_[a-z0-9_]+)?$")
DEFAULT_SCHEMA: Final = "ai_tools"
AUDIT_JSONL_PATH: Final = REPO_ROOT / ".runtime" / "audit" / "gate_execution_stats.jsonl"
FAILURES_DIR: Final = REPO_ROOT / "data" / "failures"
WINDOW_DAYS: Final = 30
#: alerter ERROR+ 落盘口径（DESIGN §1⑥：data/failures=故障率主源）
_FAILURE_LEVELS: Final = frozenset({"ERROR", "CRITICAL", "FATAL"})


class StatsError(ToolBenchError):
    """计量采集失败（fail-closed：源缺文件/畸形结构，禁静默空窗）。"""


def _window(as_of: Any | None) -> tuple[Any, Any]:
    """窗口边界（window_start, window_end）；as_of 可注入，缺省 now_utc（禁 datetime.now）。"""
    end = as_of or now_utc()
    return end - timedelta(days=WINDOW_DAYS), end


def _check_schema_name(schema: str) -> str:
    """schema 名白名单校验（fail-closed，experiment_store 同款）。"""
    if not SCHEMA_RE.match(schema or ""):
        raise ValueError(
            f"schema 名不合规：{schema!r}（只许 ai_tools 或 ai_tools_test_<后缀>，防 DDL 打偏）"
        )
    return schema


def _in_window(ts: Any, start: Any, end: Any) -> bool:
    """时间戳落窗判定（缺时间戳=不进窗，不炸——standard_checkup 同款诚实口径）。"""
    if ts is None:
        return False
    try:
        parsed = parse_iso(str(ts)) if not hasattr(ts, "tzinfo") else ts
    except (ValueError, TypeError):
        return False
    return start <= parsed <= end


# ---------------------------------------------------------------------------
# 源 1：audit_jsonl（gate_execution_stats.jsonl）
# ---------------------------------------------------------------------------

def rows_from_audit_jsonl(
    path: Path, *, as_of: Any | None = None, source_ref: str | None = None
) -> list[dict[str, Any]]:
    """gate 审计行→计量行（坏行跳过留痕 fail-open；缺文件 fail-closed）。

    口径（standard_checkup 同源）：usage=窗内审计行数，failure=failed 列表命中数。
    """
    if not path.is_file():
        raise StatsError("audit jsonl 缺文件", details={"path": str(path)})
    start, end = _window(as_of)
    runs = 0
    triggered: dict[str, int] = {}
    bad_lines = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            bad_lines += 1
            continue
        if not _in_window(rec.get("timestamp"), start, end):
            continue
        runs += 1
        for gate in rec.get("failed") or []:
            triggered[str(gate)] = triggered.get(str(gate), 0) + 1
    rows = [
        {
            "tool_id": f"gate:{gate}",
            "organ": None,
            "stat_source": "audit_jsonl",
            "usage_count": runs,
            "failure_count": hits,
            "failure_rate": (hits / runs) if runs else None,
            "latency_p50_s": None,
            "window_start": start,
            "window_end": end,
            "source_ref": source_ref or str(path),
        }
        for gate, hits in sorted(triggered.items())
    ]
    if bad_lines:
        logger.warning("audit_jsonl 坏行跳过 %d 行（fail-open 留痕）", bad_lines)
    return rows


# ---------------------------------------------------------------------------
# 源 2：failures_dir（alerter ERROR+ 落盘）
# ---------------------------------------------------------------------------

def rows_from_failures_dir(
    fail_dir: Path, *, as_of: Any | None = None, source_ref: str | None = None
) -> list[dict[str, Any]]:
    """失败落盘件→计量行（level 非 ERROR+ 不进窗；分母缺席 failure_rate 恒 null）。"""
    if not fail_dir.is_dir():
        raise StatsError("failures 目录不存在", details={"path": str(fail_dir)})
    start, end = _window(as_of)
    counts: dict[str, int] = {}
    for path in sorted(fail_dir.glob("*.json")):
        try:
            rec = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            logger.warning("failures 坏文件跳过: %s", path.name)
            continue
        level = str(rec.get("level") or "").upper()
        if level and level not in _FAILURE_LEVELS:
            continue   # 口径=alerter ERROR+ 落盘约定，其余不进窗
        if not _in_window(rec.get("timestamp"), start, end):
            continue
        key = str(rec.get("task_id") or rec.get("source") or "unknown")
        counts[key] = counts.get(key, 0) + 1
    return [
        {
            "tool_id": f"task:{key}",
            "organ": None,
            "stat_source": "failures_dir",
            "usage_count": None,        # 分母缺席（落盘只记失败）→ 禁造比率
            "failure_count": hits,
            "failure_rate": None,
            "latency_p50_s": None,
            "window_start": start,
            "window_end": end,
            "source_ref": source_ref or str(fail_dir),
        }
        for key, hits in sorted(counts.items())
    ]


# ---------------------------------------------------------------------------
# 源 3：telemetry（查询面注入）+ 源 4：manual_v0 兜底
# ---------------------------------------------------------------------------

def rows_from_telemetry(
    records: Iterable[Mapping[str, Any]], *, as_of: Any | None = None,
    source_ref: str = "telemetry_server:injected",
) -> list[dict[str, Any]]:
    """遥测记录→计量行（记录可迭代由调用方注入；缺 tool_id/name 的记录跳过留痕）。"""
    start, end = _window(as_of)
    usage: dict[str, int] = {}
    latencies: dict[str, list[float]] = {}
    failures: dict[str, int] = {}
    has_failed_field: dict[str, bool] = {}
    for rec in records:
        tool_id = str(rec.get("tool_id") or rec.get("name") or "").strip()
        if not tool_id:
            continue
        if not _in_window(rec.get("timestamp"), start, end):
            continue
        usage[tool_id] = usage.get(tool_id, 0) + 1
        latency = rec.get("latency_s", rec.get("latency_ms"))
        if isinstance(latency, (int, float)):
            latencies.setdefault(tool_id, []).append(float(latency))
        if "failed" in rec:
            has_failed_field[tool_id] = True
            if rec["failed"] is True:
                failures[tool_id] = failures.get(tool_id, 0) + 1
    rows: list[dict[str, Any]] = []
    for tool_id in sorted(usage):
        n = usage[tool_id]
        lat = sorted(latencies.get(tool_id, []))
        rate = (failures.get(tool_id, 0) / n) if has_failed_field.get(tool_id) else None
        rows.append({
            "tool_id": tool_id,
            "organ": None,
            "stat_source": "telemetry",
            "usage_count": n,
            "failure_count": failures.get(tool_id, 0) if has_failed_field.get(tool_id) else None,
            "failure_rate": rate,
            "latency_p50_s": lat[len(lat) // 2] if lat else None,
            "window_start": start,
            "window_end": end,
            "source_ref": source_ref,
        })
    return rows


def manual_row(
    tool_id: str, *, organ: str | None = None, as_of: Any | None = None,
    source_ref: str = "manual_v0",
) -> dict[str, Any]:
    """manual_v0 兜底行（无计量工具的显式标注——缺口暴露，禁假装有数据）。"""
    start, end = _window(as_of)
    if not tool_id.strip():
        raise StatsError("manual_row 缺 tool_id")
    return {
        "tool_id": tool_id.strip(),
        "organ": organ,
        "stat_source": "manual_v0",
        "usage_count": None,
        "failure_count": None,
        "failure_rate": None,
        "latency_p50_s": None,
        "window_start": start,
        "window_end": end,
        "source_ref": source_ref,
    }


# ---------------------------------------------------------------------------
# DDL-as-Code（独立 schema ai_tools；幂等；TIMESTAMPTZ）
# ---------------------------------------------------------------------------

_SQL_TABLE = """
CREATE TABLE IF NOT EXISTS {s}.tool_usage_stats (
    stat_id          BIGSERIAL PRIMARY KEY,
    tool_id          TEXT NOT NULL,
    organ            TEXT,
    stat_source      TEXT NOT NULL CHECK (stat_source IN ({sources})),
    usage_count      INTEGER,
    failure_count    INTEGER,
    failure_rate     DOUBLE PRECISION,
    latency_p50_s    DOUBLE PRECISION,
    window_start     TIMESTAMPTZ,
    window_end       TIMESTAMPTZ NOT NULL,
    source_ref       TEXT,
    recorded_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_tool_usage_window UNIQUE (tool_id, stat_source, window_start, window_end),
    CONSTRAINT ck_usage_nonneg CHECK (usage_count IS NULL OR usage_count >= 0),
    CONSTRAINT ck_failure_rate_range CHECK (failure_rate IS NULL OR
                                            (failure_rate >= 0 AND failure_rate <= 1))
)
"""

_SQL_INDEXES: Final[tuple[str, ...]] = (
    "CREATE INDEX IF NOT EXISTS ix_tool_usage_tool ON {s}.tool_usage_stats (tool_id, window_end)",
    "CREATE INDEX IF NOT EXISTS ix_tool_usage_source ON {s}.tool_usage_stats (stat_source)",
)

_SQL_UPSERT = """
INSERT INTO {s}.tool_usage_stats (
    tool_id, organ, stat_source, usage_count, failure_count, failure_rate,
    latency_p50_s, window_start, window_end, source_ref
) VALUES (
    %(tool_id)s, %(organ)s, %(stat_source)s, %(usage_count)s, %(failure_count)s,
    %(failure_rate)s, %(latency_p50_s)s, %(window_start)s, %(window_end)s, %(source_ref)s
)
ON CONFLICT (tool_id, stat_source, window_start, window_end) DO UPDATE SET
    organ = EXCLUDED.organ,
    usage_count = EXCLUDED.usage_count,
    failure_count = EXCLUDED.failure_count,
    failure_rate = EXCLUDED.failure_rate,
    latency_p50_s = EXCLUDED.latency_p50_s,
    source_ref = EXCLUDED.source_ref,
    recorded_at = now()
"""

_SQL_LIST_TOOL = (
    "SELECT * FROM {s}.tool_usage_stats WHERE tool_id = %s ORDER BY window_end DESC, stat_source"
)
_EXPECTED_RELATIONS: Final[tuple[str, ...]] = ("tool_usage_stats",)
SQL_VERIFY = (
    "SELECT table_name FROM information_schema.tables WHERE table_schema = %s ORDER BY table_name"
)


_SQL_GRANTS: Final[tuple[str, ...]] = (
    "GRANT USAGE ON SCHEMA {s} TO depgraph_reader",
    "GRANT USAGE ON SCHEMA {s} TO depgraph_writer",
    "GRANT SELECT ON {s}.tool_usage_stats TO depgraph_reader",
    "GRANT SELECT, INSERT, UPDATE ON {s}.tool_usage_stats TO depgraph_writer",
    "GRANT USAGE, SELECT ON SEQUENCE {s}.tool_usage_stats_stat_id_seq TO depgraph_writer",
)


def _ddl_statements(schema: str) -> list[str]:
    """渲染全部 DDL（幂等；stat_source CHECK 与包词表同源渲染）。"""
    sources = ", ".join(f"'{x}'" for x in STAT_SOURCES)
    return [
        f"CREATE SCHEMA IF NOT EXISTS {schema}",
        _SQL_TABLE.format(s=schema, sources=sources),
        *(tpl.format(s=schema) for tpl in _SQL_INDEXES),
    ]


def deploy(schema: str = DEFAULT_SCHEMA, *, conn: Any | None = None) -> int:
    """部署/刷新 ai_tools schema（幂等，admin 通道）。返回执行语句数。

    角色分级 GRANT：角色缺席（本地精简实例）时 SAVEPOINT 回滚该条只告警不阻断
    （DDL 主体是事务性的，不能整事务回滚）——experiment_store 同款处置。
    """
    _check_schema_name(schema)
    own = conn is None
    if own:
        conn = get_depgraph_pg_connection(superuser=True, read_only=False, autocommit=False)
    executed = 0
    try:
        cur = conn.cursor()
        for stmt in _ddl_statements(schema):
            cur.execute(stmt)
            executed += 1
        for grant in _SQL_GRANTS:
            cur.execute("SAVEPOINT sp_grant")
            try:
                cur.execute(grant.format(s=schema))
                executed += 1
                cur.execute("RELEASE SAVEPOINT sp_grant")
            # 授权失败不阻断 DDL 主体，warning 留痕
            except Exception as exc:  # noqa: BLE001
                logger.warning("GRANT 跳过：%s", exc)
                cur.execute("ROLLBACK TO SAVEPOINT sp_grant")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        if own:
            conn.close()
    return executed


def verify(schema: str = DEFAULT_SCHEMA, *, conn: Any | None = None) -> tuple[bool, list[str]]:
    """核对表是否齐全（只读，不部署）。返回 (齐全?, 缺失清单)。"""
    _check_schema_name(schema)
    own = conn is None
    if own:
        conn = get_depgraph_pg_connection(read_only=True)
    try:
        cur = conn.cursor()
        cur.execute(SQL_VERIFY, (schema,))
        found = {row[0] if not isinstance(row, dict) else row.get("table_name")
                 for row in cur.fetchall()}
        missing = [f"table:{t}" for t in _EXPECTED_RELATIONS if t not in found]
    finally:
        if own:
            conn.close()
    return (not missing), missing


class ToolUsageStore:
    """运营态计量入库服务（全经 DatabaseService；测试可注入 conn/service）。"""

    def __init__(
        self,
        schema: str = DEFAULT_SCHEMA,
        service: Any | None = None,
        write_conn: Any | None = None,
    ) -> None:
        _check_schema_name(schema)
        self.schema: Final = schema
        self._svc = service or get_db_service()
        self._write_conn_override: Final = write_conn

    def _sql(self, template: str) -> str:
        return template.format(s=self.schema)

    def read_conn(self) -> Any:
        """只读连接：经 DatabaseService（read_only=True）。"""
        return self._svc.get_depgraph_conn(read_only=True)

    def write_conn(self) -> Any:
        """写连接（测试可注入；生产=depgraph 写角色入口）。"""
        if self._write_conn_override is not None:
            return self._write_conn_override
        return get_depgraph_pg_connection(read_only=False, autocommit=True)

    def upsert(self, rows: list[dict[str, Any]]) -> int:
        """批量幂等入库（UNIQUE 冲突=同窗刷新；词表外 stat_source=StatsError 拒收）。"""
        written = 0
        for row in rows:
            if row.get("stat_source") not in STAT_SOURCES:
                raise StatsError(f"stat_source 词表外: {row.get('stat_source')!r}")
            self.write_conn().cursor().execute(self._sql(_SQL_UPSERT), row)
            written += 1
        return written

    def list_tool(self, tool_id: str) -> list[dict[str, Any]]:
        """按 tool_id 查计量行（只读，window_end 倒序）。"""
        cur = self.read_conn().cursor()
        cur.execute(self._sql(_SQL_LIST_TOOL), (tool_id,))
        out: list[dict[str, Any]] = []
        for row in cur.fetchall():
            if isinstance(row, dict):
                out.append(dict(row))
            else:
                cols = [d[0] for d in cur.description]
                out.append(dict(zip(cols, row, strict=False)))
        return out


def main(argv: list[str] | None = None) -> int:
    """CLI 入口：部署或核对 ai_tools schema（experiment_store 同模式）。"""
    import argparse

    parser = argparse.ArgumentParser(description="T1 运营态计量 DDL 登记器（ai_tools，幂等）")
    parser.add_argument("--schema", default=DEFAULT_SCHEMA, help="目标 schema（默认 ai_tools）")
    parser.add_argument("--verify", action="store_true", help="只核对不部署")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        _check_schema_name(args.schema)
        if args.verify:
            ok, missing = verify(args.schema)
            print(f"VERIFY {args.schema}: {'OK' if ok else 'MISSING ' + ','.join(missing)}")
            return 0 if ok else 3
        n = deploy(args.schema)
        ok, missing = verify(args.schema)
        print(f"DEPLOYED {args.schema} stmts={n} verify={'OK' if ok else missing}")
        return 0 if ok else 3
    except ValueError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    # CLI 边界统一转退出码 2（PG 不可达等）
    except Exception as exc:  # noqa: BLE001
        print(f"DDL FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 运维CLI入口由外部排班/人工点火, 非自动常驻任务
    sys.exit(main())
