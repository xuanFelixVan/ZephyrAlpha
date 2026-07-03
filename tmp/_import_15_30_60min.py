"""增量导入15/30/60分钟K线（2025-11~2026-07）。

策略：
1. 下载2025和2026年zip
2. 转TSV（格式与5min相同）
3. 2025年只保留 trade_time >= '2025-11-13' 的行（避免与现有数据重复）
4. 2026年全部导入
5. INSERT到对应表
"""
import zipfile
import csv
import io
import os
import sys
import subprocess
import time
import logging

BDPAN = "/root/.local/bin/bdpan"
BASE = "量化交易数据/A股分钟数据/A股_分时数据_沪深"

# 三个周期，每个周期补2025+2026
PERIODS = [
    ("15min", "15分钟_按年汇总", "c1_market.kline_15min"),
    ("30min", "30分钟_按年汇总", "c1_market.kline_30min"),
    ("60min", "60分钟_按年汇总", "c1_market.kline_60min"),
]

YEARS = [2025, 2026]
CUTOFF = "2025-11-13"  # 只导入此日期之后的数据

logging.basicConfig(level=logging.INFO, format="%(message)s",
                    handlers=[logging.StreamHandler(sys.stdout)])
log = logging.info


def download(period_dir, year, en_name, cn_name):
    zip_file = f"{year}_{en_name}.zip"
    zip_path = os.path.join(period_dir, zip_file)
    if os.path.exists(zip_path):
        log(f"  {zip_file} 已存在 ({os.path.getsize(zip_path)/1024/1024:.0f}MB)")
        return zip_path
    log(f"  下载 {zip_file}...")
    wsl_path = zip_path.replace("d:", "/mnt/d").replace("\\", "/")
    r = subprocess.run(["wsl", "-d", "Ubuntu", "-e", "bash", "-c",
                        f'{BDPAN} download "{BASE}/{cn_name}/{zip_file}" "{wsl_path}"'],
                       capture_output=True, timeout=900)
    if r.returncode != 0 or not os.path.exists(zip_path):
        log(f"  下载失败: {r.stderr.decode('utf-8', errors='replace')[:200]}")
        return None
    log(f"  下载完成 ({os.path.getsize(zip_path)/1024/1024:.0f}MB)")
    return zip_path


def zip_to_tsv(zip_path, tsv_path, year):
    """从zip读取CSV → 写TSV，2025年只保留>=CUTOFF的行"""
    total = 0
    skipped = 0
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = [n for n in zf.namelist() if n.endswith(".csv")]
        with open(tsv_path, "w", encoding="utf-8", newline="\n") as out:
            for idx, name in enumerate(names, 1):
                content = zf.read(name)
                reader = csv.reader(io.TextIOWrapper(io.BytesIO(content), encoding="utf-8-sig"))
                try:
                    next(reader)
                except StopIteration:
                    continue
                for row in reader:
                    if not row or len(row) < 9:
                        continue
                    try:
                        trade_time = row[0].strip()
                        # 2025年只保留CUTOFF之后的数据
                        if year == 2025 and trade_time < CUTOFF:
                            skipped += 1
                            continue
                        trade_date = trade_time[:10]  # YYYY-MM-DD
                        symbol = row[1].strip()
                        if symbol.startswith(("sh", "sz", "bj")):
                            symbol = symbol[2:]
                        open_p = row[3].strip() or "0"
                        close_p = row[4].strip() or "0"
                        high_p = row[5].strip() or "0"
                        low_p = row[6].strip() or "0"
                        volume = row[7].strip() or "0"
                        amount = row[8].strip() or "0"
                        pct_change = row[9].strip() if len(row) > 9 else "0"
                        amplitude = row[10].strip() if len(row) > 10 else "0"
                        # 12列: trade_date, trade_time, symbol, open, close, high, low, volume, amount, pct_change, amplitude, data_source
                        out.write(f"{trade_date}\t{trade_time}\t{symbol}\t{open_p}\t{close_p}\t{high_p}\t{low_p}\t{volume}\t{amount}\t{pct_change}\t{amplitude}\tbdpan\n")
                        total += 1
                    except (IndexError, ValueError):
                        continue
                if idx % 1000 == 0:
                    log(f"    [{idx}/{len(names)}] 写入 {total} 跳过 {skipped}")
    log(f"  写入 {total} 行, 跳过 {skipped} 行")
    return total


def import_tsv(tsv_path, table):
    sz = os.path.getsize(tsv_path) / 1024 / 1024
    log(f"  TSV: {sz:.0f}MB, 导入 {table}...")
    with open(tsv_path, "rb") as f:
        data = f.read()
    cmd = ["wsl", "-d", "Ubuntu", "-e", "clickhouse-client",
           "--query", f"INSERT INTO {table} FORMAT TSV",
           "--max_partitions_per_insert_block", "0"]
    r = subprocess.run(cmd, input=data, capture_output=True, timeout=1800)
    if r.returncode != 0:
        log(f"  导入失败: {r.stderr.decode('utf-8', errors='replace')[:300]}")
        return False
    return True


def process_period(en_name, cn_name, table):
    log(f"\n=== {en_name} ===")
    period_dir = rf"d:\ZephyrAlpha\data\raw\bdpan\{en_name}"
    os.makedirs(period_dir, exist_ok=True)
    total = 0
    for year in YEARS:
        log(f"\n--- {year}年 ---")
        zip_path = download(period_dir, year, en_name, cn_name)
        if not zip_path:
            continue
        tsv_path = os.path.join(period_dir, f"{year}_{en_name}.tsv")
        log("  转换zip → TSV...")
        t1 = time.time()
        cnt = zip_to_tsv(zip_path, tsv_path, year)
        log(f"  {cnt} 行, {time.time()-t1:.0f}s")
        t1 = time.time()
        if cnt > 0:
            if not import_tsv(tsv_path, table):
                continue
        log(f"  导入完成, {time.time()-t1:.0f}s")
        os.unlink(tsv_path)
        os.unlink(zip_path)
        total += cnt
    return total


def main():
    log("=== 15/30/60分钟K线增量补充 ===")
    grand_total = 0
    for en_name, cn_name, table in PERIODS:
        cnt = process_period(en_name, cn_name, table)
        grand_total += cnt
        log(f"\n{en_name} 完成: {cnt} 行")

    log(f"\n=== 总计: {grand_total} 行 ===")
    # 验证
    for _, _, table in PERIODS:
        r = subprocess.run(["wsl", "-d", "Ubuntu", "-e", "clickhouse-client",
                            "--query", f"SELECT '{table}', count(), min(trade_time), max(trade_time), "
                                       f"uniq(symbol) FROM {table} FORMAT TabSeparated"],
                           capture_output=True, timeout=120)
        log(f"  {r.stdout.decode('utf-8').strip()}")


if __name__ == "__main__":
    main()
