"""#4 融资融券 → margin_trading（iFind i问财，P1，新建表）。

策略：
- 倒序遍历月份（2026-07 → 2010-03，融资融券启动于2010-03-31）
- 每月查 i问财获取融资融券余额个股
- i问财查询语法（2026-07-04 实测验证）: "<YYYY年M月> 融资融券余额个股"
  返回 5534 行，列: 股票代码/股票简称/融资融券余额[YYYYMMDD]
- 融资融券启动于 2010-03-31，更早月份无数据

用法:
    python _fetch_margin_trading.py
    python _fetch_margin_trading.py --restart
    python _fetch_margin_trading.py --months 12

表结构: margin_trading(trade_date, symbol, margin_balance, margin_buy, margin_repay,
                      short_balance)
注意: i问财仅返回"融资融券余额"总额，margin_buy/margin_repay/short_balance 填 NULL。
"""
import sys
import time
import argparse
import calendar

sys.path.insert(0, r"d:\ZephyrAlpha\tmp")
from _ds_common import (
    setup_logging, load_env, ch_query, ch_insert_tsv,
    load_progress, save_progress, tsv_escape, num_or_null, year_months_backward, iwencai_to_df,
)

log = setup_logging("fetch_margin_trading")
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
    """查 i问财获取某月融资融券余额个股。

    实测查询语法（2026-07-04）: "<YYYY年M月> 融资融券余额个股"
    返回列: 股票代码/股票简称/融资融券余额[YYYYMMDD]
    """
    from iFinDPy import THS_iwencai
    query = f"{year}年{month}月 融资融券余额个股"
    try:
        return iwencai_to_df(THS_iwencai(query, "stock"))
    except Exception as e:
        log.warning(f"  {query} 失败: {e}")
        return None


def df_to_tsv(df, year, month):
    """DataFrame → TSV。trade_date 用月末日期。

    i问财返回列名含日期后缀: 融资融券余额[YYYYMMDD]
    需动态匹配以"融资融券余额"开头的列。
    margin_buy/margin_repay/short_balance 填 NULL（i问财不提供）。
    """
    last_day = calendar.monthrange(year, month)[1]
    trade_date = f"{year:04d}-{month:02d}-{last_day:02d}"
    cols = list(df.columns)

    # 动态查找"融资融券余额"列（列名带 [YYYYMMDD] 后缀）
    balance_col = None
    for c in cols:
        if "融资融券余额" in str(c) or ("余额" in str(c) and "融资" in str(c)):
            balance_col = c
            break
    # 备选：查找任何带"余额"的列
    if balance_col is None:
        for c in cols:
            if "余额" in str(c):
                balance_col = c
                break

    lines = []
    for _, row in df.iterrows():
        code = row.get("股票代码") or row.get("code") or row.get("thscode")
        sym = to_symbol(code)
        if not sym:
            continue
        # 融资融券余额
        balance = row.get(balance_col) if balance_col else None
        line = "\t".join([
            trade_date, sym,
            num_or_null(balance),        # margin_balance
            "\\N",                        # margin_buy (i问财不提供)
            "\\N",                        # margin_repay (i问财不提供)
            "\\N",                        # short_balance (i问财不提供)
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

    # 融资融券启动于 2010-03-31
    ym_list = year_months_backward(2026, 7, end_year=2010)
    if args.months:
        ym_list = ym_list[:args.months]
    log.info(f"待处理月份数: {len(ym_list)}")

    state = {} if args.restart else load_progress("fetch_margin_trading")
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
            save_progress("fetch_margin_trading", {"last_ym": f"{y}-{m:02d}"})
            time.sleep(SLEEP_BETWEEN_CALLS)
            continue
        lines = df_to_tsv(df, y, m)
        if lines:
            tsv = ("\n".join(lines) + "\n").encode("utf-8")
            if ch_insert_tsv("margin_trading", tsv):
                log.info(f"  [{i+1}/{len(ym_list)}] {y}-{m:02d} 写入 {len(lines)} 行")
        save_progress("fetch_margin_trading", {"last_ym": f"{y}-{m:02d}"})
        time.sleep(SLEEP_BETWEEN_CALLS)

    log.info("融资融券获取完成。")


if __name__ == "__main__":
    main()
