# [BLUEPRINT] MOD-ALT-012 | docs/_working/infoaxis/12_research_workbook.md §2 | 预期修正面装配
# [MODULE] zephyr.alt_data.expectation_revision_assembler
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] zephyr.data.implementations.consensus_daily_compute（RATING_SCORE_MAP 只读引用禁复制）;
#   zephyr.data.ch_reader/ch_writer（读写通道注入可测）; time_utils.now_utc（禁 datetime.now）
# [CONSUMERS] TDM-E-L3-02 九阶段选票漏斗（预期修正维度，二期接线）; 板块催化定位（评级变动事件，
#   二期）; goal_readiness 唤醒链族（research/consensus 系任务）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 纯装配禁新采集（consensus_daily 683 万行/research_report 14.7 万行已在库——P0 实查）;
#   评级方向=逐票相邻两期非空评级打分差（RATING_SCORE_MAP 真源只读；文本不识别跳过计数留痕——
#   fail-open 禁静默）; 修正三件套口径=exp02/03/05 语义对齐（expectations.py 注释互指不 import——
#   因子侧/装配侧双真源禁）; PIT：research_report 锚 publish_date、consensus 锚 trade_date;
#   SQL_* 常量无类型注解（NO-BARE-SQL ast 豁免实测教训）; DateTime64(3)+显式时区; 分母保护
#   max(n_orgs,1) 与 |eps_consensus|<1e-6 跳过（近零保护同 PEAD 口径）
# [MODIFY-GUARD] tests/alt_data/test_expectation_revision_assembler.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 钩子永不反噬调度器；源不可达=error 留因继续；写失败出声返回 error 摘要
# [TESTS] tests/alt_data/test_expectation_revision_assembler.py
# [TTL] permanent

"""预期修正面装配（st-infoaxis-20261013 P2 研报首刀）。

真源：docs/_working/infoaxis/12_research_workbook.md §0（重大发现：consensus_daily 已在库，
缺口=装配接线；rating_change 列 0/146940 全空→由本件逐票相邻评级推导生成）。

用法：
  python -m zephyr.alt_data.expectation_revision_assembly            # 唤醒过滤+装配+写
  python -m zephyr.alt_data.expectation_revision_assembly --dry-run
# [ALGO_FLOW]
# 层: 输入 → 双流装配 → 落双表
# - 输入: day 业务日＋ch_query 注入；修正窗=20 交易日先值
# - 流A 评级变动: 窗内逐票按 publish_date 排序取相邻两期非空 rating → score 差→方向
# - 流B 修正三件套: consensus_daily 当日 vs 20 日前 eps_consensus/宽度/离散度
# - 落表: rating_change_event ＋ expectation_revision_daily（均 ReplacingMergeTree 幂等）
# [/ALGO_FLOW]
"""

# create-guard-not-dup: 本模块只做研报评级变动事件流与一致预期修正三件套的装配，非回测或风险能力的第二实现
# noqa: m11-perm-manual-legitimate  M11豁免: 产线触发＝事件订阅非本文件（zephyr.strategy_pipeline.pipeline_events.wire_data_scheduler 的 scheduler.subscribe("task_completed", _on_task_completed) 内调本模块 maybe_emit_*，与 L9/GOAL-AGG 先例同款）；本文件内 `__main__`+argparse 仅为人工复现/调试入口，非 cron/daemon/常驻

from __future__ import annotations

import argparse
import logging
from collections.abc import Callable
from datetime import date as _date
from datetime import timedelta
from typing import Any, Final

from zephyr.alt_data.retail_comment_signals import _default_ch_query
from zephyr.data.assembly_runtime import make_maybe_emit as _make_hook
from zephyr.data.assembly_runtime import run_cli as _run_cli
from zephyr.shared.utils.time_utils import now_utc

_hook = _make_hook(lambda **kw: run_assembly(**kw), ("research_report", "consensus", "expectation"), "EXP-REV")
from zephyr.data.table_registry import get_registry

log = logging.getLogger(__name__)

__all__: Final = [
    "assemble_rating_changes",
    "assemble_revision_trio",
    "run_assembly",
    "maybe_emit_expectation_revision",
]

MODULE_ID: Final = "MOD-ALT-012"

#: 修正窗（交易日近似=日历日×1.45 裕量；两窗取先值比较）
_REVISION_WINDOW_DAYS: Final = 29

_WAKE_TASK_KEYS: Final = ("research_report", "consensus", "expectation")

#: 表名走 TableRegistry 真源（#ARCH-CH-024 Phase 5，禁硬编码字符串）。
_TBL_RESEARCH_REPORT: Final = get_registry().table("fund_research_report")
_TBL_CONSENSUS_DAILY: Final = get_registry().table("fund_consensus_daily")

SQL_RATINGS_IN_WINDOW = (
    "SELECT symbol, publish_date, rating FROM " + _TBL_RESEARCH_REPORT + " FINAL"
    " WHERE publish_date > '{since}' AND publish_date <= '{day}' AND rating != ''"
    " ORDER BY symbol, publish_date, report_id"
)
SQL_CONSENSUS_NOW = (
    "SELECT symbol, eps_consensus, eps_std, n_orgs, n_buy, n_add, n_negative"
    " FROM " + _TBL_CONSENSUS_DAILY + " FINAL WHERE trade_date = '{day}'"
    " AND eps_consensus IS NOT NULL AND isFinite(eps_consensus)"
)
SQL_CONSENSUS_PRIOR = (
    "SELECT symbol, eps_consensus FROM " + _TBL_CONSENSUS_DAILY + " FINAL"
    " WHERE trade_date = (SELECT max(trade_date) FROM " + _TBL_CONSENSUS_DAILY + " FINAL"
    " WHERE trade_date <= '{prior_latest}' AND trade_date > '{since}')"
    " AND eps_consensus IS NOT NULL AND isFinite(eps_consensus)"
)
SQL_INSERT = "INSERT INTO {table} ({cols}) FORMAT TSV"

_EPS_FLOOR: Final = 1e-6

#: _default_ch_query＝复用 retail_comment_signals 同款（FUNCTION-DUP 去重，extract 级克隆禁逃生），
#: lazy-import ch_reader.query 的三行包装，真源见 zephyr.alt_data.retail_comment_signals。


def _parse_tsv(text: str, ncols: int) -> list[list[str]]:
    return [p for ln in (text or "").strip().splitlines() if len(p := ln.split("\t")) == ncols]


def assemble_rating_changes(
    day: str,
    *,
    ch_query: Callable[[str], str] | None = None,
    window_days: int = _REVISION_WINDOW_DAYS,
) -> dict[str, Any]:
    """流A：窗内逐票相邻两期非空评级 → rating_change 事件（文本不识别计数留痕）。"""
    from zephyr.data.implementations.consensus_daily_compute import RATING_SCORE_MAP

    ch_query = ch_query or _default_ch_query
    since = (_date.fromisoformat(day) - timedelta(days=window_days)).isoformat()
    try:
        raw = ch_query(SQL_RATINGS_IN_WINDOW.format(since=since, day=day))
    except Exception as exc:  # noqa: BLE001
        return {"rows": [], "stats": {"error": f"research_report 不可达 {type(exc).__name__}: {exc}"[:200]}}
    by_sym: dict[str, list[tuple[str, str]]] = {}
    for sym, pub, rating in _parse_tsv(raw, 3):
        by_sym.setdefault(sym, []).append((pub, rating))
    rows: list[dict[str, Any]] = []
    stats = {"symbols": len(by_sym), "events": 0, "unmapped_rating": 0}
    for sym, hist in by_sym.items():
        if len(hist) < 2:
            continue
        (pub_now, rat_now), (pub_prev, rat_prev) = hist[-1], hist[-2]
        s_now, s_prev = RATING_SCORE_MAP.get(rat_now), RATING_SCORE_MAP.get(rat_prev)
        if s_now is None or s_prev is None:
            stats["unmapped_rating"] += 1
            continue
        if s_now == s_prev:
            continue
        direction = "upgrade" if s_now > s_prev else "downgrade"
        rows.append(
            {
                "trade_date": day,
                "symbol": sym,
                "event_date": pub_now,
                "from_score": s_prev,
                "to_score": s_now,
                "direction": direction,
                "raw_from": rat_prev,
                "raw_to": rat_now,
                "detail": f"prev_pub={pub_prev}",
            }
        )
        stats["events"] += 1
    return {"rows": rows, "stats": stats}


def assemble_revision_trio(
    day: str,
    *,
    ch_query: Callable[[str], str] | None = None,
    window_days: int = _REVISION_WINDOW_DAYS,
) -> dict[str, Any]:
    """流B：consensus 当日 vs 先窗值 → 修正三件套（momentum/breadth/dispersion）。"""
    ch_query = ch_query or _default_ch_query
    since = (_date.fromisoformat(day) - timedelta(days=window_days)).isoformat()
    prior_latest = (_date.fromisoformat(day) - timedelta(days=20)).isoformat()
    try:
        now_raw = ch_query(SQL_CONSENSUS_NOW.format(day=day))
        prior_raw = ch_query(SQL_CONSENSUS_PRIOR.format(prior_latest=prior_latest, since=since))
    except Exception as exc:  # noqa: BLE001
        return {"rows": [], "stats": {"error": f"consensus_daily 不可达 {type(exc).__name__}: {exc}"[:200]}}
    prior = {r[0]: float(r[1]) for r in _parse_tsv(prior_raw, 2)}
    rows: list[dict[str, Any]] = []
    stats = {"now_rows": 0, "matched": 0, "near_zero_skip": 0}
    for sym, eps_c, eps_std, n_orgs, n_buy, n_add, n_neg in _parse_tsv(now_raw, 7):
        stats["now_rows"] += 1
        if sym not in prior:
            continue
        eps_now, eps_prev = float(eps_c), prior[sym]
        if abs(eps_prev) < _EPS_FLOOR:
            stats["near_zero_skip"] += 1
            continue
        momentum = (eps_now - eps_prev) / abs(eps_prev)
        orgs = max(float(n_orgs or 0), 1.0)
        breadth = (float(n_buy or 0) + float(n_add or 0) - float(n_neg or 0)) / orgs
        disp = float(eps_std or 0) / abs(eps_now) if abs(eps_now) >= _EPS_FLOOR else None
        rows.append(
            {
                "trade_date": day,
                "symbol": sym,
                "eps_consensus": eps_now,
                "eps_prior": eps_prev,
                "revision_momentum": momentum,
                "revision_breadth": breadth,
                "dispersion": disp if disp is not None else "",
                "n_orgs": int(orgs),
                "detail": "",
            }
        )
        stats["matched"] += 1
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
    """双流装配→写双表；返回动作摘要。"""
    from schemas.categories.fundamental import expectation_revision_daily as schema_rev
    from schemas.categories.fundamental import rating_change_event as schema_rc

    out: dict[str, Any] = {"module": MODULE_ID, "action": "error"}
    if day is None:
        try:
            from zephyr.data.l9_readiness_aggregator import _resolve_day

            day = _resolve_day(None)
        except Exception as exc:  # noqa: BLE001
            out["error"] = f"业务日不可解析: {exc}"[:200]
            return out
    out["day"] = day
    rc = assemble_rating_changes(day, ch_query=ch_query)
    trio = assemble_revision_trio(day, ch_query=ch_query)
    out["rating_stats"], out["trio_stats"] = rc["stats"], trio["stats"]
    if rc["stats"].get("error") or trio["stats"].get("error"):
        out["error"] = rc["stats"].get("error") or trio["stats"].get("error")
        return out
    if dry_run:
        out["action"] = "dry_run"
        out["tsv_rating"] = _rows_to_tsv(rc["rows"], tuple(schema_rc.INSERT_COLUMNS))
        out["tsv_trio"] = _rows_to_tsv(trio["rows"], tuple(schema_rev.INSERT_COLUMNS))
        return out
    w = writer
    if w is None:

        def w(table: str, cols: str, tsv: str) -> bool:  # noqa: F811
            # 分块写：4195 行批实测在 ~1400 行截断（HTTP 体上限；PEAD 2824 全过）——块化根治
            from zephyr.data.ch_writer import write_tsv

            lines = tsv.split("\n")
            for i in range(0, len(lines), 1000):
                chunk = "\n".join(lines[i : i + 1000])
                if chunk and not write_tsv(table, cols, chunk.encode("utf-8")):
                    return False
            return True

    ok1 = not rc["rows"] or w(
        schema_rc.TABLE_NAME,
        "(" + ",".join(schema_rc.INSERT_COLUMNS) + ")",
        _rows_to_tsv(rc["rows"], tuple(schema_rc.INSERT_COLUMNS)),
    )
    ok2 = not trio["rows"] or w(
        schema_rev.TABLE_NAME,
        "(" + ",".join(schema_rev.INSERT_COLUMNS) + ")",
        _rows_to_tsv(trio["rows"], tuple(schema_rev.INSERT_COLUMNS)),
    )
    if not (ok1 and ok2):
        out["error"] = "CH 写入未确认——事件未全部落地，禁记成功"
        return out
    out["action"] = "emitted" if (rc["rows"] or trio["rows"]) else "emitted_empty"
    out["rating_events"] = len(rc["rows"])
    out["trio_rows"] = len(trio["rows"])
    return out


def maybe_emit_expectation_revision(task_id: object = None, success: bool = True, **_kwargs: Any) -> dict[str, Any]:
    """工厂委托（assembly_runtime.make_maybe_emit——同构钩子单点化）。"""
    return _hook(task_id, success, **_kwargs)


def main(argv: list[str] | None = None) -> int:
    return _run_cli(run_assembly, argv, __doc__)


if __name__ == "__main__":
    raise SystemExit(main())
