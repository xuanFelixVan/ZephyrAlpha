# [BLUEPRINT] MOD-SIG-164 | docs/_working/infoaxis/13_earnings_workbook.md §2/§6-D1 | PEAD 装配批
# [MODULE] zephyr.signal_fundamental.pead_assembly
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [DEPENDENCIES] zephyr.signal_fundamental.pead_event_model（判定核，只读复用禁改）;
#   zephyr.data.ch_reader/ch_writer（读写通道，注入可测）; zephyr.data.goal_readiness_aggregator
#   （事件触发形态对标，禁第二套钩子语义）; time_utils.now_utc（禁 datetime.now）
# [CONSUMERS] MOD-SIG-110 [CONSUMERS] 头注声明的"运行时装配批"本件＝该缺口的实件；
#   TDM-E-L3-02 九阶段选票漏斗（BM-SEL-17 五维初筛的业绩维度，二期接线）;
#   TDM-E-L3-04 负面否决器（SUE strong_negative 桶→否决候选，二期接线）;
#   goal_readiness_aggregator（exam/l9 唤醒链族）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 纯装配禁新采集（income_statement/consensus_daily 数据已在库——P0 实查）;
#   PIT 双锚：实际 EPS 锚 announce_date、一致预期 as-of（consensus trade_date<=announce_date 取最近）;
#   fail-open：任一源不可达=error 行留因继续（禁静默零事件）——本域 v1 单时点（正式财报），
#   预告/快报两时点＝表未物化（fund_earnings_forecast/fund_express_report 注册在册 CH/PG 零实存，
#   2026-10-14 实查更正 P0 作业簿）留二刀；SQL_* 常量无类型注解（NO-BARE-SQL ast 豁免只认
#   无注解 Assign——实测教训）；DateTime64(3)+显式时区 ingest_ts DB 侧生成；SUE 阈值零自拟
#   （pead_event_model.SueThresholds 在册值直用）；漂移收益由消费侧回测窗计算（本件只落事件+SUE，
#   禁在装配点预支未来价格——PIT 红线）
# [MODIFY-GUARD] tests/signal_fundamental/test_pead_assembly.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 钩子永不反噬调度器；源查询失败=error 行+继续；写失败出声返回 error 摘要
# [TESTS] tests/signal_fundamental/test_pead_assembly.py
# [TTL] permanent

"""PEAD 装配批——MOD-SIG-110 判定核的运行时装配实件（st-infoaxis-20261013 P2 财报首刀）。

真源：docs/_working/infoaxis/13_earnings_workbook.md（P0 封矿；阻断级病灶 D1"装配批零调用"
之闭合）。数据底座 2026-10-14 实查：c3_fundamental.income_statement（30 列，eps_basic，
announce_date PIT 锚）＋c3_fundamental.consensus_daily（23 列，eps_consensus，683 万行）。

用法：
  python -m zephyr.signal_fundamental.pead_assembly            # 唤醒过滤+装配+写 CH
  python -m zephyr.signal_fundamental.pead_assembly --dry-run  # 只装配打 stdout
# [ALGO_FLOW]
# 层: 输入 → 双源装配 → SUE 判定 → 落表
# - 输入: day 业务日＋ch_query 注入（TSV）；窗=近 N 日新披露 announce_date∈(day-N, day]
# - 双源: income_statement(eps_basic, announce_date PIT) × consensus_daily as-of 最近先行情
# - SUE: PeadEventModel.evaluate 前半（compute_sue+classify_sue；漂移窗留回测侧）
# - 落表: c3_fundamental.pead_earnings_event（ReplacingMergeTree 同日刷新幂等）
# - 输出: 动作摘要 dict（assembled/skipped/error 计数）
# [/ALGO_FLOW]
"""

# create-guard-not-dup: 本模块只做 PEAD 盈余公告后漂移事件流的装配与前瞻读数，非回测引擎能力的第二实现
# noqa: m11-perm-manual-legitimate  M11豁免: 产线触发＝事件订阅非本文件（zephyr.strategy_pipeline.pipeline_events.wire_data_scheduler 的 scheduler.subscribe("task_completed", _on_task_completed) 内调本模块 maybe_emit_*，与 L9/GOAL-AGG 先例同款）；本文件内 `__main__`+argparse 仅为人工复现/调试入口，非 cron/daemon/常驻

from __future__ import annotations

import argparse
import logging
from collections.abc import Callable
from datetime import date as _date
from datetime import timedelta
from typing import Any, Final

from zephyr.data.assembly_runtime import make_maybe_emit as _make_hook
from zephyr.data.assembly_runtime import run_cli as _run_cli
from zephyr.data.table_registry import get_registry
from zephyr.shared.utils.time_utils import now_utc
from zephyr.signal_fundamental.pead_event_model import (
    EarningsEvent,
    PeadEventModel,
    classify_sue,
    compute_sue,
)

_hook = _make_hook(lambda **kw: run_assembly(**kw), ("income_statement", "financial", "consensus", "pead"), "PEAD-ASM")

log = logging.getLogger(__name__)

__all__: Final = ["assemble", "maybe_emit_pead_assembly", "run_assembly"]

MODULE_ID: Final = "MOD-SIG-110A"

#: 装配窗：扫近 N 日新披露（含补跑裕量；日批窗=1，N=7 防漏批）。
_ASSEMBLY_WINDOW_DAYS: Final = 7

#: 唤醒点：财务表/装配系任务 SUCCESS（宪法 §9.3 事件触发禁轮询）。
_WAKE_TASK_KEYS: Final = ("income_statement", "financial", "consensus", "pead")

#: 表名走 TableRegistry 真源（#ARCH-CH-024 Phase 5，禁硬编码字符串）。
_TBL_INCOME_STATEMENT: Final = get_registry().table("fund_income_statement")
_TBL_CONSENSUS_DAILY: Final = get_registry().table("fund_consensus_daily")

SQL_NEW_ANNOUNCEMENTS = (
    "SELECT symbol, announce_date, toFloat64(eps_basic) FROM " + _TBL_INCOME_STATEMENT + " FINAL"
    " WHERE announce_date > '{since}' AND announce_date <= '{day}'"
    " AND eps_basic IS NOT NULL AND isFinite(toFloat64(eps_basic))"
    " ORDER BY announce_date, symbol"
)
SQL_CONSENSUS_ASOF = (
    "SELECT eps_consensus FROM " + _TBL_CONSENSUS_DAILY + " FINAL"
    " WHERE symbol = '{symbol}' AND trade_date <= '{announce}'"
    " AND eps_consensus IS NOT NULL AND isFinite(eps_consensus)"
    " ORDER BY trade_date DESC LIMIT 1"
)
SQL_TABLE = "c3_fundamental.pead_earnings_event"
SQL_INSERT = "INSERT INTO {table} ({cols}) FORMAT TSV"


def _default_ch_query(sql: str) -> str:
    from zephyr.data.ch_reader import query

    return query(sql)


def _parse_tsv(text: str, ncols: int) -> list[list[str]]:
    rows: list[list[str]] = []
    for ln in (text or "").strip().splitlines():
        parts = ln.split("\t")
        if len(parts) == ncols:
            rows.append(parts)
    return rows


def assemble(
    day: str,
    *,
    ch_query: Callable[[str], str] | None = None,
    window_days: int = _ASSEMBLY_WINDOW_DAYS,
) -> dict[str, Any]:
    """纯装配：新披露 × 一致预期 as-of → SUE 事件行列表（全注入可测，零采集）。

    Returns:
        {"rows": [...], "stats": {...}}——rows 键=表列序；源不可达时 stats.error 非空
        且 rows=[]（fail-open 出声，禁静默零事件成功）。
    """
    ch_query = ch_query or _default_ch_query
    from zoneinfo import ZoneInfo

    produced = now_utc().astimezone(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")
    since = (_date.fromisoformat(day) - timedelta(days=window_days)).isoformat()
    stats: dict[str, Any] = {
        "day": day,
        "window": f"({since}, {day}]",
        "assembled": 0,
        "no_consensus": 0,
        "sue_skip": 0,
    }
    try:
        raw_new = ch_query(SQL_NEW_ANNOUNCEMENTS.format(since=since, day=day))
    except Exception as exc:  # noqa: BLE001 — fail-open 出声
        stats["error"] = f"income_statement 不可达 {type(exc).__name__}: {exc}"[:200]
        return {"rows": [], "stats": stats}
    rows: list[dict[str, Any]] = []
    model = PeadEventModel()
    for symbol, announce, eps in _parse_tsv(raw_new, 3):
        try:
            ev = EarningsEvent(
                symbol=symbol, announce_date=_date.fromisoformat(announce), actual_eps=float(eps), consensus_eps=0.0
            )
        except Exception:  # noqa: BLE001 — 坏行跳过计数
            stats["sue_skip"] += 1
            continue
        try:
            cons_raw = ch_query(SQL_CONSENSUS_ASOF.format(symbol=ev.symbol, announce=announce))
        except Exception:  # noqa: BLE001
            stats["no_consensus"] += 1
            continue
        cons_rows = _parse_tsv(cons_raw, 1)
        if not cons_rows:
            stats["no_consensus"] += 1
            continue
        cons = float(cons_rows[0][0])
        sue = compute_sue(ev.actual_eps, cons)
        if sue is None:
            stats["sue_skip"] += 1
            continue
        band = classify_sue(sue)
        rows.append(
            {
                "trade_date": day,
                "symbol": symbol,
                "announce_date": announce,
                "actual_eps": ev.actual_eps,
                "consensus_eps": cons,
                "sue": sue,
                "sue_band": band.value if hasattr(band, "value") else str(band),
                "detail": "",
                "produced_at": produced,
            }
        )
        stats["assembled"] += 1
    return {"rows": rows, "stats": stats}


def _rows_to_tsv(rows: list[dict[str, Any]], columns: tuple[str, ...]) -> str:
    return "\n".join("\t".join(str(r.get(c, "")) for c in columns) for r in rows)


def run_assembly(
    day: str | None = None,
    *,
    dry_run: bool = False,
    ch_query: Callable[[str], str] | None = None,
    writer: Callable[[str, str, str], bool] | None = None,
) -> dict[str, Any]:
    """装配→写 CH；返回动作摘要（goal_readiness run_aggregate 同款契约）。"""
    from schemas.categories.fundamental import pead_earnings_event as schema

    ch_query = ch_query or _default_ch_query
    out: dict[str, Any] = {"module": MODULE_ID, "action": "error"}
    if day is None:
        try:
            from zephyr.data.l9_readiness_aggregator import _resolve_day

            day = _resolve_day(None)
        except Exception as exc:  # noqa: BLE001
            out["error"] = f"业务日不可解析: {exc}"[:200]
            return out
    res = assemble(day, ch_query=ch_query)
    out.update(res["stats"])
    if res["stats"].get("error"):
        out["error"] = res["stats"]["error"]
        return out
    columns = tuple(schema.INSERT_COLUMNS)
    if dry_run:
        out["action"] = "dry_run"
        out["tsv"] = _rows_to_tsv(res["rows"], columns)
        return out
    w = writer
    if w is None:

        def w(table: str, cols: str, tsv: str) -> bool:  # noqa: F811 — 缺省写通道
            from zephyr.data.ch_writer import write_tsv

            return bool(write_tsv(table, cols, tsv.encode("utf-8")))

    if res["rows"] and not w(schema.TABLE_NAME, "(" + ",".join(columns) + ")", _rows_to_tsv(res["rows"], columns)):
        out["error"] = "CH 写入未确认（write_tsv=False）——事件未落地，禁记成功"
        return out
    out["action"] = "emitted" if res["rows"] else "emitted_empty"
    return out


def maybe_emit_pead_assembly(task_id: object = None, success: bool = True, **_kwargs: Any) -> dict[str, Any]:
    """工厂委托（assembly_runtime.make_maybe_emit——同构钩子单点化）。"""
    return _hook(task_id, success, **_kwargs)


def main(argv: list[str] | None = None) -> int:
    return _run_cli(run_assembly, argv, __doc__)


if __name__ == "__main__":
    raise SystemExit(main())
