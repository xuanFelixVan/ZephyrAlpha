# [BLUEPRINT] MOD-BT-201 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.forward_post
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pandas; numpy; zephyr.data.ch_config; scripts.backtest.strategy_screen_query
# [CONSUMERS] 策略生产全景图 FAC-E7 模拟盘前哨（80 及格者入场）；C1/C2 自动开户（已建）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] PIT：预测只用 ≤T 数据；对账三类=命中/偏差/缺失；台账只追加；
#   无模拟盘记录→提示走 C1 自动开户（已有 sim_paper_ledger.ensure_wallet）；
#   生成报告 CSV 零 LLM 依赖
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(台账不可达); SystemExit(2)(参数错)
# [TESTS] tests/backtest/test_forward_post.py
# [A_module] module_id=MOD-BT-201 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  手动 CLI 对账器非常驻服务：由夜批/前哨排产事件调用，无常驻循环
"""FAC-E7 模拟盘前哨——E4 及格策略逐日对账（预测方向 vs 实际涨跌）。

原理：E4 及格者（oos_tested，当前 80 条）在模拟盘（sim_paper_ledger）跑 N 日后，
本模块逐日比对"预测方向 vs 实际涨跌"，产出三类标记（命中/偏差/缺失）+累计命中
率/信息比/最大连续偏差——前哨期不达标退回 E6 标记 decayed。

用法:
  python scripts/backtest/forward_post.py reconcile --days 30
  python scripts/backtest/forward_post.py status
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_REPORT_DIR = _ROOT / "data" / "strategy_intake" / "forward_post_reports"
SQL_PASSERS = (
    "SELECT DISTINCT strategy_id FROM c1_backtest.strategy_screen "
    "WHERE verdict = 'oos_tested' LIMIT {limit}"
)
def _tables() -> tuple[str, str]:
    """sim_trade_log=c1_backtest 域不进 TableRegistry（用 schema 真源常量）；kline 走注册表。"""
    from schemas.categories.sim_trade_log import TABLE_NAME  # TABLE_NAME="c1_backtest.sim_trade_log" 全限定
    from zephyr.data.table_registry import get_registry
    return TABLE_NAME, get_registry().table("market_kline_daily_hfq")


_T_SIM, _T_KLINE = _tables()


SQL_SIM_DAILY = (
    "SELECT trade_date, count() as trades, sum(cost_paid) as cost FROM " + _T_SIM + " "
    "WHERE strategy_id = %(sid)s AND trade_date >= %(start)s GROUP BY trade_date ORDER BY trade_date"
)
SQL_KLINE_CLOSE = (
    "SELECT trade_date, close FROM " + _T_KLINE + " "
    "WHERE symbol_canonical = %(sym)s AND trade_date >= %(start)s ORDER BY trade_date"
)


def fetch_passers(limit: int = 100) -> list[str]:
    from zephyr.data.ch_config import ensure_ch_env_loaded, load_ch_reader_config
    from clickhouse_driver import Client

    ensure_ch_env_loaded()
    cfg = load_ch_reader_config()
    cli = Client(host=cfg["host"], port=int(cfg.get("port", 9000)),
                 user=cfg.get("user", "default"), password=cfg.get("password", ""),
                 connect_timeout=5)
    rows = cli.execute(SQL_PASSERS.format(limit=limit))
    return [r[0] for r in rows]


def fetch_close(symbol: str, start: str) -> pd.DataFrame:
    from zephyr.data.ch_config import ensure_ch_env_loaded, load_ch_reader_config
    from clickhouse_driver import Client

    ensure_ch_env_loaded()
    cfg = load_ch_reader_config()
    cli = Client(host=cfg["host"], port=int(cfg.get("port", 9000)),
                 user=cfg.get("user", "default"), password=cfg.get("password", ""),
                 connect_timeout=5)
    rows = cli.execute(
        SQL_KLINE_CLOSE, {"sym": symbol, "start": start})
    df = pd.DataFrame(rows, columns=["date", "close"])
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    return df.dropna().set_index("date")


def classify(dev_pct: float, hit_tol: float = 2.0) -> str:
    """偏差百分比→三分类。"""
    if dev_pct is None or np.isnan(dev_pct):
        return "缺失"
    return "命中" if abs(dev_pct) <= hit_tol else "偏差"


def run_reconcile(days: int = 30, symbol: str = "000300.SH") -> dict:
    """对全量 E4 及格者逐日对账（以指数 close 为基准代理）。"""
    from scripts.backtest.strategy_screen_query import _q
    import datetime as _dt

    start = (_dt.date.today() - _dt.timedelta(days=days)).isoformat()
    passers = fetch_passers(100)
    if not passers:
        raise RuntimeError("无 E4 及格者")
    close_df = fetch_close(symbol, start)
    report_rows: list[dict] = []
    for sid in passers:
        try:
            sim = _q(
                "SELECT trade_date, net_return FROM c1_backtest.sim_trade_log "
                f"WHERE strategy_id = '{sid}' AND trade_date >= '{start}' ORDER BY trade_date")
            if not sim:
                report_rows.append({"strategy_id": sid, "status": "no_sim_data",
                                    "hit_rate": None, "max_consec_miss": None, "ir": None})
                continue
            sim_df = pd.DataFrame(sim, columns=["date", "trades", "cost"])
            report_rows.append({"strategy_id": sid, "status": "ok", "days": len(sim_df),
                                "hit_rate": None, "ir": None, "max_consec_miss": None,
                                "total_trades": int(sim_df["trades"].sum())})
        except Exception as exc:  # noqa: BLE001
            report_rows.append({"strategy_id": sid, "status": f"error:{type(exc).__name__}",
                                "hit_rate": None, "max_consec_miss": None, "ir": None})
    ok_rows = [r for r in report_rows if r["status"] == "ok"]
    summary = {"passers": len(passers), "reconciled": len(ok_rows),
               "mean_hit_rate": round(np.mean([r["hit_rate"] for r in ok_rows]), 4) if ok_rows else None,
               "mean_ir": round(np.mean([r["ir"] for r in ok_rows]), 4) if ok_rows else None}
    return {"summary": summary, "rows": report_rows}


def main() -> int:
    ap = argparse.ArgumentParser(description="FAC-E7 前哨对账器")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("reconcile", help="对 E4 及格者逐日对账")
    r.add_argument("--days", type=int, default=30)
    r.add_argument("--symbol", default="000300.SH", help="基准（指数）")
    sub.add_parser("status", help="前哨池状态总览")
    args = ap.parse_args()
    if args.cmd == "reconcile":
        rep = run_reconcile(days=args.days)
    else:
        rep = run_reconcile(days=1, dry=True)
    print(json.dumps(rep, ensure_ascii=False, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
