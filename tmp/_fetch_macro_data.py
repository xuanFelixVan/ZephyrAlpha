"""#12 宏观经济 → macro_data（AKShare，P1，全量历史）。

⚠️ 使用时必须断开 VPN（爬国内网站，VPN 导致海外 IP 被拒绝）。

获取指标: GDP / CPI / PMI / M2（+ PPI / LPR / 社融 作为补充）
策略: 全量历史（数据量小，一次性拉取）

表结构: macro_data(report_date, indicator_name, indicator_value, unit, frequency)

用法:
    python _fetch_macro_data.py
"""
import sys
import time

sys.path.insert(0, r"d:\ZephyrAlpha\tmp")
from _ds_common import setup_logging, ch_insert_tsv, tsv_escape, ch_count, ch_execute

log = setup_logging("fetch_macro_data")


def safe_float(v):
    try:
        return float(v)
    except (ValueError, TypeError):
        return ""


def fetch_gdp():
    """GDP 季度数据。ak.macro_china_gdp() → 81 行。"""
    import akshare as ak
    df = ak.macro_china_gdp()
    lines = []
    for _, row in df.iterrows():
        # 列: 季度, 国内生产总值-绝对值, 国内生产总值-同比增长, 第一产业-绝对值, ...
        quarter = str(row.iloc[0])  # 如 "2025年第1季度"
        report_date = parse_quarter_to_date(quarter)
        if not report_date:
            continue
        # GDP 绝对值
        val = safe_float(row.get("国内生产总值-绝对值"))
        if val != "":
            lines.append("\t".join([
                report_date, "GDP", tsv_escape(val), "亿元", "季度"
            ]))
        # GDP 同比
        yoy = safe_float(row.get("国内生产总值-同比增长"))
        if yoy != "":
            lines.append("\t".join([
                report_date, "GDP_同比", tsv_escape(yoy), "%", "季度"
            ]))
    return lines


def fetch_cpi():
    """CPI 月度数据。ak.macro_china_cpi()。"""
    import akshare as ak
    df = ak.macro_china_cpi()
    lines = []
    cols = list(df.columns)
    for _, row in df.iterrows():
        # 第一列通常为月份 "2025年6月"
        month_str = str(row.iloc[0])
        report_date = parse_month_to_date(month_str)
        if not report_date:
            continue
        for col in cols[1:]:
            val = safe_float(row.get(col))
            if val != "":
                lines.append("\t".join([
                    report_date, tsv_escape(col), tsv_escape(val), "", "月度"
                ]))
    return lines


def fetch_pmi():
    """PMI 月度数据。ak.macro_china_pmi()。"""
    import akshare as ak
    df = ak.macro_china_pmi()
    lines = []
    cols = list(df.columns)
    for _, row in df.iterrows():
        month_str = str(row.iloc[0])
        report_date = parse_month_to_date(month_str)
        if not report_date:
            continue
        for col in cols[1:]:
            val = safe_float(row.get(col))
            if val != "":
                lines.append("\t".join([
                    report_date, tsv_escape(col), tsv_escape(val), "", "月度"
                ]))
    return lines


def fetch_money_supply():
    """M0/M1/M2 货币供应量。ak.macro_china_money_supply()。"""
    import akshare as ak
    df = ak.macro_china_money_supply()
    lines = []
    cols = list(df.columns)
    for _, row in df.iterrows():
        month_str = str(row.iloc[0])
        report_date = parse_month_to_date(month_str)
        if not report_date:
            continue
        for col in cols[1:]:
            val = safe_float(row.get(col))
            if val != "":
                lines.append("\t".join([
                    report_date, tsv_escape(col), tsv_escape(val), "", "月度"
                ]))
    return lines


def fetch_ppi():
    """PPI 工业品出厂价格指数。ak.macro_china_ppi_yearly()。"""
    import akshare as ak
    try:
        df = ak.macro_china_ppi_yearly()
        lines = []
        cols = list(df.columns)
        for _, row in df.iterrows():
            month_str = str(row.iloc[0])
            report_date = parse_month_to_date(month_str)
            if not report_date:
                continue
            for col in cols[1:]:
                val = safe_float(row.get(col))
                if val != "":
                    lines.append("\t".join([
                        report_date, tsv_escape(col), tsv_escape(val), "", "月度"
                    ]))
        return lines
    except Exception as e:
        log.warning(f"  PPI 获取失败: {e}")
        return []


def parse_quarter_to_date(q: str):
    """'2025年第1季度' → '2025-03-31'；'2025年第1-3季度' → '2025-09-30'。"""
    import re
    m = re.match(r"(\d{4})年第([0-9\-]+)季度", q)
    if not m:
        return ""
    year = m.group(1)
    qs = m.group(2)
    if "-" in qs:
        # 如 1-3 → 第三季度末
        last = int(qs.split("-")[-1])
    else:
        last = int(qs)
    month_day = {1: "03-31", 2: "06-30", 3: "09-30", 4: "12-31"}
    md = month_day.get(last)
    return f"{year}-{md}" if md else ""


def parse_month_to_date(m: str):
    """'2025年6月' → '2025-06-30'。"""
    import re
    match = re.match(r"(\d{4})年(\d{1,2})月?", m)
    if not match:
        return ""
    y, mo = match.group(1), int(match.group(2))
    import calendar
    last_day = calendar.monthrange(int(y), mo)[1]
    return f"{y}-{mo:02d}-{last_day:02d}"


def main():
    log.info("⚠️ 确认已断开 VPN！（AKShare 爬国内网站，VPN 导致失败）")
    log.info("开始获取宏观经济数据...")

    fetchers = [
        ("GDP", fetch_gdp),
        ("CPI", fetch_cpi),
        ("PMI", fetch_pmi),
        ("M2", fetch_money_supply),
        ("PPI", fetch_ppi),
    ]
    total = 0
    for name, fn in fetchers:
        try:
            log.info(f"获取 {name} ...")
            lines = fn()
            if lines:
                tsv = ("\n".join(lines) + "\n").encode("utf-8")
                if ch_insert_tsv("macro_data", tsv):
                    log.info(f"  {name} 写入 {len(lines)} 行")
                    total += len(lines)
            else:
                log.warning(f"  {name} 无数据")
        except Exception as e:
            log.error(f"  {name} 失败: {e}")
        time.sleep(1)

    log.info(f"宏观经济获取完成，共写入 {total} 行。")
    n = ch_count("macro_data")
    log.info(f"macro_data 表当前行数: {n}")
    # 按指标验证
    from _ds_common import ch_query
    log.info(ch_query("SELECT indicator_name, count(), min(report_date), max(report_date) FROM c1_market.macro_data GROUP BY indicator_name ORDER BY indicator_name"))


if __name__ == "__main__":
    main()
