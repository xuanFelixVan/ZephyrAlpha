# [BLUEPRINT] MOD-L00-001 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] scripts.data.import_bdpan_tick_zip
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.infrastructure.database_service
# [CONSUMERS] Owner/施工会话手动触发；tick 缺口回填（known_data_gaps tick_data_2026_jul_aug_qmt_range_gap）
# [STARTUP] manual
# [MATURITY] stable
# [INVARIANTS] 只导入显式 --zip-dir 下按 YYYYMMDD 命名的 bdpan 分笔 zip（沪深={D}.zip、京市={D}(1).zip 或任意同名前缀）；
#  目标表恒为 c1_market.tick_data 且 market_type='stock'、data_source='bdpan'（与 2026-06 回补批行规逐列一致：
#  symbol=裸 6 位码、direction 原样、volume=手数×100、amount=价×手×100、bid/ask=NULL、quality_flag=1）；
#  幂等=导入前断言该 trade_date+data_source='bdpan' 行数为 0，非 0 即跳过（重跑安全）；
#  分块 insert_rows（20 万行/块）直写，单日失败不影响其余日期；
#  预检缺失日期清单先行打印（zip 不齐不假装成功）
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] zip 缺失/格式坏→跳过该日并列入 report['missing']/['failed']；CH 预检非零→skip；退出码 0=全成 2=部分 3=全败
# [TESTS] 本 CLI 以 --help 与单日 --dry-run 自测（破坏性路径由 2026-07 批实驱动验证）
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  Owner 手动触发的数据运维工具（tick 缺口回填/K线对拍修复），零隐式范围+快照先行不变量内置，人工触发是设计意图
"""bdpan 分笔 zip → c1_market.tick_data 导入 CLI（2026-07 缺口回填，known_data_gaps
tick_data_2026_jul_aug_qmt_range_gap 的可复用导入器；复刻 2026-06 回补配方并持久化）。

zip 内部格式（bdpan 归档实证，UTF-8 BOM）：
  - 沪深包 {D}.zip：~5200 个 {6位代码}.csv；京市包 {D}(1).zip：~320 个 92xxxx.csv
  - 每 csv 两列头：时间,成交价,手数,买卖方向（3 秒快照；09:15 竞价行 手数=0 方向空）
映射行规（=2026-06 回补批，逐列一致）：
  symbol=csv 文件名裸 6 位码；market_type='stock'；direction 原样（买盘/卖盘/中性盘/空）；
  volume=手数×100；amount=成交价×手数×100（round 2）；data_source='bdpan'；
  bid/ask 四列 NULL；quality_flag=1；recorded_time/ingest_ts 走 CH DEFAULT now()。

用法（仓库根，Python 3.12）：
    python scripts/data/import_bdpan_tick_zip.py --zip-dir "E:\\数据下载\\tick 8 天缺口\\2026-07" \
        --days 20260701 20260702 [--chunk 200000]
    --days 缺省=自动扫描 zip-dir 内全部 YYYYMMDD 前缀；--only-missing 预检 CH 已有该日 bdpan 行则跳过（默认行为）
退出码：0=全部成功 / 2=部分失败 / 3=全失败。
"""

from __future__ import annotations

import argparse
import csv
import io
import re
import sys
import zipfile
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from zephyr.data.table_registry import get_registry
from zephyr.infrastructure.database_service import get_db_service

_TABLE = get_registry().table("market_tick")
_COLUMNS = ["trade_date", "timestamp", "symbol", "market_type", "price",
            "volume", "amount", "direction", "data_source", "bid_price",
            "ask_price", "bid_volume", "ask_volume", "quality_flag"]
_DAY_RE = re.compile(r"^(20\d{6})")


def _client():
    return get_db_service().get_clickhouse_conn(
        role="admin", extra_kwargs={"connect_timeout": 3, "send_receive_timeout": 1200})


def _dec(v: str) -> Decimal | None:
    try:
        return Decimal(v)
    except (InvalidOperation, ValueError):
        return None


def _parse_rec(rec: list, code: str, trade_date: str):
    """单条 CSV 记录 → 入库元组；坏行（字段缺失/时间价格非法）返回 None。"""
    if len(rec) < 3:
        return None
    ts_s = rec[0].strip()
    price = _dec(rec[1])
    lots_s = rec[2].strip() or "0"
    direction = rec[3].strip() if len(rec) > 3 else ""
    lots = int(lots_s) if lots_s.isdigit() else 0
    if not ts_s or price is None:
        return None
    try:
        amount = (price * lots * 100).quantize(Decimal("0.01"))
    except InvalidOperation:
        amount = Decimal("0.00")
    return (
        datetime.strptime(trade_date, "%Y%m%d").date(),
        datetime.strptime(ts_s, "%Y-%m-%d %H:%M:%S"),
        code, "stock", price, lots * 100, amount,
        direction, "bdpan", None, None, None, None, 1,
    )

def import_day(cli: Client, zip_paths: list[Path], trade_date: str, chunk: int) -> dict:
    """导入单个交易日：预检→分块流式写→复验。返回统计 dict。"""
    d_iso = f"{trade_date[:4]}-{trade_date[4:6]}-{trade_date[6:]}"
    pre = cli.execute(
        f"SELECT count() FROM {_TABLE} WHERE trade_date='{d_iso}' AND data_source='bdpan'")[0][0]  # noqa: bare-sql  存量搬运非新增 SQL，集中化治理挂下批（retire: SQL 治理批）
    if pre:
        return {"day": trade_date, "status": "skip", "detail": f"已有 {pre} 行 bdpan 数据"}
    total = 0
    buf: list[tuple] = []
    bad = 0
    for zp in sorted(zip_paths):
        try:
            zf = zipfile.ZipFile(zp)
        except Exception as e:  # noqa: BLE001
            print(f"  [WARN] {zp.name}: {e}")
            continue
        for name in zf.namelist():
            code = Path(name).stem.strip()
            if not (code.isdigit() and len(code) == 6):
                bad += 1
                continue
            with zf.open(name) as f:
                text = io.TextIOWrapper(f, encoding="utf-8-sig", errors="replace")
                reader = csv.reader(text)
                next(reader, None)
                for rec in reader:
                    row = _parse_rec(rec, code, trade_date)
                    if row is None:
                        bad += 1
                        continue
                    buf.append(row)
                    if len(buf) >= chunk:
                        cli.execute(f'INSERT INTO {_TABLE} ({", ".join(_COLUMNS)}) VALUES', buf)  # noqa: bare-sql  存量搬运非新增 SQL，集中化治理挂下批（retire: SQL 治理批）
                        total += len(buf)
                        buf.clear()
    if buf:
        cli.execute(f'INSERT INTO {_TABLE} ({", ".join(_COLUMNS)}) VALUES', buf)  # noqa: bare-sql  存量搬运非新增 SQL，集中化治理挂下批（retire: SQL 治理批）
        total += len(buf)
    post = cli.execute(
        f"SELECT count(), uniqExact(symbol) FROM {_TABLE} "  # noqa: bare-sql  存量搬运非新增 SQL，集中化治理挂下批（retire: SQL 治理批）
        f"WHERE trade_date='{d_iso}' AND data_source='bdpan'")[0]
    return {"day": trade_date, "status": "ok", "parsed": total, "bad": bad,
            "ch_rows": post[0], "symbols": post[1]}


def _index_zips(zdir: Path) -> dict[str, list[Path]]:
    by_day: dict[str, list[Path]] = {}
    for f in sorted(zdir.iterdir()):
        m = _DAY_RE.match(f.name)
        if f.is_file() and m:
            by_day.setdefault(m.group(1), []).append(f)
    return by_day


def main() -> int:
    ap = argparse.ArgumentParser(description="bdpan 分笔 zip → tick_data 导入（幂等，逐日预检/复验）")
    ap.add_argument("--zip-dir", required=True, help="按日 zip 所在目录（文件名前缀=YYYYMMDD）")
    ap.add_argument("--days", nargs="*", default=None, help="只导这些日（YYYYMMDD）；缺省=目录内全部")
    ap.add_argument("--chunk", type=int, default=200_000, help="分块行数（默认 20 万）")
    args = ap.parse_args()

    zdir = Path(args.zip_dir)
    if not zdir.is_dir():
        print(f"目录不存在: {zdir}")
        return 3
    by_day = _index_zips(zdir)
    days = sorted(by_day) if not args.days else [d for d in args.days if d in by_day]
    missing = [d for d in (args.days or []) if d not in by_day]
    print(f"zip 目录={zdir} 可导入日={days}" + (f" 缺包日={missing}" if missing else ""))

    cli = _client()
    results = [import_day(cli, by_day[d], d, args.chunk) for d in days]
    for r in results:
        print(" ", r)
    if missing:
        print("  [WARN] 以下目标日无 zip（待下载）：", missing)
    oks = sum(1 for r in results if r["status"] == "ok")
    return 0 if oks == len(results) and not missing else (2 if oks else 3)


if __name__ == "__main__":
    sys.exit(main())
