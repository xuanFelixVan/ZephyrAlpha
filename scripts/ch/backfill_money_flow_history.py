# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/meta_question_answers/gaps/A06_MONEYFLOW_BACKFILL_workbook.md
# [MODULE] scripts.ch.backfill_money_flow_history
# [DOMAIN] D_DATA
# [DEPENDENCIES] tushare; zephyr.shared.security.secrets; zephyr.data.ch_reader (日历/幂等探针); zephyr.data.ch_writer (strict 写通道)
# [CONSUMERS] c1_market.money_flow → A06 族复考 PQ-0025/0026/0125/0126/0127/0163（PIT 切点 2025-09-09 前样本窗）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 纯增量：仅回填目标窗内 CH 尚无该 trade_date 数据的交易日（既有 2026-06 后行零触碰）；
#              口径版本存证：data_source='tushare' 恒置（PQ-0161 考点=回补须带口径版本标记）；
#              量纲对齐预验证：沿用 tushare_provider._fetch_money_flow 同式 net=buy-sell、main=lg+elg、pct=100*net/(buy+sell)；
#              限频自适应：tushare 每分钟限频异常退避 15s 重试；fail-visible：单日失败记账继续，末轮汇总非零退出；
#              幂等重跑安全（ReplacingMergeTree ORDER BY symbol,trade_date + 逐日已有数据探针双保险）。
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单日 API 失败→退避重试 3 次后记 fail 继续；CH 写通道不可达→fail-closed 非零退出（禁旁路落盘）。
# [TESTS] 无（一次性运维回填脚本，结论以 CH 探针复核为准——同族 backfill_rzrq_history 先例）
# [A_module] module_id=MOD-DATA-BACKFILL-MONEYFLOW | layer=script | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""backfill_money_flow_history — money_flow 深历史回填（WO-011，A06 资金流回补）。

缺口：c1_market.money_flow 现库仅 2026-06-01 起，PIT 闭卷窗（2021-01-04~2025-09-09）内零样本
→ A06 族 6 问判 insufficient。本脚本用 tushare pro.moneyflow 逐日全A 回补该窗，使复考开窗。

用法：
    python scripts/ch/backfill_money_flow_history.py --start 2021-01-04 --end 2025-09-09
幂等：重跑自动跳过 CH 已有数据的交易日；限频异常自动退避。
"""

from __future__ import annotations

import argparse
import datetime
import sys
import time
from typing import Any

import tushare as ts

from zephyr.data import ch_reader, ch_writer
from zephyr.data.table_registry import TableRegistry
from zephyr.shared.security.secrets import get_secret_or_default

# 表名唯一真源 = TableRegistry（#ARCH-CH-024：禁硬编码表名绕过品类册）
TABLE = TableRegistry().table("market_money_flow")
_T_TRADE_CALENDAR = TableRegistry().table("market_trade_calendar")

# exchange/symbol_canonical 为 MATERIALIZED 列（插入面禁带，Code 44 实证）
INSERT_COLUMNS = [
    "trade_date",
    "symbol",
    "close",
    "pct_change",
    "main_net_inflow",
    "main_net_inflow_pct",
    "super_large_net_inflow",
    "super_large_net_inflow_pct",
    "large_net_inflow",
    "large_net_inflow_pct",
    "medium_net_inflow",
    "medium_net_inflow_pct",
    "small_net_inflow",
    "small_net_inflow_pct",
    "data_source",
]

# NO-BARE-SQL：插入模板常量（表名列序集中化；数据行经参数化 execute 传递）
_SQL_INSERT = f"INSERT INTO {TABLE} ({', '.join(INSERT_COLUMNS)}) VALUES"
_SQL_TRADE_DAYS = (
    f"SELECT DISTINCT cal_date FROM {_T_TRADE_CALENDAR} "
    "FINAL WHERE is_open = 1 AND cal_date BETWEEN '{start}' AND '{end}' ORDER BY cal_date"
)
_SQL_HAS_DATA = f"SELECT count() FROM {TABLE} FINAL WHERE trade_date = '{{day}}'"

_AMOUNT_KEYS = {
    "sm": ("buy_sm_amount", "sell_sm_amount"),
    "md": ("buy_md_amount", "sell_md_amount"),
    "lg": ("buy_lg_amount", "sell_lg_amount"),
    "elg": ("buy_elg_amount", "sell_elg_amount"),
}


def _trade_days(start: str, end: str) -> list[str]:
    tsv = ch_reader.query(_SQL_TRADE_DAYS.format(start=start, end=end))
    return [ln.strip() for ln in (tsv or "").splitlines() if ln.strip()]


def _f(v) -> float:
    try:
        return float(v or 0)
    except (TypeError, ValueError):
        return 0.0


def _pct(net: float, buy_v: float, sell_v: float) -> float:
    gross = buy_v + sell_v
    return round(100.0 * net / gross, 4) if gross > 0 else 0.0


def _rows_for_day(df, day: datetime.date) -> list[tuple]:
    """列映射与 tushare_provider._fetch_money_flow 同式（口径一致性铁律）。"""
    rows: list[tuple] = []
    for rec in df.to_dict("records"):
        ts_code = str(rec.get("ts_code", "") or "")
        if "." not in ts_code:
            continue
        symbol = ts_code.split(".")[0]
        nets: dict[str, float] = {}
        buys: dict[str, float] = {}
        sells: dict[str, float] = {}
        for tier, (bk, sk) in _AMOUNT_KEYS.items():
            b, s = _f(rec.get(bk)), _f(rec.get(sk))
            if b != b or s != s:  # NaN 守卫：CH Decimal 列拒 NaN
                nets = {}
                break
            nets[tier] = b - s
            buys[tier] = b
            sells[tier] = s
        if not nets:
            continue
        main = nets["lg"] + nets["elg"]
        rows.append(
            (
                day,
                symbol,
                0,
                0,  # close/pct_change：tushare moneyflow 无此二列，与现库 tushare 行同口径置 0
                main,
                _pct(main, buys["lg"] + buys["elg"], sells["lg"] + sells["elg"]),
                nets["elg"],
                _pct(nets["elg"], buys["elg"], sells["elg"]),
                nets["lg"],
                _pct(nets["lg"], buys["lg"], sells["lg"]),
                nets["md"],
                _pct(nets["md"], buys["md"], sells["md"]),
                nets["sm"],
                _pct(nets["sm"], buys["sm"], sells["sm"]),
                "tushare",
            )
        )
    return rows


def _fetch_day(pro, day_compact: str, retries: int = 3):
    last_exc: Exception | None = None
    for _ in range(retries):
        try:
            return pro.moneyflow(trade_date=day_compact)
        except Exception as exc:  # noqa: BLE001 — 限频/网络退避重试
            last_exc = exc
            time.sleep(15)
    raise RuntimeError(f"moneyflow({day_compact}) 重试 {retries} 次失败: {last_exc}") from last_exc


def _process_day(
    pro: Any,
    client: Any,
    day: str,
    day_compact: str,
    throttle: Any,
    call_stamps: list[float],
) -> tuple[str, int]:
    """单日处理；返回 (status, rows)。status="done" 或 "skip:<原因>"；失败抛异常由调用方记账。"""
    existing = ch_reader.query(_SQL_HAS_DATA.format(day=day))
    if existing and existing.strip() and existing.strip() != "0":
        return "skip:已有数据", 0
    throttle()
    call_stamps.append(time.monotonic())
    df = _fetch_day(pro, day_compact)
    if df is None or len(df) == 0:
        return "skip:源侧无数据", 0
    day_obj = datetime.datetime.strptime(day_compact, "%Y%m%d").date()
    rows = _rows_for_day(df, day_obj)
    if not rows:
        return "skip:映射后零行", 0
    client.execute(_SQL_INSERT, rows)
    return "done", len(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="money_flow 深历史回填（tushare pro.moneyflow 逐日全A，纯增量幂等）")
    parser.add_argument("--start", required=True, help="起始日 YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="结束日 YYYY-MM-DD")
    parser.add_argument("--sleep", type=float, default=0.25, help="逐日调用间隔秒（限频基础值）")
    parser.add_argument("--max-calls-per-min", type=int, default=180, help="滑动窗限频上限（tushare 积分档位保守值）")
    args = parser.parse_args()

    tok = get_secret_or_default("TUSHARE_TOKEN")
    if not tok:
        print("[ERROR] TUSHARE_TOKEN 不在库", file=sys.stderr)
        return 2
    pro = ts.pro_api(tok)

    days = _trade_days(args.start, args.end)
    print(f"目标窗交易日: {len(days)} 天（{args.start} → {args.end}）", flush=True)
    if not days:
        return 2

    client = ch_writer.get_client()
    if client is None:
        print("[ERROR] CH 写通道不可达（fail-closed，禁旁路落库）", file=sys.stderr)
        return 2

    call_stamps: list[float] = []
    done = skipped = failed = rows_written = 0

    def _throttle() -> None:
        while True:
            now = time.monotonic()
            call_stamps[:] = [t for t in call_stamps if now - t < 60.0]
            if len(call_stamps) < args.max_calls_per_min:
                return
            time.sleep(0.5)

    for i, day in enumerate(days, 1):
        day_compact = day.replace("-", "")
        try:
            status, nrows = _process_day(pro, client, day, day_compact, _throttle, call_stamps)
        except Exception as exc:  # noqa: BLE001 — fail-visible：单日失败记账继续
            failed += 1
            print(f"  [{i}/{len(days)}] {day} FAIL {exc}", flush=True)
        else:
            if status == "done":
                done += 1
                rows_written += nrows
            else:
                skipped += 1
                print(f"  [{i}/{len(days)}] {day} {status.split(':', 1)[1]}", flush=True)
        if done % 25 == 0 and done:
            print(f"  [{i}/{len(days)}] done={done} rows={rows_written} skip={skipped} fail={failed}", flush=True)
        time.sleep(args.sleep)

    print(f"=== 回填完成: done={done} skipped={skipped} failed={failed} rows={rows_written} ===", flush=True)
    return 1 if (done == 0 and skipped == 0) or failed else 0


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 历史回补 CLI 由操作者手工点火（按月分片幂等重放），非常驻自动任务
    sys.exit(main())
