"""#10 美股指数 → us_index（TickFlow，P1，倒序）。

用 ETF 替代真实指数（TickFlow 免费源无真实指数）：
  SPY.US = 标普500 ETF
  DIA.US = 道琼斯 ETF
  QQQ.US = 纳斯达克100 ETF

策略：
- 倒序分批拉取日K线
- TickFlow klines.get 签名（2026-07-04 实测）:
    get(symbol, *, period, count, start_time: int, end_time: int, adjust, as_dataframe)
  ⚠️ end_time 必须是整数时间戳（秒），不是字符串！
- 分页方案：
  1. 第一批: count=500, 不带 end_time → 最新 500 条
  2. 记录最早 timestamp（int 秒）
  3. 第二批: count=500, end_time=最早timestamp-1 → 更早 500 条
  4. 重复直到无数据或达到目标条数
- TickFlow 限流 60次/min → time.sleep(1)
- 返回列: symbol, name, timestamp, trade_date, trade_time, open, high, low, close, volume, amount

用法:
    python _fetch_us_index.py
    python _fetch_us_index.py --count 5000

表结构: us_index(trade_date, symbol, open, high, low, close, volume)
"""
import sys
import time
import argparse

sys.path.insert(0, r"d:\ZephyrAlpha\tmp")
from _ds_common import setup_logging, ch_insert_tsv, tsv_escape, to_int_str, ch_count

from tickflow import TickFlow

log = setup_logging("fetch_us_index")

# 美股 ETF（替代指数）
US_ETFS = [
    ("SPY.US", "标普500ETF"),
    ("DIA.US", "道琼斯ETF"),
    ("QQQ.US", "纳斯达克100ETF"),
]

BATCH_SIZE = 500  # 每批拉取条数
MAX_BATCHES = 20  # 最多拉取批次数（500*20=10000 条/ETF）


def fetch_batch(tf, symbol: str, count: int, end_time=None):
    """拉取一批 K 线。end_time 为 int 时间戳（秒）或 None。"""
    try:
        kwargs = {"period": "1d", "count": count, "as_dataframe": True}
        if end_time is not None:
            kwargs["end_time"] = end_time
        df = tf.klines.get(symbol, **kwargs)
        return df
    except Exception as e:
        log.warning(f"  {symbol} end_time={end_time} 获取失败: {e}")
        return None


def df_to_tsv(df, symbol):
    """DataFrame → TSV。us_index 表只需 trade_date, symbol, open, high, low, close, volume。"""
    lines = []
    for _, row in df.iterrows():
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
            to_int_str(row.get("volume", 0)),  # UInt64，需 to_int_str
        ])
        lines.append(line)
    return lines


def fetch_all(tf, symbol: str, name: str, max_batches: int):
    """分批拉取某 ETF 全部历史。返回去重后的 TSV 行列表。"""
    all_lines = []
    seen_dates = set()
    earliest_ts = None
    total_fetched = 0

    for batch_idx in range(max_batches):
        log.info(f"  {symbol} 批次 {batch_idx + 1}/{max_batches}, end_time={earliest_ts}")
        df = fetch_batch(tf, symbol, BATCH_SIZE, end_time=earliest_ts)
        if df is None or len(df) == 0:
            log.info(f"  {symbol} 批次 {batch_idx + 1} 无数据，停止")
            break

        # 转换为 TSV 行并去重
        batch_lines = df_to_tsv(df, symbol)
        new_count = 0
        for line in batch_lines:
            d = line.split("\t")[0]
            if d not in seen_dates:
                seen_dates.add(d)
                all_lines.append(line)
                new_count += 1
        total_fetched += len(df)
        log.info(f"  {symbol} 批次 {batch_idx + 1}: 获取 {len(df)} 行，新增 {new_count}，累计去重 {len(all_lines)}")

        # 找到本批最早的 timestamp（int 秒）作为下一批的 end_time
        ts_col = df.get("timestamp")
        if ts_col is not None and len(ts_col) > 0:
            # timestamp 可能是 int 或 str，取最小值
            try:
                ts_list = [int(t) for t in ts_col if t is not None]
                if ts_list:
                    batch_earliest = min(ts_list)
                    if earliest_ts is not None and batch_earliest >= earliest_ts:
                        log.warning(f"  {symbol} 时间戳未前进（{batch_earliest} >= {earliest_ts}），停止")
                        break
                    earliest_ts = batch_earliest - 1
            except (ValueError, TypeError) as e:
                log.warning(f"  {symbol} 无法解析 timestamp: {e}")
                break
        else:
            log.warning(f"  {symbol} 无 timestamp 列，无法分页，停止")
            break

        time.sleep(1.2)  # 60次/min 限流防护

    return all_lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=10000,
                    help="每只ETF目标拉取K线根数（用于计算 max_batches）")
    args = ap.parse_args()
    max_batches = max(MAX_BATCHES, args.count // BATCH_SIZE + 1)

    tf = TickFlow.free()
    log.info("TickFlow 免费服务已初始化")

    total = 0
    for symbol, name in US_ETFS:
        log.info(f"获取 {name}({symbol}) ...")
        all_lines = fetch_all(tf, symbol, name, max_batches)
        if all_lines:
            tsv = ("\n".join(all_lines) + "\n").encode("utf-8")
            if ch_insert_tsv("us_index", tsv):
                log.info(f"  {symbol} 写入 {len(all_lines)} 行")
                total += len(all_lines)
        time.sleep(1)

    log.info(f"美股指数获取完成，共写入 {total} 行。")
    n = ch_count("us_index")
    log.info(f"us_index 表当前行数: {n}")


if __name__ == "__main__":
    main()
