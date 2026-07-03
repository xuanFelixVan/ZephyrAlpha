"""#9 期货K线 → futures_kline（QMT xtquant，P1，倒序）。

⚠️ 必须用 py -3.11 运行（pyd 文件最高 cp311）：
    py -3.11 _fetch_futures_kline.py
    py -3.11 _fetch_futures_kline.py --restart
    py -3.11 _fetch_futures_kline.py --days 30

QMT 配置三要素（缺一不可）：
  1. sys.path.append(r'D:\\国金证券QMT交易端\\bin.x64\\Lib\\site-packages')  # append 不是 insert
  2. os.chdir(r'D:\\国金证券QMT交易端\\bin.x64')                              # 让相对路径正确解析
  3. 禁止修改 xtdata.data_dir                                               # 会破坏底层 C++

策略：
- 获取四大期货交易所合约列表: 上期所/大商所/郑商所/中金所
- 倒序下载日K线（2026-07 → 尽可能早）
- get_market_data_ex 参数顺序: (field_list, stock_list, period, start_time, end_time)
  period 在第3位！传错会报"周期错误"
- download_history_data 返回 None 是正常的（异步下载到本地）

表结构: futures_kline(trade_date, timestamp, symbol, open, high, low, close,
                      volume, amount, open_interest, period)
"""
import sys
import os
import time
import argparse

# QMT 配置三要素 - 必须在 import xtquant 之前完成
QMT_LIB = r"D:\国金证券QMT交易端\bin.x64\Lib\site-packages"
QMT_HOME = r"D:\国金证券QMT交易端\bin.x64"
sys.path.append(QMT_LIB)  # 要素1: append 不是 insert（避免覆盖系统 numpy）
os.chdir(QMT_HOME)        # 要素2: chdir 让 ../userdata_mini/datadir 正确解析

sys.path.insert(0, r"d:\ZephyrAlpha\tmp")
from _ds_common import setup_logging, ch_insert_tsv, tsv_escape, load_progress, save_progress, to_int_str

from xtquant import xtdata

log = setup_logging("fetch_futures_kline")

# 四大期货交易所板块名（QMT sector）
FUTURES_SECTORS = ["上期所", "大商所", "郑商所", "中金所"]
SLEEP_BETWEEN = 0.3
BATCH = 50  # 每批合约数


def get_futures_contracts():
    """获取所有期货合约列表。返回 set。"""
    all_codes = set()
    for sector in FUTURES_SECTORS:
        try:
            codes = xtdata.get_stock_list_in_sector(sector)
            log.info(f"  {sector}: {len(codes)} 个合约")
            all_codes.update(codes)
        except Exception as e:
            log.warning(f"  {sector} 获取失败: {e}")
    return all_codes


def download_and_get(symbol, start, end, period="1d"):
    """下载+获取某合约K线。返回 DataFrame 或 None。

    参数顺序: download_history_data(stock_code, period, start_time, end_time)
             get_market_data_ex(field_list, stock_list, period, start_time, end_time)
             ⚠️ period 在第3位！
    """
    try:
        # 步骤1: 下载（返回 None 是正常的，数据异步写入本地）
        xtdata.download_history_data(symbol, period, start, end)
        # 步骤2: 获取（从本地读取）
        # ⚠️ period 在第3位，不是第5位
        data = xtdata.get_market_data_ex([], [symbol], period, start, end)
        if symbol in data:
            return data[symbol]
        return None
    except Exception as e:
        log.warning(f"    {symbol} 下载失败: {e}")
        return None


def parse_qmt_index(ts):
    """解析 QMT DataFrame index 为 (trade_date, timestamp) 字符串。

    QMT index 可能是:
    - YYYYMMDD 整数 (如 20250102) ← 期货/港股日K线
    - 毫秒时间戳 (如 1609459200000)
    - 微秒时间戳 (如 1609459200000000)
    - 字符串日期 (如 "2025-01-02")
    """
    import pandas as pd
    s = str(ts)
    # 字符串日期
    if "-" in s and len(s) >= 10:
        return s[:10], s[:10] + " 00:00:00"
    try:
        v = int(ts)
    except (ValueError, TypeError):
        return s[:10], s
    # YYYYMMDD 格式 (19900101 ~ 20991231)
    if 19900101 <= v <= 20991231:
        td = f"{v // 10000:04d}-{(v // 100) % 100:02d}-{v % 100:02d}"
        return td, td + " 00:00:00"
    # Unix 时间戳
    if v > 1e14:
        dt = pd.Timestamp(v, unit="us")
    elif v > 1e11:
        dt = pd.Timestamp(v, unit="ms")
    else:
        dt = pd.Timestamp(v, unit="s")
    return dt.strftime("%Y-%m-%d"), dt.strftime("%Y-%m-%d %H:%M:%S")


def df_to_tsv(df, symbol, period="1d"):
    """DataFrame -> TSV 行列表。

    volume/open_interest 是 UInt64 列，QMT 返回 float (如 179012.0)，
    必须用 to_int_str 转为整数字符串，否则 CH 解析报 'expected tab before .0'。
    """
    lines = []
    for ts, row in df.iterrows():
        trade_date, timestamp = parse_qmt_index(ts)
        o = row.get("open", 0)
        h = row.get("high", 0)
        l = row.get("low", 0)
        c = row.get("close", 0)
        v = row.get("volume", 0)
        a = row.get("amount", 0)
        oi = row.get("open_interest", row.get("settle", 0))
        line = "\t".join([
            trade_date, timestamp, symbol,
            tsv_escape(o), tsv_escape(h), tsv_escape(l), tsv_escape(c),
            to_int_str(v), tsv_escape(a), to_int_str(oi),
            period,
        ])
        lines.append(line)
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--restart", action="store_true")
    ap.add_argument("--days", type=int, default=0, help="仅最近N天（默认全量倒序）")
    args = ap.parse_args()

    # 验证 QMT 连接
    client = xtdata.get_client()
    if not client.is_connected():
        log.error("QMT 未连接！请先启动 XtMiniQmt.exe")
        return
    log.info("QMT 已连接")

    contracts = get_futures_contracts()
    contracts = sorted(contracts)
    log.info(f"期货合约总数: {len(contracts)}")

    # 时间范围：倒序下载，日K线可下载长历史
    if args.days:
        end = "20260704"
        import datetime
        start = (datetime.date(2026, 7, 4) - datetime.timedelta(days=args.days)).strftime("%Y%m%d")
    else:
        start = "20100101"  # 期货数据从 2010 开始
        end = "20260704"
    log.info(f"时间范围: {start} ~ {end}")

    state = {} if args.restart else load_progress("fetch_futures_kline")
    last_sym = state.get("last_symbol")
    started = last_sym is None

    for i, sym in enumerate(contracts):
        if not started:
            if sym == last_sym:
                started = True
            continue
        df = download_and_get(sym, start, end, period="1d")
        if df is not None and len(df) > 0:
            lines = df_to_tsv(df, sym, "1d")
            if lines:
                tsv = ("\n".join(lines) + "\n").encode("utf-8")
                if ch_insert_tsv("futures_kline", tsv):
                    log.info(f"  [{i+1}/{len(contracts)}] {sym}: {len(lines)} 行")
        else:
            log.info(f"  [{i+1}/{len(contracts)}] {sym}: 无数据")
        save_progress("fetch_futures_kline", {"last_symbol": sym})
        time.sleep(SLEEP_BETWEEN)

    log.info("期货K线获取完成。")


if __name__ == "__main__":
    main()
