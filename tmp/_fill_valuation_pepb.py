"""填充 daily_valuation 表 PE/PB/PS/PCF 缺口（iFind i问财当前快照）。

策略：
- daily_valuation 已有 OHLC（从 daily_kline backfill 到 2026-07-02），但 PE/PB/PS/PCF=0
- i问财返回 5204 只股票的当前快照（含 2026-07-03 数据）
- 在 daily_valuation 中为 2026-07-03 插入新行（PE/PB 有值，OHLC=0）
- 同时 UPDATE 2026-07-02 的行，PE/PB 用 2026-07-03 快照近似（避免 0 值）

i问财返回列:
  ['股票代码', '股票简称', '股票币种类型',
   '市盈率(pe,ttm)[20260703]', '市净率(pb)[20260703]',
   '市销率(ps,ttm)[20260703]', '市现率(pcf,经营现金流)[20260703]']

用法:
    python _fill_valuation_pepb.py            # 仅打印不写入
    python _fill_valuation_pepb.py --apply     # 实际写入
"""
import sys
import os
import argparse
import datetime

sys.path.insert(0, r"d:\ZephyrAlpha\tmp")
from _ds_common import (
    setup_logging, load_env, ch_insert_tsv, ch_execute, ch_query,
    tsv_escape, num_or_null,
)

log = setup_logging("fill_valuation_pepb")


def to_symbol(code):
    """'000686.SZ' → '000686'。"""
    s = str(code).strip().upper()
    for pfx in (".SZ", ".SH", ".BJ"):
        s = s.replace(pfx, "")
    return s if s.isdigit() and len(s) == 6 else ""


def find_pepb_columns(df):
    """从 DataFrame 列名中识别 PE/PB/PS/PCF 列。返回 (col_pe, col_pb, col_ps, col_pcf)。"""
    cols = list(df.columns)
    col_pe = col_pb = col_ps = col_pcf = None
    for c in cols:
        cl = str(c).lower()
        if "pe" in cl and "ttm" in cl:
            col_pe = c
        elif "pb" in cl and "pe" not in cl:
            col_pb = c
        elif "ps" in cl and "ttm" in cl:
            col_ps = c
        elif "pcf" in cl:
            col_pcf = c
    return col_pe, col_pb, col_ps, col_pcf


def fetch_snapshot():
    """i问财查询当前 PE/PB/PS/PCF 快照。返回 DataFrame。"""
    from iFinDPy import THS_iwencai
    q = "全部A股 市盈率TTM 市净率MRQ 市销率TTM 市现率TTM"
    log.info(f"i问财查询: {q} ...")
    result = THS_iwencai(q, "stock")
    from _ds_common import iwencai_to_df
    df = iwencai_to_df(result)
    log.info(f"查询返回 {len(df)} 行")
    return df


def df_to_tsv(df, trade_date):
    """DataFrame → TSV 行列表，用于插入 _pepb_staging。"""
    col_pe, col_pb, col_ps, col_pcf = find_pepb_columns(df)
    if not all([col_pe, col_pb, col_ps, col_pcf]):
        log.error(f"未找到全部估值列: pe={col_pe}, pb={col_pb}, ps={col_ps}, pcf={col_pcf}")
        log.error(f"实际列: {list(df.columns)}")
        return []

    lines = []
    skipped = 0
    for _, row in df.iterrows():
        code = row.get("股票代码") or row.get("code") or row.get("thscode")
        sym = to_symbol(code)
        if not sym:
            skipped += 1
            continue
        pe = num_or_null(row.get(col_pe))
        pb = num_or_null(row.get(col_pb))
        ps = num_or_null(row.get(col_ps))
        pcf = num_or_null(row.get(col_pcf))
        # 跳过全 0/None 的行
        if pe == "\\N" and pb == "\\N" and ps == "\\N" and pcf == "\\N":
            skipped += 1
            continue
        lines.append("\t".join([trade_date, sym, str(pe), str(pb), str(ps), str(pcf)]))
    log.info(f"解析: {len(lines)} 行有效, {skipped} 行跳过")
    return lines


def ensure_staging():
    """创建 staging 表。"""
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


def insert_2026_07_03_rows(trade_date):
    """为 2026-07-03 插入新行（OHLC=0，PE/PB 有值）。

    方案: 直接 INSERT INTO daily_valuation SELECT FROM _pepb_staging
    """
    sql = f"""
INSERT INTO c1_market.daily_valuation
    (trade_date, symbol, open, high, low, close, preclose, volume, amount,
     turnover, pct_change, pe_ttm, pb_mrq, ps_ttm, pcf_ncf_ttm, is_st, data_source)
SELECT
    '{trade_date}' AS trade_date, symbol,
    0 AS open, 0 AS high, 0 AS low, 0 AS close, 0 AS preclose,
    0 AS volume, 0 AS amount, 0 AS turnover, 0 AS pct_change,
    pe_ttm, pb_mrq, ps_ttm, pcf_ncf_ttm,
    0 AS is_st, 'ifind_iwencai_snapshot' AS data_source
FROM c1_market._pepb_staging
WHERE trade_date = '{trade_date}'
"""
    if ch_execute(sql):
        log.info(f"已为 {trade_date} 插入 PE/PB 行")
    else:
        log.error(f"插入 {trade_date} 失败")


def update_2026_07_02_pepb(target_date, source_date):
    """用 source_date 的快照 UPDATE target_date 的 OHLC 行 PE/PB。
    ALTER TABLE UPDATE ... FROM staging.
    """
    sql = f"""
ALTER TABLE c1_market.daily_valuation
UPDATE
    pe_ttm = s.pe_ttm,
    pb_mrq = s.pb_mrq,
    ps_ttm = s.ps_ttm,
    pcf_ncf_ttm = s.pcf_ncf_ttm
FROM c1_market._pepb_staging s
WHERE daily_valuation.trade_date = toDate('{target_date}')
  AND daily_valuation.symbol = s.symbol
  AND s.trade_date = toDate('{source_date}')
  AND daily_valuation.data_source = 'daily_kline_backfill'
"""
    if ch_execute(sql):
        log.info(f"已提交 UPDATE mutation: {target_date} ← {source_date}")
    else:
        log.error("UPDATE mutation 提交失败")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="实际写入（默认仅打印）")
    args = ap.parse_args()

    load_env()
    from iFinDPy import THS_iFinDLogin
    r = THS_iFinDLogin(os.environ["IFIND_USERNAME"], os.environ["IFIND_PASSWORD"])
    if r != 0:
        log.error(f"iFind 登录失败: {r}")
        return
    log.info("iFind 登录成功")

    df = fetch_snapshot()
    if len(df) == 0:
        log.error("i问财返回 0 行，退出")
        return

    col_pe, col_pb, col_ps, col_pcf = find_pepb_columns(df)
    log.info(f"识别列: pe={col_pe}, pb={col_pb}, ps={col_ps}, pcf={col_pcf}")

    # i问财返回日期 20260703（昨日）
    snapshot_date = "2026-07-03"

    lines = df_to_tsv(df, snapshot_date)
    if not lines:
        log.error("解析后 0 行，退出")
        return

    log.info(f"准备写入 {len(lines)} 行到 _pepb_staging (trade_date={snapshot_date})")
    if not args.apply:
        log.info("DRY RUN 模式（--apply 实际写入）")
        log.info(f"前 3 行示例:\n{chr(10).join(lines[:3])}")
        return

    ensure_staging()
    tsv = ("\n".join(lines) + "\n").encode("utf-8")
    if ch_insert_tsv("_pepb_staging", tsv):
        log.info(f"写入 _pepb_staging: {len(lines)} 行")

    # 1. 为 2026-07-03 插入新行（PE/PB 有值，OHLC=0）
    insert_2026_07_03_rows(snapshot_date)

    # 2. UPDATE 2026-07-02 的 OHLC 行 PE/PB（用 07-03 快照近似）
    update_2026_07_02_pepb("2026-07-02", snapshot_date)

    # 查 mutation 进度
    log.info("查 mutation 进度:")
    out = ch_query("SELECT database, table, is_done, parts_to_do FROM system.mutations WHERE table='daily_valuation' AND is_done=0 ORDER BY create_time DESC LIMIT 5")
    log.info(out)

    # 最终统计
    out = ch_query(f"SELECT count() as total, countIf(pe_ttm > 0) as has_pe, countIf(pb_mrq > 0) as has_pb, max(trade_date) as max_d FROM c1_market.daily_valuation WHERE trade_date >= '2025-11-12'")
    log.info(f"缺口范围统计:\n{out}")


if __name__ == "__main__":
    main()
