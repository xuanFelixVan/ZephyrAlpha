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
            "kline_index",
            "adj_factor",
            "kline_daily_hfq",
            "kline_weekly",
            "kline_monthly",
            # 以下为新增能力（MOD-L00-004 fetch 路由扩展）
            "kline_hk_daily",
            "kline_futures",
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
            # 以下为第二批新增能力（15 个数据下载能力）
            "kline_cb",
            "option_kline",
            "option_greeks",
            "index_weight",
            "sector_list",
            "l2_tick",
            "auction_data",
            "futures_kline_qmt",
            "hk_kline",
            "kline_us_daily",
            "etf_nav",
            "repurchase",
            "margin_trading_qmt",
            "dragon_tiger_qmt",
            "block_trade_qmt",
            # 以下为第三批新增能力（ETF/LOF分钟K线 + 后复权周月K）
            "kline_etf_1min",
            "kline_etf_5min",
            "kline_etf_15min",
            "kline_etf_30min",
            "kline_etf_60min",
            "kline_lof_1min",
            "kline_lof_5min",
            "kline_lof_15min",
            "kline_lof_30min",
            "kline_lof_60min",
            "kline_weekly_hfq",
            "kline_monthly_hfq",
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
            "kline_daily": ("1d", "沪深A股"),
            "kline_1min": ("1m", "沪深A股"),
            "kline_5min": ("5m", "沪深A股"),
            "kline_15min": ("15m", "沪深A股"),
            "kline_30min": ("30m", "沪深A股"),
            "kline_60min": ("1h", "沪深A股"),
            "kline_etf_1min": ("1m", "ETF"),
            "kline_etf_5min": ("5m", "ETF"),
            "kline_etf_15min": ("15m", "ETF"),
            "kline_etf_30min": ("30m", "ETF"),
            "kline_etf_60min": ("1h", "ETF"),
            "kline_lof_1min": ("1m", "LOF"),
            "kline_lof_5min": ("5m", "LOF"),
            "kline_lof_15min": ("15m", "LOF"),
            "kline_lof_30min": ("30m", "LOF"),
            "kline_lof_60min": ("1h", "LOF"),
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
            _period, _sector = _KLINE_CAPABILITIES[capability]
            yield from self._fetch_kline(payload, policy, _period, sector=_sector)
        elif capability == "kline_daily_hfq":
            # 后复权日K：复用 _fetch_kline，传 dividend_type="back"
            yield from self._fetch_kline(payload, policy, "1d", dividend_type="back")
        elif capability == "kline_weekly":
            # 周K：miniQMT 不支持 1w 周期，从日K聚合
            yield from self._fetch_kline_aggregated(payload, policy, "W")
        elif capability == "kline_monthly":
            # 月K：miniQMT 不支持 1M 周期，从日K聚合（pandas>=2.2 需用 'ME' 替代 'M'）
            yield from self._fetch_kline_aggregated(payload, policy, "ME")
        elif capability == "kline_weekly_hfq":
            # 后复权周K：从后复权日K聚合
            yield from self._fetch_kline_aggregated(payload, policy, "W", dividend_type="back")
        elif capability == "kline_monthly_hfq":
            # 后复权月K：从后复权日K聚合
            yield from self._fetch_kline_aggregated(payload, policy, "ME", dividend_type="back")
        elif capability == "adj_factor":
            yield from self._fetch_adj_factor(payload, policy)
        elif capability in _FINANCIAL_CAPABILITIES:
            yield from self._fetch_financial_statement(payload, policy, _FINANCIAL_CAPABILITIES[capability])
        elif capability == "index_constituent":
            yield from self._fetch_index_constituent(payload, policy)
        elif capability == "kline_index":
            yield from self._fetch_kline_index(payload, policy)
        # ---- 新增能力路由（MOD-L00-004 fetch 路由扩展）----
        elif capability == "kline_hk_daily":
            # 港股日K：复用 _fetch_kline，symbols 格式如 '00700.HK'
            yield from self._fetch_kline(payload, policy, "1d")
        elif capability == "kline_futures":
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
        # ---- 第二批新增能力路由（15 个数据下载能力）----
        elif capability == "kline_cb":
            # 可转债K线：get_market_data_ex，symbols 格式如 '113001.SH'
            yield from self._fetch_kline_cb(payload, policy)
        elif capability == "option_kline":
            # 期权K线：get_market_data_ex，symbols 格式如 '10000001.SH'
            yield from self._fetch_option_kline(payload, policy)
        elif capability == "option_greeks":
            # 期权Greeks：get_option_detail_data + 计算 delta/gamma/theta/vega
            yield from self._fetch_option_greeks(payload, policy)
        elif capability == "index_weight":
            # 指数权重：get_index_weight
            yield from self._fetch_index_weight(payload, policy)
        elif capability == "sector_list":
            # 板块列表：get_stock_list_in_sector / get_sector_list
            yield from self._fetch_sector_list(payload, policy)
        elif capability == "l2_tick":
            # Level-2逐笔：get_l2_quote
            yield from self._fetch_l2_tick(payload, policy)
        elif capability == "auction_data":
            # 集合竞价：get_full_tick 实时快照（写入 auction_snapshot 表）
            yield from self._fetch_auction_data(payload, policy)
        elif capability == "futures_kline_qmt":
            # 期货K线：get_market_data_ex，symbols 格式如 'IF2407.CFFEX'
            yield from self._fetch_kline_futures_qmt(payload, policy)
        elif capability == "hk_kline":
            # 港股K线：get_market_data_ex，symbols 格式如 '00700.HK'
            yield from self._fetch_hk_kline(payload, policy)
        elif capability == "kline_us_daily":
            # 美股K线：get_market_data_ex，symbols 格式如 'AAPL.US'
            yield from self._fetch_us_kline(payload, policy)
        elif capability == "etf_nav":
            # ETF净值：get_etf_info
            yield from self._fetch_etf_nav(payload, policy)
        elif capability == "repurchase":
            # 回购数据：QMT 无直接接口，占位
            yield from self._fetch_repurchase(payload, policy)
        elif capability == "margin_trading_qmt":
            # 融资融券：QMT 无直接接口，占位
            yield from self._fetch_margin_trading_qmt(payload, policy)
        elif capability == "dragon_tiger_qmt":
            # 龙虎榜：QMT 无直接接口，占位
            yield from self._fetch_dragon_tiger_qmt(payload, policy)
        elif capability == "block_trade_qmt":
            # 大宗交易：QMT 无直接接口，占位
            yield from self._fetch_block_trade_qmt(payload, policy)
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
        sector: str = "沪深A股",
    ) -> Iterator[FetchResult]:
        """抓取K线数据（日K/分钟K通用，支持A股/ETF/LOF）。

        步骤：
        1. 若 symbols 为 None，取指定板块全部标的（沪深A股/ETF/LOF）
        2. 对每个 stock_code：download_history_data 下载 -> get_market_data_ex 读取
        3. DataFrame 转 tuple 列表，每个股票作为一批 yield

        period="1d" 时列为 trade_date+symbol+OHLCV+amount（日K）
        period!="1d" 时列为 trade_date+trade_time+symbol+OHLCV+amount（分钟K）

        Args:
            payload: 下载请求
            policy: 调用策略
            period: K线周期（"1d"/"1m"/"5m"/"15m"/"30m"/"60m"）
            dividend_type: 复权类型（"none"=不复权/"back"=后复权），默认 "none"
            sector: 板块名称（"沪深A股"/"ETF"/"LOF"），默认 "沪深A股"

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
                    xtdata.get_stock_list_in_sector, policy, sector
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

    def _fetch_kline_index(
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

        table = payload.table or "c1_market.kline_index"
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
                    rows = self._parse_index_kline_rows(df, symbol, name)

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

    @staticmethod
    def _parse_index_kline_rows(df, symbol, name) -> list:
        """从 DataFrame 构造指数K线行列表。

        日K索引 YYYYMMDD（8位）-> YYYY-MM-DD；
        volume 是 UInt64，负值（某些计算指数）转为 0。
        """
        rows = []
        times = [int(ts) for ts in df.index]
        opens = df["open"].tolist()
        highs = df["high"].tolist()
        lows = df["low"].tolist()
        closes = df["close"].tolist()
        volumes = df["volume"].tolist()
        amounts = df["amount"].tolist()
        for i in range(len(times)):
            s = str(times[i])
            trade_date = f"{s[:4]}-{s[4:6]}-{s[6:8]}"
            vol = MiniQMTProvider.safe_float(volumes[i])
            if vol is not None and vol < 0:
                vol = 0
            vol = int(vol) if vol is not None else 0
            rows.append((
                trade_date,
                symbol,
                name,
                MiniQMTProvider.safe_float(opens[i]),
                MiniQMTProvider.safe_float(highs[i]),
                MiniQMTProvider.safe_float(lows[i]),
                MiniQMTProvider.safe_float(closes[i]),
                vol,
                MiniQMTProvider.safe_float(amounts[i]),
                "miniqmt",  # data_source
            ))
        return rows

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
        dividend_type: str = "none",
    ) -> Iterator[FetchResult]:
        """抓取日K数据并聚合为周K/月K（支持不复权/后复权）。

        miniQMT 不支持直接下载 "1w"/"1M" 周期，需下载日K后用 pandas resample 聚合。
        聚合规则：open=首日、close=末日、high=max、low=min、volume/amount=sum。
        trade_date 取周期内最后交易日的日期。
        amplitude/pct_change/change/turnover 在表中无 DEFAULT，但 miniQMT 不提供，填 0。
        data_source 有 DEFAULT 'local_qfq'，不返回。

        Args:
            payload: 下载请求
            policy: 调用策略
            freq: 聚合频率（"W"=周K，"ME"=月K，pandas>=2.2 用 ME 替代 M）
            dividend_type: 复权类型（"none"=不复权/"back"=后复权），默认 "none"

        Yields:
            FetchResult: 每个股票一批
        """
        from xtquant import xtdata
        import pandas as pd

        is_hfq = (dividend_type == "back")
        if freq == "W":
            table = payload.table or ("c1_market.kline_weekly_hfq" if is_hfq else "c1_market.kline_weekly")
        else:
            table = payload.table or ("c1_market.kline_monthly_hfq" if is_hfq else "c1_market.kline_monthly")

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
                # 读取日K行情（后复权时传 dividend_type='back'，count=-1 表示全部）
                data = self._call_with_policy(
                    xtdata.get_market_data_ex,
                    policy,
                    [], [stock_code], "1d", start_str, end_str, -1, dividend_type,
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
                from xtquant import xtdata
                import pandas as pd
                symbol = self._stock_to_symbol(stock_code)
                # 1. 获取合约详情（exchange 等静态信息）
                detail = self._call_with_policy(
                    xtdata.get_instrument_detail, policy, stock_code,
                )
                exchange = ""
                if detail:
                    exchange = detail.get("ExchangeID", "")
                # 2. 下载并获取历史日K线
                try:
                    self._call_with_policy(
                        xtdata.download_history_data, policy,
                        stock_code, "1d", start_str, end_str,
                    )
                except Exception as e:
                    self._log.debug(f"download_history_data({stock_code}) 失败: {e}")
                kline_data = self._call_with_policy(
                    xtdata.get_market_data_ex, policy,
                    [], [stock_code], "1d", start_str, end_str,
                )
                kline_df = kline_data.get(stock_code) if kline_data else None
                rows = []
                if kline_df is not None and len(kline_df) > 0:
                    # 尝试从 K线获取持仓量字段
                    oi_col = None
                    for col in ("open_interest", "position", "Position"):
                        if col in kline_df.columns:
                            oi_col = col
                            break
                    if oi_col:
                        for dt in kline_df.index:
                            oi = self.safe_float(kline_df.loc[dt, oi_col])
                            rows.append((
                                pd.Timestamp(dt).strftime("%Y-%m-%d"),
                                symbol,
                                int(oi) if oi is not None else None,
                                None, None, None,
                                exchange, "miniqmt",
                            ))
                    else:
                        # K线无持仓量字段，fallback 到当前快照
                        if detail:
                            long_pos = self.safe_float(detail.get("LongPosition"))
                            short_pos = self.safe_float(detail.get("ShortPosition"))
                            long_vol = self.safe_float(detail.get("LongVolume"))
                            short_vol = self.safe_float(detail.get("ShortVolume"))
                            rows.append((
                                payload.end.isoformat(), symbol,
                                int(long_pos) if long_pos is not None else None,
                                int(short_pos) if short_pos is not None else None,
                                int(long_vol) if long_vol is not None else None,
                                int(short_vol) if short_vol is not None else None,
                                exchange, "miniqmt",
                            ))
                else:
                    # 无 K线数据，fallback 到当前快照
                    if detail:
                        long_pos = self.safe_float(detail.get("LongPosition"))
                        short_pos = self.safe_float(detail.get("ShortPosition"))
                        long_vol = self.safe_float(detail.get("LongVolume"))
                        short_vol = self.safe_float(detail.get("ShortVolume"))
                        rows.append((
                            payload.end.isoformat(), symbol,
                            int(long_pos) if long_pos is not None else None,
                            int(short_pos) if short_pos is not None else None,
                            int(long_vol) if long_vol is not None else None,
                            int(short_vol) if short_vol is not None else None,
                            exchange, "miniqmt",
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

        table = payload.table or "c3_fundamental.shareholder_count"
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

    # ============== 期权波动率曲面 ==============

    def _get_option_detail_safe(self, opt_code: str, policy) -> dict | None:
        """安全获取期权合约详情（绕过 xtquant get_option_detail_data bug）。

        xtquant 的 get_option_detail_data 内部代码：
            ret['OptUndlCodeFull'] = ret['OptUndlUniCode'] + '.' + ret['OptUndlMarket']
        当 OptUndlUniCode 为 None 时崩溃（TypeError: NoneType + str）。

        本方法改用 get_instrument_detail 获取详情，并解析出原有字段：
        - Underlying: 标的代码（如 "588000.SH"）
        - ExercisePrice: 行权价（float）
        - EndDelivDate: 到期日（如 "20260826"）
        - OptType: 1=认购(call), 0=认沽(put)

        从 InstrumentName 解析行权价和认购/认沽：
        - "科创50购8月2400" → 购=call, 2400/1000=2.4
        - "沪深300ETF沽7月5500" → 沽=put, 5500/1000=5.5

        从 ProductID 解析标的代码：
        - "科创50(588000)" → 588000 + 交易所后缀

        Args:
            opt_code: 期权合约代码（如 "10011948.SHO"）
            policy: 调用策略

        Returns:
            dict: {Underlying, ExercisePrice, EndDelivDate, OptType} 或 None
        """
        import re
        from xtquant import xtdata

        detail = self._call_with_policy(
            xtdata.get_instrument_detail, policy, opt_code,
        )
        if not detail:
            return None

        name = detail.get("InstrumentName", "")
        product_id = detail.get("ProductID", "")
        expire_date = detail.get("ExpireDate", "")
        exchange = detail.get("ExchangeID", "")

        # 解析认购/认沽：购=call(1), 沽=put(0)
        opt_type = 1 if "购" in name else 0

        # 解析行权价：从名称末尾提取数字 / 1000
        strike = None
        m = re.search(r"(\d{3,5})$", name)
        if m:
            strike = int(m.group(1)) / 1000.0

        # 解析标的代码：从 ProductID "科创50(588000)" 提取 588000
        underlying = ""
        m2 = re.search(r"\((\d{6})\)", product_id)
        if m2:
            code = m2.group(1)
            # 根据交易所确定后缀：SHO→SH, SZO→SZ
            if exchange in ("SHO", "SH"):
                underlying = f"{code}.SH"
            elif exchange in ("SZO", "SZ"):
                underlying = f"{code}.SZ"
            else:
                underlying = code

        return {
            "Underlying": underlying,
            "ExercisePrice": strike,
            "EndDelivDate": str(expire_date) if expire_date else "",
            "OptType": opt_type,
        }

    def _fetch_option_iv_surface(
        self,
        payload: FetchPayload,
        policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """抓取期权隐含波动率（IV）曲面数据。

        使用 xtdata.get_option_detail_data 获取期权合约详情（行权价/到期日/
        标的/期权类型），用 xtdata.get_market_data_ex 获取期权与标的收盘价，
        结合 Black-Scholes 模型 + Newton-Raphson 迭代反解隐含波动率。
        表 schema: (trade_date, symbol, underlying, strike, expiry, opt_type,
                    iv, data_source)

        Args:
            payload: 下载请求（symbols为期权合约代码列表）
            policy: 调用策略

        Yields:
            FetchResult: 每个期权一批
        """
        import math

        table = payload.table or "c1_market.option_iv_surface"
        columns = [
            "trade_date", "symbol", "underlying", "strike", "expiry",
            "opt_type", "iv", "data_source",
        ]
        trade_date = payload.end.isoformat()
        symbols = payload.symbols or []
        last_key = self._date_to_str(payload.end)

        try:
            start_str = self._date_to_str(payload.start)
            end_str = self._date_to_str(payload.end)
        except Exception as e:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=0.0, error=f"日期转换失败: {e}",
            )
            return

        # 标准正态分布 PDF / CDF
        def _pdf(x):
            return math.exp(-x ** 2 / 2) / math.sqrt(2 * math.pi)

        def _cdf(x):
            return 0.5 * (1 + math.erf(x / math.sqrt(2)))

        def _bs_price(S, K, T, r, sigma, opt_type):
            """Black-Scholes 期权理论价格。"""
            if S <= 0 or K <= 0 or T <= 0 or sigma <= 0:
                return None
            d1 = (math.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * math.sqrt(T))
            d2 = d1 - sigma * math.sqrt(T)
            if opt_type == "call":
                return S * _cdf(d1) - K * math.exp(-r * T) * _cdf(d2)
            return K * math.exp(-r * T) * _cdf(-d2) - S * _cdf(-d1)

        def _solve_iv(S, K, T, r, market_price, opt_type):
            """Newton-Raphson 迭代反解隐含波动率。

            初始 IV=0.3，迭代 100 次，精度 1e-6。
            不收敛或 vega 过小时返回 None。
            """
            if (S is None or K is None or market_price is None
                    or S <= 0 or K <= 0 or T <= 0 or market_price <= 0):
                return None
            sigma = 0.3
            for _ in range(100):
                price = _bs_price(S, K, T, r, sigma, opt_type)
                if price is None:
                    return None
                d1 = (math.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * math.sqrt(T))
                vega = S * _pdf(d1) * math.sqrt(T)
                if vega < 1e-8:
                    return None
                diff = price - market_price
                if abs(diff) < 1e-6:
                    return round(sigma, 6)
                sigma = sigma - diff / vega
                # 防止 sigma 跑出合理范围
                if sigma <= 0:
                    sigma = 1e-4
                elif sigma > 5:
                    sigma = 5
            return None

        for opt_code in symbols:
            t0 = time.time()
            try:
                from xtquant import xtdata
                # 使用 _get_option_detail_safe 绕过 xtquant get_option_detail_data bug
                # （get_option_detail_data 内部 OptUndlUniCode 为 None 时崩溃）
                detail = self._get_option_detail_safe(opt_code, policy)
                rows = []
                if detail:
                    symbol = self._stock_to_symbol(opt_code)
                    underlying = detail.get("Underlying", "")
                    strike = self.safe_float(detail.get("ExercisePrice"))
                    expiry = detail.get("EndDelivDate", "")
                    opt_type = "call" if detail.get("OptType", 0) == 1 else "put"
                    r = 0.03
                    # 解析到期日（T 在遍历时逐日计算）
                    exp_date = None
                    if expiry:
                        try:
                            exp_str = str(expiry)
                            if len(exp_str) >= 8:
                                exp_date = datetime.date(
                                    int(exp_str[:4]), int(exp_str[4:6]), int(exp_str[6:8])
                                )
                        except Exception:
                            pass
                    # 1. 下载并获取期权历史收盘价
                    try:
                        self._call_with_policy(
                            xtdata.download_history_data, policy,
                            opt_code, "1d", start_str, end_str,
                        )
                    except Exception as e:
                        self._log.debug(f"download_history_data({opt_code}) 失败: {e}")
                    opt_data = self._call_with_policy(
                        xtdata.get_market_data_ex, policy,
                        [], [opt_code], "1d", start_str, end_str,
                    )
                    opt_df = opt_data.get(opt_code) if opt_data else None
                    if opt_df is None or len(opt_df) == 0:
                        yield FetchResult(
                            table=table, columns=columns, rows=[],
                            last_key=last_key, elapsed_sec=time.time() - t0,
                        )
                        continue
                    # 2. 下载并获取标的 historical 收盘价
                    ul_df = None
                    if underlying:
                        try:
                            self._call_with_policy(
                                xtdata.download_history_data, policy,
                                underlying, "1d", start_str, end_str,
                            )
                        except Exception as e:
                            self._log.debug(f"download_history_data({underlying}) 失败: {e}")
                        ul_data = self._call_with_policy(
                            xtdata.get_market_data_ex, policy,
                            [], [underlying], "1d", start_str, end_str,
                        )
                        ul_df = ul_data.get(underlying) if ul_data else None
                    if ul_df is None or len(ul_df) == 0:
                        yield FetchResult(
                            table=table, columns=columns, rows=[],
                            last_key=last_key, elapsed_sec=time.time() - t0,
                        )
                        continue
                    # 3. 对齐日期索引，遍历每个交易日计算 IV
                    import pandas as pd
                    common_dates = opt_df.index.intersection(ul_df.index)
                    for dt in common_dates:
                        opt_close = self.safe_float(opt_df.loc[dt, "close"])
                        spot = self.safe_float(ul_df.loc[dt, "close"])
                        if opt_close is None or opt_close <= 0 or spot is None or spot <= 0:
                            continue
                        # T 基于当前遍历日期计算
                        if exp_date:
                            cur_date = pd.Timestamp(dt).date()
                            days = (exp_date - cur_date).days
                            T = max(days / 365.0, 0.001)
                        else:
                            T = 0.25
                        iv = _solve_iv(spot, strike, T, r, opt_close, opt_type)
                        rows.append((
                            pd.Timestamp(dt).strftime("%Y-%m-%d"),
                            symbol, underlying, strike,
                            str(expiry)[:10] if expiry else None,
                            opt_type,
                            iv,
                            "miniqmt",
                        ))
                yield FetchResult(
                    table=table, columns=columns, rows=rows,
                    last_key=last_key, elapsed_sec=time.time() - t0,
                )
            except Exception as e:
                # 单个期权合约出错不中断整个任务（xtquant get_option_detail_data 可能有 bug）
                self._log.warning(f"{opt_code} IV曲面抓取失败，跳过: {e}")
                continue

    # ============== 可转债波动率 ==============

    def _fetch_convertible_bond_iv(
        self,
        payload: FetchPayload,
        policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """抓取可转债隐含波动率数据。

        使用 xtdata.get_instrument_detail 获取可转债详情（转股价/到期日/
        票面利率/正股代码），用 xtdata.get_market_data_ex 获取可转债与正股
        收盘价，结合简化模型（max(纯债价值, 转换价值) + BS 期权价值）+
        Newton-Raphson 迭代反解隐含波动率，并计算 BS Greeks (delta/gamma/theta/vega)
        和转股溢价率。
        表 schema: (trade_date, symbol, underlying, iv,
                    delta, gamma, theta, vega, conversion_premium,
                    data_source)

        Args:
            payload: 下载请求（symbols为可转债代码列表）
            policy: 调用策略

        Yields:
            FetchResult: 每只可转债一批
        """
        import math

        table = payload.table or "c1_market.convertible_bond_iv"
        columns = [
            "trade_date", "symbol", "underlying", "iv",
            "delta", "gamma", "theta", "vega", "conversion_premium",
            "data_source",
        ]
        trade_date = payload.end.isoformat()
        symbols = payload.symbols or []
        last_key = self._date_to_str(payload.end)

        try:
            start_str = self._date_to_str(payload.start)
            end_str = self._date_to_str(payload.end)
        except Exception as e:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=0.0, error=f"日期转换失败: {e}",
            )
            return

        # 标准正态分布 PDF / CDF
        def _pdf(x):
            return math.exp(-x ** 2 / 2) / math.sqrt(2 * math.pi)

        def _cdf(x):
            return 0.5 * (1 + math.erf(x / math.sqrt(2)))

        def _bs_call(S, K, T, r, sigma):
            """Black-Scholes 看涨期权理论价格。"""
            if S <= 0 or K <= 0 or T <= 0 or sigma <= 0:
                return None
            d1 = (math.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * math.sqrt(T))
            d2 = d1 - sigma * math.sqrt(T)
            return S * _cdf(d1) - K * math.exp(-r * T) * _cdf(d2)

        def _bond_value(coupon_rate, T, r, face_value=100.0):
            """纯债价值：现金流贴现（票面利率年化，到期还本100元）。"""
            if T <= 0:
                return face_value
            annual_coupon = coupon_rate * face_value
            n = max(1, int(math.ceil(T)))
            if r <= 0:
                return face_value + annual_coupon * n
            pv = 0.0
            for t in range(1, n + 1):
                pv += annual_coupon / ((1 + r) ** t)
            pv += face_value / ((1 + r) ** n)
            return pv

        def _solve_cb_iv(S, K, T, r, market_price, coupon_rate):
            """Newton-Raphson 反解可转债隐含波动率，并计算 BS Greeks。

            模型：理论价 = max(纯债价值, 转换价值) + BS_call(S, K, T, r, σ)
            初始 σ=0.3，迭代 100 次，精度 1e-6。
            vega = S * sqrt(T) * N'(d1)（原始 dPrice/dσ，不除100）。
            不收敛或 vega 过小时 iv 返回 None。

            Returns:
                tuple: (iv, bond_value, convert_value, delta, gamma, theta, vega)
                其中 Greeks 基于收敛后的 σ 计算；iv=None 时 Greeks 也为 None。
            """
            if (S is None or K is None or market_price is None
                    or S <= 0 or K <= 0 or T <= 0 or market_price <= 0):
                return None, None, None, None, None, None, None
            bond_val = _bond_value(coupon_rate, T, r)
            convert_val = S / K * 100.0  # 转换价值 = 正股价 / 转股价 × 100
            floor_value = max(bond_val, convert_val)
            sigma = 0.3
            sqrt_T = math.sqrt(T)
            for _ in range(100):
                opt_price = _bs_call(S, K, T, r, sigma)
                if opt_price is None:
                    return None, bond_val, convert_val, None, None, None, None
                theory_price = floor_value + opt_price
                d1 = (math.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * sqrt_T)
                d2 = d1 - sigma * sqrt_T
                pdf_d1 = _pdf(d1)
                vega_raw = S * pdf_d1 * sqrt_T  # 原始 vega，不除100
                if vega_raw < 1e-8:
                    return None, bond_val, convert_val, None, None, None, None
                diff = theory_price - market_price
                if abs(diff) < 1e-6:
                    delta = _cdf(d1)
                    denom = S * sigma * sqrt_T
                    gamma = pdf_d1 / denom if denom > 0 else None
                    theta = (-S * pdf_d1 * sigma / (2 * sqrt_T)) - r * K * math.exp(-r * T) * _cdf(d2)
                    return (round(sigma, 6), bond_val, convert_val,
                            round(delta, 6), round(gamma, 6) if gamma is not None else None,
                            round(theta, 6), round(vega_raw, 6))
                sigma = sigma - diff / vega_raw
                if sigma <= 0:
                    sigma = 1e-4
                elif sigma > 5:
                    sigma = 5
            return None, bond_val, convert_val, None, None, None, None

        # 从 akshare 获取可转债详情（转股价/正股代码），miniQMT 不提供这些字段
        cb_details_map = {}
        try:
            import akshare as ak
            cov_df = self._call_with_policy(ak.bond_zh_cov, policy)
            for _, row in cov_df.iterrows():
                bond_code = str(row.get("债券代码", "")).strip()
                stock_code = str(row.get("正股代码", "")).strip()
                conv_price = self.safe_float(row.get("转股价"))
                if not bond_code or not stock_code:
                    continue
                # 转换正股代码为 miniQMT 格式
                if stock_code.startswith(("60", "68")):
                    ul = stock_code + ".SH"
                elif stock_code.startswith(("00", "30")):
                    ul = stock_code + ".SZ"
                elif stock_code.startswith(("8", "4")):
                    ul = stock_code + ".BJ"
                else:
                    ul = stock_code
                cb_details_map[bond_code] = {"underlying": ul, "convert_price": conv_price}
            self._log.info(f"获取 {len(cb_details_map)} 只可转债详情（akshare bond_zh_cov）")
        except Exception as e:
            self._log.warning(f"akshare bond_zh_cov 失败: {e}")

        for cb_code in symbols:
            t0 = time.time()
            try:
                from xtquant import xtdata
                detail = self._call_with_policy(
                    xtdata.get_instrument_detail, policy, cb_code,
                )
                rows = []
                if detail:
                    symbol = self._stock_to_symbol(cb_code)
                    # miniQMT 字段名是 ExpireDate（非 EndDate）
                    end_date = detail.get("ExpireDate", "")
                    # 从 akshare 映射获取转股价和正股代码
                    code_6 = cb_code.split(".")[0]
                    cb_info = cb_details_map.get(code_6, {})
                    convert_price = cb_info.get("convert_price")
                    underlying = cb_info.get("underlying", "")
                    # coupon_rate miniQMT/akshare 均不提供，使用默认值 0.5%
                    coupon_rate = 0.005
                    r = 0.03
                    # 解析到期日（T 在遍历时逐日计算）
                    exp_date = None
                    if end_date:
                        try:
                            ed_str = str(end_date)
                            if len(ed_str) >= 8:
                                exp_date = datetime.date(
                                    int(ed_str[:4]), int(ed_str[4:6]), int(ed_str[6:8])
                                )
                        except Exception:
                            pass
                    # 1. 下载并获取可转债历史收盘价
                    try:
                        self._call_with_policy(
                            xtdata.download_history_data, policy,
                            cb_code, "1d", start_str, end_str,
                        )
                    except Exception as e:
                        self._log.debug(f"download_history_data({cb_code}) 失败: {e}")
                    cb_data = self._call_with_policy(
                        xtdata.get_market_data_ex, policy,
                        [], [cb_code], "1d", start_str, end_str,
                    )
                    cb_df = cb_data.get(cb_code) if cb_data else None
                    if cb_df is None or len(cb_df) == 0:
                        yield FetchResult(
                            table=table, columns=columns, rows=[],
                            last_key=last_key, elapsed_sec=time.time() - t0,
                        )
                        continue
                    # 2. 下载并获取正股 historical 收盘价
                    ul_df = None
                    if underlying:
                        try:
                            self._call_with_policy(
                                xtdata.download_history_data, policy,
                                underlying, "1d", start_str, end_str,
                            )
                        except Exception as e:
                            self._log.debug(f"download_history_data({underlying}) 失败: {e}")
                        ul_data = self._call_with_policy(
                            xtdata.get_market_data_ex, policy,
                            [], [underlying], "1d", start_str, end_str,
                        )
                        ul_df = ul_data.get(underlying) if ul_data else None
                    if ul_df is None or len(ul_df) == 0:
                        yield FetchResult(
                            table=table, columns=columns, rows=[],
                            last_key=last_key, elapsed_sec=time.time() - t0,
                        )
                        continue
                    # 3. 转股价必须 > 0
                    if convert_price is None or convert_price <= 0:
                        yield FetchResult(
                            table=table, columns=columns, rows=[],
                            last_key=last_key, elapsed_sec=time.time() - t0,
                        )
                        continue
                    # 4. 对齐日期索引，遍历每个交易日计算 IV
                    import pandas as pd
                    common_dates = cb_df.index.intersection(ul_df.index)
                    for dt in common_dates:
                        cb_price = self.safe_float(cb_df.loc[dt, "close"])
                        spot = self.safe_float(ul_df.loc[dt, "close"])
                        if cb_price is None or cb_price <= 0 or spot is None or spot <= 0:
                            continue
                        if exp_date:
                            cur_date = pd.Timestamp(dt).date()
                            days = (exp_date - cur_date).days
                            T = max(days / 365.0, 0.001)
                        else:
                            T = 0.25
                        iv, bond_val, convert_val, delta, gamma, theta, vega_val = _solve_cb_iv(
                            spot, convert_price, T, r, cb_price, coupon_rate,
                        )
                        # 转股溢价率 = (可转债价 / 转换价值 - 1) × 100
                        if convert_val and convert_val > 0:
                            conversion_premium = round((cb_price / convert_val - 1) * 100, 4)
                        else:
                            conversion_premium = None
                        rows.append((
                            pd.Timestamp(dt).strftime("%Y-%m-%d"),
                            symbol, underlying, iv,
                            delta, gamma, theta, vega_val,
                            conversion_premium, "miniqmt",
                        ))
                yield FetchResult(
                    table=table, columns=columns, rows=rows,
                    last_key=last_key, elapsed_sec=time.time() - t0,
                )
            except Exception as e:
                yield FetchResult(
                    table=table, columns=columns, rows=[],
                    last_key=last_key, elapsed_sec=time.time() - t0,
                    error=f"{cb_code} 可转债IV抓取失败: {e}",
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
                if front_df is None or len(front_df) == 0 or next_df is None or len(next_df) == 0:
                    yield FetchResult(
                        table=table, columns=columns, rows=[],
                        last_key=last_key, elapsed_sec=time.time() - t0,
                    )
                    continue
                # 对齐日期索引，遍历每个交易日计算基差
                import pandas as pd
                common_dates = front_df.index.intersection(next_df.index)
                symbol = self._stock_to_symbol(front_code)
                front_sym = self._stock_to_symbol(front_code)
                next_sym = self._stock_to_symbol(next_code)
                for dt in common_dates:
                    front_close = self.safe_float(front_df.loc[dt, "close"])
                    next_close = self.safe_float(next_df.loc[dt, "close"])
                    basis = None
                    if front_close is not None and next_close is not None:
                        basis = round(front_close - next_close, 4)
                    rows.append((
                        pd.Timestamp(dt).strftime("%Y-%m-%d"),
                        symbol, front_sym, next_sym,
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
        """抓取分笔（Tick）数据，写入 c1_market.tick_data。

        使用 xtdata.get_market_data_ex(period='tick') 获取分笔行情。
        tick 数据量很大，每次只取 1 只股票 1 天。
        统一写入 tick_data 表（百度云历史 + QMT 增量），百度云历史无 bid/ask 列为 NULL。
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

        table = payload.table or "c1_market.tick_data"
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

        行格式对齐 tick_data 表：
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

    # ============== 第二批新增能力（15 个数据下载能力）==============

    def _fetch_simple_kline(
        self,
        payload: FetchPayload,
        policy: SourcePolicy,
        default_table: str,
    ) -> Iterator[FetchResult]:
        """通用简版K线抓取（OHLCV 标准列，适用于可转债/期权/期货/港股/美股K线）。

        复用 download_history_data + get_market_data_ex 模式，统一写入
        (trade_date, symbol, open, high, low, close, volume, amount, data_source)。
        symbols 由 payload 指定（不自动取全市场，避免误拉非目标品种）。

        Args:
            payload: 下载请求（symbols 必须指定标的列表）
            policy: 调用策略
            default_table: 默认目标表（payload.table 为空时使用）

        Yields:
            FetchResult: 每个标的一批
        """
        from xtquant import xtdata

        table = payload.table or default_table
        columns = [
            "trade_date", "symbol", "open", "high", "low", "close",
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

        symbols = payload.symbols or []
        last_key = end_str

        for stock_code in symbols:
            t0 = time.time()
            try:
                self._call_with_policy(
                    xtdata.download_history_data, policy,
                    stock_code, "1d", start_str, end_str,
                )
                data = self._call_with_policy(
                    xtdata.get_market_data_ex, policy,
                    [], [stock_code], "1d", start_str, end_str,
                )

                rows = []
                df = data.get(stock_code) if data else None
                if df is not None and len(df) > 0:
                    symbol = self._stock_to_symbol(stock_code)
                    times = [int(ts) for ts in df.index]
                    opens = df["open"].tolist()
                    highs = df["high"].tolist()
                    lows = df["low"].tolist()
                    closes = df["close"].tolist()
                    volumes = df["volume"].tolist()
                    amounts = df["amount"].tolist()
                    for i in range(len(times)):
                        s = str(times[i])
                        trade_date = f"{s[:4]}-{s[4:6]}-{s[6:8]}"
                        vol = self.safe_float(volumes[i])
                        vol = int(vol) if vol is not None else None
                        rows.append((
                            trade_date, symbol,
                            self.safe_float(opens[i]),
                            self.safe_float(highs[i]),
                            self.safe_float(lows[i]),
                            self.safe_float(closes[i]),
                            vol,
                            self.safe_float(amounts[i]),
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
                    error=f"{stock_code} 抓取失败: {e}",
                )

    # ============== 可转债K线 ==============

    def _fetch_kline_cb(
        self, payload: FetchPayload, policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """抓取可转债日K线数据。

        使用 xtdata.get_market_data_ex(period='1d')，symbols 格式如 '113001.SH'。
        若 symbols 为空，尝试从'沪深转债'板块获取标的列表。
        表 schema: (trade_date, symbol, open, high, low, close, volume, amount, data_source)

        Args:
            payload: 下载请求
            policy: 调用策略

        Yields:
            FetchResult: 每个可转债一批
        """
        from xtquant import xtdata

        # symbols 为空时尝试取沪深转债板块
        if not payload.symbols:
            try:
                cb_list = self._call_with_policy(
                    xtdata.get_stock_list_in_sector, policy, "沪深转债"
                )
                if cb_list:
                    payload = FetchPayload(
                        table=payload.table, symbols=cb_list,
                        start=payload.start, end=payload.end,
                        incremental=payload.incremental, extra=payload.extra,
                    )
            except Exception as e:
                self._log.warning(f"获取可转债板块失败: {e}")

        yield from self._fetch_simple_kline(payload, policy, "c1_market.kline_cb")

    # ============== 期权K线 ==============

    def _fetch_option_kline(
        self, payload: FetchPayload, policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """抓取期权日K线数据。

        使用 xtdata.get_market_data_ex(period='1d')，symbols 格式如 '10000001.SH'。
        若 symbols 为空，尝试用 get_option_list 获取期权合约列表。
        表 schema: (trade_date, symbol, open, high, low, close, volume, amount, data_source)

        Args:
            payload: 下载请求
            policy: 调用策略

        Yields:
            FetchResult: 每个期权一批
        """
        from xtquant import xtdata

        # symbols 为空时从上证期权+深证期权板块获取合约列表
        if not payload.symbols:
            try:
                opts = []
                for sector_name in ("上证期权", "深证期权"):
                    lst = self._call_with_policy(
                        xtdata.get_stock_list_in_sector, policy, sector_name
                    )
                    if lst:
                        opts.extend(lst)
                if opts:
                    # 限制前 100 个（期权合约太多）
                    payload = FetchPayload(
                        table=payload.table, symbols=opts[:100],
                        start=payload.start, end=payload.end,
                        incremental=payload.incremental, extra=payload.extra,
                    )
            except Exception as e:
                self._log.warning(f"获取期权列表失败: {e}")

        yield from self._fetch_simple_kline(payload, policy, "c1_market.option_kline")

    # ============== 期权Greeks ==============

    def _fetch_option_greeks(
        self, payload: FetchPayload, policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """抓取期权Greeks数据（delta/gamma/theta/vega）。

        使用 xtdata.get_option_detail_data 获取期权合约详情（行权价/到期日/标的价格），
        结合 Black-Scholes 模型计算 Greeks。
        表 schema: (trade_date, symbol, underlying, strike, expiry, opt_type,
                    delta, gamma, theta, vega, data_source)

        Args:
            payload: 下载请求（symbols为期权合约代码列表）
            policy: 调用策略

        Yields:
            FetchResult: 每个期权一批
        """
        table = payload.table or "c1_market.option_greeks"
        columns = [
            "trade_date", "symbol", "underlying", "strike", "expiry",
            "opt_type", "delta", "gamma", "theta", "vega", "data_source",
        ]
        symbols = payload.symbols or []
        last_key = self._date_to_str(payload.end)

        try:
            start_str = self._date_to_str(payload.start)
            end_str = self._date_to_str(payload.end)
        except Exception as e:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=0.0, error=f"日期转换失败: {e}",
            )
            return

        for opt_code in symbols:
            t0 = time.time()
            try:
                from xtquant import xtdata
                import pandas as pd
                # 使用 _get_option_detail_safe 绕过 xtquant get_option_detail_data bug
                detail = self._get_option_detail_safe(opt_code, policy)
                rows = []
                if detail:
                    symbol = self._stock_to_symbol(opt_code)
                    underlying = detail.get("Underlying", "")
                    strike = self.safe_float(detail.get("ExercisePrice"))
                    expiry = detail.get("EndDelivDate", "")
                    opt_type = "call" if detail.get("OptType", 0) == 1 else "put"
                    r = 0.03
                    # 解析到期日
                    exp_date = None
                    if expiry:
                        try:
                            exp_str = str(expiry)
                            if len(exp_str) >= 8:
                                exp_date = datetime.date(
                                    int(exp_str[:4]), int(exp_str[4:6]), int(exp_str[6:8])
                                )
                        except Exception:
                            pass
                    # 1. 下载并获取期权历史收盘价
                    try:
                        self._call_with_policy(
                            xtdata.download_history_data, policy,
                            opt_code, "1d", start_str, end_str,
                        )
                    except Exception as e:
                        self._log.debug(f"download_history_data({opt_code}) 失败: {e}")
                    opt_data = self._call_with_policy(
                        xtdata.get_market_data_ex, policy,
                        [], [opt_code], "1d", start_str, end_str,
                    )
                    opt_df = opt_data.get(opt_code) if opt_data else None
                    if opt_df is None or len(opt_df) == 0:
                        yield FetchResult(
                            table=table, columns=columns, rows=[],
                            last_key=last_key, elapsed_sec=time.time() - t0,
                        )
                        continue
                    # 2. 下载并获取标的 historical 收盘价
                    ul_df = None
                    if underlying:
                        try:
                            self._call_with_policy(
                                xtdata.download_history_data, policy,
                                underlying, "1d", start_str, end_str,
                            )
                        except Exception as e:
                            self._log.debug(f"download_history_data({underlying}) 失败: {e}")
                        ul_data = self._call_with_policy(
                            xtdata.get_market_data_ex, policy,
                            [], [underlying], "1d", start_str, end_str,
                        )
                        ul_df = ul_data.get(underlying) if ul_data else None
                    if ul_df is None or len(ul_df) == 0:
                        yield FetchResult(
                            table=table, columns=columns, rows=[],
                            last_key=last_key, elapsed_sec=time.time() - t0,
                        )
                        continue
                    # 3. 对齐日期索引，遍历每个交易日计算 Greeks
                    # sigma 用标的 20 日历史波动率（年化）
                    ul_close = ul_df["close"].astype(float)
                    ul_ret = ul_close.pct_change()
                    common_dates = opt_df.index.intersection(ul_df.index)
                    for dt in common_dates:
                        spot = self.safe_float(ul_df.loc[dt, "close"])
                        if spot is None or spot <= 0:
                            continue
                        # T 基于当前遍历日期计算
                        if exp_date:
                            cur_date = pd.Timestamp(dt).date()
                            days = (exp_date - cur_date).days
                            T = max(days / 365.0, 0.001)
                        else:
                            T = 0.25
                        # 历史波动率：截止当日的 20 日收益率标准差 × sqrt(244)
                        pos = ul_df.index.get_loc(dt)
                        if pos >= 20:
                            hist_vol = ul_ret.iloc[pos - 19 : pos + 1].std()
                            sigma = self.safe_float(hist_vol)
                            if sigma is None or sigma <= 0:
                                sigma = 0.3
                            else:
                                sigma = sigma * (244 ** 0.5)
                        else:
                            sigma = 0.3
                        greeks = self._calc_bs_greeks(spot, strike, T, r, sigma, opt_type)
                        if greeks:
                            rows.append((
                                pd.Timestamp(dt).strftime("%Y-%m-%d"),
                                symbol, underlying, strike,
                                str(expiry)[:10] if expiry else None,
                                opt_type,
                                greeks["delta"], greeks["gamma"],
                                greeks["theta"], greeks["vega"],
                                "miniqmt",
                            ))
                yield FetchResult(
                    table=table, columns=columns, rows=rows,
                    last_key=last_key, elapsed_sec=time.time() - t0,
                )
            except Exception as e:
                # 单个期权合约出错不中断整个任务（xtquant get_option_detail_data 可能有 bug）
                self._log.warning(f"{opt_code} Greeks抓取失败，跳过: {e}")
                continue

    @staticmethod
    def _calc_bs_greeks(S, K, T, r, sigma, opt_type):
        """Black-Scholes 模型计算期权 Greeks。

        Args:
            S: 标的现价
            K: 行权价
            T: 剩余期限（年）
            r: 无风险利率
            sigma: 波动率
            opt_type: "call" 或 "put"

        Returns:
            dict: {delta, gamma, theta, vega} 或 None（参数不足时）
        """
        if S is None or K is None or S <= 0 or K <= 0 or T <= 0 or sigma <= 0:
            return None
        import math
        d1 = (math.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        # 标准正态分布 PDF 和 CDF
        def _pdf(x):
            return math.exp(-x ** 2 / 2) / math.sqrt(2 * math.pi)
        def _cdf(x):
            return 0.5 * (1 + math.erf(x / math.sqrt(2)))
        gamma = _pdf(d1) / (S * sigma * math.sqrt(T))
        vega = S * _pdf(d1) * math.sqrt(T) / 100  # vega per 1% vol change
        if opt_type == "call":
            delta = _cdf(d1)
            theta = (
                -S * _pdf(d1) * sigma / (2 * math.sqrt(T))
                - r * K * math.exp(-r * T) * _cdf(d2)
            ) / 365  # theta per day
        else:
            delta = _cdf(d1) - 1
            theta = (
                -S * _pdf(d1) * sigma / (2 * math.sqrt(T))
                + r * K * math.exp(-r * T) * _cdf(-d2)
            ) / 365
        return {
            "delta": round(delta, 6),
            "gamma": round(gamma, 6),
            "theta": round(theta, 6),
            "vega": round(vega, 6),
        }

    # ============== 指数权重 ==============

    def _fetch_index_weight(
        self, payload: FetchPayload, policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """抓取指数成分股权重数据。

        先调用 xtdata.download_index_weight() 下载最新权重数据，
        再用 xtdata.get_index_weight(index_code) 获取权重字典 {stock_code: weight}。
        表 schema: (trade_date, index_code, symbol, weight, data_source)

        Args:
            payload: 下载请求（symbols 为指数代码列表，如 ['000300.SH']）
            policy: 调用策略

        Yields:
            FetchResult: 每个指数一批
        """
        from xtquant import xtdata

        table = payload.table or "c1_market.index_weight"
        columns = ["trade_date", "index_code", "symbol", "weight", "data_source"]
        trade_date = payload.end.isoformat()
        # 默认核心指数
        index_codes = payload.symbols or [
            "000016.SH", "000300.SH", "000905.SH", "000852.SH",
        ]
        last_key = self._date_to_str(payload.end)

        # 先下载权重数据（无参数，下载全部）
        try:
            self._call_with_policy(xtdata.download_index_weight, policy)
        except Exception as e:
            self._log.warning(f"download_index_weight 失败: {e}")

        for index_code in index_codes:
            t0 = time.time()
            try:
                weight_dict = self._call_with_policy(
                    xtdata.get_index_weight, policy, index_code,
                )
                rows = []
                if weight_dict:
                    for stock_code, weight in weight_dict.items():
                        symbol = self._stock_to_symbol(stock_code)
                        rows.append((
                            trade_date, index_code, symbol,
                            self.safe_float(weight),
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
                    error=f"{index_code} 权重抓取失败: {e}",
                )

    # ============== 板块列表 ==============

    def _fetch_sector_list(
        self, payload: FetchPayload, policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """抓取板块成分股列表。

        使用 xtdata.get_stock_list_in_sector 获取指定板块的成分股。
        若 payload.extra["sectors"] 指定板块名列表，遍历各板块；
        否则默认取"沪深A股"。
        表 schema: (trade_date, sector_name, symbol, data_source)

        Args:
            payload: 下载请求
            policy: 调用策略

        Yields:
            FetchResult: 每个板块一批
        """
        from xtquant import xtdata

        table = payload.table or "c1_market.sector_list"
        columns = ["trade_date", "sector_name", "symbol", "data_source"]
        trade_date = payload.end.isoformat()
        extra = payload.extra or {}
        # 允许 extra["sectors"] 指定板块列表，默认沪深A股
        sectors = extra.get("sectors", ["沪深A股"])
        last_key = self._date_to_str(payload.end)

        # 先下载板块数据
        try:
            self._call_with_policy(xtdata.download_sector_data, policy)
        except Exception as e:
            self._log.warning(f"download_sector_data 失败: {e}")

        for sector_name in sectors:
            t0 = time.time()
            try:
                stock_list = self._call_with_policy(
                    xtdata.get_stock_list_in_sector, policy, sector_name
                )
                rows = []
                if stock_list:
                    for stock_code in stock_list:
                        symbol = self._stock_to_symbol(stock_code)
                        rows.append((trade_date, sector_name, symbol, "miniqmt"))
                yield FetchResult(
                    table=table, columns=columns, rows=rows,
                    last_key=last_key, elapsed_sec=time.time() - t0,
                )
            except Exception as e:
                yield FetchResult(
                    table=table, columns=columns, rows=[],
                    last_key=last_key, elapsed_sec=time.time() - t0,
                    error=f"板块[{sector_name}]抓取失败: {e}",
                )

    # ============== Level-2逐笔 ==============

    def _fetch_l2_tick(
        self, payload: FetchPayload, policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """抓取 Level-2 逐笔行情数据。

        使用 xtdata.get_l2_quote 获取 L2 报价数据（含买卖盘）。
        需 L2 行情权限，数据量很大，每次只取少量标的。
        表 schema: (trade_date, timestamp, symbol, price, volume, amount,
                    bid_price, ask_price, data_source)

        Args:
            payload: 下载请求
            policy: 调用策略

        Yields:
            FetchResult: 每个标的一批
        """
        from xtquant import xtdata
        import numpy as np

        table = payload.table or "c1_market.l2_tick"
        columns = [
            "trade_date", "timestamp", "symbol", "price", "volume",
            "amount", "bid_price", "ask_price", "data_source",
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

        symbols = payload.symbols or []
        last_key = end_str

        for stock_code in symbols:
            t0 = time.time()
            try:
                data = self._call_with_policy(
                    xtdata.get_l2_quote, policy,
                    [], stock_code, start_str, end_str, -1,
                )
                rows = self._parse_l2_records(data, stock_code, payload.end)
                yield FetchResult(
                    table=table, columns=columns, rows=rows,
                    last_key=last_key, elapsed_sec=time.time() - t0,
                )
            except Exception as e:
                yield FetchResult(
                    table=table, columns=columns, rows=[],
                    last_key=last_key, elapsed_sec=time.time() - t0,
                    error=f"{stock_code} L2抓取失败: {e}",
                )

    def _parse_l2_records(self, data, stock_code: str, end_date) -> list[tuple]:
        """解析 L2 numpy structured array 为行列表（降低 _fetch_l2_tick 复杂度）。

        Args:
            data: xtdata.get_l2_quote 返回的 numpy structured array
            stock_code: 标的代码
            end_date: fallback 日期

        Returns:
            行元组列表
        """
        import numpy as np

        if data is None or not isinstance(data, np.ndarray) or data.size == 0:
            return []
        symbol = self._stock_to_symbol(stock_code)
        rows: list[tuple] = []
        for rec in data:
            ts = int(rec["time"]) if rec["time"] else 0
            s = str(ts)
            trade_date, timestamp = self._format_tick_timestamp(s, end_date)
            price = self.safe_float(rec["lastPrice"])
            vol = self.safe_float(rec["volume"])
            vol = int(vol) if vol is not None else None
            amt = self.safe_float(rec["amount"])
            bid_price = self._extract_first_price(rec, "bidPrice")
            ask_price = self._extract_first_price(rec, "askPrice")
            rows.append((
                trade_date, timestamp, symbol, price, vol, amt,
                bid_price, ask_price, "miniqmt",
            ))
        return rows

    @staticmethod
    def _extract_first_price(rec, field_name: str):
        """从 numpy record 的数组字段中提取首个价格（降低复杂度）。"""
        arr = rec[field_name]
        if arr is not None and len(arr) > 0:
            return MiniQMTProvider.safe_float(arr[0])
        return None

    # ============== 集合竞价数据 ==============

    def _fetch_auction_data(
        self, payload: FetchPayload, policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """抓取集合竞价数据（实时快照）。

        使用 xtdata.get_full_tick 获取实时行情快照，适用于集合竞价时段（9:15-9:25）。
        写入已有的 auction_snapshot 表。
        表 schema: (trade_date, timestamp, symbol, price, volume, amount, data_source)

        Args:
            payload: 下载请求
            policy: 调用策略

        Yields:
            FetchResult: 一批（全部标的）
        """
        from xtquant import xtdata

        table = payload.table or "c1_market.auction_snapshot"
        columns = ["trade_date", "timestamp", "symbol", "price", "volume", "amount", "data_source"]

        symbols = payload.symbols
        if not symbols:
            try:
                symbols = self._call_with_policy(
                    xtdata.get_stock_list_in_sector, policy, "沪深A股"
                )
            except Exception as e:
                yield FetchResult(
                    table=table, columns=[], rows=[], last_key="",
                    elapsed_sec=0.0, error=f"获取标的清单失败: {e}",
                )
                return

        t0 = time.time()
        try:
            # get_full_tick 一次最多取一定数量标的，分批调用
            batch_size = 200
            rows = []
            trade_date = payload.end.isoformat()
            for i in range(0, len(symbols), batch_size):
                batch = symbols[i:i + batch_size]
                tick_data = self._call_with_policy(
                    xtdata.get_full_tick, policy, batch,
                )
                if tick_data:
                    for stock_code, tick in tick_data.items():
                        if not tick:
                            continue
                        symbol = self._stock_to_symbol(stock_code)
                        price = self.safe_float(tick.get("lastPrice"))
                        vol = self.safe_float(tick.get("volume"))
                        vol = int(vol) if vol is not None else None
                        amt = self.safe_float(tick.get("amount"))
                        # timetag 格式为 "YYYYMMDDHHMMSSmmm"
                        timetag = tick.get("timetag", "")
                        ts_str = str(timetag)
                        if len(ts_str) >= 14:
                            timestamp = (
                                f"{ts_str[:4]}-{ts_str[4:6]}-{ts_str[6:8]} "
                                f"{ts_str[8:10]}:{ts_str[10:12]}:{ts_str[12:14]}"
                            )
                        else:
                            timestamp = trade_date + " 09:25:00"
                        rows.append((
                            trade_date, timestamp, symbol, price, vol, amt,
                            "miniqmt",
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
                error=f"集合竞价数据抓取失败: {e}",
            )

    # ============== 期货K线（QMT） ==============

    def _fetch_kline_futures_qmt(
        self, payload: FetchPayload, policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """抓取期货日K线数据（QMT 专用表）。

        使用 xtdata.get_market_data_ex(period='1d')，symbols 格式如 'IF2407.CFFEX'。
        若 symbols 为空，从'商品期货'+'股指期货期货板块'获取合约列表。
        表 schema: (trade_date, symbol, open, high, low, close, volume, amount, data_source)

        Args:
            payload: 下载请求
            policy: 调用策略

        Yields:
            FetchResult: 每个合约一批
        """
        from xtquant import xtdata

        if not payload.symbols:
            try:
                futures = []
                for sector_name in ("商品期货", "股指期货期货板块"):
                    lst = self._call_with_policy(
                        xtdata.get_stock_list_in_sector, policy, sector_name
                    )
                    if lst:
                        futures.extend(lst)
                if futures:
                    payload = FetchPayload(
                        table=payload.table, symbols=futures,
                        start=payload.start, end=payload.end,
                        incremental=payload.incremental, extra=payload.extra,
                    )
            except Exception as e:
                self._log.warning(f"获取期货合约列表失败: {e}")

        yield from self._fetch_simple_kline(payload, policy, "c1_market.kline_futures_qmt")

    # ============== 港股K线 ==============

    def _fetch_hk_kline(
        self, payload: FetchPayload, policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """抓取港股日K线数据。

        使用 xtdata.get_market_data_ex(period='1d')，symbols 格式如 '00700.HK'。
        若 symbols 为空，从'港股主板'板块获取前200只港股。
        表 schema: (trade_date, symbol, open, high, low, close, volume, amount, data_source)

        Args:
            payload: 下载请求
            policy: 调用策略

        Yields:
            FetchResult: 每个港股一批
        """
        from xtquant import xtdata

        if not payload.symbols:
            try:
                hk_list = self._call_with_policy(
                    xtdata.get_stock_list_in_sector, policy, "港股主板"
                )
                if hk_list:
                    # 限制前 200 只（港股太多，避免超时）
                    payload = FetchPayload(
                        table=payload.table, symbols=hk_list[:200],
                        start=payload.start, end=payload.end,
                        incremental=payload.incremental, extra=payload.extra,
                    )
            except Exception as e:
                self._log.warning(f"获取港股列表失败: {e}")

        yield from self._fetch_simple_kline(payload, policy, "c1_market.hk_kline")

    # ============== 美股K线 ==============

    def _fetch_us_kline(
        self, payload: FetchPayload, policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """抓取美股日K线数据。

        使用 xtdata.get_market_data_ex(period='1d')，symbols 格式如 'AAPL.US'。
        需 QMT 开通美股行情权限。QMT 板块列表无美股板块，symbols 必须手动指定。
        表 schema: (trade_date, symbol, open, high, low, close, volume, amount, data_source)

        Args:
            payload: 下载请求（symbols 必须指定美股代码列表）
            policy: 调用策略

        Yields:
            FetchResult: 每个美股一批
        """
        if not payload.symbols:
            yield FetchResult(
                table=payload.table or "c1_market.kline_us_daily",
                columns=[], rows=[], last_key="",
                elapsed_sec=0.0,
                error="QMT 无美股板块，需在 tasks.yaml 中手动指定 symbols（如 ['AAPL.US', 'MSFT.US']），且需开通美股行情权限",
            )
            return
        yield from self._fetch_simple_kline(payload, policy, "c1_market.kline_us_daily")

    # ============== ETF净值 ==============

    def _fetch_etf_nav(
        self, payload: FetchPayload, policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """抓取 ETF 基金净值数据。

        使用 xtdata.get_etf_info 获取 ETF 基金信息（含净值/现金余额等）。
        表 schema: (trade_date, symbol, etf_code, nav, cash_balance, data_source)

        Args:
            payload: 下载请求（symbols 为 ETF 代码列表，如 ['510050.SH']）
            policy: 调用策略

        Yields:
            FetchResult: 每个ETF一批
        """
        from xtquant import xtdata

        table = payload.table or "c1_market.etf_nav"
        columns = ["trade_date", "symbol", "etf_code", "nav", "cash_balance", "data_source"]
        trade_date = payload.end.isoformat()
        symbols = payload.symbols or []
        # symbols 为空时从沪深ETF板块获取前200只
        if not symbols:
            try:
                etf_list = self._call_with_policy(
                    xtdata.get_stock_list_in_sector, policy, "沪深ETF"
                )
                if etf_list:
                    symbols = etf_list[:200]
            except Exception as e:
                self._log.warning(f"获取ETF列表失败: {e}")
        last_key = self._date_to_str(payload.end)

        for stock_code in symbols:
            t0 = time.time()
            try:
                info = self._call_with_policy(
                    xtdata.get_etf_info, policy, stock_code,
                )
                rows = []
                if info:
                    symbol = self._stock_to_symbol(stock_code)
                    etf_code = info.get("etfCode", "")
                    nav = self.safe_float(info.get("cashBalance"))
                    cash_balance = self.safe_float(info.get("maxCashRatio"))
                    rows.append((
                        trade_date, symbol, etf_code, nav, cash_balance,
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
                    error=f"{stock_code} ETF净值抓取失败: {e}",
                )

    # ============== 回购数据（占位） ==============

    def _fetch_repurchase(
        self, payload: FetchPayload, policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """回购数据占位方法。

        QMT 无直接提供回购数据的接口。回购数据建议通过 AKShare
        （ak.stock_repurchase_em）或交易所公告获取。
        返回 error 占位。

        Yields:
            FetchResult: 含 error 的占位结果
        """
        yield FetchResult(
            table=payload.table or "c1_market.repurchase",
            columns=[], rows=[], last_key="",
            elapsed_sec=0.0,
            error="QMT无回购数据接口，建议使用AKShare stock_repurchase_em",
        )

    # ============== 融资融券（QMT占位） ==============

    def _fetch_margin_trading_qmt(
        self, payload: FetchPayload, policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """融资融券数据占位方法（QMT）。

        QMT 无直接提供融资融券数据的接口。融资融券数据已通过 AKShare
        （stock_margin_detail_sse/szse）实现，见 tasks.yaml margin_trading_incremental。
        返回 error 占位。

        Yields:
            FetchResult: 含 error 的占位结果
        """
        yield FetchResult(
            table=payload.table or "c1_market.margin_trading_qmt",
            columns=[], rows=[], last_key="",
            elapsed_sec=0.0,
            error="QMT无融资融券接口，已由AKShare Provider覆盖（margin_trading_incremental）",
        )

    # ============== 龙虎榜（QMT占位） ==============

    def _fetch_dragon_tiger_qmt(
        self, payload: FetchPayload, policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """龙虎榜数据占位方法（QMT）。

        QMT 无直接提供龙虎榜数据的接口。龙虎榜数据已通过 AKShare
        （stock_lhb_detail_em）实现，见 tasks.yaml dragon_tiger_incremental。
        返回 error 占位。

        Yields:
            FetchResult: 含 error 的占位结果
        """
        yield FetchResult(
            table=payload.table or "c1_market.dragon_tiger_qmt",
            columns=[], rows=[], last_key="",
            elapsed_sec=0.0,
            error="QMT无龙虎榜接口，已由AKShare Provider覆盖（dragon_tiger_incremental）",
        )

    # ============== 大宗交易（QMT占位） ==============

    def _fetch_block_trade_qmt(
        self, payload: FetchPayload, policy: SourcePolicy,
    ) -> Iterator[FetchResult]:
        """大宗交易数据占位方法（QMT）。

        QMT 无直接提供大宗交易数据的接口。大宗交易数据已通过 AKShare
        （stock_dzjy_mrmx）实现，见 tasks.yaml block_trade_incremental。
        返回 error 占位。

        Yields:
            FetchResult: 含 error 的占位结果
        """
        yield FetchResult(
            table=payload.table or "c1_market.block_trade_qmt",
            columns=[], rows=[], last_key="",
            elapsed_sec=0.0,
            error="QMT无大宗交易接口，已由AKShare Provider覆盖（block_trade_incremental）",
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
