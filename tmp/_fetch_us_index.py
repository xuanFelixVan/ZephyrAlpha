"""#10 美股指数 → us_index（TickFlow，P1，倒序）。

用 ETF 替代真实指数（TickFlow 免费源无真实指数）：
  SPY.US = 标普500 ETF
  DIA.US = 道琼斯 ETF
  QQQ.US = 纳斯达克100 ETF

策略：
- 倒序获取日K线（count=500 一批，分批拉满历史）
- TickFlow 限流 60次/min → time.sleep(1)
- 返回列: symbol, name, timestamp, trade_date, trade_time, open, high, low, close, volume, amount

用法:
    python _fetch_us_index.py
    python _fetch_us_index.py --count 2000

表结构: us_index(trade_date, symbol, open, high, low, close, volume)
"""
import sys
import time
import argparse

sys.path.insert(0, r"d:\ZephyrAlpha\tmp")
from _ds_common import setup_logging, ch_insert_tsv, tsv_escape, ch_count

from tickflow import TickFlow

log = setup_logging("fetch_us_index")

# 美股 ETF（替代指数）
US_ETFS = [
    ("SPY.US", "标普500ETF"),
    ("DIA.US", "道琼斯ETF"),
    ("QQQ.US", "纳斯达克100ETF"),
]


def fetch_one(tf, symbol: str, count: int):
    """获取单只 ETF 日K线。返回 DataFrame 或 None。"""
    try:
        df = tf.klines.get(symbol, period="1d", count=count, as_dataframe=True)
        return df
    except Exception as e:
        log.warning(f"  {symbol} 获取失败: {e}")
        return None


def df_to_tsv(df, symbol):
    """DataFrame → TSV。us_index 表只需 trade_date, symbol, open, high, low, close, volume。"""
    lines = []
    for _, row in df.iterrows():
        # 优先用 trade_date，其次 timestamp
        td = row.get("trade_date") or row.get("timestamp")
        if td is None:
            continue
        td_str = str(td)[:10]  # YYYY-MM-DD
        line = "\t".join([
            td_str, symbol,
            tsv_escape(row.get("open", 0)),
            tsv_escape(row.get("high", 0)),
            tsv_escape(row.get("low", 0)),
            tsv_escape(row.get("close", 0)),
            tsv_escape(row.get("volume", 0)),
        ])
        lines.append(line)
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=2000, help="每只ETF拉取K线根数")
    args = ap.parse_args()

    tf = TickFlow.free()
    log.info("TickFlow 免费服务已初始化")

    total = 0
    for symbol, name in US_ETFS:
        log.info(f"获取 {name}({symbol}) count={args.count} ...")
        # 分批拉取避免限流（500 一批）
        all_lines = []
        batch_size = 500
        fetched = 0
        while fetched < args.count:
            this_batch = min(batch_size, args.count - fetched)
            df = fetch_one(tf, symbol, this_batch)
            if df is None or len(df) == 0:
                log.warning(f"  {symbol} 批次 {fetched} 无数据，停止")
                break
            lines = df_to_tsv(df, symbol)
            all_lines.extend(lines)
            fetched += this_batch
            log.info(f"  {symbol} 已获取 {fetched}/{args.count}")
            time.sleep(1.2)  # 60次/min 限流防护

        if all_lines:
            # 去重（按 trade_date）
            seen = set()
            uniq = []
            for line in all_lines:
                d = line.split("\t")[0]
                if d not in seen:
                    seen.add(d)
                    uniq.append(line)
            tsv = ("\n".join(uniq) + "\n").encode("utf-8")
            if ch_insert_tsv("us_index", tsv):
                log.info(f"  {symbol} 写入 {len(uniq)} 行")
                total += len(uniq)
        time.sleep(1)

    log.info(f"美股指数获取完成，共写入 {total} 行。")
    # 验证
    n = ch_count("us_index")
    log.info(f"us_index 表当前行数: {n}")


if __name__ == "__main__":
    main()
