"""导入日K线（前复权）到 c1_market.kline_daily。

daily_qfq.zip 内含5895个CSV（每股票1个）
CSV列: 日期,股票代码,开盘,收盘,最高,最低,成交量,成交额,振幅,涨跌幅,涨跌额,换手率
TSV列: trade_date,symbol,open,close,high,low,volume,amount,amplitude,pct_change,change,turnover,data_source
"""
import zipfile
import csv
import io
import os
import subprocess
import time
import logging
import sys

DLDIR = r"d:\ZephyrAlpha\data\raw\bdpan\daily"
ZIP_PATH = os.path.join(DLDIR, "daily_qfq.zip")
TSV_PATH = os.path.join(DLDIR, "daily_qfq.tsv")

logging.basicConfig(level=logging.INFO, format="%(message)s",
                    handlers=[logging.StreamHandler(sys.stdout)])
log = logging.info


def zip_to_tsv():
    """从zip读取所有CSV → 写TSV，返回行数"""
    total = 0
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        names = [n for n in zf.namelist() if n.endswith(".csv")]
        log(f"  CSV文件数: {len(names)}")
        with open(TSV_PATH, "w", encoding="utf-8", newline="\n") as out:
            for idx, name in enumerate(names, 1):
                content = zf.read(name)
                reader = csv.reader(io.TextIOWrapper(io.BytesIO(content), encoding="utf-8-sig"))
                try:
                    next(reader)  # skip header
                except StopIteration:
                    continue
                for row in reader:
                    if not row or len(row) < 8:
                        continue
                    try:
                        trade_date = row[0].strip()
                        symbol = row[1].strip()
                        open_p = row[2].strip() or "0"
                        close_p = row[3].strip() or "0"
                        high_p = row[4].strip() or "0"
                        low_p = row[5].strip() or "0"
                        volume = row[6].strip() or "0"
                        amount = row[7].strip() or "0"
                        amplitude = row[8].strip() if len(row) > 8 else "0"
                        pct_change = row[9].strip() if len(row) > 9 else "0"
                        change = row[10].strip() if len(row) > 10 else "0"
                        turnover = row[11].strip() if len(row) > 11 else "0"
                        out.write(f"{trade_date}\t{symbol}\t{open_p}\t{close_p}\t{high_p}\t{low_p}\t{volume}\t{amount}\t{amplitude}\t{pct_change}\t{change}\t{turnover}\tbdpan_qfq\n")
                        total += 1
                    except (IndexError, ValueError):
                        continue
                if idx % 500 == 0:
                    log(f"    [{idx}/{len(names)}] 累计 {total} 行")
    return total


def import_tsv():
    sz = os.path.getsize(TSV_PATH) / 1024 / 1024
    log(f"  TSV: {sz:.0f}MB, 导入中...")
    with open(TSV_PATH, "rb") as f:
        data = f.read()
    cmd = ["wsl", "-d", "Ubuntu", "-e", "clickhouse-client",
           "--query", "INSERT INTO c1_market.kline_daily FORMAT TSV",
           "--max_partitions_per_insert_block", "0"]
    r = subprocess.run(cmd, input=data, capture_output=True, timeout=600)
    if r.returncode != 0:
        log(f"  导入失败: {r.stderr.decode('utf-8', errors='replace')[:300]}")
        return False
    return True


def main():
    log("=== 日K线导入（daily_qfq）===")
    t0 = time.time()
    log("1. 转换zip → TSV...")
    cnt = zip_to_tsv()
    log(f"  {cnt} 行, {time.time()-t0:.0f}s")

    t1 = time.time()
    log("2. 导入ClickHouse...")
    if not import_tsv():
        return
    log(f"  导入完成, {time.time()-t1:.0f}s")

    # 清理
    os.unlink(TSV_PATH)

    # 验证
    r = subprocess.run(["wsl", "-d", "Ubuntu", "-e", "clickhouse-client",
                        "--query", "SELECT count(), min(trade_date), max(trade_date), "
                                   "uniq(symbol) FROM c1_market.kline_daily FORMAT TabSeparated"],
                       capture_output=True, timeout=60)
    log(f"3. 验证: {r.stdout.decode('utf-8').strip()}")
    log(f"总耗时 {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
