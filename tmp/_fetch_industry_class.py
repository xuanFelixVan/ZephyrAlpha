"""#7 行业分类 → industry_class（iFind i问财，P1，全量静态）。

策略（v2，2026-07-04 重写）：
- 一次 i问财查询 "申万行业分类" 获取全部 5534 股票的 SW1/SW2/SW3 分类路径
- 解析 "所属申万行业" 列（格式: "SW1--SW2--SW3"）
- 写入 industry_class(symbol, industry_sw, industry_zsi, industry_level)
- v1 用 THS_DataPool + AKShare index_component_sw 均失败（试用账号限制 + AKShare库bug）

用法:
    python _fetch_industry_class.py            # 全量获取
    python _fetch_industry_class.py --truncate  # 清空后重新获取

表结构: industry_class(symbol, industry_sw, industry_zsi, industry_level, data_source DEFAULT 'ifind')
"""
import sys
import os
import argparse
import datetime

sys.path.insert(0, r"d:\ZephyrAlpha\tmp")
from _ds_common import (
    setup_logging, load_env, ch_insert_tsv, ch_execute, ch_count,
    iwencai_to_df, tsv_escape,
)

log = setup_logging("fetch_industry_class")
DOWNLOAD_DATE = datetime.date.today().isoformat()


def to_symbol(code):
    """将 i问财返回的股票代码转为 6 位数字。如 '000001.SZ' → '000001'。"""
    s = str(code).strip().upper()
    for pfx in (".SZ", ".SH", ".BJ", ".TI"):
        s = s.replace(pfx, "")
    for pfx in ("SH", "SZ", "BJ"):
        if s.startswith(pfx):
            s = s[len(pfx):]
    return s if s.isdigit() and len(s) == 6 else ""


def parse_sw_path(sw_str):
    """解析 "SW1--SW2--SW3" 格式，返回 [sw1, sw2, sw3]（不足补空）。"""
    parts = str(sw_str).split("--")
    # 去除前后空格
    parts = [p.strip() for p in parts]
    while len(parts) < 3:
        parts.append("")
    return parts[:3]


def fetch_all_sw():
    """一次 i问财查询获取全部 A 股的申万行业分类。返回 DataFrame。"""
    from iFinDPy import THS_iwencai
    log.info("i问财查询: 申万行业分类 ...")
    result = THS_iwencai("申万行业分类", "stock")
    df = iwencai_to_df(result)
    log.info(f"查询返回 {len(df)} 行")
    return df


def df_to_tsv(df):
    """DataFrame → TSV 行列表。

    i问财返回列: 股票代码, 股票简称, 所属申万行业
    解析 "所属申万行业" 为 SW1/SW2/SW3，每只股票写 3 行（level 1/2/3）。
    """
    lines = []
    col_sw = None
    for c in df.columns:
        if "申万行业" in str(c):
            col_sw = c
            break
    if col_sw is None:
        log.error(f"未找到申万行业列，实际列: {list(df.columns)}")
        return lines

    for _, row in df.iterrows():
        code = row.get("股票代码") or row.get("code") or row.get("thscode")
        sym = to_symbol(code)
        if not sym:
            continue
        sw_str = row.get(col_sw, "")
        sw1, sw2, sw3 = parse_sw_path(sw_str)
        # 写入 SW1（level 1）
        if sw1:
            lines.append("\t".join([sym, tsv_escape(sw1), "", "1"]))
        # 写入 SW2（level 2）
        if sw2:
            lines.append("\t".join([sym, tsv_escape(sw2), "", "2"]))
        # 写入 SW3（level 3）
        if sw3:
            lines.append("\t".join([sym, tsv_escape(sw3), "", "3"]))
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--truncate", action="store_true", help="清空表后重新获取")
    args = ap.parse_args()

    load_env()
    from iFinDPy import THS_iFinDLogin
    r = THS_iFinDLogin(os.environ["IFIND_USERNAME"], os.environ["IFIND_PASSWORD"])
    if r != 0:
        log.error(f"iFind 登录失败: {r}")
        return
    log.info("iFind 登录成功")

    if args.truncate:
        log.info("清空 industry_class 表 ...")
        ch_execute("TRUNCATE TABLE c1_market.industry_class")

    df = fetch_all_sw()
    if len(df) == 0:
        log.error("i问财返回 0 行，退出")
        return

    lines = df_to_tsv(df)
    log.info(f"解析得到 {len(lines)} 行（含 SW1/SW2/SW3 三级）")

    if lines:
        tsv = ("\n".join(lines) + "\n").encode("utf-8")
        if ch_insert_tsv("industry_class", tsv):
            log.info(f"写入 {len(lines)} 行成功")

    # 去重（同 symbol + level 可能有多条）
    log.info("执行 OPTIMIZE FINAL 去重 ...")
    ch_execute("OPTIMIZE TABLE c1_market.industry_class FINAL")

    n = ch_count("industry_class")
    n_l1 = ch_count("industry_class", "industry_level=1")
    n_l2 = ch_count("industry_class", "industry_level=2")
    n_l3 = ch_count("industry_class", "industry_level=3")
    n_sym = ch_count("industry_class", "1=1")  # placeholder
    log.info(f"完成。industry_class: {n} 行 (L1={n_l1}, L2={n_l2}, L3={n_l3})")

    # 统计 SW1 覆盖
    from _ds_common import ch_query
    out = ch_query("SELECT industry_sw, count() as cnt FROM c1_market.industry_class WHERE industry_level=1 GROUP BY industry_sw ORDER BY cnt DESC LIMIT 10")
    log.info(f"SW1 行业 Top10:\n{out}")


if __name__ == "__main__":
    main()
