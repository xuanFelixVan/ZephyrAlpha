"""#1 估值 PE/PB/PS/PCF → daily_valuation（iFind THS_BasicData，P0）。

策略：
- 从 stock_list 读取全部股票（5534 只）
- 倒序遍历年末日期（2026-06-30, 2025-12-31, 2025-06-30, ... → 1990-12-31）
- 每只股票每年末调用 THS_BasicData 获取 PE/PB/PS/PCF 静态值（type=100）
- 写入 staging 表 _pepb_staging，最后用 ALTER TABLE UPDATE 合并到 daily_valuation
- iFind 试用限制：5min 限 1 年数据 → 批量间 sleep，可配置

用法:
    python _fetch_valuation.py            # 续传（从断点继续）
    python _fetch_valuation.py --restart   # 重新开始
    python _fetch_valuation.py --merge     # 仅执行 staging→daily_valuation 合并
    python _fetch_valuation.py --year 2025 # 仅处理指定年

注意:
- daily_valuation.symbol 为 6 位数字；stock_list.ts_code 为 000001.SZ（iFind 用）
- ALTER TABLE UPDATE 是异步 mutation，合并后用 system.mutations 查进度
"""
import sys
import time
import argparse

sys.path.insert(0, r"d:\ZephyrAlpha\tmp")
from _ds_common import (
    setup_logging, load_env, ch_query, ch_execute, ch_insert_tsv,
    get_stock_list, load_progress, save_progress, tsv_escape, year_months_backward,
)

log = setup_logging("fetch_valuation")

# 年末+半年末日期（倒序），覆盖估值快照点
SNAPSHOT_DATES = [
    "2026-06-30", "2025-12-31", "2025-06-30", "2024-12-31", "2024-06-30",
    "2023-12-31", "2023-06-30", "2022-12-31", "2022-06-30",
    "2021-12-31", "2021-06-30", "2020-12-31", "2020-06-30",
    "2019-12-31", "2019-06-30", "2018-12-31", "2018-06-30",
    "2017-12-31", "2017-06-30", "2016-12-31", "2016-06-30",
    "2015-12-31", "2015-06-30", "2014-12-31", "2014-06-30",
    "2013-12-31", "2013-06-30", "2012-12-31", "2012-06-30",
    "2011-12-31", "2011-06-30", "2010-12-31", "2010-06-30",
    "2009-12-31", "2009-06-30", "2008-12-31", "2008-06-30",
    "2007-12-31", "2007-06-30", "2006-12-31", "2006-06-30",
    "2005-12-31", "2005-06-30", "2004-12-31", "2004-06-30",
    "2003-12-31", "2003-06-30", "2002-12-31", "2002-06-30",
    "2001-12-31", "2001-06-30", "2000-12-31", "2000-06-30",
    "1999-12-31", "1999-06-30", "1998-12-31", "1998-06-30",
    "1997-12-31", "1997-06-30", "1996-12-31", "1996-06-30",
    "1995-12-31", "1994-12-31", "1993-12-31", "1992-12-31", "1991-12-31", "1990-12-31",
]
SLEEP_BETWEEN_CALLS = 0.5  # 秒，iFind 限流防护
BATCH_INSERT_SIZE = 500   # 每 N 只股票批量写入一次


def ensure_staging():
    """创建 staging 表（存 PE/PB/PS/PCF 快照）。"""
    ch_execute("""
CREATE TABLE IF NOT EXISTS c1_market._pepb_staging (
    trade_date Date,
    symbol String,
    pe_ttm Decimal(18,4),
    pb_mrq Decimal(18,4),
    ps_ttm Decimal(18,4),
    pcf_ncf_ttm Decimal(18,4)
) ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
""")


def fetch_one(ifind, ts_code: str, date: str):
    """调用 THS_BasicData 获取单只股票某日 PE/PB/PS/PCF。返回 (pe, pb, ps, pcf) 或 None。"""
    from iFinDPy import THS_BasicData, THS_Trans2DataFrame
    indicators = "ths_pe_stock;ths_pb_stock;ths_ps_stock;ths_pcf_stock_ttm"
    params = f"{date},100;{date},100;{date},100;{date},100"
    try:
        raw = THS_BasicData(ts_code, indicators, params)
        df = THS_Trans2DataFrame(raw)
        if df is None or len(df) == 0:
            return None
        row = df.iloc[0]
        pe = row.get("ths_pe_stock")
        pb = row.get("ths_pb_stock")
        ps = row.get("ths_ps_stock")
        pcf = row.get("ths_pcf_stock_ttm")
        return (pe, pb, ps, pcf)
    except Exception as e:
        log.warning(f"  {ts_code} {date} 获取失败: {e}")
        return None


def run_fetch(ifind, stocks, dates, restart=False):
    """主获取循环。"""
    state = {} if restart else load_progress("fetch_valuation")
    last_date = state.get("last_date")
    last_stock_idx = state.get("last_stock_idx", 0)
    buf = []

    # 定位起始 date
    if last_date and last_date in dates:
        start_date_idx = dates.index(last_date)
    else:
        start_date_idx = 0

    for di in range(start_date_idx, len(dates)):
        date = dates[di]
        log.info(f"=== 处理日期 {date} ({di+1}/{len(dates)}) ===")
        stock_start = last_stock_idx if di == start_date_idx else 0
        for si in range(stock_start, len(stocks)):
            ts_code, symbol, name = stocks[si]
            res = fetch_one(ifind, ts_code, date)
            if res:
                pe, pb, ps, pcf = res
                line = "\t".join([
                    date, symbol,
                    tsv_escape(pe), tsv_escape(pb), tsv_escape(ps), tsv_escape(pcf),
                ])
                buf.append(line)
            if len(buf) >= BATCH_INSERT_SIZE:
                tsv = ("\n".join(buf) + "\n").encode("utf-8")
                if ch_insert_tsv("_pepb_staging", tsv):
                    log.info(f"  写入 {len(buf)} 行")
                buf = []
            save_progress("fetch_valuation", {"last_date": date, "last_stock_idx": si + 1})
            time.sleep(SLEEP_BETWEEN_CALLS)
        # 每个日期结束，flush 剩余
        if buf:
            tsv = ("\n".join(buf) + "\n").encode("utf-8")
            if ch_insert_tsv("_pepb_staging", tsv):
                log.info(f"  日期 {date} 完成，写入剩余 {len(buf)} 行")
            buf = []
        save_progress("fetch_valuation", {"last_date": date, "last_stock_idx": 0})

    log.info("获取完成。运行 --merge 执行合并到 daily_valuation。")


def run_merge():
    """将 staging 合并到 daily_valuation（ALTER TABLE UPDATE ... FROM）。"""
    log.info("开始合并 staging → daily_valuation ...")
    # ClickHouse 22.3+ 支持 UPDATE ... FROM
    sql = """
ALTER TABLE c1_market.daily_valuation
UPDATE
    pe_ttm = s.pe_ttm,
    pb_mrq = s.pb_mrq,
    ps_ttm = s.ps_ttm,
    pcf_ncf_ttm = s.pcf_ncf_ttm
FROM c1_market._pepb_staging s
WHERE daily_valuation.symbol = s.symbol
  AND daily_valuation.trade_date = s.trade_date
"""
    if ch_execute(sql):
        log.info("合并 mutation 已提交。用以下命令查进度：")
        log.info("  wsl -d Ubuntu -- clickhouse-client --query "
                 "\"SELECT * FROM system.mutations WHERE table='daily_valuation' AND is_done=0\"")
    else:
        log.error("合并失败。检查 ClickHouse 版本是否支持 UPDATE...FROM（需 22.3+）。")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--restart", action="store_true")
    ap.add_argument("--merge", action="store_true")
    ap.add_argument("--year", type=int, help="仅处理指定年份的快照")
    args = ap.parse_args()

    load_env()
    if args.merge:
        run_merge()
        return

    if not args.merge:
        ensure_staging()

    from iFinDPy import THS_iFinDLogin
    import os
    r = THS_iFinDLogin(os.environ["IFIND_USERNAME"], os.environ["IFIND_PASSWORD"])
    if r != 0:
        log.error(f"iFind 登录失败: {r}")
        return
    log.info("iFind 登录成功")

    stocks = get_stock_list(only_listed=True)
    log.info(f"股票总数: {len(stocks)}")

    dates = SNAPSHOT_DATES
    if args.year:
        dates = [d for d in dates if d.startswith(str(args.year))]
    log.info(f"快照日期数: {len(dates)}")

    run_fetch(None, stocks, dates, restart=args.restart)


if __name__ == "__main__":
    main()
