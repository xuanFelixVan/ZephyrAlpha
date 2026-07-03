"""补导5分钟K线缺失年份（2006/2020-2026）到 kline_5min_bdpan_new。

前提：
- kline_5min_bdpan_new 已存在（含 2000-2005, 2007-2019 完整数据）
- amount 列已 ALTER 为 Float64
- 2006/2020 不完整数据已 DELETE

策略：
1. 逐年：下载zip → 转TSV → 导入 → 删除临时文件
2. 完成后原子替换 kline_5min ← _bdpan_new
"""
import zipfile
import csv
import io
import os
import sys
import subprocess
import time
import logging

DLDIR = r"d:\ZephyrAlpha\data\raw\bdpan\5min"
BDPAN = "/root/.local/bin/bdpan"
BASE = "量化交易数据/A股分钟数据/A股_分时数据_沪深/5分钟_按年汇总"

logging.basicConfig(level=logging.INFO, format="%(message)s",
                    handlers=[logging.StreamHandler(sys.stdout)])
log = logging.info

# 需要补导的年份（2006不完整 + 2020不完整 + 2021-2026缺失）
YEARS = [2006, 2020, 2021, 2022, 2023, 2024, 2025, 2026]


def download_year(year):
    zip_file = f"{year}_5min.zip"
    zip_path = os.path.join(DLDIR, zip_file)
    if os.path.exists(zip_path):
        log(f"  {zip_file} 已存在 ({os.path.getsize(zip_path)/1024/1024:.0f}MB)")
        return zip_path
    log(f"  下载 {zip_file}...")
    wsl_path = zip_path.replace("d:", "/mnt/d").replace("\\", "/")
    r = subprocess.run(["wsl", "-d", "Ubuntu", "-e", "bash", "-c",
                        f'{BDPAN} download "{BASE}/{zip_file}" "{wsl_path}"'],
                       capture_output=True, timeout=900)
    if r.returncode != 0 or not os.path.exists(zip_path):
        log(f"  下载失败: {r.stderr.decode('utf-8', errors='replace')[:200]}")
        return None
    log(f"  下载完成 ({os.path.getsize(zip_path)/1024/1024:.0f}MB)")
    return zip_path


def zip_to_tsv(zip_path, tsv_path):
    """从zip读取所有CSV → 写TSV，返回行数"""
    total = 0
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = [n for n in zf.namelist() if n.endswith(".csv")]
        with open(tsv_path, "w", encoding="utf-8", newline="\n") as out:
            for idx, name in enumerate(names, 1):
                content = zf.read(name)
                reader = csv.reader(io.TextIOWrapper(io.BytesIO(content), encoding="utf-8"))
                try:
                    next(reader)  # skip header
                except StopIteration:
                    continue
                for row in reader:
                    if not row or len(row) < 9:
                        continue
                    try:
                        trade_time = row[0].strip()
                        symbol = row[1].strip()
                        if symbol.startswith(("sh", "sz", "bj")):
                            symbol = symbol[2:]
                        open_p = row[3].strip() or "0"
                        close_p = row[4].strip() or "0"
                        high_p = row[5].strip() or "0"
                        low_p = row[6].strip() or "0"
                        volume = row[7].strip() or "0"
                        amount = row[8].strip() or "0"
                        out.write(f"{trade_time}\t{symbol}\t{open_p}\t{high_p}\t{low_p}\t{close_p}\t{volume}\t{amount}\tbdpan\n")
                        total += 1
                    except (IndexError, ValueError):
                        continue
                if idx % 200 == 0:
                    log(f"    [{idx}/{len(names)}] 累计 {total} 行")
    return total


def import_tsv(tsv_path):
    sz = os.path.getsize(tsv_path) / 1024 / 1024
    log(f"  TSV: {sz:.0f}MB, 导入中...")
    with open(tsv_path, "rb") as f:
        data = f.read()
    cmd = ["wsl", "-d", "Ubuntu", "-e", "clickhouse-client",
           "--query", "INSERT INTO c1_market.kline_5min_bdpan_new FORMAT TSV",
           "--max_partitions_per_insert_block", "0"]
    r = subprocess.run(cmd, input=data, capture_output=True, timeout=1800)
    if r.returncode != 0:
        log(f"  导入失败: {r.stderr.decode('utf-8', errors='replace')[:300]}")
        return False
    return True


def process_year(year):
    log(f"\n--- {year}年 ---")
    t0 = time.time()
    zip_path = download_year(year)
    if not zip_path:
        return 0
    tsv_path = os.path.join(DLDIR, f"{year}_5min.tsv")
    log(f"  读取zip → TSV...")
    t1 = time.time()
    cnt = zip_to_tsv(zip_path, tsv_path)
    log(f"  {cnt} 行, {time.time()-t1:.0f}s")
    t1 = time.time()
    if not import_tsv(tsv_path):
        return 0
    log(f"  导入完成, {time.time()-t1:.0f}s")
    os.unlink(tsv_path)
    os.unlink(zip_path)
    log(f"  ✓ {year}年: {cnt} 行, 总耗时 {time.time()-t0:.0f}s")
    return cnt


def atomic_replace():
    sqls = [
        "DROP TABLE IF EXISTS c1_market.kline_5min_old",
        "RENAME TABLE c1_market.kline_5min TO c1_market.kline_5min_old, "
        "c1_market.kline_5min_bdpan_new TO c1_market.kline_5min",
    ]
    for sql in sqls:
        r = subprocess.run(["wsl", "-d", "Ubuntu", "-e", "clickhouse-client", "--query", sql],
                           capture_output=True, timeout=120)
        if r.returncode != 0:
            log(f"  RENAME失败: {r.stderr.decode('utf-8', errors='replace')[:200]}")
            return False
    return True


def main():
    os.makedirs(DLDIR, exist_ok=True)
    log("=== 5分钟K线补导（缺失年份）===")
    log(f"待处理年份: {YEARS}")
    total = 0
    for year in YEARS:
        cnt = process_year(year)
        total += cnt
        log(f"  累计: {total} 行")

    log(f"\n补导完成: {total} 行")
    r = subprocess.run(["wsl", "-d", "Ubuntu", "-e", "clickhouse-client",
                        "--query", "SELECT count(), min(trade_time), max(trade_time), "
                                   "uniq(symbol) FROM c1_market.kline_5min_bdpan_new FORMAT TabSeparated"],
                       capture_output=True, timeout=120)
    log(f"  新表验证: {r.stdout.decode('utf-8').strip()}")

    log("\n执行原子替换...")
    if atomic_replace():
        log("  ✓ 替换成功")
        r = subprocess.run(["wsl", "-d", "Ubuntu", "-e", "clickhouse-client",
                            "--query", "SELECT count(), min(trade_time), max(trade_time), "
                                       "uniq(symbol) FROM c1_market.kline_5min FORMAT TabSeparated"],
                           capture_output=True, timeout=120)
        log(f"  最终验证: {r.stdout.decode('utf-8').strip()}")
    else:
        log("  ✗ 替换失败")


if __name__ == "__main__":
    main()
