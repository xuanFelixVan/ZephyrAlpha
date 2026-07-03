"""导入5分钟K线到ClickHouse（逐年处理，原子表替换策略）。

策略：
1. 创建新表 _bdpan_new
2. 逐年：下载zip → 转TSV → 导入新表 → 删除zip和TSV
3. 全部完成后 → 原子替换

用法: python _import_5min.py [test|all]
  test - 只处理2000年（已下载）
  all  - 处理2000-2026所有年份
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


def create_new_table():
    """创建_new表"""
    subprocess.run(["wsl", "-d", "Ubuntu", "-e", "clickhouse-client",
                    "--query", "DROP TABLE IF EXISTS c1_market.kline_5min_bdpan_new"],
                   capture_output=True, timeout=30)
    r = subprocess.run(["wsl", "-d", "Ubuntu", "-e", "clickhouse-client",
                        "--query", "CREATE TABLE c1_market.kline_5min_bdpan_new AS c1_market.kline_5min"],
                       capture_output=True, timeout=30)
    return r.returncode == 0


def download_year(year):
    """下载某一年的5分钟K线zip"""
    zip_file = f"{year}_5min.zip"
    zip_path = os.path.join(DLDIR, zip_file)
    if os.path.exists(zip_path):
        log(f"  {zip_file} 已存在 ({os.path.getsize(zip_path)/1024/1024:.0f}MB)")
        return zip_path
    log(f"  下载 {zip_file}...")
    r = subprocess.run(["wsl", "-d", "Ubuntu", "-e", "bash", "-c",
                        f'{BDPAN} download "{BASE}/{zip_file}" "{zip_path.replace("d:", "/mnt/d").replace(chr(92), "/")}"'],
                       capture_output=True, timeout=600)
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
                next(reader)  # skip header
                for row in reader:
                    if not row or len(row) < 9:
                        continue
                    # CSV: 时间,代码,名称,开盘价,收盘价,最高价,最低价,成交量,成交额,涨幅,振幅
                    # TSV: trade_time, symbol, open, high, low, close, volume, amount, data_source
                    try:
                        trade_time = row[0].strip()  # 2000-06-09 09:35:00
                        # 代码 sh600000 → 600000
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
    """导入TSV到_new表"""
    sz = os.path.getsize(tsv_path) / 1024 / 1024
    log(f"  TSV: {sz:.0f}MB, 导入中...")
    with open(tsv_path, "rb") as f:
        data = f.read()
    cmd = ["wsl", "-d", "Ubuntu", "-e", "clickhouse-client",
           "--query", "INSERT INTO c1_market.kline_5min_bdpan_new FORMAT TSV",
           "--max_partitions_per_insert_block", "0"]
    r = subprocess.run(cmd, input=data, capture_output=True, timeout=600)
    if r.returncode != 0:
        log(f"  导入失败: {r.stderr.decode('utf-8', errors='replace')[:300]}")
        return False
    return True


def process_year(year):
    """处理单一年份"""
    log(f"\n--- {year}年 ---")
    t0 = time.time()

    # 1. 下载
    zip_path = download_year(year)
    if not zip_path:
        return 0

    # 2. 转TSV
    tsv_path = os.path.join(DLDIR, f"{year}_5min.tsv")
    log(f"  读取zip → TSV...")
    t1 = time.time()
    cnt = zip_to_tsv(zip_path, tsv_path)
    log(f"  {cnt} 行, {time.time()-t1:.0f}s")

    # 3. 导入
    t1 = time.time()
    if not import_tsv(tsv_path):
        return 0
    log(f"  导入完成, {time.time()-t1:.0f}s")

    # 4. 清理
    os.unlink(tsv_path)
    if year != 2000:  # 保留2000年样本（已下载）
        os.unlink(zip_path)

    log(f"  ✓ {year}年: {cnt} 行, 总耗时 {time.time()-t0:.0f}s")
    return cnt


def atomic_replace():
    """原子表替换"""
    sqls = [
        "DROP TABLE IF EXISTS c1_market.kline_5min_old",
        "RENAME TABLE c1_market.kline_5min TO c1_market.kline_5min_old, "
        "c1_market.kline_5min_bdpan_new TO c1_market.kline_5min",
    ]
    for sql in sqls:
        r = subprocess.run(["wsl", "-d", "Ubuntu", "-e", "clickhouse-client", "--query", sql],
                           capture_output=True, timeout=60)
        if r.returncode != 0:
            log(f"  RENAME失败: {r.stderr.decode('utf-8', errors='replace')[:200]}")
            return False
    return True


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "test"
    years = [2000] if mode == "test" else list(range(2000, 2027))

    os.makedirs(DLDIR, exist_ok=True)

    log("=== 5分钟K线导入 ===")
    log("1. 创建_new表...")
    if not create_new_table():
        log("创建失败!")
        return

    log("2. 逐年处理...")
    total = 0
    for year in years:
        cnt = process_year(year)
        total += cnt
        log(f"  累计: {total} 行")

    log(f"\n3. 总计导入: {total} 行")

    # 4. 验证（导入前）
    r = subprocess.run(["wsl", "-d", "Ubuntu", "-e", "clickhouse-client",
                        "--query", "SELECT count(), min(trade_time), max(trade_time), "
                                   "uniq(symbol) FROM c1_market.kline_5min_bdpan_new FORMAT TabSeparated"],
                       capture_output=True, timeout=60)
    log(f"  新表验证: {r.stdout.decode('utf-8').strip()}")

    # 5. 原子替换（仅 all 模式）
    if mode == "all":
        log("4. 原子表替换...")
        if atomic_replace():
            log("  ✓ 替换成功")
            r = subprocess.run(["wsl", "-d", "Ubuntu", "-e", "clickhouse-client",
                                "--query", "SELECT count(), min(trade_time), max(trade_time), "
                                           "uniq(symbol) FROM c1_market.kline_5min FORMAT TabSeparated"],
                               capture_output=True, timeout=60)
            log(f"  最终验证: {r.stdout.decode('utf-8').strip()}")
        else:
            log("  ✗ 替换失败")


if __name__ == "__main__":
    main()
