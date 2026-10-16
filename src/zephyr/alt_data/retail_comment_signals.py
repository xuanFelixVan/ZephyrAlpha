# [BLUEPRINT] MOD-ALT-013 | docs/_working/infoaxis/14_retail_ir_workbook.md §2 | 千股千评信号装配
# [MODULE] zephyr.alt_data.retail_comment_signals
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] zephyr.data.ch_reader/ch_writer（读写通道注入可测，写口分块 1000 行/块）;
#   zephyr.data.ch_writer.tsv_escape（TSV 转义同真源，None/NaN→\N）; schemas.categories.market.
#   alt_stock_comment_signal（DDL/列清单只读）
# [CONSUMERS] 情绪线 L2-05 daily_condition_sensor 候选（正交化残差二期接线）; 板块情绪
#   org_participation 聚合（二期）; cohort_daily_ledger retail 辅列（C3 双轨裁定后）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 纯装配禁新采集（alt_stock_comment 88,372 行×17 交易日在库——P0 实查）;
#   attention_z=当日 attention_index 对全横截面 zscore（母体 std，std<1e-9→None 分母保护）;
#   attention_chg=对前一交易日 attention_index 环比差（同表 FINAL 先值查询，无先值→None）;
#   retail_sentiment_proxy=-composite_score 反向（千股千评散户看多度与未来收益文献为反向）;
#   千股千评无好差评枚举为既定事实，禁凭连续量伪造离散情绪档；SQL_* 常量无类型注解
#   （NO-BARE-SQL ast 豁免实测教训）；CH TSV 出参 NULL=\N 须显式还原 None；PIT 锚=快照
#   trade_date（11:00UTC 日更延迟）；fail-open 禁静默（源不可达=error 留因继续）
# [MODIFY-GUARD] tests/alt_data/test_retail_comment_signals.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 钩子永不反噬调度器；源不可达=error 留因继续；写失败出声返回 error 摘要
# [TESTS] tests/alt_data/test_retail_comment_signals.py
# [A_module] module_id=MOD-ALT-013 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] mod-alt-013-retail-comment-signals-20261014

"""散户评论信号装配（st-infoaxis-20261013 P2 千股千评首刀）。

真源：docs/_working/infoaxis/14_retail_ir_workbook.md §2（千股千评 88,372 行×12 列
连续量在库，无好差评枚举；独有价值=机构参与度＋注意力横截面标准化；Q8 已批出信号
先行，60 天采样窗退役判据绑定）。

用法：
  python -m zephyr.alt_data.retail_comment_signals            # 唤醒过滤+装配+写
  python -m zephyr.alt_data.retail_comment_signals --dry-run
# [ALGO_FLOW]
# 层: 输入 → 当日横截面 → zscore/环比/反向 → 落表
# - 输入: day 业务日＋ch_query 注入
# - 当日: alt_stock_comment FINAL 当日行（attention_index/org_participation/composite_score）
# - zscore: attention_index 对当日全横截面 (x-mean)/母体std（std<1e-9→None）
# - 环比: attention_chg=今日-前一交易日（前一日同表 FINAL 查询，无先值→None）
# - 反向: retail_sentiment_proxy=-composite_score
# - 落表: alt_stock_comment_signal（ReplacingMergeTree 幂等；写口列串括号形；1000 行/块分块写）
# [/ALGO_FLOW]
"""

# create-guard-not-dup: 本模块只做千股千评散户情绪微信号的横截面标准化，非新闻情绪分析能力的第二实现（数据源与消费面均不同）
# noqa: m11-perm-manual-legitimate  M11豁免: 产线触发＝事件订阅非本文件（zephyr.strategy_pipeline.pipeline_events.wire_data_scheduler 的 scheduler.subscribe("task_completed", _on_task_completed) 内调本模块 maybe_emit_*，与 L9/GOAL-AGG 先例同款）；本文件内 `__main__`+argparse 仅为人工复现/调试入口，非 cron/daemon/常驻

from __future__ import annotations

import argparse
import logging
from collections.abc import Callable
from datetime import date as _date
from typing import Any, Final

from zephyr.data.assembly_runtime import make_maybe_emit as _make_hook
from zephyr.data.assembly_runtime import run_cli as _run_cli

_hook = _make_hook(lambda **kw: run_signals(), ("alt_comment", "stock_comment"), "RETAIL-CMT")
from zephyr.data.table_registry import get_registry

log = logging.getLogger(__name__)

__all__: Final = [
    "assemble_signals",
    "run_signals",
    "maybe_emit_retail_comment_signals",
]

MODULE_ID: Final = "MOD-ALT-013"

_WAKE_TASK_KEYS: Final = ("alt_comment", "stock_comment")

_SQL_TABLE: Final = get_registry().table("market_alt_stock_comment")

SQL_TODAY = (
    "SELECT symbol, attention_index, org_participation, composite_score"
    f" FROM {_SQL_TABLE} FINAL WHERE trade_date = '{{day}}'"
)
SQL_PRIOR = (
    f"SELECT symbol, trade_date, attention_index FROM {_SQL_TABLE} FINAL"
    f" WHERE trade_date = (SELECT max(trade_date) FROM {_SQL_TABLE}"
    " WHERE trade_date < '{day}')"
)

_STD_FLOOR: Final = 1e-9
_CHUNK_ROWS: Final = 1000


def _default_ch_query(sql: str) -> str:
    from zephyr.data.ch_reader import query

    return query(sql)


def _parse_tsv(text: str, ncols: int) -> list[list[str | None]]:
    """TSV 出参解析；CH NULL（\\N）还原 None（数值列靠此防空串误读）。"""
    out: list[list[str | None]] = []
    for ln in (text or "").strip().splitlines():
        parts = ln.split("\t")
        if len(parts) != ncols:
            continue
        out.append([None if p == "\\N" else p for p in parts])
    return out


def _to_float(s: str | None) -> float | None:
    if s is None:
        return None
    try:
        v = float(s)
    except ValueError:
        return None
    return v if v == v else None  # NaN→None


def _cross_zscore_map(
    pairs: list[tuple[str, float | None]],
) -> tuple[dict[str, float], int]:
    """当日横截面 zscore：母体 std，std<1e-9→空 map（分母保护）。"""
    vals = [v for _, v in pairs if v is not None]
    if len(vals) < 2:
        return {}, 0
    mean = sum(vals) / len(vals)
    std = (sum((v - mean) ** 2 for v in vals) / len(vals)) ** 0.5
    if std < _STD_FLOOR:
        return {}, 0
    zmap = {sym: (v - mean) / std for sym, v in pairs if v is not None}
    return zmap, len(zmap)


def assemble_signals(
    day: str,
    *,
    ch_query: Callable[[str], str] | None = None,
) -> dict[str, Any]:
    """当日千股千评行 → attention_z/attention_chg/retail_sentiment_proxy 信号行。"""
    ch_query = ch_query or _default_ch_query
    try:
        today_raw = ch_query(SQL_TODAY.format(day=day))
        prior_raw = ch_query(SQL_PRIOR.format(day=day))
    except Exception as exc:  # noqa: BLE001
        return {"rows": [], "stats": {"error": f"alt_stock_comment 不可达 {type(exc).__name__}: {exc}"[:200]}}

    prior_date = ""
    prior: dict[str, float | None] = {}
    for sym, d, ai in _parse_tsv(prior_raw, 3):
        if sym is None:
            continue
        prior[sym] = _to_float(ai)
        if not prior_date and d:
            prior_date = d

    today: list[tuple[str, float | None, float | None, float | None]] = []
    for sym, ai, op, cs in _parse_tsv(today_raw, 4):
        if sym is None:
            continue
        today.append((sym, _to_float(ai), _to_float(op), _to_float(cs)))

    zmap, z_rows = _cross_zscore_map([(sym, ai) for sym, ai, _, _ in today])

    rows: list[dict[str, Any]] = []
    chg_rows = proxy_rows = 0
    for sym, ai, op, cs in today:
        z = zmap.get(sym)
        chg: float | None = None
        if ai is not None and sym in prior and prior[sym] is not None:
            chg = ai - (prior[sym] or 0.0)
        proxy = -cs if cs is not None else None
        if chg is not None:
            chg_rows += 1
        if proxy is not None:
            proxy_rows += 1
        parts = [f"attention_index={'\\N' if ai is None else ai}"]
        if prior_date:
            parts.append(f"prior_date={prior_date}")
        rows.append(
            {
                "trade_date": day,
                "symbol": sym,
                "attention_z": z,
                "attention_chg": chg,
                "org_participation": op,
                "composite_score": cs,
                "retail_sentiment_proxy": proxy,
                "detail": ";".join(parts),
            }
        )
    stats = {
        "today_rows": len(rows),
        "zscore_rows": z_rows,
        "chg_rows": chg_rows,
        "proxy_rows": proxy_rows,
        "prior_date": prior_date,
    }
    return {"rows": rows, "stats": stats}


def _rows_to_tsv(rows: list[dict[str, Any]], columns: tuple[str, ...]) -> str:
    from zephyr.data.ch_writer import tsv_escape

    return "\n".join("\t".join(tsv_escape(r.get(c)) for c in columns) for r in rows)


def _chunked_writer() -> Callable[[str, str, str], bool]:
    """默认写口：分块 1000 行/块（HTTP 体上限实测教训，MOD-ALT-012 同款根治）。"""

    def w(table: str, cols: str, tsv: str) -> bool:
        from zephyr.data.ch_writer import write_tsv

        lines = tsv.split("\n")
        for i in range(0, len(lines), _CHUNK_ROWS):
            chunk = "\n".join(lines[i : i + _CHUNK_ROWS])
            if chunk and not write_tsv(table, cols, chunk.encode("utf-8")):
                return False
        return True

    return w


def run_signals(
    day: str | None = None,
    *,
    dry_run: bool = False,
    ch_query: Callable[[str], str] | None = None,
    writer: Callable[[str, str, str], bool] | None = None,
) -> dict[str, Any]:
    """装配→写 alt_stock_comment_signal；返回动作摘要（fail-open 禁静默）。"""
    from schemas.categories.market import alt_stock_comment_signal as schema

    out: dict[str, Any] = {"module": MODULE_ID, "action": "error"}
    if day is None:
        try:
            from zephyr.data.l9_readiness_aggregator import _resolve_day

            day = _resolve_day(None)
        except Exception as exc:  # noqa: BLE001
            out["error"] = f"业务日不可解析: {exc}"[:200]
            return out
    out["day"] = day
    sig = assemble_signals(day, ch_query=ch_query)
    out["stats"] = sig["stats"]
    if sig["stats"].get("error"):
        out["error"] = sig["stats"]["error"]
        return out
    cols = "(" + ",".join(schema.INSERT_COLUMNS) + ")"
    if dry_run:
        out["action"] = "dry_run"
        out["tsv"] = _rows_to_tsv(sig["rows"], tuple(schema.INSERT_COLUMNS))
        return out
    w = writer or _chunked_writer()

    ok = not sig["rows"] or w(schema.TABLE_NAME, cols, _rows_to_tsv(sig["rows"], tuple(schema.INSERT_COLUMNS)))
    if not ok:
        out["error"] = "CH 写入未确认——信号未全部落地，禁记成功"
        return out
    out["action"] = "emitted" if sig["rows"] else "emitted_empty"
    out["signal_rows"] = len(sig["rows"])
    return out


def maybe_emit_retail_comment_signals(task_id: object = None, success: bool = True, **_kwargs: Any) -> dict[str, Any]:
    """工厂委托（assembly_runtime.make_maybe_emit——同构钩子单点化）。"""
    return _hook(task_id, success, **_kwargs)


def main(argv: list[str] | None = None) -> int:
    return _run_cli(lambda **kw: run_signals(), argv, __doc__)


if __name__ == "__main__":
    raise SystemExit(main())
