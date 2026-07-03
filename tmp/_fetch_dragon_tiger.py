"""#3 龙虎榜 → dragon_tiger（iFind i问财，P1，新建表）。

策略：
- 倒序遍历交易日（2026-07 → 1990），每天查 i问财获取龙虎榜个股
- i问财查询语法: "<date> 龙虎榜个股"（实测 2025-06-30 返回 5536 行）

用法:
    python _fetch_dragon_tiger.py            # 续传
    python _fetch_dragon_tiger.py --restart
    python _fetch_dragon_tiger.py --days 30

表结构: dragon_tiger(trade_date, symbol, name, reason, net_buy, buy_amount, sell_amount)
"""
import sys
import time
import argparse

sys.path.insert(0, r"d:\ZephyrAlpha\tmp")
from _ds_common import (
    setup_logging, load_env, ch_query, ch_insert_tsv,
    load_progress, save_progress, tsv_escape, iwencai_to_df,
)

log = setup_logging("fetch_dragon_tiger")
SLEEP_BETWEEN_CALLS = 1.0


def get_trading_dates_backward(end_date="2026-07-04", days=None):
    sql = (f"SELECT cal_date FROM c1_market.trade_calendar "
           f"WHERE is_open=1 AND cal_date <= '{end_date}' ORDER BY cal_date DESC")
    if days:
        sql += f" LIMIT {days}"
    return [l.strip() for l in ch_query(sql).strip().split("\n") if l.strip()]


def to_symbol(code):
    """i问财代码 → 6 位 symbol。"""
    s = str(code).strip().upper()
    for pfx in (".SZ", ".SH", ".BJ"):
        s = s.replace(pfx, "")
    for pfx in ("SH", "SZ", "BJ"):
        if s.startswith(pfx):
            s = s[len(pfx):]
    return s if s.isdigit() and len(s) == 6 else ""


def fetch_day(date_compact: str):
    from iFinDPy import THS_iwencai
    # date_compact: 20260701 → 查询 "2026年7月1日 龙虎榜个股"
    y, m, d = date_compact[:4], int(date_compact[4:6]), int(date_compact[6:8])
    query = f"{y}年{m}月{d}日 龙虎榜个股"
    try:
        return iwencai_to_df(THS_iwencai(query, "stock"))
    except Exception as e:
        log.warning(f"  {query} 失败: {e}")
        return None


def df_to_tsv(df, date):
    cols = list(df.columns)
    lines = []
    for _, row in df.iterrows():
        code = row.get("股票代码") or row.get("code") or row.get("thscode")
        sym = to_symbol(code)
        if not sym:
            continue
        def g(*names):
            for n in names:
                if n in cols:
                    v = row.get(n)
                    return "" if v is None else v
            return ""
        line = "\t".join([
            date, sym,
            tsv_escape(g("股票简称", "name")),
            tsv_escape(g("上榜原因", "reason", "龙虎榜原因")),
            tsv_escape(g("净买入", "net_buy", "龙虎榜净买入")),
            tsv_escape(g("买入额", "buy_amount", "龙虎榜买入额")),
            tsv_escape(g("卖出额", "sell_amount", "龙虎榜卖出额")),
        ])
        lines.append(line)
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--restart", action="store_true")
    ap.add_argument("--days", type=int)
    args = ap.parse_args()

    load_env()
    from iFinDPy import THS_iFinDLogin
    import os
    r = THS_iFinDLogin(os.environ["IFIND_USERNAME"], os.environ["IFIND_PASSWORD"])
    if r != 0:
        log.error(f"iFind 登录失败: {r}")
        return
    log.info("iFind 登录成功")

    dates = get_trading_dates_backward(days=args.days)
    log.info(f"待处理交易日数: {len(dates)}")

    state = {} if args.restart else load_progress("fetch_dragon_tiger")
    last_date = state.get("last_date")
    start_idx = 0
    if last_date and last_date in dates:
        start_idx = dates.index(last_date) + 1

    for di in range(start_idx, len(dates)):
        date = dates[di]
        date_compact = date.replace("-", "")
        df = fetch_day(date_compact)
        if df is None or len(df) == 0:
            log.info(f"  [{di+1}/{len(dates)}] {date} 无龙虎榜")
            save_progress("fetch_dragon_tiger", {"last_date": date})
            time.sleep(SLEEP_BETWEEN_CALLS)
            continue
        lines = df_to_tsv(df, date)
        if lines:
            tsv = ("\n".join(lines) + "\n").encode("utf-8")
            if ch_insert_tsv("dragon_tiger", tsv):
                log.info(f"  [{di+1}/{len(dates)}] {date} 写入 {len(lines)} 行")
        save_progress("fetch_dragon_tiger", {"last_date": date})
        time.sleep(SLEEP_BETWEEN_CALLS)

    log.info("龙虎榜获取完成。")


if __name__ == "__main__":
    main()
