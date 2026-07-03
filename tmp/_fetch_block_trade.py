"""#5 大宗交易 → block_trade（iFind i问财，P1，新建表）。

策略：
- 倒序遍历月份（2026-07 → 2010）
- 每月查 i问财获取大宗交易个股
- i问财查询语法: "<YYYY年M月> 大宗交易个股"（实测 2025年6月 返回 1340 行）

用法:
    python _fetch_block_trade.py
    python _fetch_block_trade.py --restart
    python _fetch_block_trade.py --months 12

表结构: block_trade(trade_date, symbol, price, volume, amount, buyer, seller)
"""
import sys
import time
import argparse

sys.path.insert(0, r"d:\ZephyrAlpha\tmp")
from _ds_common import (
    setup_logging, load_env, ch_insert_tsv,
    load_progress, save_progress, tsv_escape, year_months_backward,
)

log = setup_logging("fetch_block_trade")
SLEEP_BETWEEN_CALLS = 1.5


def to_symbol(code):
    s = str(code).strip().upper()
    for pfx in (".SZ", ".SH", ".BJ"):
        s = s.replace(pfx, "")
    for pfx in ("SH", "SZ", "BJ"):
        if s.startswith(pfx):
            s = s[len(pfx):]
    return s if s.isdigit() and len(s) == 6 else ""


def fetch_month(year: int, month: int):
    from iFinDPy import THS_iwencai
    query = f"{year}年{month}月 大宗交易个股"
    try:
        return THS_iwencai(query, "stock")
    except Exception as e:
        log.warning(f"  {query} 失败: {e}")
        return None


def df_to_tsv(df, year, month):
    import calendar
    last_day = calendar.monthrange(year, month)[1]
    trade_date = f"{year:04d}-{month:02d}-{last_day:02d}"
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
            trade_date, sym,
            tsv_escape(g("price", "成交价", "大宗交易价格")),
            tsv_escape(g("volume", "成交量", "大宗交易成交量")),
            tsv_escape(g("amount", "成交额", "大宗交易成交额")),
            tsv_escape(g("buyer", "买方", "买方营业部")),
            tsv_escape(g("seller", "卖方", "卖方营业部")),
        ])
        lines.append(line)
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--restart", action="store_true")
    ap.add_argument("--months", type=int)
    args = ap.parse_args()

    load_env()
    from iFinDPy import THS_iFinDLogin
    import os
    r = THS_iFinDLogin(os.environ["IFIND_USERNAME"], os.environ["IFIND_PASSWORD"])
    if r != 0:
        log.error(f"iFind 登录失败: {r}")
        return
    log.info("iFind 登录成功")

    ym_list = year_months_backward(2026, 7, end_year=2010)
    if args.months:
        ym_list = ym_list[:args.months]
    log.info(f"待处理月份数: {len(ym_list)}")

    state = {} if args.restart else load_progress("fetch_block_trade")
    last_ym = state.get("last_ym")
    start_idx = 0
    if last_ym:
        for i, ym in enumerate(ym_list):
            if f"{ym[0]}-{ym[1]:02d}" == last_ym:
                start_idx = i + 1
                break

    for i in range(start_idx, len(ym_list)):
        y, m = ym_list[i]
        df = fetch_month(y, m)
        if df is None or len(df) == 0:
            log.info(f"  [{i+1}/{len(ym_list)}] {y}-{m:02d} 无数据")
            save_progress("fetch_block_trade", {"last_ym": f"{y}-{m:02d}"})
            time.sleep(SLEEP_BETWEEN_CALLS)
            continue
        lines = df_to_tsv(df, y, m)
        if lines:
            tsv = ("\n".join(lines) + "\n").encode("utf-8")
            if ch_insert_tsv("block_trade", tsv):
                log.info(f"  [{i+1}/{len(ym_list)}] {y}-{m:02d} 写入 {len(lines)} 行")
        save_progress("fetch_block_trade", {"last_ym": f"{y}-{m:02d}"})
        time.sleep(SLEEP_BETWEEN_CALLS)

    log.info("大宗交易获取完成。")


if __name__ == "__main__":
    main()
