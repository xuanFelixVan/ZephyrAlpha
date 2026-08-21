# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §tqcenter
# [MODULE] zephyr.data.implementations.tqcenter_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] tqcenter (external E:\tdx\PYPlugins\user); clickhouse_driver
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] tqcenter SDK封装为IngestProviderBase；880xxx板块日K+成分股+快照；需通达信客户端运行；50只/批分批下载
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] tqcenter初始化失败->RuntimeError; 单批下载失败->log+继续; ClickHouse写入失败->log+继续
# [TESTS] tests/zephyr/data/test_providers.py::TestTQCenterHelpers::TestTQCenterFetchRoute
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""tqcenter 数据源 Provider 实现。

封装 tqcenter SDK（通达信插件），继承 IngestProviderBase。
- 880xxx 板块指数日K线（get_market_data）
- 板块成分股映射（get_stock_list_in_sector）
- 板块实时快照轮询（get_market_snapshot）
- K线重采样（DB内聚合，不依赖tqcenter）

关键设计：
- connect() 注入 E:\\tdx\\PYPlugins\\user 路径，初始化 tq
- fetch() 按 payload.extra["capability"] 路由到具体方法
- 50只/批分批下载避免tqcenter超时
- requires_process=True（需通达信客户端运行）
"""

from __future__ import annotations

import datetime
import logging
import math
import sys
import time
from decimal import Decimal
from pathlib import Path
from typing import Iterator

from zephyr.shared.security.secrets import SecretsError, get_secret_or_default, get_service_secret

from ..policy_registry import SourcePolicy
from ..provider_base import (
    CapabilityContract,
    FetchPayload,
    FetchResult,
    IngestProviderBase,
    IngestProviderMeta,
)
from ..table_registry import get_registry

log = logging.getLogger(__name__)

# 通达信插件目录走配置真源（secret_registry.yaml: TDX_PLUGIN_DIR，env_file=.env）；未配置回退默认安装路径
try:
    _TQCENTER_PATH = get_service_secret("TDX_PLUGIN_DIR", "tqcenter", required=False) or r"E:\tdx\PYPlugins\user"
except SecretsError:
    # service "tqcenter" 未登记于 secrets._SERVICE_ENV_FILES 时，降级读 os.environ（根 .env 由 zephyr/__init__.py 自动加载）
    _TQCENTER_PATH = get_secret_or_default("TDX_PLUGIN_DIR", r"E:\tdx\PYPlugins\user")

_TBL_KLINE_SECTOR_880 = get_registry().table("market_sector_kline_880")
_TBL_SECTOR_CONSTITUENT = get_registry().table("market_sector_constituent_880")
_TBL_SECTOR_SNAPSHOT = get_registry().table("market_sector_snapshot_880")

_MKT_INDEX_CODES = [f"88000{i}.SH" for i in range(1, 10)]
_BATCH_SIZE = 50
_BEIJING_TZ = datetime.timezone(datetime.timedelta(hours=8))

_COLUMNS_KLINE_880 = [
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

_COLUMNS_CONSTITUENT = [
    "sector_code",
    "sector_name",
    "stock_code",
    "update_date",
    "data_source",
    "valid_from",
]

_COLUMNS_SNAPSHOT = [
    "trade_date",
    "timestamp",
    "sector_code",
    "market_type",
    "now_price",
    "open_price",
    "max_price",
    "min_price",
    "last_close",
    "before_5min_now",
    "average_price",
    "volume",
    "now_vol",
    "amount",
    "up_home",
    "down_home",
    "inside",
    "outside",
    "zangsu",
    "data_source",
]


def _safe_val(val, default):
    """安全提取数值，NaN/None→default。"""
    if val is None:
        return default
    if isinstance(val, float) and math.isnan(val):
        return default
    return val


class TQCenterProvider(IngestProviderBase):
    """tqcenter（通达信插件）数据源 Provider。

    封装 tqcenter SDK，支持 880xxx 板块日K线、成分股、快照。
    需通达信客户端运行（requires_process=True）。
    """

    source_name: str = "tqcenter"
    meta: IngestProviderMeta = IngestProviderMeta(
        name="tqcenter",
        display_name="通达信插件",
        auth_type="anonymous",
        requires_process=True,
        thread_safety="single_thread",
        rate_limit_default=0,
        capabilities=[
            CapabilityContract("kline_sector_880", supports_symbols_null=True),
            CapabilityContract("sector_constituent", supports_symbols_null=True),
            CapabilityContract("sector_snapshot_collection", supports_symbols_null=True),
            "kline_resampling",
        ],
        known_issues=["需通达信客户端运行", "单线程串行", "50只/批分批下载"],
    )

    def __init__(self):
        super().__init__()
        self._tq = None

    # ---- 生命周期 ----

    def connect(self) -> None:
        """建立连接：注入 tqcenter 路径并初始化。"""
        if _TQCENTER_PATH not in sys.path:
            sys.path.insert(0, _TQCENTER_PATH)
        from tqcenter import tq  # 外部 SDK（sys.path 注入，非 pip 安装；E402 不适用——函数内导入）

        tq.initialize(str(Path(__file__).resolve()))
        self._tq = tq
        self._connected = True
        self._log.info("tqcenter 已连接（通达信插件）")

    def health_check(self) -> bool:
        """探活：验证 tq 可用且能获取板块列表。"""
        if not self._connected or self._tq is None:
            return False
        try:
            sectors = self._tq.get_sector_list()
            return sectors is not None
        except Exception:  # noqa: BLE001
            return False

    def disconnect(self) -> None:
        """断开连接。"""
        if self._tq is not None:
            try:
                close = getattr(self._tq, "close", None)
                if close:
                    close()
            except Exception as e:  # noqa: BLE001
                self._log.warning(f"tqcenter 关闭异常: {e}")
        self._tq = None
        self._connected = False

    # ---- 数据获取 ----

    def fetch(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """按 capability 路由到具体获取方法。"""
        if not self._connected or self._tq is None:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error="tqcenter 未连接",
            )
            return

        capability = (payload.extra or {}).get("capability")
        if capability == "kline_sector_880":
            yield from self._fetch_kline_sector_880(payload, policy)
        elif capability == "sector_constituent":
            yield from self._fetch_sector_constituent(payload, policy)
        elif capability == "sector_snapshot_collection":
            yield from self._fetch_sector_snapshot(payload, policy)
        elif capability == "kline_resampling":
            yield from self._resample_kline(payload, policy)
        else:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error=f"unsupported capability: {capability}",
            )

    # ---- 1. 880xxx 板块日K线 ----

    def _get_sector_list(self) -> list[str]:
        """获取全部880xxx板块代码（含市场指数）。"""
        sectors = self._tq.get_sector_list() or []
        s880 = sorted([s for s in sectors if isinstance(s, str) and s.startswith("880")])
        for code in _MKT_INDEX_CODES:
            if code not in s880:
                s880.append(code)
        self._log.info(f"获取880xxx板块代码: {len(s880)} 只")
        return s880

    def _fetch_kline_sector_880(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """获取880xxx板块指数日K线（tqcenter get_market_data）。

        50只/批分批下载，日K线写入 kline_sector_880 表。
        """
        table = payload.table or _TBL_KLINE_SECTOR_880
        symbols = payload.symbols
        if not symbols:
            symbols = self._get_sector_list()
        if not symbols:
            yield FetchResult(
                table=table,
                columns=_COLUMNS_KLINE_880,
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error="无法获取板块代码列表",
            )
            return

        period = (payload.extra or {}).get("period", "1d")
        days = (payload.extra or {}).get("days", 5)
        count = days if period == "1d" else days * 240

        t0 = time.time()
        total_rows = 0
        total_batches = (len(symbols) + _BATCH_SIZE - 1) // _BATCH_SIZE

        for i in range(0, len(symbols), _BATCH_SIZE):
            batch = symbols[i : i + _BATCH_SIZE]
            batch_num = i // _BATCH_SIZE + 1
            try:
                self._tq.refresh_kline(stock_list=batch, period=period)
                df = self._tq.get_market_data(stock_list=batch, count=count, period=period)
                rows = self._parse_kline_df(df, batch, period)
                if rows:
                    total_rows += len(rows)
                    yield FetchResult(
                        table=table,
                        columns=_COLUMNS_KLINE_880,
                        rows=rows,
                        last_key=datetime.date.today().isoformat(),
                        elapsed_sec=time.time() - t0,
                    )
                self._log.info(f"  批次 {batch_num}/{total_batches}: {len(batch)} 只 → {len(rows)} 行")
            except Exception as e:  # noqa: BLE001 — 5.135治标
                self._log.error(f"  批次 {batch_num}/{total_batches} 失败: {e}")
            time.sleep(0.3)

        self._log.info(f"=== kline_sector_880 完成: {total_rows} 行 ===")

    def _parse_kline_df(self, df, sector_codes: list[str], period: str) -> list[tuple]:
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
            trade_date, dt = self._ts_to_datetime(ts, period)
            for code in sector_codes:
                if code not in open_df.columns:
                    continue
                row = self._extract_row(ts, code, period, trade_date, dt, dfs)
                if row is not None:
                    rows.append(row)
        return rows

    @staticmethod
    def _ts_to_datetime(ts, period: str) -> tuple:
        """时间戳转 (trade_date, datetime)。"""
        if isinstance(ts, datetime.datetime):
            d = ts.date()
            return d, ts
        import pandas as pd

        if isinstance(ts, pd.Timestamp):
            if period == "1d":
                d = ts.date()
                return d, datetime.datetime(d.year, d.month, d.day)
            dt = ts.to_pydatetime()
            return dt.date(), dt
        dt = datetime.datetime.strptime(str(ts)[:19], "%Y-%m-%d %H:%M:%S")
        return dt.date(), dt

    @staticmethod
    def _extract_row(ts, code, period, trade_date, dt, dfs):
        """从 DataFrame 提取单行 K线数据。"""
        open_df, high_df, low_df, close_df, vol_df, amt_df, ff_df = dfs
        o = open_df.loc[ts, code]
        if o is None:
            return None
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

    # ---- 2. 板块成分股 ----

    def _fetch_sector_constituent(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """获取880xxx板块成分股映射（tqcenter get_stock_list_in_sector）。

        全量刷新，每个板块获取其成分股列表。
        """
        table = payload.table or _TBL_SECTOR_CONSTITUENT
        symbols = payload.symbols
        if not symbols:
            symbols = self._get_sector_list()
        if not symbols:
            yield FetchResult(
                table=table,
                columns=_COLUMNS_CONSTITUENT,
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error="无法获取板块代码列表",
            )
            return

        t0 = time.time()
        today = datetime.date.today()
        batch_rows: list[tuple] = []

        for idx, sector_code in enumerate(symbols):
            try:
                stocks = self._tq.get_stock_list_in_sector(sector_code) or []
                for stock_code in stocks:
                    if not isinstance(stock_code, str) or not stock_code.strip():
                        continue
                    batch_rows.append(
                        (
                            sector_code,
                            "",
                            stock_code.strip(),
                            today,
                            "tqcenter",
                            today,
                        )
                    )
            except Exception as e:  # noqa: BLE001
                self._log.warning(f"获取 {sector_code} 成分股失败: {e}")

            if len(batch_rows) >= 500:
                yield FetchResult(
                    table=table,
                    columns=_COLUMNS_CONSTITUENT,
                    rows=batch_rows[:],
                    last_key=today.isoformat(),
                    elapsed_sec=time.time() - t0,
                )
                batch_rows.clear()

            if (idx + 1) % 100 == 0:
                self._log.info(f"sector_constituent 进度: {idx + 1}/{len(symbols)}")

            time.sleep(0.1)

        if batch_rows:
            yield FetchResult(
                table=table,
                columns=_COLUMNS_CONSTITUENT,
                rows=batch_rows[:],
                last_key=today.isoformat(),
                elapsed_sec=time.time() - t0,
            )

        self._log.info("=== sector_constituent 完成 ===")

    # ---- 3. 板块实时快照（轮询模式） ----

    def _fetch_sector_snapshot(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """获取880xxx板块实时快照（tqcenter get_market_snapshot）。

        轮询模式：一次性获取全部板块快照，写入 sector_snapshot 表。
        """
        table = payload.table or _TBL_SECTOR_SNAPSHOT
        symbols = payload.symbols
        if not symbols:
            symbols = self._get_sector_list()
        if not symbols:
            yield FetchResult(
                table=table,
                columns=_COLUMNS_SNAPSHOT,
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error="无法获取板块代码列表",
            )
            return

        t0 = time.time()
        now = datetime.datetime.now(_BEIJING_TZ)
        today = now.date()
        batch_rows: list[tuple] = []

        for i in range(0, len(symbols), _BATCH_SIZE):
            batch = symbols[i : i + _BATCH_SIZE]
            try:
                # #ARCH-DATA-016: tqcenter get_market_snapshot 真实签名为单代码
                # (stock_code: str) -> Dict（SDK 在 E:\tdx\PYPlugins\user\tqcenter.py，
                # 项目外无版本锁定）。原 stock_list=batch 批量签名不存在，每批 TypeError
                # 被吞 → sector_snapshot 持续 0 行。逐代码调用并组装 {code: snap}。
                snapshots: dict = {}
                for code in batch:
                    try:
                        snap = self._tq.get_market_snapshot(stock_code=code)
                        if snap:
                            snapshots[code] = snap
                    except Exception as e:  # noqa: BLE001 — 单代码失败不拖垮整批
                        self._log.debug(f"快照单代码 {code} 失败: {e}")
                if not snapshots:
                    continue
                for code, snap in snapshots.items():
                    row = self._parse_snapshot(code, snap, today, now)
                    if row:
                        batch_rows.append(row)
            except Exception as e:  # noqa: BLE001
                self._log.warning(f"快照批次 {i // _BATCH_SIZE + 1} 失败: {e}")

            if len(batch_rows) >= 500:
                yield FetchResult(
                    table=table,
                    columns=_COLUMNS_SNAPSHOT,
                    rows=batch_rows[:],
                    last_key=today.isoformat(),
                    elapsed_sec=time.time() - t0,
                )
                batch_rows.clear()

            time.sleep(0.3)

        if batch_rows:
            yield FetchResult(
                table=table,
                columns=_COLUMNS_SNAPSHOT,
                rows=batch_rows[:],
                last_key=today.isoformat(),
                elapsed_sec=time.time() - t0,
            )

        self._log.info(f"=== sector_snapshot 完成: {len(batch_rows)} 行 ===")

    @staticmethod
    def _parse_snapshot(code, snap, trade_date, ts):
        """解析单条快照数据。

        #ARCH-DATA-016：tqcenter SDK 返回 PascalCase 键（Now/Open/Max/...），
        原 snake_case 读取全 miss → 即使调用成功也产出全 NULL/0 行。
        键名以 E:\\tdx\\PYPlugins\\user\\tqcenter.py 2026-08-14 实测 dump 为准。
        """
        if not snap or not isinstance(snap, dict):
            return None
        try:
            return (
                trade_date,
                ts,
                code,
                "sector",
                _safe_val(snap.get("Now"), None),
                _safe_val(snap.get("Open"), None),
                _safe_val(snap.get("Max"), None),
                _safe_val(snap.get("Min"), None),
                _safe_val(snap.get("LastClose"), None),
                _safe_val(snap.get("Before5MinNow"), None),
                _safe_val(snap.get("Average"), None),
                int(float(_safe_val(snap.get("Volume"), 0))),
                int(float(_safe_val(snap.get("NowVol"), 0))),
                _safe_val(snap.get("Amount"), 0.0),
                int(float(_safe_val(snap.get("UpHome"), 0))),
                int(float(_safe_val(snap.get("DownHome"), 0))),
                int(float(_safe_val(snap.get("Inside"), 0))),
                int(float(_safe_val(snap.get("Outside"), 0))),
                _safe_val(snap.get("Zangsu"), 0.0),
                "tqcenter",
            )
        except Exception:  # noqa: BLE001
            return None

    # ---- 4. K线重采样（DB内聚合） ----

    def _resample_kline(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """K线重采样——ClickHouse DB内 toStartOfInterval 聚合。

        1m/5m → 15m/30m/60m，幂等 DELETE+INSERT。
        不依赖 tqcenter，纯 DB 操作。
        """
        table = payload.table or _TBL_KLINE_SECTOR_880
        from .. import ch_writer
        from ..ch_reader import query as ch_query

        today = datetime.date.today()
        t0 = time.time()

        resample_pairs = [
            ("1m", "15min"),
            ("1m", "30min"),
            ("1m", "60min"),
            ("5m", "15min"),
            ("5m", "30min"),
            ("5m", "60min"),
        ]

        total_inserted = 0
        for src_period, dst_period in resample_pairs:
            try:
                interval = dst_period.replace("min", "minute")
                delete_sql = f"ALTER TABLE {table} DELETE WHERE period = '{dst_period}' AND trade_date = today()"
                ch_query(delete_sql)

                insert_sql = (
                    f"INSERT INTO {table} "
                    f"(period, trade_date, timestamp, sector_code, sector_name, "
                    f"open, high, low, close, volume, amount, forward_factor, data_source) "
                    f"SELECT '{dst_period}', toDate(timestamp), timestamp, sector_code, sector_name, "
                    f"argMin(open, timestamp), max(high), min(low), argMax(close, timestamp), "
                    f"sum(volume), sum(amount), max(forward_factor), 'tqcenter' "
                    f"FROM {table} "
                    f"WHERE period = '{src_period}' AND trade_date = today() "
                    f"GROUP BY sector_code, sector_name, toStartOfInterval(timestamp, INTERVAL 1 {interval})"
                )
                ch_query(insert_sql)

                count_r = ch_query(
                    f"SELECT count() FROM {table} WHERE period = '{dst_period}' AND trade_date = today()"
                )
                inserted = int(count_r.strip()) if count_r.strip() else 0
                total_inserted += inserted
                self._log.info(f"  重采样 {src_period}→{dst_period}: {inserted} 行")
            except Exception as e:  # noqa: BLE001
                self._log.error(f"  重采样 {src_period}→{dst_period} 失败: {e}")

        yield FetchResult(
            table=table,
            columns=[],
            rows=[],
            last_key=today.isoformat(),
            elapsed_sec=time.time() - t0,
        )
        self._log.info(f"=== kline_resampling 完成: {total_inserted} 行 ===")
