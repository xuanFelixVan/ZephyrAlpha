"""#2 资金流向 → money_flow（iFind i问财，P0，全量重建）。

策略：
- 倒序遍历交易日（2026-07 → 1990），每天查 i问财获取全部股票资金流向
- i问财查询语法: "<date> 主力资金流向"（需实测调整）
- money_flow.symbol 格式为 sh600000/sz000001（前缀+6位）
- i问财返回的"股票代码"需转换为 sh/sz 前缀格式

用法:
    python _fetch_money_flow.py            # 续传
    python _fetch_money_flow.py --restart  # 重新开始
    python _fetch_money_flow.py --days 30  # 仅处理最近 N 天

注意:
- i问财返回行数可能受限，查询语法需实测调优
- money_flow 表当前 13200 行/98 只/2025-04~11，目标全量重建
"""
import sys
import time
import argparse

sys.path.insert(0, r"d:\ZephyrAlpha\tmp")
from _ds_common import (
    setup_logging, load_env, ch_query, ch_execute, ch_insert_tsv,
    load_progress, save_progress, tsv_escape,
)

log = setup_logging("fetch_money_flow")
SLEEP_BETWEEN_CALLS = 1.0  # i问财限流防护


def get_trading_dates_backward(end_date: str = "2026-07-04", days: int = None):
    """从 trade_calendar 读取交易日列表（倒序）。"""
    sql = (f"SELECT cal_date FROM c1_market.trade_calendar "
           f"WHERE is_open=1 AND cal_date <= '{end_date}' "
           f"ORDER BY cal_date DESC")
    if days:
        sql += f" LIMIT {days}"
    out = ch_query(sql)
    return [line.strip() for line in out.strip().split("\n") if line.strip()]


def to_flow_symbol(iwencai_code: str) -> str:
    """i问财返回的股票代码 → money_flow.symbol 格式（sh/sz+6位）。

    i问财返回格式可能为: 000001 / 000001.SZ / SZ000001 等。
    """
    s = str(iwencai_code).strip().upper()
    # 去掉 .SZ/.SH 后缀
    s = s.replace(".SZ", "").replace(".SH", "").replace(".BJ", "")
    # 去掉前缀字母
    for pfx in ("SH", "SZ", "BJ"):
        if s.startswith(pfx):
            s = s[len(pfx):]
            break
    if not s.isdigit() or len(s) != 6:
        return ""
    # 加前缀
    if s.startswith(("60", "68", "90", "11", "51")):
        return "sh" + s
    if s.startswith(("00", "30", "20")):
        return "sz" + s
    if s.startswith(("43", "83", "87", "92")):
        return "bj" + s
    return "sh" + s  # 默认


def fetch_day(ifind, date: str):
    """查 i问财获取某日全部股票资金流向。返回 DataFrame 或 None。"""
    from iFinDPy import THS_iwencai
    # 查询语法（需实测调整；备选: "<date> 主力资金流向个股", "<date> 全部股票主力资金流向"）
    query = f"{date.replace('-', '年')}日 主力资金流向"
    try:
        df = THS_iwencai(query, "stock")
        return df
    except Exception as e:
        log.warning(f"  {date} 查询失败: {e}")
        return None


def df_to_tsv(df, date: str):
    """DataFrame → TSV 行列表。money_flow 列：trade_date, symbol, close, pct_change,
    main_net_inflow, main_net_inflow_pct, super_large_net_inflow, super_large_net_inflow_pct,
    large_net_inflow, large_net_inflow_pct, medium_net_inflow, medium_net_inflow_pct,
    small_net_inflow, small_net_inflow_pct
    """
    lines = []
    cols = list(df.columns)
    for _, row in df.iterrows():
        code = row.get("股票代码") or row.get("code") or row.get("thscode")
        sym = to_flow_symbol(code)
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
            tsv_escape(g("close", "收盘价", "最新价")),
            tsv_escape(g("pct_change", "涨跌幅", "涨跌幅(%)")),
            tsv_escape(g("main_net_inflow", "主力净流入-净额", "主力资金流向")),
            tsv_escape(g("main_net_inflow_pct", "主力净流入-净占比", "主力净流入净占比")),
            tsv_escape(g("super_large_net_inflow", "超大单净流入-净额", "超大单净流入")),
            tsv_escape(g("super_large_net_inflow_pct", "超大单净流入-净占比")),
            tsv_escape(g("large_net_inflow", "大单净流入-净额", "大单净流入")),
            tsv_escape(g("large_net_inflow_pct", "大单净流入-净占比")),
            tsv_escape(g("medium_net_inflow", "中单净流入-净额", "中单净流入")),
            tsv_escape(g("medium_net_inflow_pct", "中单净流入-净占比")),
            tsv_escape(g("small_net_inflow", "小单净流入-净额", "小单净流入")),
            tsv_escape(g("small_net_inflow_pct", "小单净流入-净占比")),
        ])
        lines.append(line)
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--restart", action="store_true")
    ap.add_argument("--days", type=int, help="仅处理最近 N 天")
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

    state = {} if args.restart else load_progress("fetch_money_flow")
    last_date = state.get("last_date")
    start_idx = 0
    if last_date and last_date in dates:
        start_idx = dates.index(last_date) + 1

    for di in range(start_idx, len(dates)):
        date = dates[di]
        df = fetch_day(None, date.replace("-", ""))
        if df is None or len(df) == 0:
            log.info(f"  [{di+1}/{len(dates)}] {date} 无数据")
            save_progress("fetch_money_flow", {"last_date": date})
            time.sleep(SLEEP_BETWEEN_CALLS)
            continue
        lines = df_to_tsv(df, date)
        if lines:
            tsv = ("\n".join(lines) + "\n").encode("utf-8")
            if ch_insert_tsv("money_flow", tsv):
                log.info(f"  [{di+1}/{len(dates)}] {date} 写入 {len(lines)} 行")
        save_progress("fetch_money_flow", {"last_date": date})
        time.sleep(SLEEP_BETWEEN_CALLS)

    log.info("资金流向获取完成。")


if __name__ == "__main__":
    main()
