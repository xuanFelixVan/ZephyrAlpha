# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.miniqmt_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] xtquant SDK (xtdata.download_history_data/get_market_data_ex)
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] connect() 仅验证 SDK 可导入；单线程使用（xtquant 非线程安全）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] fetch 异常->yield FetchResult(error=str)；_ts_to_date 按 UTC 解释避免跨日
# [TESTS] tests/zephyr/data/test_providers.py::TestMiniQMTHelpers
# [A_module] module_id=MOD-L00-004-miniqmt_provider | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-L00-004 数据源集成器 · MiniQMTProvider 实现。

封装 xtquant SDK（miniQMT），继承 DataSourceBase。

设计要点：
- xtquant 连接的是本地 XtMiniQmt.exe 进程，无需显式登录，但要求进程在跑
- xtquant 非线程安全，本 Provider 按 single_thread 模型使用
- xtquant 在方法内部 import，避免模块加载时就要求 SDK 安装
- stock_code 格式 "000001.SZ" / "600000.SH"，period 如 "1d"/"5m"/"1m"
- start_time/end_time 格式 "YYYYMMDD"
"""
from __future__ import annotations

import datetime
import time
import logging
from typing import Iterator

from ..provider_base import DataSourceBase, FetchPayload, FetchResult, DataSourceMeta
from ..policy_registry import SourcePolicy


class MiniQMTProvider(DataSourceBase):
    """miniQMT（迅投 xtquant）数据源 Provider。

    通过本地 XtMiniQmt.exe 进程获取行情/财务/指数成分数据。
    单线程使用（xtquant 非线程安全）。
    """

    source_name: str = "miniqmt"

    meta: DataSourceMeta = DataSourceMeta(
        name="miniqmt",
        display_name="miniQMT 迅投",
        auth_type="account",
        requires_process=True,
        thread_safety="single_thread",
        rate_limit_default=0,
        capabilities=[
            "kline_daily",
            "kline_1min",
            "kline_5min",
            "financial_statement",
            "index_constituent",
            "index_kline",
            "adj_factor",
            "kline_daily_hfq",
            "kline_weekly",
            "kline_monthly",
            # 以下为新增能力（MOD-L00-004 fetch 路由扩展）
            "hk_daily_kline",
            "futures_kline",
            "futures_position",
            "shareholder",
            "earnings_forecast",
            "express_report",
            "dividend",
            "option_iv_surface",
            "convertible_bond_iv",
            "futures_term_structure",
            "tick_data",
            "auction_snapshot",
            "index_quote",
            "stock_list",
        ],
        known_issues=[
            "需XtMiniQmt.exe进程",
            "单线程",
            "高频数据时间限制",
        ],
    )

    # ============== 生命周期方法 ==============

    def connect(self) -> None:
        """建立连接。

        xtquant 连接本地 XtMiniQmt.exe 进程，无需显式登录。
        此处仅验证 SDK 可导入，并标记连接状态。
        """
        try:
            from xtquant import xtdata  # noqa: F401  仅验证 SDK 可导入
        except ImportError as e:
            self._connected = False
            self._log.error(f"xtquant SDK 导入失败，请确认已安装: {e}")
            raise
        self._connected = True
        self._log.info("miniQMT 连接就绪（依赖本地 XtMiniQmt.exe 进程）")

    def health_check(self) -> bool:
        """探活：尝试调用 xtdata.get_stock_list_in_sector 读取沪深A股列表。"""
        try:
            from xtquant import xtdata
            xtdata.get_stock_list_in_sector("沪深A股")
            return True
        except Exception as e:
            self._log.warning(f"miniQMT health_check 失败: {e}")
            return False

    def disconnect(self) -> None:
        """断开连接。xtquant 无显式登出，仅重置状态标记。"""
        self._connected = False
        self._log.info("miniQMT 已断开")

    # ============== fetch 路由 ==============

    def fetch(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """按 payload.extra["capability"] 路由到具体抓取方法。

        Args:
            payload: 下载请求，extra["capability"] 指定能力
            policy: 调用策略（限流/重试）

        Yields:
            FetchResult: 每批一个
        """
        extra = payload.extra or {}
        capability = extra.get("capability")
        # K线类能力统一路由到 _fetch_kline，按 period 区分
        _KLINE_CAPABILITIES = {
            "kline_daily": "1d",
            "kline_1min": "1m",
            "kline_5min": "5m",
            "kline_15min": "15m",
            "kline_30min": "30m",
            "kline_60min": "1h",
        }
        # 财务报表类能力统一路由到 _fetch_financial_statement，按 table_list 区分
        _FINANCIAL_CAPABILITIES = {
            "balance_sheet": "Balance",
            "income_statement": "Income",
            "cashflow_statement": "CashFlow",
            "financial_indicator": "Capital",
            "main_business": "Income",
        }
        if capability in _KLINE_CAPABILITIES:
            yield from self._fetch_kline(payload, policy, _KLINE_CAPABILITIES[capability])
        elif capability == "kline_daily_hfq":
            # 后复权日K：复用 _fetch_kline，传 dividend_type="back"
            yield from self._fetch_kline(payload, policy, "1d", dividend_type="back")
        elif capability == "kline_weekly":
            # 周K：miniQMT 不支持 1w 周期，从日K聚合
            yield from self._fetch_kline_aggregated(payload, policy, "W")
        elif capability == "kline_monthly":
            # 月K：miniQMT 不支持 1M 周期，从日K聚合（pandas>=2.2 需用 'ME' 替代 'M'）
            yield from self._fetch_kline_aggregated(payload, policy, "ME")
        elif capability == "adj_factor":
            yield from self._fetch_adj_factor(payload, policy)
        elif capability in _FINANCIAL_CAPABILITIES:
            yield from self._fetch_financial_statement(payload, policy, _FINANCIAL_CAPABILITIES[capability])
        elif capability == "index_constituent":
            yield from self._fetch_index_constituent(payload, policy)
        elif capability == "index_kline":
            yield from self._fetch_index_kline(payload, policy)
        # ---- 新增能力路由（MOD-L00-004 fetch 路由扩展）----
        elif capability == "hk_daily_kline":
            # 港股日K：复用 _fetch_kline，symbols 格式如 '00700.HK'
            yield from self._fetch_kline(payload, policy, "1d")
        elif capability == "futures_kline":
            # 期货K线：复用 _fetch_kline，symbols 格式如 'IF2406.CF'
            yield from self._fetch_kline(payload, policy, "1d")
        elif capability == "futures_position":
            yield from self._fetch_futures_position(payload, policy)
        elif capability == "shareholder":
            yield from self._fetch_shareholder(payload, policy)
        elif capability == "earnings_forecast":
            yield from self._fetch_earnings_forecast(payload, policy)
        elif capability == "express_report":
            yield from self._fetch_express_report(payload, policy)
        elif capability == "dividend":
            yield from self._fetch_dividend(payload, policy)
        elif capability == "option_iv_surface":
            yield from self._fetch_option_iv_surface(payload, policy)
        elif capability == "convertible_bond_iv":
            yield from self._fetch_convertible_bond_iv(payload, policy)
        elif capability == "futures_term_structure":
            yield from self._fetch_futures_term_structure(payload, policy)
        elif capability == "tick_data":
            yield from self._fetch_tick_data(payload, policy)
        elif capability == "auction_snapshot":
            yield from self._fetch_auction_snapshot(payload, policy)
        elif capability == "index_quote":
            yield from self._fetch_index_quote(payload, policy)
        elif capability == "stock_list":
            yield from self._fetch_stock_list(payload, policy)
        else:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error=f"未知 capability: {capability}",
            )

    # ============== K线通用方法（日K/分钟K） ==============

    def _fetch_kline(
        self,
        payload: FetchPayload,
        policy: SourcePolicy,
        period: str,
        dividend_type: str = "none",
    ) -> Iterator[FetchResult]:
        """抓取K线数据（日K/分钟K通用）。

        步骤：
        1. 若 symbols 为 None，取沪深A股全部标的
        2. 对每个 stock_code：download_history_data 下载 -> get_market_data_ex 读取
        3. DataFrame 转 tuple 列表，每个股票作为一批 yield

        period="1d" 时列为 trade_date+symbol+OHLCV+amount（日K）
        period!="1d" 时列为 trade_date+trade_time+symbol+OHLCV+amount（分钟K）

        Args:
            payload: 下载请求
            policy: 调用策略
            period: K线周期（"1d"/"1m"/"5m"/"15m"/"30m"/"60m"）
            dividend_type: 复权类型（"none"=不复权/"back"=后复权），默认 "none"

        Yields:
            FetchResult: 每个股票一批
        """
        from xtquant import xtdata

        is_hfq = (dividend_type == "back")
        # 后复权日K落入 kline_daily_hfq 表，普通日K落入 kline_daily 表
        default_table = "c1_market.kline_daily_hfq" if is_hfq else "c1_market.kline_daily"
        table = payload.table or default_table
        is_daily = (period == "1d")
        if is_daily:
            if is_hfq:
                # kline_daily_hfq 表列为 OCLH 顺序；amplitude/pct_change/change/turnover/data_source 有 DEFAULT 不返回
                columns = ["trade_date", "symbol", "open", "close", "high", "low", "volume", "amount"]
            else:
                columns = ["trade_date", "symbol", "open", "high", "low", "close", "volume", "amount"]
        elif "kline_1min" in table:
            # kline_1min 表有 pct_change/amplitude（无 DEFAULT），需补充；data_source 有 DEFAULT
            columns = ["trade_date", "trade_time", "symbol", "open", "close", "high", "low", "volume", "amount", "pct_change", "amplitude"]
        elif "kline_5min" in table:
            # kline_5min 表无 trade_date，data_source 无 DEFAULT 需补充
            columns = ["trade_time", "symbol", "open", "high", "low", "close", "volume", "amount", "data_source"]
        else:
            columns = ["trade_date", "trade_time", "symbol", "open", "high", "low", "close", "volume", "amount"]

        try:
            start_str = self._date_to_str(payload.start)
            end_str = self._date_to_str(payload.end)
        except Exception as e:
            yield FetchResult(
                table=table, columns=[], rows=[], last_key="",
                elapsed_sec=0.0, error=f"日期转换失败: {e}",
            )
            return

        # 1. 获取标的清单
        try:
            symbols = payload.symbols
            if not symbols:
                symbols = self._call_with_policy(
                    xtdata.get_stock_list_in_sector, policy, "沪深A股"
                )
        except Exception as e:
            yield FetchResult(
                table=table, columns=[], rows=[], last_key="",
                elapsed_sec=0.0, error=f"获取标的清单失败: {e}",
            )
            return

        last_key = self._date_to_str(payload.end)

        # 2. 逐标的下载+读取
        for stock_code in symbols:
            t0 = time.time()
            try:
                # 下载历史数据
                self._call_with_policy(
                    xtdata.download_history_data,
                    policy,
                    stock_code, period, start_str, end_str,
                )
                # 读取行情（后复权时传 dividend_type='back'，count=-1 表示全部）
                data = self._call_with_policy(
                    xtdata.get_market_data_ex,
                    policy,
                    [], [stock_code], period, start_str, end_str, -1, dividend_type,
                )

                # 3. DataFrame -> tuple 列表
                rows = []
                df = data.get(stock_code) if data else None
                if df is not None and len(df) > 0:
                    symbol = self._stock_to_symbol(stock_code)
                    # xtquant DataFrame 索引为 numpy.int64：
                    #   日K索引为 YYYYMMDD 格式整数（如 20260703）
                    #   分钟K索引为 YYYYMMDDHHMMSS 格式整数（如 20260703093000）
                    times = [int(ts) for ts in df.index]
                    opens = df["open"].tolist()
                    highs = df["high"].tolist()
                    lows = df["low"].tolist()
                    closes = df["close"].tolist()
                    volumes = df["volume"].tolist()
                    amounts = df["amount"].tolist()
                    for i in range(len(times)):
                        s = str(times[i])
                        if is_daily:
                            # 日K：YYYYMMDD（8 位）-> YYYY-MM-DD
                            trade_date = f"{s[:4]}-{s[4:6]}-{s[6:8]}"
                            # volume 在 ClickHouse 中是 UInt64，需转 int
                            vol = self.safe_float(volumes[i])
                            vol = int(vol) if vol is not None else None
                            if is_hfq:
                                # kline_daily_hfq 表列为 OCLH 顺序
                                rows.append((
                                    trade_date,
                                    symbol,
                                    self.safe_float(opens[i]),
                                    self.safe_float(closes[i]),
                                    self.safe_float(highs[i]),
                                    self.safe_float(lows[i]),
                                    vol,
                                    self.safe_float(amounts[i]),
                                ))
                            else:
                                rows.append((
                                    trade_date,
                                    symbol,
                                    self.safe_float(opens[i]),
                                    self.safe_float(highs[i]),
                                    self.safe_float(lows[i]),
                                    self.safe_float(closes[i]),
                                    vol,
                                    self.safe_float(amounts[i]),
                                ))
                        else:
                            # 分钟K：YYYYMMDDHHMMSS（14 位）-> 拆分 date 和 datetime
                            trade_date = f"{s[:4]}-{s[4:6]}-{s[6:8]}"
                            trade_time = (
                                f"{s[:4]}-{s[4:6]}-{s[6:8]} "
                                f"{s[8:10]}:{s[10:12]}:{s[12:14]}"
                            )
                            vol = self.safe_float(volumes[i])
                            vol = int(vol) if vol is not None else None
                            if "kline_1min" in table:
                                # kline_1min: 补充 pct_change=0, amplitude=0
                                rows.append((
                                    trade_date,
                                    trade_time,
                                    symbol,
                                    self.safe_float(opens[i]),
                                    self.safe_float(closes[i]),
                                    self.safe_float(highs[i]),
                                    self.safe_float(lows[i]),
                                    vol,
                                    self.safe_float(amounts[i]),
                                    0,  # pct_change（miniQMT 不提供）
                                    0,  # amplitude（miniQMT 不提供）
                                ))
                            elif "kline_5min" in table:
                                # kline_5min: 无 trade_date，补充 data_source
                                rows.append((
                                    trade_time,
                                    symbol,
                                    self.safe_float(opens[i]),
                                    self.safe_float(highs[i]),
                                    self.safe_float(lows[i]),
                                    self.safe_float(closes[i]),
                                    vol,
                                    self.safe_float(amounts[i]),
                                    "miniqmt",  # data_source
                                ))
                            else:
                                rows.append((
                                    trade_date,
                                    trade_time,
                                    symbol,
                                    self.safe_float(opens[i]),
                                    self.safe_float(highs[i]),
                                    self.safe_float(lows[i]),
                                    self.safe_float(closes[i]),
                                    vol,
                                    self.safe_float(amounts[i]),
                                ))

                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=rows,
                    last_key=last_key,
                    elapsed_sec=time.time() - t0,
                )
            except Exception as e:
                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=[],
                    last_key=last_key,
                    elapsed_sec=time.time() - t0,
                    error=f"{stock_code} 抓取失败: {e}",
                )

    # ============== 财务报表 ==============

    def _fetch_financial_statement(
        self,
        payload: FetchPayload,
        policy: SourcePolicy,
        table_list: str,
    ) -> Iterator[FetchResult]:
        """抓取财务报表数据（Balance/Income/CashFlow/Capital）。

        使用 xtdata.download_financial_data2 下载 + get_financial_data 读取。
        table_list 参数对应 xtquant 的报表名（Balance/Income/CashFlow/Capital）。

        Args:
            payload: 下载请求
            policy: 调用策略
            table_list: xtquant 报表名（"Balance"/"Income"/"CashFlow"/"Capital"）

        Yields:
            FetchResult: 每个股票一批
        """
        from xtquant import xtdata

        table = payload.table or f"c3_fundamental.{table_list.lower()}"
        start_str = self._date_to_str(payload.start)
        end_str = self._date_to_str(payload.end)

        # 1. 获取标的清单
        try:
            symbols = payload.symbols
            if not symbols:
                symbols = self._call_with_policy(
                    xtdata.get_stock_list_in_sector, policy, "沪深A股"
                )
        except Exception as e:
            yield FetchResult(
                table=table, columns=[], rows=[], last_key="",
                elapsed_sec=0.0, error=f"获取标的清单失败: {e}",
            )
            return

        last_key = end_str

        # 2. 逐标的下载+读取
        for stock_code in symbols:
            t0 = time.time()
            try:
                # 下载财务数据
                self._call_with_policy(
                    xtdata.download_financial_data2,
                    policy,
                    [stock_code], '', start_str, end_str,
                )
                # 读取财务数据
                fd = self._call_with_policy(
                    xtdata.get_financial_data,
                    policy,
                    [stock_code], [table_list], start_str, end_str, 'report_time',
                )

                # 3. 转换为 rows
                rows = []
                columns = ["symbol"]  # 默认列（无数据时）
                stock_data = fd.get(stock_code) if fd else None
                if stock_data and table_list in stock_data:
                    df = stock_data[table_list]
                    if df is not None and len(df) > 0:
                        symbol = self._stock_to_symbol(stock_code)
                        # 列名从 DataFrame 动态提取
                        col_names = list(df.columns)
                        for _, row in df.iterrows():
                            row_values = []
                            for col in col_names:
                                v = row.get(col)
                                if col in ('date', 'announce_date', 'report_date', 'enddate'):
                                    row_values.append(str(v) if v is not None else None)
                                else:
                                    row_values.append(self.safe_float(v))
                            rows.append(tuple([symbol] + row_values))

                        columns = ["symbol"] + col_names

                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=rows,
                    last_key=last_key,
                    elapsed_sec=time.time() - t0,
                )
            except Exception as e:
                yield FetchResult(
                    table=table,
                    columns=["symbol"],
                    rows=[],
                    last_key=last_key,
                    elapsed_sec=time.time() - t0,
                    error=f"{stock_code} 财务数据抓取失败: {e}",
                )

    # ============== 指数成分股 ==============

    # 板块名 -> 指数代码映射（与 c1_market.index_constituent 现有数据一致）
    _INDEX_SECTOR_MAP = {
        "上证50": "000016.SH",
        "沪深300": "000300.SH",
        "中证500": "000905.SH",
        "中证1000": "000852.SH",
        "中小板指": "399005.SZ",
        "创业板指": "399006.SZ",
    }

    def _fetch_index_constituent(
        self,
        payload: FetchPayload,
        policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """抓取指数成分股列表。

        先调用 xtdata.download_sector_data() 自动下载最新板块数据，
        再用 xtdata.get_stock_list_in_sector 获取各指数成分股。
        遍历 _INDEX_SECTOR_MAP 中的 6 个核心指数，每个指数作为一批 yield。

        表 schema: (trade_date, index_code, symbol, weight, action, data_source)
        miniQMT 不提供权重，weight=0, action='', data_source='miniqmt'。
        若需权重数据，应优先使用 iFind Provider。

        Args:
            payload: 下载请求（payload.end 作为 trade_date）
            policy: 调用策略

        Yields:
            FetchResult: 每个指数一批
        """
        from xtquant import xtdata

        table = payload.table or "c1_market.index_constituent"
        columns = ["trade_date", "index_code", "symbol", "weight", "action", "data_source"]

        trade_date = payload.end.isoformat()
        extra = payload.extra or {}
        # 允许 payload.extra["sectors"] 覆盖默认列表
        sectors = extra.get("sectors", list(self._INDEX_SECTOR_MAP.keys()))

        # 先下载板块数据（确保 get_stock_list_in_sector 能返回成分股）
        # QMT 客户端需在运行，否则 download_sector_data 报"无法连接行情服务"
        try:
            self._call_with_policy(xtdata.download_sector_data, policy)
            self._log.info("download_sector_data 完成")
        except Exception as e:
            self._log.warning(f"download_sector_data 失败（不影响已有缓存数据）: {e}")

        for sector_name in sectors:
            index_code = self._INDEX_SECTOR_MAP.get(sector_name, sector_name)
            t0 = time.time()
            try:
                stock_list = self._call_with_policy(
                    xtdata.get_stock_list_in_sector, policy, sector_name
                )

                rows = []
                if stock_list:
                    for stock_code in stock_list:
                        symbol = self._stock_to_symbol(stock_code)
                        # weight=0（miniQMT 不提供权重）, action='', data_source='miniqmt'
                        rows.append((trade_date, index_code, symbol, 0, "", "miniqmt"))

                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=rows,
                    last_key=self._date_to_str(payload.end),
                    elapsed_sec=time.time() - t0,
                )
            except Exception as e:
                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=[],
                    last_key="",
                    elapsed_sec=time.time() - t0,
                    error=f"获取指数成分失败[{sector_name}]: {e}",
                )

    # ============== 指数K线 ==============

    def _fetch_index_kline(
        self,
        payload: FetchPayload,
        policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """抓取指数日K线数据。

        使用 xtdata.get_stock_list_in_sector("沪深指数") 获取指数列表，
        逐个 download_history_data + get_market_data_ex 读取日K，
        get_instrument_detail 获取指数名称。

        表 schema: (trade_date, symbol, name, open, high, low, close,
                    volume, amount, data_source)
        advance_count/decline_count/quality_flag 由 CH DEFAULT 填充。

        Args:
            payload: 下载请求（payload.symbols 可指定指数代码列表，
                     None 时取"沪深指数"板块全部）
            policy: 调用策略

        Yields:
            FetchResult: 每个指数一批
        """
        from xtquant import xtdata

        table = payload.table or "c1_market.index_kline"
        columns = [
            "trade_date", "symbol", "name",
            "open", "high", "low", "close",
            "volume", "amount", "data_source",
        ]

        try:
            start_str = self._date_to_str(payload.start)
            end_str = self._date_to_str(payload.end)
        except Exception as e:
            yield FetchResult(
                table=table, columns=[], rows=[], last_key="",
                elapsed_sec=0.0, error=f"日期转换失败: {e}",
            )
            return

        # 1. 获取指数清单
        try:
            index_codes = payload.symbols
            if not index_codes:
                index_codes = self._call_with_policy(
                    xtdata.get_stock_list_in_sector, policy, "沪深指数"
                )
        except Exception as e:
            yield FetchResult(
                table=table, columns=[], rows=[], last_key="",
                elapsed_sec=0.0, error=f"获取指数清单失败: {e}",
            )
            return

        last_key = end_str

        # 2. 逐指数下载+读取
        for index_code in index_codes:
            t0 = time.time()
            try:
                # 下载历史数据
                self._call_with_policy(
                    xtdata.download_history_data,
                    policy,
                    index_code, "1d", start_str, end_str,
                )
                # 读取行情
                data = self._call_with_policy(
                    xtdata.get_market_data_ex,
                    policy,
                    [], [index_code], "1d", start_str, end_str,
                )

                # 3. 获取指数名称
                symbol = self._stock_to_symbol(index_code)
                try:
                    detail = xtdata.get_instrument_detail(index_code)
                    name = detail.get("InstrumentName", "") if detail else ""
                except Exception:
                    name = ""

                # 4. DataFrame -> tuple 列表
                rows = []
                df = data.get(index_code) if data else None
                if df is not None and len(df) > 0:
                    times = [int(ts) for ts in df.index]
                    opens = df["open"].tolist()
                    highs = df["high"].tolist()
                    lows = df["low"].tolist()
                    closes = df["close"].tolist()
                    volumes = df["volume"].tolist()
                    amounts = df["amount"].tolist()
                    for i in range(len(times)):
                        s = str(times[i])
                        # 日K索引 YYYYMMDD（8位）-> YYYY-MM-DD
                        trade_date = f"{s[:4]}-{s[4:6]}-{s[6:8]}"
                        vol = self.safe_float(volumes[i])
                        # volume 是 UInt64，负值（某些计算指数）转为 0
                        if vol is not None and vol < 0:
                            vol = 0
                        vol = int(vol) if vol is not None else 0
                        rows.append((
                            trade_date,
                            symbol,
                            name,
                            self.safe_float(opens[i]),
                            self.safe_float(highs[i]),
                            self.safe_float(lows[i]),
                            self.safe_float(closes[i]),
                            vol,
                            self.safe_float(amounts[i]),
                            "miniqmt",  # data_source
                        ))

                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=rows,
                    last_key=last_key,
                    elapsed_sec=time.time() - t0,
                )
            except Exception as e:
                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=[],
                    last_key=last_key,
                    elapsed_sec=time.time() - t0,
                    error=f"{index_code} 指数K线抓取失败: {e}",
                )

    # ============== 复权因子 ==============

    def _fetch_adj_factor(
        self,
        payload: FetchPayload,
        policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """抓取复权因子数据。

        使用 xtdata.get_divid_factors(stock_code) 获取除权除息因子。
        表 schema: (trade_date, symbol, adj_factor, data_source, quality_flag DEFAULT 1)
        返回列不含 quality_flag（有 DEFAULT）。

        Args:
            payload: 下载请求（start/end 用于过滤日期范围）
            policy: 调用策略

        Yields:
            FetchResult: 每个股票一批
        """
        from xtquant import xtdata

        table = payload.table or "c1_market.adj_factor"
        columns = ["trade_date", "symbol", "adj_factor", "data_source"]

        # 日期范围过滤（"YYYY-MM-DD" 字符串可直接字典序比较）
        start_date = payload.start.isoformat()
        end_date = payload.end.isoformat()

        # 1. 获取标的清单
        try:
            symbols = payload.symbols
            if not symbols:
                symbols = self._call_with_policy(
                    xtdata.get_stock_list_in_sector, policy, "沪深A股"
                )
        except Exception as e:
            yield FetchResult(
                table=table, columns=[], rows=[], last_key="",
                elapsed_sec=0.0, error=f"获取标的清单失败: {e}",
            )
            return

        last_key = self._date_to_str(payload.end)

        # 2. 逐标的获取复权因子
        for stock_code in symbols:
            t0 = time.time()
            try:
                df = self._call_with_policy(
                    xtdata.get_divid_factors, policy, stock_code,
                )

                rows = []
                if df is not None and len(df) > 0:
                    symbol = self._stock_to_symbol(stock_code)
                    # get_divid_factors 返回 DataFrame，含 'time'(Unix毫秒) 和 'dr'(除权除息因子) 列
                    for _, row in df.iterrows():
                        ts = row.get("time")
                        dr = row.get("dr")
                        if ts is None:
                            continue
                        # time（毫秒时间戳）-> "YYYY-MM-DD"（按本地时区，符合中国市场）
                        trade_date = datetime.datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
                        # 按 payload.start/end 过滤日期范围
                        if trade_date < start_date or trade_date > end_date:
                            continue
                        rows.append((
                            trade_date,
                            symbol,
                            self.safe_float(dr),
                            "miniqmt",  # data_source
                        ))

                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=rows,
                    last_key=last_key,
                    elapsed_sec=time.time() - t0,
                )
            except Exception as e:
                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=[],
                    last_key=last_key,
                    elapsed_sec=time.time() - t0,
                    error=f"{stock_code} 复权因子抓取失败: {e}",
                )

    # ============== 周/月K线（从日K聚合） ==============

    def _fetch_kline_aggregated(
        self,
        payload: FetchPayload,
        policy: SourcePolicy,
        freq: str,
    ) -> Iterator[FetchResult]:
        """抓取日K数据并聚合为周K/月K。

        miniQMT 不支持直接下载 "1w"/"1M" 周期，需下载日K后用 pandas resample 聚合。
        聚合规则：open=首日、close=末日、high=max、low=min、volume/amount=sum。
        trade_date 取周期内最后交易日的日期。
        amplitude/pct_change/change/turnover 在表中无 DEFAULT，但 miniQMT 不提供，填 0。
        data_source 有 DEFAULT 'local_qfq'，不返回。

        Args:
            payload: 下载请求
            policy: 调用策略
            freq: 聚合频率（"W"=周K，"ME"=月K，pandas>=2.2 用 ME 替代 M）

        Yields:
            FetchResult: 每个股票一批
        """
        from xtquant import xtdata
        import pandas as pd

        if freq == "W":
            table = payload.table or "c1_market.kline_weekly"
        else:
            table = payload.table or "c1_market.kline_monthly"

        columns = [
            "trade_date", "symbol", "open", "close", "high", "low",
            "volume", "amount", "amplitude", "pct_change", "change", "turnover",
        ]

        try:
            start_str = self._date_to_str(payload.start)
            end_str = self._date_to_str(payload.end)
        except Exception as e:
            yield FetchResult(
                table=table, columns=[], rows=[], last_key="",
                elapsed_sec=0.0, error=f"日期转换失败: {e}",
            )
            return

        # 1. 获取标的清单
        try:
            symbols = payload.symbols
            if not symbols:
                symbols = self._call_with_policy(
                    xtdata.get_stock_list_in_sector, policy, "沪深A股"
                )
        except Exception as e:
            yield FetchResult(
                table=table, columns=[], rows=[], last_key="",
                elapsed_sec=0.0, error=f"获取标的清单失败: {e}",
            )
            return

        last_key = end_str

        # 2. 逐标的下载日K + 聚合
        for stock_code in symbols:
            t0 = time.time()
            try:
                # 下载日K历史数据
                self._call_with_policy(
                    xtdata.download_history_data,
                    policy,
                    stock_code, "1d", start_str, end_str,
                )
                # 读取日K行情
                data = self._call_with_policy(
                    xtdata.get_market_data_ex,
                    policy,
                    [], [stock_code], "1d", start_str, end_str,
                )

                rows = []
                df = data.get(stock_code) if data else None
                if df is not None and len(df) > 0:
                    symbol = self._stock_to_symbol(stock_code)
                    # xtquant 日K索引为 YYYYMMDD 格式整数，转为 datetime 用于 resample
                    df = df.copy()
                    orig_dates = [str(int(ts)) for ts in df.index]
                    # 保留原始日期字符串，用于取周期内最后交易日
                    df["_orig_date"] = orig_dates
                    df.index = pd.to_datetime(orig_dates, format="%Y%m%d")

                    # resample 聚合（W=周、ME=月）
                    agg = df.resample(freq).agg({
                        "open": "first",
                        "close": "last",
                        "high": "max",
                        "low": "min",
                        "volume": "sum",
                        "amount": "sum",
                        "_orig_date": "last",  # 周期内最后交易日的 YYYYMMDD
                    }).dropna(subset=["open"])

                    for _, row in agg.iterrows():
                        td_str = row["_orig_date"]
                        trade_date = f"{td_str[:4]}-{td_str[4:6]}-{td_str[6:8]}"
                        vol = self.safe_float(row["volume"])
                        vol = int(vol) if vol is not None else None
                        rows.append((
                            trade_date,
                            symbol,
                            self.safe_float(row["open"]),
                            self.safe_float(row["close"]),
                            self.safe_float(row["high"]),
                            self.safe_float(row["low"]),
                            vol,
                            self.safe_float(row["amount"]),
                            0,  # amplitude（miniQMT 不提供）
                            0,  # pct_change（miniQMT 不提供）
                            0,  # change（miniQMT 不提供）
                            0,  # turnover（miniQMT 不提供）
                        ))

                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=rows,
                    last_key=last_key,
                    elapsed_sec=time.time() - t0,
                )
            except Exception as e:
                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=[],
                    last_key=last_key,
                    elapsed_sec=time.time() - t0,
                    error=f"{stock_code} 聚合K线抓取失败: {e}",
                )

    # ============== 期货持仓 ==============

    def _fetch_futures_position(
        self,
        payload: FetchPayload,
        policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """抓取期货持仓数据。

        遍历 symbols 逐合约调用 xtdata.get_instrument_detail 获取合约详情，
        提取持仓相关字段（LongPosition/ShortPosition/ExchangeID 等）。

        表 schema: (trade_date, symbol, long_position, short_position,
                    long_volume, short_volume, exchange, data_source)
        quality_flag 有 DEFAULT 1，不返回。

        Args:
            payload: 下载请求（symbols 为期货合约代码列表，如 ['IF2406.CF']）
            policy: 调用策略

        Yields:
            FetchResult: 每个合约一批
        """
        from xtquant import xtdata

        table = payload.table or "c1_market.futures_position"
        columns = [
            "trade_date", "symbol", "long_position", "short_position",
            "long_volume", "short_volume", "exchange", "data_source",
        ]
        trade_date = payload.end.isoformat()
        symbols = payload.symbols or []
        last_key = self._date_to_str(payload.end)

        for stock_code in symbols:
            t0 = time.time()
            try:
                detail = self._call_with_policy(
                    xtdata.get_instrument_detail, policy, stock_code,
                )
                rows = []
                if detail:
                    symbol = self._stock_to_symbol(stock_code)
                    exchange = detail.get("ExchangeID", "")
                    long_pos = self.safe_float(detail.get("LongPosition"))
                    short_pos = self.safe_float(detail.get("ShortPosition"))
                    long_vol = self.safe_float(detail.get("LongVolume"))
                    short_vol = self.safe_float(detail.get("ShortVolume"))
                    rows.append((
                        trade_date,
                        symbol,
                        int(long_pos) if long_pos is not None else None,
                        int(short_pos) if short_pos is not None else None,
                        int(long_vol) if long_vol is not None else None,
                        int(short_vol) if short_vol is not None else None,
                        exchange,
                        "miniqmt",
                    ))
                yield FetchResult(
                    table=table, columns=columns, rows=rows,
                    last_key=last_key, elapsed_sec=time.time() - t0,
                )
            except Exception as e:
                yield FetchResult(
                    table=table, columns=columns, rows=[],
                    last_key=last_key, elapsed_sec=time.time() - t0,
                    error=f"抓取失败: {e}",
                )

    # ============== 股东数据 ==============

    def _fetch_shareholder(
        self,
        payload: FetchPayload,
        policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """抓取股东数据（十大股东 / 股东人数）。

        使用 xtdata.get_financial_data(table_list=['十大股东','股东人数'])。
        优先提取"股东人数"表的截止日期与股东户数，映射到 shareholder 表 schema。
        表 schema: (symbol, end_date, holder_count, data_source)
        quality_flag 有 DEFAULT 1，不返回。

        Args:
            payload: 下载请求
            policy: 调用策略

        Yields:
            FetchResult: 每个股票一批
        """
        from xtquant import xtdata

        table = payload.table or "c3_fundamental.shareholder"
        columns = ["symbol", "end_date", "holder_count", "data_source"]
        start_str = self._date_to_str(payload.start)
        end_str = self._date_to_str(payload.end)

        try:
            symbols = payload.symbols
            if not symbols:
                symbols = self._call_with_policy(
                    xtdata.get_stock_list_in_sector, policy, "沪深A股"
                )
        except Exception as e:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=0.0, error=f"获取标的清单失败: {e}",
            )
            return

        last_key = end_str
        for stock_code in symbols:
            t0 = time.time()
            try:
                self._call_with_policy(
                    xtdata.download_financial_data2, policy,
                    [stock_code], '', start_str, end_str,
                )
                fd = self._call_with_policy(
                    xtdata.get_financial_data, policy,
                    [stock_code], ['十大股东', '股东人数'],
                    start_str, end_str, 'report_time',
                )
                rows = []
                stock_data = fd.get(stock_code) if fd else None
                if stock_data:
                    symbol = self._stock_to_symbol(stock_code)
                    # 优先取"股东人数"表
                    holder_df = stock_data.get('股东人数')
                    if holder_df is not None and len(holder_df) > 0:
                        for _, row in holder_df.iterrows():
                            # 截止日期：尝试多种列名
                            end_date = None
                            for key in ('date', 'enddate', 'end_date', '报告期'):
                                v = row.get(key)
                                if v is not None:
                                    end_date = str(v)[:10]
                                    break
                            # 股东户数：尝试多种列名
                            holder_count = None
                            for key in ('holder_number', '股东户数', 'holder_num', '股东人数'):
                                v = row.get(key)
                                if v is not None:
                                    holder_count = self.safe_float(v)
                                    break
                            rows.append((symbol, end_date, holder_count, "miniqmt"))
                yield FetchResult(
                    table=table, columns=columns, rows=rows,
                    last_key=last_key, elapsed_sec=time.time() - t0,
                )
            except Exception as e:
                yield FetchResult(
                    table=table, columns=columns, rows=[],
                    last_key=last_key, elapsed_sec=time.time() - t0,
                    error=f"抓取失败: {e}",
                )

    # ============== 盈利预测 ==============

    def _fetch_earnings_forecast(
        self,
        payload: FetchPayload,
        policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """抓取盈利预测数据（QMT ProfitForecast 表）。

        使用 xtdata.get_financial_data(table_list=['ProfitForecast'])。
        列名从 DataFrame 动态提取（与 _fetch_financial_statement 同模式）。

        Args:
            payload: 下载请求
            policy: 调用策略

        Yields:
            FetchResult: 每个股票一批
        """
        yield from self._fetch_financial_by_table(payload, policy, "ProfitForecast")

    # ============== 业绩快报 ==============

    def _fetch_express_report(
        self,
        payload: FetchPayload,
        policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """抓取业绩快报数据（QMT Performance 表）。

        使用 xtdata.get_financial_data(table_list=['Performance'])。
        列名从 DataFrame 动态提取（与 _fetch_financial_statement 同模式）。

        Args:
            payload: 下载请求
            policy: 调用策略

        Yields:
            FetchResult: 每个股票一批
        """
        yield from self._fetch_financial_by_table(payload, policy, "Performance")

    def _fetch_financial_by_table(
        self,
        payload: FetchPayload,
        policy: SourcePolicy,
        table_list: str,
    ) -> Iterator[FetchResult]:
        """通用财务数据抓取（按指定 table_list），列名动态提取。

        与 _fetch_financial_statement 同模式，但 table_list 由调用方指定，
        目标表名取 payload.table 或 c3_fundamental.<table_list 小写>。

        Args:
            payload: 下载请求
            policy: 调用策略
            table_list: xtquant 报表名（如 "ProfitForecast"/"Performance"）

        Yields:
            FetchResult: 每个股票一批
        """
        from xtquant import xtdata

        table = payload.table or f"c3_fundamental.{table_list.lower()}"
        start_str = self._date_to_str(payload.start)
        end_str = self._date_to_str(payload.end)

        try:
            symbols = payload.symbols
            if not symbols:
                symbols = self._call_with_policy(
                    xtdata.get_stock_list_in_sector, policy, "沪深A股"
                )
        except Exception as e:
            yield FetchResult(
                table=table, columns=[], rows=[], last_key="",
                elapsed_sec=0.0, error=f"获取标的清单失败: {e}",
            )
            return

        last_key = end_str
        for stock_code in symbols:
            t0 = time.time()
            try:
                self._call_with_policy(
                    xtdata.download_financial_data2, policy,
                    [stock_code], '', start_str, end_str,
                )
                fd = self._call_with_policy(
                    xtdata.get_financial_data, policy,
                    [stock_code], [table_list], start_str, end_str, 'report_time',
                )
                rows = []
                columns = ["symbol"]
                stock_data = fd.get(stock_code) if fd else None
                if stock_data and table_list in stock_data:
                    df = stock_data[table_list]
                    if df is not None and len(df) > 0:
                        symbol = self._stock_to_symbol(stock_code)
                        col_names = list(df.columns)
                        for _, row in df.iterrows():
                            row_values = []
                            for col in col_names:
                                v = row.get(col)
                                if col in ('date', 'announce_date', 'report_date', 'enddate'):
                                    row_values.append(str(v) if v is not None else None)
                                else:
                                    row_values.append(self.safe_float(v))
                            rows.append(tuple([symbol] + row_values))
                        columns = ["symbol"] + col_names
                yield FetchResult(
                    table=table, columns=columns, rows=rows,
                    last_key=last_key, elapsed_sec=time.time() - t0,
                )
            except Exception as e:
                yield FetchResult(
                    table=table, columns=["symbol"], rows=[],
                    last_key=last_key, elapsed_sec=time.time() - t0,
                    error=f"抓取失败: {e}",
                )

    # ============== 分红送股 ==============

    def _fetch_dividend(
        self,
        payload: FetchPayload,
        policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """抓取分红送股数据。

        遍历 symbols 调用 xtdata.get_divid_factors 获取除权除息信息。
        表 schema: (trade_date, symbol, divid_per_share, split_per_share,
                    funds_per_share, data_source)

        Args:
            payload: 下载请求（start/end 用于过滤日期范围）
            policy: 调用策略

        Yields:
            FetchResult: 每个股票一批
        """
        from xtquant import xtdata

        table = payload.table or "c3_fundamental.dividend"
        columns = [
            "trade_date", "symbol", "divid_per_share",
            "split_per_share", "funds_per_share", "data_source",
        ]
        start_date = payload.start.isoformat()
        end_date = payload.end.isoformat()

        try:
            symbols = payload.symbols
            if not symbols:
                symbols = self._call_with_policy(
                    xtdata.get_stock_list_in_sector, policy, "沪深A股"
                )
        except Exception as e:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=0.0, error=f"获取标的清单失败: {e}",
            )
            return

        last_key = self._date_to_str(payload.end)
        for stock_code in symbols:
            t0 = time.time()
            try:
                df = self._call_with_policy(
                    xtdata.get_divid_factors, policy, stock_code,
                )
                rows = []
                if df is not None and len(df) > 0:
                    symbol = self._stock_to_symbol(stock_code)
                    for _, row in df.iterrows():
                        ts = row.get("time")
                        if ts is None:
                            continue
                        trade_date = datetime.datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
                        if trade_date < start_date or trade_date > end_date:
                            continue
                        rows.append((
                            trade_date,
                            symbol,
                            self.safe_float(row.get("divid_per_share")),
                            self.safe_float(row.get("split_per_share")),
                            self.safe_float(row.get("funds_per_share")),
                            "miniqmt",
                        ))
                yield FetchResult(
                    table=table, columns=columns, rows=rows,
                    last_key=last_key, elapsed_sec=time.time() - t0,
                )
            except Exception as e:
                yield FetchResult(
                    table=table, columns=columns, rows=[],
                    last_key=last_key, elapsed_sec=time.time() - t0,
                    error=f"抓取失败: {e}",
                )

    # ============== 期权波动率曲面（占位） ==============

    def _fetch_option_iv_surface(
        self,
        payload: FetchPayload,
        policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """期权波动率曲面数据占位方法。

        xtquant 不直接支持期权 IV 曲面数据，需通过 xtquant 订阅获取，
        暂未实现。返回 error 占位。

        Yields:
            FetchResult: 含 error 的占位结果
        """
        yield FetchResult(
            table=payload.table or "c1_market.option_iv_surface",
            columns=[], rows=[], last_key="",
            elapsed_sec=0.0,
            error="期权波动率曲面数据需通过xtquant订阅获取，暂未实现",
        )

    # ============== 可转债波动率（占位） ==============

    def _fetch_convertible_bond_iv(
        self,
        payload: FetchPayload,
        policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """可转债波动率数据占位方法。

        xtquant 不直接支持可转债 IV 数据，暂未实现。返回 error 占位。

        Yields:
            FetchResult: 含 error 的占位结果
        """
        yield FetchResult(
            table=payload.table or "c1_market.convertible_bond_iv",
            columns=[], rows=[], last_key="",
            elapsed_sec=0.0,
            error="可转债波动率数据暂未实现",
        )

    # ============== 期货期限结构 ==============

    def _fetch_futures_term_structure(
        self,
        payload: FetchPayload,
        policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """抓取期货期限结构数据。

        使用 xtdata.get_market_data_ex 获取多个合约的收盘价，
        构建近月/次月价格对及基差。
        表 schema: (trade_date, symbol, front_contract, next_contract,
                    front_price, next_price, basis, data_source)
        quality_flag 有 DEFAULT 1，不返回。

        symbols 为期货合约列表，按到期日排序后取相邻两月构建期限结构。

        Args:
            payload: 下载请求
            policy: 调用策略

        Yields:
            FetchResult: 每个品种一批
        """
        from xtquant import xtdata

        table = payload.table or "c1_market.futures_term_structure"
        columns = [
            "trade_date", "symbol", "front_contract", "next_contract",
            "front_price", "next_price", "basis", "data_source",
        ]

        try:
            start_str = self._date_to_str(payload.start)
            end_str = self._date_to_str(payload.end)
        except Exception as e:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=0.0, error=f"日期转换失败: {e}",
            )
            return

        symbols = payload.symbols or []
        last_key = end_str
        trade_date = payload.end.isoformat()

        # 逐对相邻合约构建期限结构
        for i in range(len(symbols) - 1):
            front_code = symbols[i]
            next_code = symbols[i + 1]
            t0 = time.time()
            try:
                # 下载并读取近月合约收盘价
                self._call_with_policy(
                    xtdata.download_history_data, policy,
                    front_code, "1d", start_str, end_str,
                )
                front_data = self._call_with_policy(
                    xtdata.get_market_data_ex, policy,
                    [], [front_code], "1d", start_str, end_str,
                )
                # 下载并读取次月合约收盘价
                self._call_with_policy(
                    xtdata.download_history_data, policy,
                    next_code, "1d", start_str, end_str,
                )
                next_data = self._call_with_policy(
                    xtdata.get_market_data_ex, policy,
                    [], [next_code], "1d", start_str, end_str,
                )

                rows = []
                front_df = front_data.get(front_code) if front_data else None
                next_df = next_data.get(next_code) if next_data else None
                if front_df is not None and len(front_df) > 0:
                    front_close = self.safe_float(front_df["close"].iloc[-1])
                else:
                    front_close = None
                if next_df is not None and len(next_df) > 0:
                    next_close = self.safe_float(next_df["close"].iloc[-1])
                else:
                    next_close = None

                basis = None
                if front_close is not None and next_close is not None:
                    basis = round(front_close - next_close, 4)

                symbol = self._stock_to_symbol(front_code)
                rows.append((
                    trade_date, symbol,
                    self._stock_to_symbol(front_code),
                    self._stock_to_symbol(next_code),
                    front_close, next_close, basis,
                    "miniqmt",
                ))
                yield FetchResult(
                    table=table, columns=columns, rows=rows,
                    last_key=last_key, elapsed_sec=time.time() - t0,
                )
            except Exception as e:
                yield FetchResult(
                    table=table, columns=columns, rows=[],
                    last_key=last_key, elapsed_sec=time.time() - t0,
                    error=f"抓取失败: {e}",
                )

    # ============== 分笔数据 ==============

    def _fetch_tick_data(
        self,
        payload: FetchPayload,
        policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """抓取分笔（Tick）数据，写入 c1_market.tick_history。

        使用 xtdata.get_market_data_ex(period='tick') 获取分笔行情。
        tick 数据量很大，每次只取 1 只股票 1 天。
        统一写入 tick_history 表（百度云历史 + QMT 增量），百度云历史无 bid/ask 列为 NULL。
        表 schema: (trade_date, timestamp, symbol, market_type, price, volume,
                    amount, direction, data_source, bid_price, ask_price,
                    bid_volume, ask_volume, quality_flag)

        Args:
            payload: 下载请求
            policy: 调用策略

        Yields:
            FetchResult: 每个股票一批
        """
        from xtquant import xtdata

        table = payload.table or "c1_market.tick_history"
        columns = [
            "trade_date", "timestamp", "symbol", "market_type", "price",
            "volume", "amount", "direction", "data_source",
            "bid_price", "ask_price", "bid_volume", "ask_volume",
        ]

        try:
            start_str = self._date_to_str(payload.start)
            end_str = self._date_to_str(payload.end)
        except Exception as e:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=0.0, error=f"日期转换失败: {e}",
            )
            return

        symbols = payload.symbols or []
        last_key = end_str

        for stock_code in symbols:
            t0 = time.time()
            try:
                # tick 数据量很大，先下载
                self._call_with_policy(
                    xtdata.download_history_data, policy,
                    stock_code, "tick", start_str, end_str,
                )
                data = self._call_with_policy(
                    xtdata.get_market_data_ex, policy,
                    [], [stock_code], "tick", start_str, end_str,
                )

                df = data.get(stock_code) if data else None
                rows = self._parse_tick_rows(df, stock_code, payload.end)
                yield FetchResult(
                    table=table, columns=columns, rows=rows,
                    last_key=last_key, elapsed_sec=time.time() - t0,
                )
            except Exception as e:
                yield FetchResult(
                    table=table, columns=columns, rows=[],
                    last_key=last_key, elapsed_sec=time.time() - t0,
                    error=f"抓取失败: {e}",
                )

    def _parse_tick_rows(self, df, stock_code: str, end_date) -> list[tuple]:
        """解析 tick DataFrame 为行列表（降低 _fetch_tick_data 复杂度）。

        行格式对齐 tick_history 表：
        (trade_date, timestamp, symbol, market_type, price, volume, amount,
         direction, data_source, bid_price, ask_price, bid_volume, ask_volume)

        Args:
            df: xtdata.get_market_data_ex 返回的 DataFrame
            stock_code: 标的代码
            end_date: 结束日期（fallback trade_date）

        Returns:
            行元组列表
        """
        if df is None or len(df) == 0:
            return []
        symbol = self._stock_to_symbol(stock_code)
        market_type = self._detect_market_type(stock_code)
        rows: list[tuple] = []
        for ts, row in df.iterrows():
            s = str(int(ts))
            trade_date, timestamp = self._format_tick_timestamp(s, end_date)
            price = self.safe_float(row.get("price") or row.get("last"))
            vol = self.safe_float(row.get("volume"))
            vol = int(vol) if vol is not None else None
            amt = self.safe_float(row.get("amount"))
            rows.append((
                trade_date, timestamp, symbol, market_type, price, vol, amt,
                "",  # direction: QMT 不提供买卖方向
                "miniqmt",
                self.safe_float(row.get("bid_price") or row.get("bid1")),
                self.safe_float(row.get("ask_price") or row.get("ask1")),
                self.safe_float(row.get("bid_volume") or row.get("bidSize1")),
                self.safe_float(row.get("ask_volume") or row.get("askSize1")),
            ))
        return rows

    @staticmethod
    def _detect_market_type(stock_code: str) -> str:
        """根据代码后缀和前缀推断 market_type。

        .BJ → stock_bj；指数(000/399.SH/SZ) → index；
        ETF(15/51/52) → etf；可转债(11/12) → cb；其余 → stock。
        """
        code = stock_code.split(".")[0].zfill(6)
        suffix = stock_code.split(".")[-1] if "." in stock_code else ""
        if suffix == "BJ":
            return "stock_bj"
        prefix = code[:3]
        if prefix in ("399",) or (prefix == "000" and suffix == "SH"):
            return "index"
        if prefix[:2] in ("15", "51", "52"):
            return "etf"
        if prefix[:2] in ("11", "12"):
            return "cb"
        return "stock"

    @staticmethod
    def _format_tick_timestamp(s: str, end_date) -> tuple[str, str]:
        """格式化 tick 时间戳为 (trade_date, timestamp) 字符串。

        tick 索引为 YYYYMMDDHHMMSS 格式整数或时间戳。

        Args:
            s: 时间戳数字字符串
            end_date: fallback 日期

        Returns:
            (trade_date, timestamp) 元组
        """
        if len(s) >= 8:
            trade_date = f"{s[:4]}-{s[4:6]}-{s[6:8]}"
        else:
            trade_date = end_date.isoformat()
        if len(s) >= 14:
            timestamp = (
                f"{s[:4]}-{s[4:6]}-{s[6:8]} "
                f"{s[8:10]}:{s[10:12]}:{s[12:14]}"
            )
        else:
            timestamp = trade_date + " 00:00:00"
        return trade_date, timestamp

    # ============== 集合竞价快照（占位） ==============

    def _fetch_auction_snapshot(
        self,
        payload: FetchPayload,
        policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """集合竞价快照占位方法。

        集合竞价快照需实时订阅（9:15-9:25），暂未实现。返回 error 占位。

        Yields:
            FetchResult: 含 error 的占位结果
        """
        yield FetchResult(
            table=payload.table or "c1_market.auction_snapshot",
            columns=[], rows=[], last_key="",
            elapsed_sec=0.0,
            error="集合竞价快照需实时订阅，暂未实现",
        )

    # ============== 指数行情 ==============

    def _fetch_index_quote(
        self,
        payload: FetchPayload,
        policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """抓取指数实时行情快照。

        使用 xtdata.get_market_data_ex(period='1d') 获取指数行情。
        symbols 格式如 '000001.SH'。
        表 schema: (trade_date, timestamp, symbol, price, volume, amount, data_source)
        quality_flag 有 DEFAULT 1，不返回。

        Args:
            payload: 下载请求
            policy: 调用策略

        Yields:
            FetchResult: 每个指数一批
        """
        from xtquant import xtdata

        table = payload.table or "c1_market.index_quote"
        columns = [
            "trade_date", "timestamp", "symbol",
            "price", "volume", "amount", "data_source",
        ]

        try:
            start_str = self._date_to_str(payload.start)
            end_str = self._date_to_str(payload.end)
        except Exception as e:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=0.0, error=f"日期转换失败: {e}",
            )
            return

        symbols = payload.symbols or []
        last_key = end_str

        for index_code in symbols:
            t0 = time.time()
            try:
                self._call_with_policy(
                    xtdata.download_history_data, policy,
                    index_code, "1d", start_str, end_str,
                )
                data = self._call_with_policy(
                    xtdata.get_market_data_ex, policy,
                    [], [index_code], "1d", start_str, end_str,
                )

                rows = []
                df = data.get(index_code) if data else None
                if df is not None and len(df) > 0:
                    symbol = index_code  # 指数代码保留后缀
                    # 取最后一条作为快照
                    last_idx = df.index[-1]
                    s = str(int(last_idx))
                    if len(s) >= 8:
                        trade_date = f"{s[:4]}-{s[4:6]}-{s[6:8]}"
                    else:
                        trade_date = payload.end.isoformat()
                    timestamp = trade_date + " 15:00:00"
                    close = self.safe_float(df["close"].iloc[-1])
                    vol = self.safe_float(df["volume"].iloc[-1])
                    vol = int(vol) if vol is not None else 0
                    amt = self.safe_float(df["amount"].iloc[-1])
                    rows.append((
                        trade_date, timestamp, symbol,
                        close, vol, amt, "miniqmt",
                    ))
                yield FetchResult(
                    table=table, columns=columns, rows=rows,
                    last_key=last_key, elapsed_sec=time.time() - t0,
                )
            except Exception as e:
                yield FetchResult(
                    table=table, columns=columns, rows=[],
                    last_key=last_key, elapsed_sec=time.time() - t0,
                    error=f"抓取失败: {e}",
                )

    # ============== 股票列表 ==============

    def _fetch_stock_list(
        self,
        payload: FetchPayload,
        policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """抓取股票列表（全量刷新）。

        使用 xtdata.get_stock_list_in_sector('沪深A股') 获取全A股列表，
        配合 xtdata.get_instrument_detail 获取个股详情（名称/上市日/行业等）。
        表 schema: (ts_code, symbol, name, area, industry, fullname, enname,
                    cn_spell, market, exchange, currency, list_status,
                    list_date, delist_date, hs_hold, actual_controller,
                    controller_type)

        Args:
            payload: 下载请求
            policy: 调用策略

        Yields:
            FetchResult: 一批（全部股票）
        """
        from xtquant import xtdata

        table = payload.table or "c1_market.stock_list"
        columns = [
            "ts_code", "symbol", "name", "area", "industry", "fullname",
            "enname", "cn_spell", "market", "exchange", "currency",
            "list_status", "list_date", "delist_date", "hs_hold",
            "actual_controller", "controller_type",
        ]
        t0 = time.time()
        try:
            stock_codes = self._call_with_policy(
                xtdata.get_stock_list_in_sector, policy, "沪深A股"
            )
            rows = []
            if stock_codes:
                for stock_code in stock_codes:
                    symbol = self._stock_to_symbol(stock_code)
                    # 获取个股详情
                    try:
                        detail = self._call_with_policy(
                            xtdata.get_instrument_detail, policy, stock_code,
                        )
                    except Exception:
                        detail = None
                    name = ""
                    exchange = ""
                    list_date = None
                    delist_date = None
                    industry = ""
                    if detail:
                        name = detail.get("InstrumentName", "")
                        exchange = detail.get("ExchangeID", "")
                        # 上市日期：CreateTime / OpenDate 格式 YYYYMMDD
                        open_date = detail.get("OpenDate") or detail.get("CreateTime")
                        if open_date:
                            ds = str(open_date)
                            if len(ds) >= 8:
                                list_date = f"{ds[:4]}-{ds[4:6]}-{ds[6:8]}"
                        expire = detail.get("ExpireDate")
                        if expire:
                            ds = str(expire)
                            if len(ds) >= 8:
                                delist_date = f"{ds[:4]}-{ds[4:6]}-{ds[6:8]}"
                    rows.append((
                        stock_code,  # ts_code
                        symbol,
                        name,
                        "",  # area
                        industry,
                        "",  # fullname
                        "",  # enname
                        "",  # cn_spell
                        "A股",  # market
                        exchange,
                        "CNY",  # currency
                        "上市",  # list_status
                        list_date,
                        delist_date,
                        "",  # hs_hold
                        "",  # actual_controller
                        "",  # controller_type
                    ))
            yield FetchResult(
                table=table, columns=columns, rows=rows,
                last_key=self._date_to_str(payload.end),
                elapsed_sec=time.time() - t0,
            )
        except Exception as e:
            yield FetchResult(
                table=table, columns=columns, rows=[],
                last_key="", elapsed_sec=time.time() - t0,
                error=f"获取股票列表失败: {e}",
            )

    # ============== 辅助方法 ==============

    @staticmethod
    def _date_to_str(d: datetime.date) -> str:
        """datetime.date -> "YYYYMMDD" 字符串。"""
        return d.strftime("%Y%m%d")

    @staticmethod
    def _ts_to_date(ts_ms) -> str:
        """毫秒时间戳 -> "YYYY-MM-DD" 字符串（按 UTC 解释，避免本地时区跨日）。

        xtquant 返回的 time 列为中国市场收盘后的毫秒时间戳，但 trade_date
        只取日期部分，使用 UTC 解释可避免本地时区偏移导致跨日。
        """
        return datetime.datetime.utcfromtimestamp(ts_ms / 1000).strftime("%Y-%m-%d")

    @staticmethod
    def _ts_to_datetime(ts_ms) -> str:
        """毫秒时间戳 -> "YYYY-MM-DD HH:MM:SS" 字符串（按 UTC 解释）。

        分钟K线需要完整时间戳，用于 trade_time 列。
        """
        return datetime.datetime.utcfromtimestamp(ts_ms / 1000).strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _stock_to_symbol(stock_code: str) -> str:
        """stock_code 去后缀："000001.SZ" -> "000001"。"""
        return stock_code.split(".")[0]

    @staticmethod
    def safe_float(v) -> float | None:
        """转 float，失败或 NaN 返回 None。"""
        if v is None:
            return None
        try:
            f = float(v)
        except (TypeError, ValueError):
            return None
        if f != f:  # NaN
            return None
        return f
