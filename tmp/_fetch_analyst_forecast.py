"""#13 分析师预期 → analyst_forecast（AKShare，P1，倒序）。

⚠️ 使用时必须断开 VPN。

策略：
- 遍历 stock_list 全部股票
- 调用 ak.stock_profit_forecast_ths(symbol="600000") 获取一致预期 EPS
- AKShare 限速 <1次/秒 → sleep(1)
- symbol 参数为 6 位数字（不带后缀）

用法:
    python _fetch_analyst_forecast.py
    python _fetch_analyst_forecast.py --restart
    python _fetch_analyst_forecast.py --limit 100

表结构: analyst_forecast(report_date, symbol, forecast_year, forecast_eps,
                          forecast_pe, rating, analyst_count)
"""
import sys
import time
import argparse

sys.path.insert(0, r"d:\ZephyrAlpha\tmp")
from _ds_common import (
    setup_logging, ch_insert_tsv, tsv_escape,
    get_stock_list, load_progress, save_progress,
)

log = setup_logging("fetch_analyst_forecast")
SLEEP_BETWEEN = 1.2  # AKShare 限速


def fetch_forecast(symbol: str):
    """获取单只股票分析师一致预期。返回 DataFrame 或 None。"""
    import akshare as ak
    try:
        df = ak.stock_profit_forecast_ths(symbol=symbol)
        return df
    except Exception as e:
        return None


def df_to_tsv(df, symbol):
    """DataFrame → TSV。"""
    lines = []
    cols = list(df.columns)
    for _, row in df.iterrows():
        def g(*names):
            for n in names:
                if n in cols:
                    v = row.get(n)
                    return "" if v is None else v
            return ""
        # report_date: 通常为统计日期或报告期
        report_date = g("统计日期", "日期", "date", "报告期")
        if not report_date:
            continue
        rd = str(report_date)[:10]
        line = "\t".join([
            rd, symbol,
            tsv_escape(g("forecast_year", "预测年度", "年度")),
            tsv_escape(g("forecast_eps", "预测每股收益", "一致预期EPS", "每股收益")),
            tsv_escape(g("forecast_pe", "预测市盈率", "一致预期PE")),
            tsv_escape(g("rating", "评级", "投资评级")),
            tsv_escape(g("analyst_count", "分析师家数", "机构家数", "研究员人数")),
        ])
        lines.append(line)
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--restart", action="store_true")
    ap.add_argument("--limit", type=int, help="仅处理前N只股票")
    args = ap.parse_args()

    log.info("⚠️ 确认已断开 VPN！")

    stocks = get_stock_list(only_listed=True)
    log.info(f"股票总数: {len(stocks)}")
    if args.limit:
        stocks = stocks[:args.limit]
        log.info(f"限制处理前 {args.limit} 只")

    state = {} if args.restart else load_progress("fetch_analyst_forecast")
    last_sym = state.get("last_symbol")
    started = last_sym is None

    total = 0
    for i, (ts_code, symbol, name) in enumerate(stocks):
        if not started:
            if symbol == last_sym:
                started = True
            continue
        df = fetch_forecast(symbol)
        if df is not None and len(df) > 0:
            lines = df_to_tsv(df, symbol)
            if lines:
                tsv = ("\n".join(lines) + "\n").encode("utf-8")
                if ch_insert_tsv("analyst_forecast", tsv):
                    total += len(lines)
                    if (i + 1) % 50 == 0:
                        log.info(f"  [{i+1}/{len(stocks)}] {symbol} {name}: 累计 {total} 行")
        else:
            if (i + 1) % 100 == 0:
                log.info(f"  [{i+1}/{len(stocks)}] {symbol} {name}: 无预期数据")
        save_progress("fetch_analyst_forecast", {"last_symbol": symbol})
        time.sleep(SLEEP_BETWEEN)

    log.info(f"分析师预期获取完成，共写入 {total} 行。")
    from _ds_common import ch_count
    n = ch_count("analyst_forecast")
    log.info(f"analyst_forecast 表当前行数: {n}")


if __name__ == "__main__":
    main()
