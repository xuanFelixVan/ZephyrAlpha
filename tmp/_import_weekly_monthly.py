"""导入weekly/monthly K线到ClickHouse（原子表替换策略）。

策略：
1. 创建新表 _bdpan_new
2. 从zip读取所有CSV → 转TSV → 通过clickhouse-client导入新表
3. DROP旧备份表_old → RENAME替换

用法: python _import_weekly_monthly.py [weekly|monthly|both]
"""
import zipfile
import csv
import io
import os
import sys
import subprocess
import time
import logging

KLINE_DIR = r"d:\ZephyrAlpha\data\raw\bdpan\kline"

logging.basicConfig(level=logging.INFO, format="%(message)s",
                    handlers=[logging.StreamHandler(sys.stdout)])
log = logging.info


def create_new_table(table):
    """创建_new表（结构与原表相同）"""
    sql = f"DROP TABLE IF EXISTS c1_market.{table}_bdpan_new"
    subprocess.run(["wsl", "-d", "Ubuntu", "-e", "clickhouse-client", "--query", sql],
                   capture_output=True, timeout=30)
    sql = f"CREATE TABLE c1_market.{table}_bdpan_new AS c1_market.{table}"
    r = subprocess.run(["wsl", "-d", "Ubuntu", "-e", "clickhouse-client", "--query", sql],
                       capture_output=True, timeout=30)
    if r.returncode != 0:
        log(f"  创建新表失败: {r.stderr.decode('utf-8', errors='replace')[:200]}")
        return False
    return True


def zip_to_tsv(zip_path, tsv_path):
    """从zip读取所有CSV → 写TSV，返回行数"""
    total = 0
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = [n for n in zf.namelist() if n.endswith(".csv")]
        log(f"  {len(names)} 个CSV文件")
        with open(tsv_path, "w", encoding="utf-8", newline="\n") as out:
            for idx, name in enumerate(names, 1):
                content = zf.read(name)
                reader = csv.reader(io.TextIOWrapper(io.BytesIO(content), encoding="utf-8"))
                next(reader)  # skip header
                for row in reader:
                    if not row or len(row) < 12:
                        continue
                    # 12列: 日期,股票代码,开盘,收盘,最高,最低,成交量,成交额,振幅,涨跌幅,涨跌额,换手率
                    parts = []
                    for i, val in enumerate(row[:12]):
                        v = val.strip()
                        # 空值处理
                        if i in (6,):  # volume → 0
                            parts.append(v if v else "0")
                        elif i in (3, 4, 5, 6, 7, 8, 9, 10, 11):  # 数值列 → 0
                            parts.append(v if v else "0")
                        else:
                            parts.append(v)
                    parts.append("bdpan_qfq")  # data_source
                    out.write("\t".join(parts))
                    out.write("\n")
                    total += 1
                if idx % 1000 == 0:
                    log(f"  [{idx}/{len(names)}] 累计 {total} 行")
    return total


def import_tsv(tsv_path, table):
    """用clickhouse-client导入TSV到_new表（分批导入避免内存问题）"""
    sz = os.path.getsize(tsv_path) / 1024 / 1024
    log(f"  TSV大小: {sz:.1f}MB, 导入中...")
    with open(tsv_path, "rb") as f:
        data = f.read()
    cmd = ["wsl", "-d", "Ubuntu", "-e", "clickhouse-client",
           "--query", f"INSERT INTO c1_market.{table}_bdpan_new FORMAT TSV",
           "--max_partitions_per_insert_block", "0"]
    r = subprocess.run(cmd, input=data, capture_output=True, timeout=300)
    if r.returncode != 0:
        log(f"  导入失败: {r.stderr.decode('utf-8', errors='replace')[:300]}")
        return False
    return True


def atomic_replace(table):
    """原子表替换: DROP _old → RENAME _bdpan_new → _old"""
    sqls = [
        f"DROP TABLE IF EXISTS c1_market.{table}_old",
        f"RENAME TABLE c1_market.{table} TO c1_market.{table}_old, "
        f"c1_market.{table}_bdpan_new TO c1_market.{table}",
    ]
    for sql in sqls:
        r = subprocess.run(["wsl", "-d", "Ubuntu", "-e", "clickhouse-client", "--query", sql],
                           capture_output=True, timeout=30)
        if r.returncode != 0:
            log(f"  RENAME失败: {r.stderr.decode('utf-8', errors='replace')[:200]}")
            return False
    return True


def verify_count(table):
    """验证行数"""
    r = subprocess.run(["wsl", "-d", "Ubuntu", "-e", "clickhouse-client",
                        "--query", f"SELECT count(), min(trade_date), max(trade_date), "
                                   f"uniq(symbol) FROM c1_market.{table} FORMAT TabSeparated"],
                       capture_output=True, timeout=30)
    return r.stdout.decode("utf-8").strip()


def process(zip_file, table, tsv_file):
    """处理单个K线类型"""
    zip_path = os.path.join(KLINE_DIR, zip_file)
    tsv_path = os.path.join(KLINE_DIR, tsv_file)

    log(f"\n{'='*60}")
    log(f"处理 {table} ({zip_file})")
    log(f"{'='*60}")

    # 1. 创建新表
    log("1. 创建_new表...")
    if not create_new_table(table):
        return False

    # 2. zip → TSV
    log("2. 读取zip → TSV...")
    t0 = time.time()
    cnt = zip_to_tsv(zip_path, tsv_path)
    log(f"  {cnt} 行, {time.time()-t0:.0f}s")

    # 3. 导入ClickHouse
    log("3. 导入ClickHouse...")
    t0 = time.time()
    if not import_tsv(tsv_path, table):
        return False
    log(f"  导入完成, {time.time()-t0:.0f}s")

    # 4. 原子替换
    log("4. 原子表替换...")
    if not atomic_replace(table):
        return False

    # 5. 验证
    log("5. 验证...")
    result = verify_count(table)
    log(f"  {table}: {result}")

    # 6. 清理TSV
    os.unlink(tsv_path)
    log(f"  ✓ {table} 完成")

    return True


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "both"

    if mode in ("weekly", "both"):
        process("weekly_qfq.zip", "kline_weekly", "weekly.tsv")

    if mode in ("monthly", "both"):
        process("monthly_qfq.zip", "kline_monthly", "monthly.tsv")

    log("\n=== 完成 ===")


if __name__ == "__main__":
    main()
