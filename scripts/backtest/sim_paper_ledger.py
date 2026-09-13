# [BLUEPRINT] MOD-BT-084 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.sim_paper_ledger
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.data.ch_config
# [CONSUMERS] c1_backtest.sim_pocket_daily（STR-VREV-025 模拟盘钱包）；每日自动化（接线另批）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 一策略一钱包（STR-VREV-025，初始 100 万=Owner 批准）；信号=当日收盘判定收盘执行
#   （方案 C 口径）；成本=冻结土规（买 2.5bp+5bp，卖 2.5bp+10bp+5bp）；幂等（同策略+日替换写）；
#   模拟盘模式 mode 标记 replay_demo/sim_daily
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(行情缺失/落库未确认)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-099 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""模拟盘方案 C 账本——恐慌反弹（STR-VREV-025）虚拟钱包。

规则（与回测翻译件 c4_e3da6fa71af1 同口径）：上证昨日收盘跌幅<=-1.5% 且当日<=-1.4% →
次日按中证1000 收盘价全仓买入；持有满 19 交易日强制平仓。钱包初始 100 万（Owner 批）。
mode=replay_demo 历史演示（验证管线）/sim_daily 正式模拟盘日账。
用法：python scripts/backtest/sim_paper_ledger.py --mode replay_demo（回放验证）
      python scripts/backtest/sim_paper_ledger.py --mode sim_daily（每日收盘后跑一次）
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

STRATEGY_ID = "STR-VREV-025"
INITIAL_CAPITAL = 1_000_000.0
DROP_PREV, DROP_TODAY, HOLD_N = -0.015, -0.014, 20
SYMBOL = "000852"
BUY_COST, SELL_COST = (2.5 + 5.0) / 10000.0, (2.5 + 10.0 + 5.0) / 10000.0
_TABLE = "c1_backtest.sim_pocket_daily"
_COLS = ("(trade_date, strategy_id, initial_capital, cash, position_symbol, shares, position_value,"
         " equity, daily_pnl, signal, mode, run_id, note)")


_client = None


def _q(sql: str):
    """只读查询（进程内单客户端缓存+退出关闭，禁 socket 泄漏）。"""
    global _client
    if _client is None:
        import atexit

        from zephyr.data.ch_config import ensure_ch_env_loaded, load_ch_reader_config

        ensure_ch_env_loaded()
        cfg = load_ch_reader_config()
        from clickhouse_driver import Client

        _client = Client(host=cfg["host"], port=int(cfg.get("port", 9000)),
                         user=cfg.get("user", "default"), password=cfg.get("password", ""),
                         connect_timeout=5)
        atexit.register(_client.disconnect)
    return _client.execute(sql)


def run(mode: str, start: str, end: str, run_id: str | None = None) -> dict:
    run_id = run_id or f"sim-{mode}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    sh = pd_idx("000001", start, end)
    px = pd_idx(SYMBOL, start, end)
    if sh.empty or px.empty:
        raise RuntimeError("指数行情缺失")
    ret = sh["close"].pct_change()
    panic = (ret.shift(1) <= DROP_PREV) & (ret <= DROP_TODAY)
    dates = list(px.index)
    px_map = px["close"].to_dict()
    cash, shares, hold_day = INITIAL_CAPITAL, 0.0, 0
    entry_px = 0.0
    out_rows = []
    events = []
    prev_equity = INITIAL_CAPITAL
    for dt in dates:
        px_now = float(px_map[dt])
        signal = "cash"
        if shares > 0:
            hold_day += 1
            signal = "holding"
            if hold_day >= HOLD_N:
                cost = shares * px_now * SELL_COST
                proceeds = shares * px_now * (1 - SELL_COST)
                events.append([dt.strftime("%Y-%m-%d"), STRATEGY_ID, SYMBOL, "exit",
                               shares, px_now, cost, proceeds,
                               f"持有满{HOLD_N - 1}交易日平仓(入场价{entry_px:.2f})", mode, run_id])
                cash, shares, hold_day = proceeds, 0.0, 0
                signal = "exit"
        elif bool(panic.loc[dt]):
            buy_cost = cash * BUY_COST
            shares = cash / px_now * (1 - BUY_COST)
            entry_px = px_now
            cash = 0.0
            hold_day = 1
            signal = "entry"
            events.append([dt.strftime("%Y-%m-%d"), STRATEGY_ID, SYMBOL, "entry",
                           shares, px_now, buy_cost, 0.0,
                           f"恐慌触发:上证两日跌幅达阈值({DROP_PREV}/{DROP_TODAY})", mode, run_id])
        pos_val = shares * px_now
        equity = cash + pos_val
        daily_pnl = equity - prev_equity
        prev_equity = equity
        out_rows.append([dt.strftime("%Y-%m-%d"), STRATEGY_ID, INITIAL_CAPITAL, round(cash, 2),
                         SYMBOL if shares > 0 else "", round(shares, 2), round(pos_val, 2),
                         round(equity, 2), round(daily_pnl, 2), signal, mode, run_id, ""])
    return {"rows": out_rows, "events": events, "final_equity": round(prev_equity, 2),
            "days": len(dates), "entry_px_last": entry_px}


def pd_idx(sym: str, start: str, end: str):
    sys.path.insert(0, str(Path(__file__).resolve().parent / "translated"))
    from _c4_engine import load_index

    df = load_index(sym, start, end, fields=("close",))
    return df


def rebuild(strategy_id: str, mode: str, start: str, end: str) -> list[list]:
    """从 sim_trade_log 事件流重建钱包日账（后备方案：账本损毁可全量重建）。"""
    ev = _q(f"SELECT trade_date, action, shares, cash_after, run_id FROM c1_backtest.sim_trade_log FINAL "
            f"WHERE strategy_id = '{strategy_id}' AND mode = '{mode}' "
            f"ORDER BY trade_date, action")
    ev_by_date = {str(r[0]): r for r in ev}
    px = pd_idx(SYMBOL, start, end)
    px_map = px["close"].to_dict()
    cash, shares = INITIAL_CAPITAL, 0.0
    rows = []
    prev_equity = INITIAL_CAPITAL
    for dt in px.index:
        ds = dt.strftime("%Y-%m-%d")
        signal = "holding" if shares > 0 else "cash"
        run_id = "rebuild"
        if ds in ev_by_date:
            _, action, sh, cash_after, run_id = ev_by_date[ds]
            if action == "entry":
                shares, cash = float(sh), float(cash_after)
            else:
                shares, cash = 0.0, float(cash_after)
            signal = action
        pos_val = shares * float(px_map[dt]) if shares > 0 else 0.0
        equity = cash + pos_val
        daily_pnl = equity - prev_equity
        prev_equity = equity
        rows.append([ds, strategy_id, INITIAL_CAPITAL, round(cash, 2),
                     SYMBOL if shares > 0 else "", round(shares, 2), round(pos_val, 2),
                     round(equity, 2), round(daily_pnl, 2), signal, mode, f"rebuild-{run_id}", ""])
    return rows


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description="模拟盘方案C钱包（恐慌反弹）")
    ap.add_argument("--mode", choices=["replay_demo", "sim_daily"], required=True)
    ap.add_argument("--start", default=None)
    ap.add_argument("--end", default=None)
    ap.add_argument("--rebuild", action="store_true",
                    help="从事件流重建钱包日账（后备方案，不产生新事件）")
    args = ap.parse_args()
    if args.mode == "replay_demo":
        start, end = args.start or "2026-07-01", args.end or date.today().strftime("%Y-%m-%d")
    else:
        start = end = args.start or date.today().strftime("%Y-%m-%d")
    if args.rebuild:
        rows = rebuild(STRATEGY_ID, args.mode, start, end)
        from zephyr.data import ch_writer

        def cell2(v):
            if v is None:
                return chr(92) + "N"
            return str(v).replace(chr(9), " ").replace(chr(10), " ")

        tsv = "\n".join("\t".join(cell2(v) for v in r) for r in rows) + "\n"
        if not ch_writer.write_tsv(_TABLE, _COLS, tsv.encode("utf-8")):
            raise RuntimeError("重建落库未确认——fail-closed")
        print(json.dumps({"rebuild": True, "rows": len(rows)}, ensure_ascii=False))
        return
    res = run(args.mode, start, end, run_id=f"sim-{args.mode}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}")
    from zephyr.data import ch_writer

    def cell(v):
        if v is None:
            return chr(92) + "N"
        return str(v).replace(chr(9), " ").replace(chr(10), " ")

    tsv = "\n".join("\t".join(cell(v) for v in r) for r in res["rows"]) + "\n"
    if not ch_writer.write_tsv(_TABLE, _COLS, tsv.encode("utf-8")):
        raise RuntimeError("落库未确认——fail-closed")
    ev_cols = ("(trade_date, strategy_id, symbol, action, shares, price, cost_paid, cash_after,"
               " signal_reason, mode, run_id)")
    if res["events"]:
        ev_tsv = "\n".join("\t".join(cell(v) for v in r) for r in res["events"]) + "\n"
        if not ch_writer.write_tsv("c1_backtest.sim_trade_log", ev_cols, ev_tsv.encode("utf-8")):
            raise RuntimeError("事件流水落库未确认——fail-closed")
    print(json.dumps({"mode": args.mode, "days": res["days"], "final_equity": res["final_equity"],
                      "rows": len(res["rows"]), "events": len(res["events"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
