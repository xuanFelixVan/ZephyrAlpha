"""将CSV文件转换为TSV并导入ClickHouse基础信息表。

每个CSV的列定义和转换逻辑硬编码在此脚本中。
"""
import csv
import os
import sys
import subprocess
import re
import logging

CSV_DIR = r"d:\ZephyrAlpha\data\raw\bdpan\csv"
TSV_DIR = r"d:\ZephyrAlpha\tmp\base_tsv"
os.makedirs(TSV_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(message)s",
                    handlers=[logging.StreamHandler(sys.stdout)])
log = logging.info


def date8(s):
    """YYYYMMDD → YYYY-MM-DD; 空值返回 1970-01-01 (Date默认值)"""
    s = (s or "").strip()
    if not s or len(s) != 8 or not s.isdigit():
        return "1970-01-01"
    return f"{s[:4]}-{s[4:6]}-{s[6:8]}"


def date_iso(s):
    """YYYY-MM-DD 或空 → 保持; 空值返回 1970-01-01"""
    s = (s or "").strip()
    if not s:
        return "1970-01-01"
    # 处理 YYYY-MM-DD 或 YYYY/MM/DD
    s = s.replace("/", "-")
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        return s
    return date8(s.replace("-", ""))


def fnum(s):
    """转Float，空值返回0"""
    s = (s or "").strip()
    if not s:
        return "0"
    try:
        return str(float(s))
    except:
        return "0"


def inum(s):
    """转Int，空值返回0"""
    s = (s or "").strip()
    if not s:
        return "0"
    try:
        return str(int(float(s)))
    except:
        return "0"


def isopen(s):
    """'交易'→1, 其他→0"""
    return "1" if (s or "").strip() == "交易" else "0"


def esc(s):
    """TSV转义: Tab/Newline替换"""
    if s is None:
        return ""
    s = str(s).strip()
    return s.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")


def conv_row(row, convs):
    """根据转换函数列表转换一行"""
    parts = []
    for i, conv in enumerate(convs):
        val = row[i] if i < len(row) else ""
        parts.append(conv(val))
    return "\t".join(parts)


def process_csv(csv_file, convs, tsv_file):
    """读取CSV → 写TSV，返回行数"""
    path = os.path.join(CSV_DIR, csv_file)
    tsv_path = os.path.join(TSV_DIR, tsv_file)
    count = 0
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        with open(tsv_path, "w", encoding="utf-8", newline="\n") as out:
            for row in reader:
                if not row or all(not c.strip() for c in row):
                    continue
                out.write(conv_row(row, convs))
                out.write("\n")
                count += 1
    log(f"  {csv_file} → {tsv_file}: {count} 行")
    return count, tsv_path


def import_tsv(tsv_path, table):
    """用clickhouse-client导入TSV (通过Python stdin传递数据)"""
    with open(tsv_path, "rb") as f:
        data = f.read()
    cmd = ["wsl", "-d", "Ubuntu", "-e", "clickhouse-client",
           "--query", f"INSERT INTO c1_market.{table} FORMAT TSV"]
    r = subprocess.run(cmd, input=data, capture_output=True, timeout=60)
    if r.returncode != 0:
        log(f"  ERROR {table}: {r.stderr.decode('utf-8', errors='replace')[:300]}")
        return False
    return True


def main():
    tasks = [
        # (csv_file, tsv_file, table, convs)
        ("stock_list.csv", "stock_list.tsv", "stock_list",
         [esc, esc, esc, esc, esc, esc, esc, esc, esc, esc, esc, esc, date8, date8, esc, esc, esc]),
        ("trade_calendar.csv", "trade_calendar.tsv", "trade_calendar",
         [esc, date_iso, isopen, date_iso]),
        ("index_list.csv", "index_list.tsv", "index_list",
         [esc, esc, esc, esc, esc, date8, fnum, date8, esc, fnum]),
        ("hk_stock_list.csv", "hk_stock_list.tsv", "hk_stock_list",
         [esc, esc]),
        ("hk_trade_calendar.csv", "hk_trade_calendar.tsv", "hk_trade_calendar",
         [date_iso, isopen, date_iso]),
        ("convertible_bond_list.csv", "convertible_bond_list.tsv", "convertible_bond_list",
         [esc, esc, esc, esc, esc, esc, fnum, fnum, fnum, fnum, fnum,
          date8, date8, esc, fnum, fnum, inum, date8, date8, esc, date8, date8, date8,
          fnum, fnum, esc, fnum, esc, esc, esc]),
        ("etf_list.csv", "etf_list.tsv", "etf_list",
         [esc, esc, esc, esc, esc, esc, date_iso, date_iso, esc, esc, esc, esc, fnum, esc]),
        ("lof_list.csv", "lof_list.tsv", "lof_list",
         [esc, esc]),
        ("etf_benchmark.csv", "etf_benchmark.tsv", "etf_benchmark",
         [esc, esc, esc, esc, date8, date8, fnum, esc]),
        ("tdx_sector_info.csv", "tdx_sector_info.tsv", "tdx_sector_info",
         [esc, date8, esc, esc, inum, fnum, fnum, fnum, fnum]),
        ("tdx_market_index.csv", "tdx_market_index.tsv", "tdx_market_index",
         [esc, esc]),
    ]

    log("=== CSV → TSV 转换 ===")
    all_tsv = []
    for csv_f, tsv_f, table, convs in tasks:
        if not os.path.exists(os.path.join(CSV_DIR, csv_f)):
            log(f"  SKIP {csv_f} (不存在)")
            continue
        cnt, tsv_path = process_csv(csv_f, convs, tsv_f)
        all_tsv.append((tsv_path, table, cnt))

    log("\n=== TSV → ClickHouse 导入 ===")
    total = 0
    for tsv_path, table, cnt in all_tsv:
        if import_tsv(tsv_path, table):
            log(f"  ✓ {table}: {cnt} 行")
            total += cnt
        else:
            log(f"  ✗ {table}: 失败")
    log(f"\n总计导入: {total} 行")


if __name__ == "__main__":
    main()
