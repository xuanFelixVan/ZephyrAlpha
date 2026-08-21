# -*- coding: utf-8 -*-
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §sector_kline
# [MODULE] zephyr.data.sector_kline_downloader
# [DOMAIN] D_DATA
# [DEPENDENCIES] clickhouse_driver; tqcenter (external E:\tdx\PYPlugins\user); pandas
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 盘后批量下载880xxx板块K线写入ClickHouse kline_sector_880表；支持1d/1m/5m三周期（15m/30m/60m后续从1m/5m合成）；50只/批分批下载避免tqcenter超时；ReplacingMergeTree幂等写入
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] tqcenter初始化失败->RuntimeError; 单批下载失败->log+继续(不中断); ClickHouse写入失败->log+继续
# [TESTS] tests/zephyr/data/test_sector_kline_downloader.py
# [TTL] task_bound
"""880xxx 板块指数K线下载器——盘后从 tqcenter 下载日K/分钟K写入 ClickHouse。

支持周期：1d（日K立即可用）/ 1m / 5m（需通达信客户端先下载扩展市场分钟线）。
15m/30m/60m 不被 tqcenter 直接支持，后续从 1m/5m 合成。

启动:
    python -m zephyr.data.sector_kline_downloader                  # 默认下载1d最近30天
    python -m zephyr.data.sector_kline_downloader --period 1d --days 30
    python -m zephyr.data.sector_kline_downloader --period 1m --days 1
    python -m zephyr.data.sector_kline_downloader --period all      # 全周期
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from zephyr.data.table_registry import get_registry
from zephyr.shared.security.secrets import SecretsError, get_secret_or_default, get_service_secret

log = logging.getLogger(__name__)

# 裁定 #ARCH-CH-024: 删除硬编码 IP/端口/库名（绕过 ch_config 真源治本）
# 连接配置由 ch_writer 内部从 ch_config.load_ch_config() 读取（config/.env.clickhouse 真源）
# Phase 5: 表名从 business_data_categories.yaml 真源派生（TableRegistry 消费层）
_CH_TABLE = get_registry().table("market_sector_kline_880")

# 通达信插件目录走配置真源（secret_registry.yaml: TDX_PLUGIN_DIR，env_file=.env）；未配置回退默认安装路径
try:
    _TQCENTER_PATH = get_service_secret("TDX_PLUGIN_DIR", "tqcenter", required=False) or r"E:\tdx\PYPlugins\user"
except SecretsError:
    # service "tqcenter" 未登记于 secrets._SERVICE_ENV_FILES 时，降级读 os.environ（根 .env 由 zephyr/__init__.py 自动加载）
    _TQCENTER_PATH = get_secret_or_default("TDX_PLUGIN_DIR", r"E:\tdx\PYPlugins\user")

_MKT_INDEX_CODES = [f"88000{i}.SH" for i in range(1, 10)]

_BATCH_SIZE = 50

_SUPPORTED_PERIODS = ["1d", "1m", "5m"]

_COLUMNS = [
    "period",
    "trade_date",
    "timestamp",
    "sector_code",
    "sector_name",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "amount",
    "forward_factor",
    "data_source",
]

# 裁定 #ARCH-CH-024: 删除手写 INSERT SQL，改用 ch_writer.write_result（含列过滤+二级降级）


def _init_tqcenter():
    """初始化 tqcenter 连接。"""
    if _TQCENTER_PATH not in sys.path:
        sys.path.insert(0, _TQCENTER_PATH)
    from tqcenter import tq  # noqa: import-integrity  external-module-tqcenter-not-pip-installed

    tq.initialize(str(Path(__file__).resolve()))
    return tq


def _get_sector_list(tq) -> list[str]:
    """获取全部880xxx板块代码（含mkt_index）。"""
    sectors = tq.get_sector_list() or []
    s880 = sorted([s for s in sectors if isinstance(s, str) and s.startswith("880")])
    for code in _MKT_INDEX_CODES:
        if code not in s880:
            s880.append(code)
    log.info("获取880xxx板块代码: %d 只", len(s880))
    return s880


def _safe_val(val, default):
    """安全提取数值，NaN/None→default。"""
    import math

    if val is None:
        return default
    if isinstance(val, float) and math.isnan(val):
        return default
    return val


def _ts_to_datetime(ts, period: str) -> tuple:
    """时间戳转 (trade_date, datetime)。"""
    import pandas as pd

    if isinstance(ts, pd.Timestamp):
        if period == "1d":
            d = ts.date()
            return d, datetime(d.year, d.month, d.day)
        dt = ts.to_pydatetime()
        return dt.date(), dt
    dt = datetime.strptime(str(ts)[:19], "%Y-%m-%d %H:%M:%S")
    return dt.date(), dt


def _extract_row(ts, code, period, trade_date, dt, dfs):
    """从 DataFrame 提取单行 K线数据。"""
    from decimal import Decimal

    open_df, high_df, low_df, close_df, vol_df, amt_df, ff_df = dfs
    o = open_df.loc[ts, code]
    if o is None:
        return None
    import math

    if isinstance(o, float) and math.isnan(o):
        return None
    o_val = Decimal(str(o))
    h_raw = high_df.loc[ts, code] if high_df is not None else o
    l_raw = low_df.loc[ts, code] if low_df is not None else o
    c_raw = close_df.loc[ts, code] if close_df is not None else o
    v_raw = vol_df.loc[ts, code] if vol_df is not None else 0
    a_raw = amt_df.loc[ts, code] if amt_df is not None else 0.0
    ff_raw = ff_df.loc[ts, code] if ff_df is not None else 1.0
    return (
        period,
        trade_date,
        dt,
        code,
        "",
        o_val,
        Decimal(str(_safe_val(h_raw, o))),
        Decimal(str(_safe_val(l_raw, o))),
        Decimal(str(_safe_val(c_raw, o))),
        int(_safe_val(v_raw, 0)),
        float(_safe_val(a_raw, 0.0)),
        float(_safe_val(ff_raw, 1.0)),
        "tqcenter",
    )


def _parse_kline_df(df: dict, sector_codes: list[str], period: str) -> list[tuple]:
    """解析 tqcenter get_market_data 返回的 dict-of-DataFrames。"""
    if not df or not isinstance(df, dict):
        return []

    open_df = df.get("Open")
    if open_df is None or open_df.empty:
        return []

    dfs = (
        open_df,
        df.get("High", open_df),
        df.get("Low", open_df),
        df.get("Close", open_df),
        df.get("Volume", open_df),
        df.get("Amount", open_df),
        df.get("ForwardFactor", open_df),
    )

    rows = []
    for ts in open_df.index:
        trade_date, dt = _ts_to_datetime(ts, period)
        for code in sector_codes:
            if code not in open_df.columns:
                continue
            row = _extract_row(ts, code, period, trade_date, dt, dfs)
            if row is not None:
                rows.append(row)
    return rows


def _write_to_ch(rows: list[tuple]) -> int:
    """批量写入 ClickHouse（通过 ch_writer 统一入口，裁定 #ARCH-CH-024 治本）。

    改造前：直连 clickhouse_driver.Client + 手写 INSERT SQL（绕过 ch_config/ch_writer/DatabaseService 三层）
    改造后：通过 ch_writer.write_result（自动列过滤 + 二级降级 HTTP→本地落盘兜底）
    """
    if not rows:
        return 0
    from zephyr.data import ch_writer
    from zephyr.data.provider_base import FetchResult

    result = FetchResult(
        table=_CH_TABLE,
        columns=_COLUMNS,
        rows=rows,
        last_key="",
        elapsed_sec=0.0,
    )
    ok = ch_writer.write_result(result)
    return len(rows) if ok else 0


def download_period(tq, sector_codes: list[str], period: str, count: int) -> int:
    """下载指定周期的K线数据。"""
    if period not in _SUPPORTED_PERIODS:
        log.warning("不支持周期 %s", period)
        return 0

    log.info("=== 下载 %s K线, count=%d, 板块数=%d ===", period, count, len(sector_codes))
    total_rows = 0
    total_batches = (len(sector_codes) + _BATCH_SIZE - 1) // _BATCH_SIZE

    for i in range(0, len(sector_codes), _BATCH_SIZE):
        batch = sector_codes[i : i + _BATCH_SIZE]
        batch_num = i // _BATCH_SIZE + 1
        try:
            tq.refresh_kline(stock_list=batch, period=period)
            df = tq.get_market_data(stock_list=batch, count=count, period=period)
            rows = _parse_kline_df(df, batch, period)
            written = _write_to_ch(rows)
            total_rows += written
            log.info("  批次 %d/%d: %d 只 → %d 行", batch_num, total_batches, len(batch), written)
        except Exception as e:  # noqa: BLE001 — 5.135治标
            log.error("  批次 %d/%d 失败: %s", batch_num, total_batches, e)
        time.sleep(0.3)

    log.info("=== %s 完成: %d 行 ===", period, total_rows)
    return total_rows


def main() -> int:
    """盘后K线下载入口。"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(description="880xxx 板块K线下载器")
    parser.add_argument("--period", default="1d", help="K线周期: 1d/1m/5m/all")
    parser.add_argument("--days", type=int, default=30, help="获取最近N天K线")
    args = parser.parse_args()

    log.info("=== 880xxx 板块K线下载器启动 ===")
    tq = _init_tqcenter()
    sector_codes = _get_sector_list(tq)

    periods = _SUPPORTED_PERIODS if args.period == "all" else [args.period]
    total = 0
    for p in periods:
        c = args.days if p == "1d" else args.days * 240
        total += download_period(tq, sector_codes, p, c)

    tq.close()
    log.info("=== 完成: %d 行 ===", total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
