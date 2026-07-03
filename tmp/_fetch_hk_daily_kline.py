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
from _ds_common import setup_logging, ch_insert_tsv, tsv_escape, load_progress, save_progress, to_int_str

from xtquant import xtdata

log = setup_logging("fetch_hk_daily_kline")
SLEEP_BETWEEN = 0.3


def get_hk_stocks():
    """获取港股列表。返回 [(code, name), ...]。

    QMT 板块名实测（2026-07-04）：
      - "香港联交所股票" = 全部港股（含港股通+非港股通）
      - "港股通" = 0 只（此板块名不存在）
    """
    try:
        codes = xtdata.get_stock_list_in_sector("香港联交所股票")
        log.info(f"香港联交所股票成分股: {len(codes)} 只")
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


def parse_qmt_index(ts):
    """解析 QMT DataFrame index 为 trade_date 字符串 (YYYY-MM-DD)。

    QMT index 可能是:
    - YYYYMMDD 整数 (如 20250102) ← 港股日K线
    - 毫秒时间戳 (如 1609459200000)
    - 微秒时间戳 (如 1609459200000000)
    - 字符串日期 (如 "2025-01-02")
    """
    import pandas as pd
    # 字符串日期
    s = str(ts)
    if "-" in s and len(s) >= 10:
        return s[:10]
    try:
        v = int(ts)
    except (ValueError, TypeError):
        return s[:10]
    # YYYYMMDD 格式 (19900101 ~ 20991231)
    if 19900101 <= v <= 20991231:
        return f"{v // 10000:04d}-{(v // 100) % 100:02d}-{v % 100:02d}"
    # Unix 时间戳
    if v > 1e14:
        return pd.Timestamp(v, unit="us").strftime("%Y-%m-%d")
    elif v > 1e11:
        return pd.Timestamp(v, unit="ms").strftime("%Y-%m-%d")
    else:
        return pd.Timestamp(v, unit="s").strftime("%Y-%m-%d")


def df_to_tsv(df, symbol, name):
    """DataFrame -> TSV。volume 是 UInt64，需 to_int_str 转整数字符串。"""
    lines = []
    for ts, row in df.iterrows():
        trade_date = parse_qmt_index(ts)
        line = "\t".join([
            trade_date, symbol, tsv_escape(name),
            tsv_escape(row.get("open", 0)),
            tsv_escape(row.get("high", 0)),
            tsv_escape(row.get("low", 0)),
            tsv_escape(row.get("close", 0)),
            to_int_str(row.get("volume", 0)),
            tsv_escape(row.get("amount", 0)),
        ])
        lines.append(line)
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--restart", action="store_true")
    ap.add_argument("--days", type=int, default=0)
    ap.add_argument("--limit", type=int, default=0, help="仅处理前N只（测试用）")
    args = ap.parse_args()

    client = xtdata.get_client()
    if not client.is_connected():
        log.error("QMT 未连接！请先启动 XtMiniQmt.exe")
        return
    log.info("QMT 已连接")

    stocks = get_hk_stocks()
    log.info(f"港股总数: {len(stocks)}")
    if stocks:
        log.info(f"  前3只: {stocks[:3]}")

    if args.days:
        import datetime
        end = "20260704"
        start = (datetime.date(2026, 7, 4) - datetime.timedelta(days=args.days)).strftime("%Y%m%d")
    else:
        start = "20100101"
        end = "20260704"
    log.info(f"时间范围: {start} ~ {end}")

    if args.limit:
        stocks = stocks[:args.limit]
        log.info(f"测试模式: 仅处理前 {len(stocks)} 只")

    state = {} if args.restart else load_progress("fetch_hk_daily_kline")
    last_sym = state.get("last_symbol")

    # 用索引切片代替 continue 跳过（修复 last_sym 不匹配时全跳过的 bug）
    start_idx = 0
    if last_sym and not args.restart:
        for i, (s, _) in enumerate(stocks):
            if s == last_sym:
                start_idx = i  # 从 last_sym 开始（含，重新处理该只）
                break
        else:
            log.warning(f"进度文件 last_sym={last_sym} 不在当前股票列表中，从头开始")
            start_idx = 0
    log.info(f"从索引 {start_idx} 开始 (last_sym={last_sym})")

    for i in range(start_idx, len(stocks)):
        sym, name = stocks[i]
        try:
            df = download_and_get(sym, start, end)
            if df is not None and len(df) > 0:
                lines = df_to_tsv(df, sym, name)
                if lines:
                    tsv = ("\n".join(lines) + "\n").encode("utf-8")
                    if ch_insert_tsv("hk_daily_kline", tsv):
                        log.info(f"  [{i+1}/{len(stocks)}] {sym} {name}: {len(lines)} 行")
                else:
                    log.info(f"  [{i+1}/{len(stocks)}] {sym} {name}: df有{len(df)}行但转换后0行")
            else:
                log.info(f"  [{i+1}/{len(stocks)}] {sym} {name}: 无数据")
        except Exception as e:
            log.error(f"  [{i+1}/{len(stocks)}] {sym} {name}: 异常 {e}", exc_info=True)
        save_progress("fetch_hk_daily_kline", {"last_symbol": sym})
        time.sleep(SLEEP_BETWEEN)

    log.info("港股日K线获取完成。")


if __name__ == "__main__":
    main()
