"""#11 港股日K线 → hk_daily_kline（QMT xtquant，P1，倒序）。

⚠️ 必须用 py -3.11 运行：
    py -3.11 _fetch_hk_daily_kline.py
    py -3.11 _fetch_hk_daily_kline.py --restart
    py -3.11 _fetch_hk_daily_kline.py --days 365

QMT 配置三要素（见 _fetch_futures_kline.py 头部说明）。
策略：
- 获取港股通成分股（已验证 957 只）
- 倒序下载日K线（2026-07 → 尽可能早）
- get_market_data_ex 参数顺序: period 在第3位

表结构: hk_daily_kline(trade_date, symbol, name, open, high, low, close, volume, amount)
"""
import sys
import os
import time
import argparse

QMT_LIB = r"D:\国金证券QMT交易端\bin.x64\Lib\site-packages"
QMT_HOME = r"D:\国金证券QMT交易端\bin.x64"
sys.path.append(QMT_LIB)
os.chdir(QMT_HOME)

sys.path.insert(0, r"d:\ZephyrAlpha\tmp")
from _ds_common import setup_logging, ch_insert_tsv, tsv_escape, load_progress, save_progress

from xtquant import xtdata

log = setup_logging("fetch_hk_daily_kline")
SLEEP_BETWEEN = 0.3


def get_hk_stocks():
    """获取港股通成分股列表。返回 [(code, name), ...]。"""
    try:
        codes = xtdata.get_stock_list_in_sector("港股通")
        log.info(f"港股通成分股: {len(codes)} 只")
        # 获取股票名称
        result = []
        for code in codes:
            try:
                info = xtdata.get_instrument_detail(code)
                name = info.get("InstrumentName", "") if info else ""
                result.append((code, name))
            except Exception:
                result.append((code, ""))
        return result
    except Exception as e:
        log.error(f"获取港股通列表失败: {e}")
        return []


def download_and_get(symbol, start, end):
    """下载+获取港股日K线。period 在第3位。"""
    try:
        xtdata.download_history_data(symbol, "1d", start, end)
        data = xtdata.get_market_data_ex([], [symbol], "1d", start, end)
        if symbol in data:
            return data[symbol]
        return None
    except Exception as e:
        log.warning(f"    {symbol} 下载失败: {e}")
        return None


def df_to_tsv(df, symbol, name):
    """DataFrame → TSV。"""
    import pandas as pd
    lines = []
    for ts, row in df.iterrows():
        try:
            if isinstance(ts, (int, float)):
                dt = pd.Timestamp(ts, unit="s") if ts > 1e11 else pd.Timestamp(ts, unit="ms")
            else:
                dt = pd.Timestamp(ts)
            trade_date = dt.strftime("%Y-%m-%d")
        except Exception:
            trade_date = str(ts)[:10]
        line = "\t".join([
            trade_date, symbol, tsv_escape(name),
            tsv_escape(row.get("open", 0)),
            tsv_escape(row.get("high", 0)),
            tsv_escape(row.get("low", 0)),
            tsv_escape(row.get("close", 0)),
            tsv_escape(row.get("volume", 0)),
            tsv_escape(row.get("amount", 0)),
        ])
        lines.append(line)
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--restart", action="store_true")
    ap.add_argument("--days", type=int, default=0)
    args = ap.parse_args()

    client = xtdata.get_client()
    if not client.is_connected():
        log.error("QMT 未连接！请先启动 XtMiniQmt.exe")
        return
    log.info("QMT 已连接")

    stocks = get_hk_stocks()
    log.info(f"港股总数: {len(stocks)}")

    if args.days:
        import datetime
        end = "20260704"
        start = (datetime.date(2026, 7, 4) - datetime.timedelta(days=args.days)).strftime("%Y%m%d")
    else:
        start = "20100101"
        end = "20260704"
    log.info(f"时间范围: {start} ~ {end}")

    state = {} if args.restart else load_progress("fetch_hk_daily_kline")
    last_sym = state.get("last_symbol")
    started = last_sym is None

    for i, (sym, name) in enumerate(stocks):
        if not started:
            if sym == last_sym:
                started = True
            continue
        df = download_and_get(sym, start, end)
        if df is not None and len(df) > 0:
            lines = df_to_tsv(df, sym, name)
            if lines:
                tsv = ("\n".join(lines) + "\n").encode("utf-8")
                if ch_insert_tsv("hk_daily_kline", tsv):
                    log.info(f"  [{i+1}/{len(stocks)}] {sym} {name}: {len(lines)} 行")
        else:
            log.info(f"  [{i+1}/{len(stocks)}] {sym} {name}: 无数据")
        save_progress("fetch_hk_daily_kline", {"last_symbol": sym})
        time.sleep(SLEEP_BETWEEN)

    log.info("港股日K线获取完成。")


if __name__ == "__main__":
    main()
