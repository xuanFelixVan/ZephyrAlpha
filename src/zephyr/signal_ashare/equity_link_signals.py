# [BLUEPRINT] MOD-SIG-163 | docs/_working/infoaxis/11_equity_workbook.md §2 | 股权三信号族装配
# [MODULE] zephyr.signal_ashare.equity_link_signals
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] PG edge_holding/node_entity（depgraph 只读注入）; CH equity_pledge_detail
#   （ch_reader 注入）; zephyr.data.ch_writer（写通道注入）
# [CONSUMERS] TDM-E-L3-12-2 龙虎榜席位↔实体归并（feed 边 quarterly，二期接线）;
#   卖出域 X-S1 负面委托（质押链风险集，二期）; 消融考卡 TDM-E-L9-G3__ablation__02
#   （keep_if_lift≥0.05 随卡冻结）; goal_readiness 唤醒链族
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 纯装配禁新采集（edge_holding 150 万行/质押明细在库——P0 实查）;
#   三信号族封闭={nium_san_cross,same_holder_link,pledge_chain}; 牛散判定=自然人名形态
#   （2-4 汉字正则）×机构词负面表×跨票≥NUISAN_MIN_HOLDS（阈值=结构性定义非判据门柱，
#   5 家=市场惯例牛散口径）; PIT：edge_holding 锚 valid_from/valid_to 双时态（只取现行对），
#   质押锚 announce_date; fail-open：任一源不可达=该族 error 行留因继续，禁静默零信号;
#   SQL 常量 SQL_* 无类型注解（NO-BARE-SQL ast 豁免实测教训）; DateTime64(3)+显式时区;
#   自然人正则勿用于法律身份认定（数据形态过滤非合规结论——词表负面表留扩展位）
# [MODIFY-GUARD] tests/signal_ashare/test_equity_link_signals.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 钩子永不反噬调度器; 单族失败不拦他族; 写失败出声返回 error 摘要
# [TESTS] tests/signal_ashare/test_equity_link_signals.py
# [TTL] permanent

"""股权三信号族装配器（st-infoaxis-20261013 P2 股权首刀）。

真源：docs/_working/infoaxis/11_equity_workbook.md §1-§2（输出契约=三信号族；牛散词典冷启动
=免费挖掘先行＝P1-C2 默认）。2026-10-14 实查校准：自然人过滤（2-4 汉字×机构负面表）命中的
跨票榜＝徐开东/夏重阳/周宇光等市场知名牛散（过滤器自验证）。
# [ALGO_FLOW]
# 层: 输入 → 三族装配 → 落表
# - 牛散跨票: 自然人×机构负面表过滤→跨票计数≥5→(person, targets[])
# - 同持有人联动: 任意持有人（含公司）跨票≥2 且持股比例≥HOLD_MIN→联动组
# - 质押链: equity_pledge_detail 未解押且 pledge_ratio≥RISK_HIGH→风险标的集
# - 落表: c3_fundamental.equity_link_signal（family/subject/targets TSV 列/方向/强度/证据）
# [/ALGO_FLOW]
"""

# create-guard-not-dup: 本模块只做股权关联三信号族（牛散跨票／同持有人联动／质押链）的装配，非风险或回测能力的第二实现
# noqa: m11-perm-manual-legitimate  M11豁免: 产线触发＝事件订阅非本文件（zephyr.strategy_pipeline.pipeline_events.wire_data_scheduler 的 scheduler.subscribe("task_completed", _on_task_completed) 内调本模块 maybe_emit_*，与 L9/GOAL-AGG 先例同款）；本文件内 `__main__`+argparse 仅为人工复现/调试入口，非 cron/daemon/常驻

from __future__ import annotations

import argparse
import logging
from collections.abc import Callable
from typing import Any, Final

from zephyr.data.assembly_runtime import make_maybe_emit as _make_hook
from zephyr.data.assembly_runtime import run_cli as _run_cli
from zephyr.shared.utils.time_utils import now_utc

_hook = _make_hook(lambda **kw: run_assembly(**kw), ("edge_holding", "equity_pledge", "top10", "equity"), "EQUITY-LINK")
from zephyr.data.table_registry import get_registry

log = logging.getLogger(__name__)

__all__: Final = ["assemble_signals", "run_assembly", "maybe_emit_equity_link"]

MODULE_ID: Final = "MOD-SIG-138E"

#: 牛散跨票下限（市场惯例口径，结构性定义非判据门柱）
NIUSAN_MIN_HOLDS: Final = 5
#: 同持有人联动：持股比例下限（stake_pct，%）
HOLD_MIN_PCT: Final = 5.0
#: 质押风险线（pledge_ratio，%——80% 接近平仓惯例高压区；数值沿用披露口径非自拟判据）
PLEDGE_RISK_PCT: Final = 80.0

_WAKE_TASK_KEYS: Final = ("edge_holding", "equity_pledge", "top10", "equity")

#: 表名走 TableRegistry 真源（#ARCH-CH-024 Phase 5，禁硬编码字符串）。
_TBL_EQUITY_PLEDGE: Final = get_registry().table("fund_equity_pledge_detail")

SQL_NIUSAN = (
    "SELECT e.name, count(DISTINCT h.to_entity) AS n, "
    " string_agg(DISTINCT h.to_entity, ',') AS targets"
    " FROM edge_holding h JOIN node_entity e ON e.entity_id = h.from_entity"
    " WHERE h.from_entity LIKE 'PE:%' AND h.valid_to IS NULL"
    " AND e.name ~ '^[一-龥]{{2,4}}$'"
    " AND e.name !~ '(基金|资管|保险|银行|证券|社保|汇金|信托|公司|集团|有限|合伙)'"
    " GROUP BY e.name HAVING count(DISTINCT h.to_entity) >= {min_holds}"
    " ORDER BY n DESC LIMIT 200"
)
SQL_SAME_HOLDER = (
    "SELECT h.from_entity, e.name, count(DISTINCT h.to_entity) AS n,"
    " string_agg(DISTINCT h.to_entity, ',') AS targets"
    " FROM edge_holding h JOIN node_entity e ON e.entity_id = h.from_entity"
    " WHERE h.valid_to IS NULL AND h.stake_pct >= {min_pct}"
    " GROUP BY h.from_entity, e.name"
    " HAVING count(DISTINCT h.to_entity) >= 2"
    " ORDER BY n DESC LIMIT 500"
)
SQL_PLEDGE_RISK = (
    "SELECT DISTINCT symbol, shareholder_name, pledge_ratio FROM " + _TBL_EQUITY_PLEDGE + " FINAL"
    " WHERE is_released = 0 AND pledge_ratio >= {min_pct}"
    " AND announce_date > '{since}'"
    " ORDER BY pledge_ratio DESC LIMIT 300"
)
SQL_INSERT = "INSERT INTO {table} ({cols}) FORMAT TSV"

_ORG_NEGATIVE_HINT = ("基金", "资管", "保险", "银行", "证券", "社保", "汇金", "信托", "公司", "集团", "有限", "合伙")


def _default_pg_query(sql: str) -> list[tuple]:
    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    conn = get_depgraph_pg_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        return cur.fetchall()
    finally:
        try:
            conn.close()
        except Exception:  # noqa: BLE001 — 只读已毕
            pass


def _default_ch_query(sql: str) -> str:
    from zephyr.data.ch_reader import query

    return query(sql)


def _parse_target_list(targets: str) -> str:
    """targets 列（逗号分隔实体）→ 落表 TSV 安全串（管道分隔＋制表符清洗）。"""
    return "|".join(t.strip().replace("\t", " ") for t in (targets or "").split(",") if t.strip())


def assemble_signals(
    day: str,
    *,
    since: str = "1970-01-01",
    pg_query: Callable[[str], list[tuple]] | None = None,
    ch_query: Callable[[str], str] | None = None,
) -> dict[str, Any]:
    """三族装配（全注入可测）。返回 {"rows": [...], "stats": {...}}；单族失败=该族 error 留因继续。"""
    pg_query = pg_query or _default_pg_query
    ch_query = ch_query or _default_ch_query
    stats: dict[str, Any] = {"day": day, "nium_san": 0, "same_holder": 0, "pledge": 0}
    rows: list[dict[str, Any]] = []
    # ① 牛散跨票
    try:
        for name, n, targets in pg_query(SQL_NIUSAN.format(min_holds=NIUSAN_MIN_HOLDS)):
            rows.append(
                {
                    "trade_date": day,
                    "family": "nium_san_cross",
                    "subject": str(name),
                    "targets": _parse_target_list(targets),
                    "direction": 1,
                    "strength": float(n),
                    "evidence": f"cross_holdings={n}",
                }
            )
            stats["nium_san"] += 1
    except Exception as exc:  # noqa: BLE001 — fail-open 单族
        stats["nium_san_error"] = f"{type(exc).__name__}: {exc}"[:200]
    # ② 同持有人联动（含公司持有人）
    try:
        for entity, name, n, targets in pg_query(SQL_SAME_HOLDER.format(min_pct=HOLD_MIN_PCT)):
            rows.append(
                {
                    "trade_date": day,
                    "family": "same_holder_link",
                    "subject": str(name or entity),
                    "targets": _parse_target_list(targets),
                    "direction": 1,
                    "strength": float(n),
                    "evidence": f"entity={entity};cross={n};stake>={HOLD_MIN_PCT}%",
                }
            )
            stats["same_holder"] += 1
    except Exception as exc:  # noqa: BLE001
        stats["same_holder_error"] = f"{type(exc).__name__}: {exc}"[:200]
    # ③ 质押链风险集
    try:
        from zephyr.data.ch_reader import query_rows

        for symbol, holder, ratio in query_rows(SQL_PLEDGE_RISK.format(min_pct=PLEDGE_RISK_PCT, since=since)):
            rows.append(
                {
                    "trade_date": day,
                    "family": "pledge_chain",
                    "subject": str(holder),
                    "targets": str(symbol),
                    "direction": -1,
                    "strength": float(ratio) / 100.0,
                    "evidence": f"pledge_ratio={ratio}%",
                }
            )
            stats["pledge"] += 1
    except Exception as exc:  # noqa: BLE001
        stats["pledge_error"] = f"{type(exc).__name__}: {exc}"[:200]
    return {"rows": rows, "stats": stats}


def _rows_to_tsv(rows: list[dict[str, Any]], columns: tuple[str, ...]) -> str:
    return "\n".join("\t".join(str(r.get(c, "")) for c in columns) for r in rows)


def run_assembly(
    day: str | None = None,
    *,
    dry_run: bool = False,
    pg_query: Callable[[str], list[tuple]] | None = None,
    ch_query: Callable[[str], str] | None = None,
    writer: Callable[[str, str, str], bool] | None = None,
) -> dict[str, Any]:
    """装配→写 CH（c3_fundamental.equity_link_signal）；返回动作摘要。"""
    from schemas.categories.fundamental import equity_link_signal as schema

    out: dict[str, Any] = {"module": MODULE_ID, "action": "error"}
    if day is None:
        try:
            from zephyr.data.l9_readiness_aggregator import _resolve_day

            day = _resolve_day(None)
        except Exception as exc:  # noqa: BLE001
            out["error"] = f"业务日不可解析: {exc}"[:200]
            return out
    out["day"] = day
    res = assemble_signals(day, pg_query=pg_query, ch_query=ch_query)
    out.update(res["stats"])
    if (
        res["stats"].get("nium_san_error")
        and res["stats"].get("same_holder_error")
        and res["stats"].get("pledge_error")
    ):
        out["error"] = "三族全不可达——读数未产，禁记成功"
        return out
    if dry_run:
        out["action"] = "dry_run"
        out["tsv"] = _rows_to_tsv(res["rows"], tuple(schema.INSERT_COLUMNS))
        return out
    w = writer
    if w is None:

        def w(table: str, cols: str, tsv: str) -> bool:  # noqa: F811
            from zephyr.data.ch_writer import write_tsv

            return bool(write_tsv(table, cols, tsv.encode("utf-8")))

    if res["rows"] and not w(
        schema.TABLE_NAME, ",".join(schema.INSERT_COLUMNS), _rows_to_tsv(res["rows"], tuple(schema.INSERT_COLUMNS))
    ):
        out["error"] = "CH 写入未确认——信号未落地，禁记成功"
        return out
    out["action"] = "emitted" if res["rows"] else "emitted_empty"
    out["rows"] = len(res["rows"])
    return out


def maybe_emit_equity_link(task_id: object = None, success: bool = True, **_kwargs: Any) -> dict[str, Any]:
    """工厂委托（assembly_runtime.make_maybe_emit——同构钩子单点化）。"""
    return _hook(task_id, success, **_kwargs)


def main(argv: list[str] | None = None) -> int:
    return _run_cli(run_assembly, argv, __doc__)


if __name__ == "__main__":
    raise SystemExit(main())
