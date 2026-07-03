"""导入分笔成交Tick数据到ClickHouse c1_market.tick_history（按月处理）。

策略（参照download_plan_20260704.md §1.5）：
1. bdpan ls 列出月份目录内所有日zip
2. 逐日下载zip → 解压合并TSV（添加symbol/market_type列）
3. clickhouse-client 导入TSV → 删除本地zip和TSV
4. 验证行数 → 检查D盘空间（<50GB暂停）
5. 正常顺序下载（从最早到最新），空间不足时停止

字段映射（CSV → tick_history）：
  时间(2026-07-01 09:15:00) → trade_date + timestamp
  成交价(10.05)             → price
  手数(5)                   → volume (×100)
  (计算)                    → amount (= price × volume)
  买卖方向                  → direction (空值填"中性盘")
  文件名(000001.csv)        → symbol (去.csv)
  (按数据来源)              → market_type
  (固定)                    → data_source='bdpan'

用法:
  python _import_tick.py <market_type> [start_ym] [end_ym]
  market_type ∈ stock|stock_bj|index|hk|etf|lof|cb|sector|mkt_index
  start_ym/end_ym 格式 YYYY-MM，默认覆盖该类数据的完整范围

示例:
  python _import_tick.py etf                    # 下载ETF全量(2005-02~2026-07)
  python _import_tick.py stock 2000-06 2010-12  # 沪深A股 2000-06~2010-12
"""
import csv
import io
import logging
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile
from typing import List, Optional, Tuple

# ===== 配置 =====
DLDIR = r"d:\ZephyrAlpha\data\raw\bdpan\tick"
BDPAN = "/root/.local/bin/bdpan"
CLICKHOUSE = ["wsl", "-d", "Ubuntu", "-e", "clickhouse-client"]
TABLE = "c1_market.tick_history"
PAUSE_THRESHOLD_GB = 50  # D盘剩余<50GB暂停

# market_type → (网盘路径, 默认起始月份, 默认结束月份)
# 起止月份来自 tmp/tick_download_ranges.txt 探查结果
MARKET_CONFIG = {
    "stock":      ("量化交易数据/A股数据_分笔数据/分笔成交_按月归档_沪深/",                    "2000-06", "2026-07"),
    "stock_bj":   ("量化交易数据/A股数据_分笔数据/分笔成交_按月归档_京市/",                    "2020-07", "2026-07"),
    "index":      ("量化交易数据/A股数据_分笔成交_指数/指数分笔成交_沪深京_按月归档/",         "2000-07", "2026-07"),
    "hk":         ("量化交易数据/港股_分笔成交/港股_分笔成交_按月归档/",                      "2025-01", "2026-07"),
    "etf":        ("量化交易数据/基金_分笔成交/ETF分笔成交_按月归档/",                        "2005-02", "2026-07"),
    "lof":        ("量化交易数据/基金_分笔成交/LOF分笔成交_按月归档/",                        "2008-06", "2026-07"),
    "cb":         ("量化交易数据/可转债_分笔成交/可转债_分笔成交_按月归档/",                  "2018-09", "2026-07"),
    "sector":     ("量化交易数据/通达信板块_分笔成交/通达信板块_分笔成交_按月归档/",          "2011-11", "2026-07"),
    "mkt_index":  ("量化交易数据/通达信板块_分笔成交/通达信_市场统计指数_分笔成交_按月归档/", "2011-11", "2026-07"),
}

logging.basicConfig(level=logging.INFO, format="%(message)s",
                    handlers=[logging.StreamHandler(sys.stdout)])
log = logging.info


# ===== 工具函数 =====
def wsl_path(win_path: str) -> str:
    """d:\\foo\\bar → /mnt/d/foo/bar"""
    p = win_path.replace("\\", "/")
    if len(p) >= 2 and p[1] == ":":
        return f"/mnt/{p[0].lower()}{p[2:]}"
    return p


def get_d_free_gb() -> float:
    """获取D盘可用空间(GB)"""
    usage = shutil.disk_usage("d:\\")
    return usage.free / 1024 ** 3


def parse_ym(ym: str) -> Tuple[int, int]:
    """'2000-06' → (2000, 6)"""
    m = re.match(r"^(\d{4})-(\d{2})$", ym)
    if not m:
        raise ValueError(f"非法月份格式: {ym} (应为 YYYY-MM)")
    return int(m.group(1)), int(m.group(2))


def ym_to_int(ym: str) -> int:
    y, m = parse_ym(ym)
    return y * 100 + m


def int_to_ym(n: int) -> str:
    return f"{n // 100:04d}-{n % 100:02d}"


def next_ym(ym: str) -> str:
    y, m = parse_ym(ym)
    if m == 12:
        return f"{y + 1:04d}-01"
    return f"{y:04d}-{m + 1:02d}"


def gen_ym_range(start: str, end: str) -> List[str]:
    """生成 start~end 的连续月份列表（含两端）"""
    out = []
    cur = start
    # 安全上限1000个月防死循环
    for _ in range(1000):
        out.append(cur)
        if cur == end:
            break
        cur = next_ym(cur)
    return out


# ===== bdpan 操作 =====
def bdpan_ls_months(bdpan_dir: str) -> List[str]:
    """bdpan ls 月份目录，返回 YYYY-MM 列表（按字母升序）"""
    r = subprocess.run(["wsl", "-d", "Ubuntu", "-e", "bash", "-c",
                        f'{BDPAN} ls "{bdpan_dir}"'],
                       capture_output=True, timeout=120)
    if r.returncode != 0:
        log(f"  bdpan ls 失败: {r.stderr.decode('utf-8', errors='replace')[:200]}")
        return []
    out = r.stdout.decode("utf-8", errors="replace")
    months = re.findall(r"\b(\d{4}-\d{2})\b", out)
    # 去重保序
    seen = set()
    uniq = []
    for m in months:
        if m not in seen:
            seen.add(m)
            uniq.append(m)
    return sorted(uniq)


def bdpan_ls_day_zips(bdpan_month_dir: str) -> List[str]:
    """列出某月份目录下的所有日zip文件名（不含路径）。

    文件名格式为 YYYYMMDD.zip（如 20260702.zip，无短横线）。
    """
    r = subprocess.run(["wsl", "-d", "Ubuntu", "-e", "bash", "-c",
                        f'{BDPAN} ls "{bdpan_month_dir}"'],
                       capture_output=True, timeout=120)
    if r.returncode != 0:
        return []
    out = r.stdout.decode("utf-8", errors="replace")
    # 文件名形如 20260702.zip
    return sorted(set(re.findall(r"(\d{8}\.zip)", out)))


def bdpan_download(remote_path: str, local_path: str, timeout: int = 1800) -> bool:
    """下载单个文件"""
    r = subprocess.run(["wsl", "-d", "Ubuntu", "-e", "bash", "-c",
                        f'{BDPAN} download "{remote_path}" "{wsl_path(local_path)}"'],
                       capture_output=True, timeout=timeout)
    return r.returncode == 0 and os.path.exists(local_path)


# ===== TSV 转换 =====
# 9类市场分3种格式（实测2026-07-04）：
#   A股股票(stock/stock_bj): 时间,成交价,手数,买卖方向  → 手数×100=volume，时间用-
#   基金/转债(etf/lof/cb):   时间,成交价,成交量,买卖方向 → 成交量已是股数，时间用/
#   港股(hk):                时间,价格,现量,买卖方向     → 现量已是股数，时间用/且无秒
#   指数/板块(index/sector/mkt_index): 时间,价位,成交额  → volume=0, amount=成交额, 无方向


def normalize_timestamp(ts: str) -> str:
    """时间标准化：'/' → '-'；无秒补 ':00。

    输入可能格式：
      2000-06-09 09:30:00 (标准)
      2005/02/23 09:30:00 (斜杠)
      2025/01/02 09:20    (无秒)
    """
    ts = ts.strip().replace("/", "-")
    # 长度16 = YYYY-MM-DD HH:MM，补秒
    if len(ts) == 16:
        ts += ":00"
    return ts


def parse_row_by_header(row: list, header_field3: str, market_type: str, symbol: str) -> Optional[str]:
    """根据表头第3字段名解析行，返回TSV行字符串（含换行符）或None。

    TSV输出列: trade_date timestamp symbol market_type price volume amount direction data_source
    """
    if len(row) < 3:
        return None
    ts = normalize_timestamp(row[0])
    if len(ts) < 19:
        return None
    trade_date = ts[:10]

    price_s = row[1].strip()
    field3_val = row[2].strip()
    if not price_s or not field3_val:
        return None
    try:
        price = float(price_s)
    except ValueError:
        return None

    # 去BOM
    f3 = header_field3.strip().lstrip("\ufeff")

    if f3 == "手数":
        # A股股票：手数×100
        try:
            hands = float(field3_val)
        except ValueError:
            return None
        volume = int(hands * 100)
        amount = round(price * volume, 2)
        direction = row[3].strip() if len(row) >= 4 else ""
    elif f3 in ("成交量", "现量"):
        # 基金/港股：已是股数
        try:
            volume = int(float(field3_val))
        except ValueError:
            return None
        amount = round(price * volume, 2)
        direction = row[3].strip() if len(row) >= 4 else ""
    elif f3 == "成交额":
        # 指数/板块：第3字段=成交额，无volume/方向
        try:
            amount = float(field3_val)
        except ValueError:
            return None
        volume = 0
        direction = ""
    else:
        return None

    if not direction:
        direction = "中性盘"

    return (f"{trade_date}\t{ts}\t{symbol}\t{market_type}\t"
            f"{price:.4f}\t{volume}\t{amount:.2f}\t{direction}\tbdpan\n")


def zip_to_tsv_append(zip_path: str, tsv_path: str, market_type: str) -> int:
    """解压日zip → 追加到月份TSV，返回行数。

    自动识别表头第3字段（手数/成交量/现量/成交额）选择对应转换逻辑。
    """
    rows = 0
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        with open(tsv_path, "a", encoding="utf-8", newline="\n") as out:
            for name in names:
                base = os.path.basename(name)
                symbol = base[:-4] if base.lower().endswith(".csv") else base
                # 过滤异常文件名（如 macOS 的 __MACOSX 目录）
                if not symbol or symbol.startswith(".") or "__" in name:
                    continue
                try:
                    content = zf.read(name)
                except Exception:
                    continue
                reader = csv.reader(io.TextIOWrapper(io.BytesIO(content), encoding="utf-8"))
                try:
                    header = next(reader)
                except StopIteration:
                    continue
                # 表头第3字段名决定转换逻辑
                field3 = header[2] if len(header) >= 3 else ""
                for row in reader:
                    tsv_line = parse_row_by_header(row, field3, market_type, symbol)
                    if tsv_line:
                        out.write(tsv_line)
                        rows += 1
    return rows


# ===== ClickHouse 导入 =====
def import_tsv(tsv_path: str) -> bool:
    """导入TSV到tick_history表"""
    sz_mb = os.path.getsize(tsv_path) / 1024 / 1024
    log(f"  TSV: {sz_mb:.0f}MB, 导入中...")
    with open(tsv_path, "rb") as f:
        data = f.read()
    cmd = CLICKHOUSE + [
        "--query", f"INSERT INTO {TABLE} FORMAT TSV",
        "--max_partitions_per_insert_block", "0",
    ]
    r = subprocess.run(cmd, input=data, capture_output=True, timeout=3600)
    if r.returncode != 0:
        log(f"  导入失败: {r.stderr.decode('utf-8', errors='replace')[:300]}")
        return False
    return True


def query_ch(sql: str, timeout: int = 120) -> str:
    r = subprocess.run(CLICKHOUSE + ["--query", sql],
                       capture_output=True, timeout=timeout)
    return r.stdout.decode("utf-8", errors="replace").strip()


def count_month_rows(market_type: str, year_month: str) -> int:
    """统计指定市场+月份在表中的行数"""
    y, m = parse_ym(year_month)
    sql = (f"SELECT count() FROM {TABLE} WHERE market_type='{market_type}' "
           f"AND toYYYYMM(trade_date)={y * 100 + m} FORMAT TabSeparated")
    out = query_ch(sql)
    try:
        return int(out)
    except ValueError:
        return -1


# ===== 单月处理 =====
def process_month(year_month: str, market_type: str, bdpan_base: str) -> Tuple[int, bool]:
    """处理单个月份，返回 (导入行数, 是否暂停)"""
    log(f"\n--- {market_type} / {year_month} ---")
    t0 = time.time()

    # 0. 空间检查
    free_gb = get_d_free_gb()
    if free_gb < PAUSE_THRESHOLD_GB:
        log(f"  ⚠ D盘剩余 {free_gb:.1f}GB < {PAUSE_THRESHOLD_GB}GB，暂停下载")
        return 0, True

    # 1. 列出日zip
    month_remote = f"{bdpan_base}{year_month}/"
    day_zips = bdpan_ls_day_zips(month_remote)
    if not day_zips:
        log(f"  月份目录无zip: {month_remote}")
        return 0, False
    log(f"  {len(day_zips)} 个日zip")

    month_local_dir = os.path.join(DLDIR, market_type, year_month)
    os.makedirs(month_local_dir, exist_ok=True)

    month_tsv = os.path.join(month_local_dir, f"{year_month}.tsv")
    # 先清空月份合并TSV
    if os.path.exists(month_tsv):
        os.unlink(month_tsv)

    total_rows = 0
    # 2. 逐日下载→解压→合并TSV
    for idx, dz in enumerate(day_zips, 1):
        remote = f"{month_remote}{dz}"
        local_zip = os.path.join(month_local_dir, dz)
        if not bdpan_download(remote, local_zip):
            log(f"  [{idx}/{len(day_zips)}] 下载失败: {dz}")
            continue
        # 追加模式写入月份TSV
        rows = zip_to_tsv_append(local_zip, month_tsv, market_type)
        total_rows += rows
        # 删除日zip释放空间
        try:
            os.unlink(local_zip)
        except OSError:
            pass
        if idx % 5 == 0 or idx == len(day_zips):
            log(f"  [{idx}/{len(day_zips)}] 累计 {total_rows} 行, D盘剩余 {get_d_free_gb():.1f}GB")

    if total_rows == 0:
        log(f"  月份无有效数据，跳过导入")
        return 0, False

    # 3. 导入ClickHouse
    t1 = time.time()
    if not import_tsv(month_tsv):
        log(f"  导入失败，保留TSV供排查: {month_tsv}")
        return 0, False
    log(f"  导入完成, {time.time() - t1:.0f}s")

    # 4. 删除本地TSV
    try:
        os.unlink(month_tsv)
    except OSError:
        pass

    # 5. 验证行数
    ch_rows = count_month_rows(market_type, year_month)
    if ch_rows >= 0 and ch_rows != total_rows:
        log(f"  ⚠ 行数不一致: TSV={total_rows}, CH={ch_rows}")
    else:
        log(f"  ✓ 行数一致: {ch_rows}")

    log(f"  ✓ {year_month}: {total_rows} 行, 总耗时 {time.time() - t0:.0f}s, "
        f"D盘剩余 {get_d_free_gb():.1f}GB")
    return total_rows, False


# ===== 主流程 =====
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    market_type = sys.argv[1]
    if market_type not in MARKET_CONFIG:
        print(f"错误: 未知 market_type '{market_type}'，可选: {list(MARKET_CONFIG.keys())}")
        sys.exit(1)

    bdpan_base, default_start, default_end = MARKET_CONFIG[market_type]
    start_ym = sys.argv[2] if len(sys.argv) > 2 else default_start
    end_ym = sys.argv[3] if len(sys.argv) > 3 else default_end

    # 用 bdpan ls 实际查得的月份列表作为下载顺序（避免生成不存在的月份）
    log(f"=== {market_type} 分笔成交导入 ===")
    log(f"配置: {start_ym} ~ {end_ym}")
    log(f"网盘路径: {bdpan_base}")

    log("探查网盘实际月份目录...")
    actual_months = bdpan_ls_months(bdpan_base)
    if not actual_months:
        log("网盘无任何月份目录，退出")
        return

    # 过滤出 [start, end] 范围内的月份
    si, ei = ym_to_int(start_ym), ym_to_int(end_ym)
    months = [m for m in actual_months if si <= ym_to_int(m) <= ei]
    log(f"实际待下载月份: {len(months)} 个 (网盘共 {len(actual_months)} 个)")
    if months:
        log(f"  范围: {months[0]} ~ {months[-1]}")

    os.makedirs(DLDIR, exist_ok=True)

    total_rows = 0
    paused = False
    for idx, ym in enumerate(months, 1):
        log(f"\n[{idx}/{len(months)}] 处理 {ym}")
        rows, pause = process_month(ym, market_type, bdpan_base)
        total_rows += rows
        log(f"  累计: {total_rows} 行")
        if pause:
            paused = True
            log(f"  ⛔ 因D盘空间不足暂停，已完成 {idx}/{len(months)} 个月份")
            break

    log(f"\n=== {market_type} 完成 ===")
    log(f"导入月份: {len(months) if not paused else idx} / {len(months)}")
    log(f"导入行数: {total_rows}")

    # 最终验证
    sql = (f"SELECT count(), uniq(symbol), min(trade_date), max(trade_date) "
           f"FROM {TABLE} WHERE market_type='{market_type}' FORMAT TabSeparated")
    log(f"CH表验证: {query_ch(sql)}")


if __name__ == "__main__":
    main()
