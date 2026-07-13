# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.ifind_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] iFinDPy SDK (THS_iFinDLogin/THS_BasicData/THS_Trans2DataFrame)
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] connect() 从 IFIND_LICENSE 环境变量读 license；配额错误码-4318/-4309 透传不重试
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] fetch 异常->yield FetchResult(error=str)；配额耗尽->yield error 并 return
# [TESTS] tests/zephyr/data/test_providers.py::TestIFindHelpers
# [A_module] module_id=MOD-L00-004-ifind_provider | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""IFindProvider 实现（MOD-L00-004 §4.3 数据源集成器）。

封装同花顺 iFinDPy SDK，继承 DataSourceBase，提供日频估值等数据拉取能力。

支持的能力（capability，通过 payload.extra["capability"] 路由）：
- daily_valuation: 日频估值（PE/PB/PS/PCF），写入 c1_market.daily_valuation
- kline_daily: 日K线（前复权，THS_HistoryQuotes），写入 c1_market.kline_daily
- kline_index: 指数日K线（THS_HistoryQuotes），写入 c1_market.kline_index
- money_flow: 资金流向（THS_iwencai i问财），写入 c1_market.money_flow

设计要点：
- THS_iFinDLogin / THS_BasicData 等在方法内部 import，避免模块加载时就要求 iFinDPy 安装
- 月度配额错误码 -4318/-4309 直接透传给上层（配额耗尽重试无意义，不在 retry_on 中）
- THS_BasicData 调用经基类 _call_with_policy 包裹，自动限流 + 重试
- 凭证从环境变量 IFIND_USERNAME/IFIND_PASSWORD 读取
"""
from __future__ import annotations

import os
import time
import logging
import datetime
from typing import Iterator

from ..provider_base import DataSourceBase, FetchPayload, FetchResult, DataSourceMeta
from ..policy_registry import SourcePolicy


class IFindProvider(DataSourceBase):
    """同花顺 iFind 数据源 Provider。

    通过 iFinDPy SDK 拉取 A 股估值/K线/资金流等数据。
    认证方式：license_key（环境变量 IFIND_LICENSE）。
    线程安全模型：thread_local（每个线程需独立登录）。
    """

    source_name: str = "ifind"
    meta: DataSourceMeta = DataSourceMeta(
        name="ifind",
        display_name="同花顺 iFind",
        auth_type="username_password",
        requires_process=False,
        thread_safety="thread_local",
        rate_limit_default=0,
        capabilities=["kline_daily", "daily_valuation", "money_flow", "kline_index",
                      "edb_data", "industry_class_suppl",
                      "concept_sector", "realtime_snapshot",
                      "sector_meta"],
        known_issues=["月度配额-4318", "试用账号不支持沪深港通"],
    )

    # iFind 估值指标列表（THS_BD 不支持分号分隔多指标，需逐个查询）
    # (iFind指标名, 目标列名)
    _VALUATION_INDICATOR_LIST = [
        ("ths_pe_stock", "pe_ttm"),
        ("ths_pb_stock", "pb_mrq"),
        ("ths_ps_stock", "ps_ttm"),
        ("ths_pcf_stock_ttm", "pcf_ncf_ttm"),
    ]

    # 估值表列顺序
    _VALUATION_COLUMNS = ["trade_date", "symbol", "pe_ttm", "pb_mrq", "ps_ttm", "pcf_ncf_ttm"]
    # 估值目标表
    _VALUATION_TABLE = "c1_market.daily_valuation"

    # ---- kline_daily 能力 ----
    _KLINE_INDICATORS = "preClose,open,high,low,close,change,changeRatio,volume,turnoverRatio,amount"
    _KLINE_PARAMS = "Interval:D,CPS:1,baseDate:1900-01-01,Currency:YSHB,fill:Previous"
    _KLINE_COLUMNS = ["trade_date", "symbol", "open", "close", "high", "low",
                      "volume", "amount", "amplitude", "pct_change", "change",
                      "turnover", "data_source"]
    _KLINE_TABLE = "c1_market.kline_daily"

    # ---- kline_index 能力 ----
    _INDEX_KLINE_INDICATORS = "open,high,low,close,volume,amount"
    _INDEX_KLINE_PARAMS = "Interval:D,CPS:0,baseDate:1900-01-01,Currency:YSHB,fill:Previous"
    _INDEX_KLINE_COLUMNS = ["trade_date", "symbol", "name", "open", "high", "low",
                            "close", "volume", "amount", "advance_count",
                            "decline_count", "data_source", "quality_flag"]
    _INDEX_KLINE_TABLE = "c1_market.kline_index"
    # 主要指数代码 -> 名称 映射（iFind 格式）
    _INDEX_NAME_MAP = {
        "000001.SH": "上证指数",
        "399001.SZ": "深证成指",
        "399006.SZ": "创业板指",
        "399005.SZ": "中小板指",
        "000300.SH": "沪深300",
        "000905.SH": "中证500",
        "000852.SH": "中证1000",
        "000016.SH": "上证50",
        "000688.SH": "科创50",
    }

    # ---- money_flow 能力 ----
    _MONEY_FLOW_COLUMNS = ["trade_date", "symbol", "close", "pct_change",
                           "main_net_inflow", "main_net_inflow_pct",
                           "super_large_net_inflow", "super_large_net_inflow_pct",
                           "large_net_inflow", "large_net_inflow_pct",
                           "medium_net_inflow", "medium_net_inflow_pct",
                           "small_net_inflow", "small_net_inflow_pct",
                           "data_source"]
    _MONEY_FLOW_TABLE = "c1_market.money_flow"

    # CH fallback: 从 stock_list 获取在册 A 股 ts_code（SQL_ 前缀豁免 NO-BARE-SQL gate）
    SQL_STOCK_LIST_BY_STATUS = (
        "SELECT ts_code FROM c1_market.stock_list "
        "WHERE list_status = '上市' ORDER BY ts_code FORMAT TabSeparated"
    )

    # 每批 yield 的行数上限
    _BATCH_SIZE = 500

    def __init__(self):
        super().__init__()
        # THS_iFinDLogin 的返回值，供诊断/重登判断
        self._login_result: int | None = None

    # ============== 连接 / 登出 ==============

    def connect(self) -> None:
        """登录 iFind：从环境变量读取 username/password，调用 THS_iFinDLogin。

        成功（返回 0）则置 _connected=True；失败（负数）抛 RuntimeError。
        login 返回值存入 self._login_result 供后续诊断。

        Raises:
            RuntimeError: 凭证缺失或登录返回负数错误码。
        """
        from iFinDPy import THS_iFinDLogin

        username = os.environ.get("IFIND_USERNAME")
        password = os.environ.get("IFIND_PASSWORD")
        if not username or not password:
            raise RuntimeError(
                "环境变量 IFIND_USERNAME/IFIND_PASSWORD 未设置，无法登录 iFind"
            )

        self._log.info("正在登录 iFind ...")
        result = THS_iFinDLogin(username, password)
        self._login_result = result

        # 0 表示成功，负数表示失败
        if isinstance(result, (int, float)) and result < 0:
            self._connected = False
            raise RuntimeError(f"iFind 登录失败，错误码: {result}")

        self._connected = True
        self._log.info(f"iFind 登录成功，返回值: {result}")

    def health_check(self) -> bool:
        """探活：用 000001.SZ 的 PE 查询做心跳。

        不抛异常即视为健康（iFind 错误码以异常或 dict 形式返回时被捕获）。

        Returns:
            True 表示连接可用。
        """
        if not self._connected:
            return False
        try:
            from iFinDPy import THS_BasicData
            THS_BasicData("000001.SZ", "ths_pe_stock", "2024-12-31,100")
            return True
        except Exception as e:
            self._log.warning(f"iFind 健康检查失败: {e}")
            return False

    def disconnect(self) -> None:
        """登出 iFind。即使登出抛异常也标记为已断开。"""
        try:
            from iFinDPy import THS_iFinDLogout
            THS_iFinDLogout()
            self._log.info("iFind 已登出")
        except Exception as e:
            self._log.warning(f"iFind 登出异常（已忽略）: {e}")
        finally:
            self._connected = False

    # ============== 数据拉取 ==============

    def fetch(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """按策略拉取数据，根据 payload.extra["capability"] 路由到具体子方法。

        Args:
            payload: 下载请求，extra["capability"] 决定走哪个子方法。
            policy: 调用策略（限流/重试）。

        Yields:
            FetchResult: 分批结果或错误结果。
        """
        extra = payload.extra or {}
        capability = extra.get("capability")

        if capability == "daily_valuation":
            yield from self._fetch_daily_valuation(payload, policy)
        elif capability == "kline_daily":
            yield from self._fetch_kline_daily(payload, policy)
        elif capability == "kline_index":
            yield from self._fetch_kline_index(payload, policy)
        elif capability == "money_flow":
            yield from self._fetch_money_flow(payload, policy)
        # ---- 新增能力路由（MOD-L00-004 fetch 路由扩展）----
        elif capability == "edb_data":
            yield from self._fetch_edb_data(payload, policy)
        elif capability == "industry_class_suppl":
            yield from self._fetch_industry_class_suppl(payload, policy)
        elif capability == "concept_sector":
            yield from self._fetch_concept_sector(payload, policy)
        elif capability == "realtime_snapshot":
            yield from self._fetch_realtime_snapshot(payload, policy)
        elif capability == "sector_meta":
            yield from self._fetch_sector_meta(payload, policy)
        else:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error=f"未知 capability: {capability}",
            )

    def _fetch_daily_valuation(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """拉取日频估值（PE/PB/PS/PCF），写入 c1_market.daily_valuation。

        THS_BD 不支持分号分隔多指标（返回 -209），需逐个指标单独查询后合并。

        输入：
            payload.symbols: ts_code 列表，如 ["000001.SZ","000002.SZ"]
            payload.extra["snapshot_dates"]: 日期字符串列表，如 ["2024-12-31","2024-06-30"]

        输出列顺序: ["trade_date","symbol","pe_ttm","pb_mrq","ps_ttm","pcf_ncf_ttm"]
        每 500 行 yield 一个 FetchResult；last_key 为当前处理的 date。

        遇到配额耗尽（-4318/-4309）或其他 iFind 错误码时，yield 错误结果并 return。
        """
        from iFinDPy import THS_BasicData, THS_Trans2DataFrame

        symbols = payload.symbols or []
        extra = payload.extra or {}
        snapshot_dates = extra.get("snapshot_dates", [])

        # snapshot_dates 为空时，自动从 payload.start/end 生成（每日一条）
        if not snapshot_dates and payload.start and payload.end:
            cur = payload.start
            while cur <= payload.end:
                # 简单按日生成（含非交易日，THS_BD 对非交易日返回空值，不影响）
                snapshot_dates.append(cur.isoformat())
                cur += datetime.timedelta(days=1)

        if not symbols or not snapshot_dates:
            yield FetchResult(
                table=self._VALUATION_TABLE,
                columns=self._VALUATION_COLUMNS,
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error="symbols 或 snapshot_dates 为空",
            )
            return

        batch_rows: list[tuple] = []
        start_ts = time.time()

        for date in snapshot_dates:
            for ts_code in symbols:
                # THS_BD 不支持分号多指标，逐个查询
                vals: dict[str, float] = {}
                fatal_error = None
                for ind_name, col_name in self._VALUATION_INDICATOR_LIST:
                    params = f"{date},100"
                    try:
                        raw = self._call_with_policy(
                            THS_BasicData, policy,
                            ts_code, ind_name, params,
                        )
                    except Exception as e:
                        self._log.error(f"THS_BasicData 调用异常 {ts_code}@{date}/{ind_name}: {e}")
                        fatal_error = str(e)
                        break

                    # 检查 iFind 错误码
                    is_error, code, msg = self._check_ifind_error(raw)
                    if is_error:
                        if code in (-4318, -4309):
                            fatal_error = f"iFind配额耗尽: {code}"
                            self._log.error(f"{ts_code}@{date}/{ind_name} {fatal_error}")
                            break
                        elif code == -209 and col_name == "pcf_ncf_ttm":
                            # PCF 在 THS_BD 中不支持(-209)，跳过，稍后用 i问财补齐
                            self._log.debug(f"PCF THS_BD 不支持(-209) {ts_code}@{date}，将用 i问财补齐")
                            continue
                        else:
                            fatal_error = f"iFind错误: {code} {msg}".strip()
                            self._log.error(f"{ts_code}@{date}/{ind_name} {fatal_error}")
                            break

                    # 转 DataFrame 提取值
                    try:
                        df = THS_Trans2DataFrame(raw)
                        if df is not None and len(df) > 0:
                            vals[col_name] = self.safe_float(df.iloc[0].get(ind_name))
                    except Exception as e:
                        self._log.warning(f"THS_Trans2DataFrame 失败 {ts_code}@{date}/{ind_name}: {e}")

                # PCF 用 i问财补齐（THS_BD 不支持 ths_pcf_stock_ttm，i问财可查当天值）
                if "pcf_ncf_ttm" not in vals and not fatal_error:
                    today_str = datetime.date.today().isoformat()
                    if date == today_str:
                        try:
                            pcf_val = self._fetch_pcf_via_iwencai(ts_code, policy)
                            if pcf_val is not None:
                                vals["pcf_ncf_ttm"] = pcf_val
                        except Exception as e:
                            self._log.warning(f"i问财查 PCF 失败 {ts_code}: {e}")

                # 致命错误（配额/连接）→ yield error 并 return
                if fatal_error and ("配额" in fatal_error or "-4318" in fatal_error):
                    yield FetchResult(
                        table=self._VALUATION_TABLE,
                        columns=self._VALUATION_COLUMNS,
                        rows=[],
                        last_key=date,
                        elapsed_sec=time.time() - start_ts,
                        error=fatal_error,
                    )
                    return

                symbol = self._ts_code_to_symbol(ts_code)
                batch_rows.append((
                    date, symbol,
                    vals.get("pe_ttm"),
                    vals.get("pb_mrq"),
                    vals.get("ps_ttm"),
                    vals.get("pcf_ncf_ttm"),
                ))

                # 每 500 行 yield 一次
                if len(batch_rows) >= self._BATCH_SIZE:
                    yield FetchResult(
                        table=self._VALUATION_TABLE,
                        columns=self._VALUATION_COLUMNS,
                        rows=batch_rows[:],
                        last_key=date,
                        elapsed_sec=time.time() - start_ts,
                    )
                    batch_rows.clear()
                    start_ts = time.time()

            # 当前 date 处理完，yield 剩余行
            if batch_rows:
                yield FetchResult(
                    table=self._VALUATION_TABLE,
                    columns=self._VALUATION_COLUMNS,
                    rows=batch_rows[:],
                    last_key=date,
                    elapsed_sec=time.time() - start_ts,
                )
                batch_rows.clear()
                start_ts = time.time()

    def _fetch_pcf_via_iwencai(self, ts_code: str, policy: SourcePolicy) -> float | None:
        """用 i问财(THS_iwencai) 查 PCF（市现率）。

        THS_BD 不支持 ths_pcf_stock_ttm（返回 -209），改用 i问财查当天最新值。
        i问财只返回当天值，不支持历史日期查询。

        Args:
            ts_code: 股票代码，如 "600000.SH"
            policy: 调用策略

        Returns:
            PCF 值或 None
        """
        from iFinDPy import THS_iwencai, THS_Trans2DataFrame

        query = f"{ts_code} 市现率"
        raw = self._call_with_policy(THS_iwencai, policy, query, "stock")
        df = THS_Trans2DataFrame(raw)
        if df is not None and len(df) > 0:
            # 列名格式: 市现率(pcf,经营现金流)[20260710]
            for col in df.columns:
                if "市现率" in col or "pcf" in col.lower():
                    return self.safe_float(df.iloc[0][col])
        return None

    # ============== kline_daily 能力 ==============

    def _fetch_kline_daily(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """拉取日K线（前复权），写入 c1_market.kline_daily。

        使用 THS_HistoryQuotes（Interval:D, CPS:1 前复权）。
        指标: preClose/open/high/low/close/change/changeRatio/volume/turnoverRatio/amount
        amplitude 由 (high-low)/preClose*100 计算。

        Args:
            payload: symbols 为 iFind ts_code 列表（如 ["600000.SH"]）；
                     None 时通过 THS_DataPool 获取全部A股。
            policy: 调用策略

        Yields:
            FetchResult: 每 500 行一批
        """
        from iFinDPy import THS_HistoryQuotes, THS_Trans2DataFrame

        symbols = payload.symbols
        if not symbols:
            symbols = self._get_all_a_share_codes(policy)
        if not symbols:
            yield FetchResult(
                table=self._KLINE_TABLE, columns=self._KLINE_COLUMNS,
                rows=[], last_key="", elapsed_sec=0.0,
                error="无法获取标的清单（symbols 为空且 THS_DataPool 失败）",
            )
            return

        start_str = payload.start.strftime("%Y-%m-%d")
        end_str = payload.end.strftime("%Y-%m-%d")
        last_key = end_str
        batch_rows: list[tuple] = []
        start_ts = time.time()

        for ts_code in symbols:
            # 调用 THS_HistoryQuotes
            try:
                raw = self._call_with_policy(
                    THS_HistoryQuotes, policy,
                    ts_code, self._KLINE_INDICATORS, self._KLINE_PARAMS,
                    start_str, end_str,
                )
            except Exception as e:
                self._log.warning(f"THS_HistoryQuotes 调用失败 {ts_code}: {e}")
                continue

            # 检查错误码
            is_error, code, msg = self._check_ifind_error(raw)
            if is_error:
                if code in (-4318, -4309):
                    yield FetchResult(
                        table=self._KLINE_TABLE, columns=self._KLINE_COLUMNS,
                        rows=[], last_key=last_key,
                        elapsed_sec=time.time() - start_ts,
                        error=f"iFind配额耗尽: {code}",
                    )
                    return
                self._log.warning(f"{ts_code} iFind错误: {code} {msg}")
                continue

            # 转 DataFrame
            try:
                df = THS_Trans2DataFrame(raw)
            except Exception as e:
                self._log.warning(f"THS_Trans2DataFrame 失败 {ts_code}: {e}")
                continue

            if df is None or len(df) == 0:
                continue

            symbol = self._ts_code_to_symbol(ts_code)  # "600000.SH" -> "600000"

            for idx, row in df.iterrows():
                # 日期：DataFrame index 或 "time" 列
                trade_date = self._extract_date(idx, row)
                if not trade_date:
                    continue

                pre_close = self.safe_float(row.get("preClose"))
                open_ = self.safe_float(row.get("open"))
                close = self.safe_float(row.get("close"))
                high = self.safe_float(row.get("high"))
                low = self.safe_float(row.get("low"))
                volume = self.safe_float(row.get("volume"))
                amount = self.safe_float(row.get("amount"))
                change = self.safe_float(row.get("change"))
                pct_change = self.safe_float(row.get("changeRatio"))
                turnover = self.safe_float(row.get("turnoverRatio"))

                # amplitude = (high - low) / preClose * 100
                if pre_close and pre_close != 0 and high is not None and low is not None:
                    amplitude = round((high - low) / pre_close * 100, 4)
                else:
                    amplitude = 0.0

                batch_rows.append((
                    trade_date, symbol,
                    open_ or 0.0, close or 0.0, high or 0.0, low or 0.0,
                    int(volume) if volume else 0,
                    amount or 0.0,
                    amplitude,
                    pct_change or 0.0,
                    change or 0.0,
                    turnover or 0.0,
                    "ifind_qfq",
                ))

                if len(batch_rows) >= self._BATCH_SIZE:
                    yield FetchResult(
                        table=self._KLINE_TABLE, columns=self._KLINE_COLUMNS,
                        rows=batch_rows[:], last_key=last_key,
                        elapsed_sec=time.time() - start_ts,
                    )
                    batch_rows.clear()
                    start_ts = time.time()

        # yield 剩余
        if batch_rows:
            yield FetchResult(
                table=self._KLINE_TABLE, columns=self._KLINE_COLUMNS,
                rows=batch_rows[:], last_key=last_key,
                elapsed_sec=time.time() - start_ts,
            )

    # ============== kline_index 能力 ==============

    def _fetch_kline_index(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """拉取指数日K线，写入 c1_market.kline_index。

        使用 THS_HistoryQuotes（Interval:D, CPS:0 不复权）。
        payload.symbols 为指数代码列表（如 ["000300.SH"]）；
        None 时使用默认主要指数列表。

        Args:
            payload: 下载请求
            policy: 调用策略

        Yields:
            FetchResult: 每个指数一批
        """
        from iFinDPy import THS_HistoryQuotes, THS_Trans2DataFrame

        symbols = payload.symbols
        if not symbols:
            symbols = list(self._INDEX_NAME_MAP.keys())

        start_str = payload.start.strftime("%Y-%m-%d")
        end_str = payload.end.strftime("%Y-%m-%d")
        last_key = end_str
        batch_rows: list[tuple] = []
        start_ts = time.time()

        for ts_code in symbols:
            try:
                raw = self._call_with_policy(
                    THS_HistoryQuotes, policy,
                    ts_code, self._INDEX_KLINE_INDICATORS, self._INDEX_KLINE_PARAMS,
                    start_str, end_str,
                )
            except Exception as e:
                self._log.warning(f"THS_HistoryQuotes(index) 调用失败 {ts_code}: {e}")
                continue

            is_error, code, msg = self._check_ifind_error(raw)
            if is_error:
                if code in (-4318, -4309):
                    yield FetchResult(
                        table=self._INDEX_KLINE_TABLE,
                        columns=self._INDEX_KLINE_COLUMNS,
                        rows=[], last_key=last_key,
                        elapsed_sec=time.time() - start_ts,
                        error=f"iFind配额耗尽: {code}",
                    )
                    return
                self._log.warning(f"{ts_code} iFind错误: {code} {msg}")
                continue

            try:
                df = THS_Trans2DataFrame(raw)
            except Exception as e:
                self._log.warning(f"THS_Trans2DataFrame 失败 {ts_code}: {e}")
                continue

            if df is None or len(df) == 0:
                continue

            name = self._INDEX_NAME_MAP.get(ts_code, "")

            for idx, row in df.iterrows():
                trade_date = self._extract_date(idx, row)
                if not trade_date:
                    continue

                batch_rows.append(
                    self._build_index_kline_row(trade_date, ts_code, name, row)
                )

                if len(batch_rows) >= self._BATCH_SIZE:
                    yield FetchResult(
                        table=self._INDEX_KLINE_TABLE,
                        columns=self._INDEX_KLINE_COLUMNS,
                        rows=batch_rows[:], last_key=last_key,
                        elapsed_sec=time.time() - start_ts,
                    )
                    batch_rows.clear()
                    start_ts = time.time()

        if batch_rows:
            yield FetchResult(
                table=self._INDEX_KLINE_TABLE,
                columns=self._INDEX_KLINE_COLUMNS,
                rows=batch_rows[:], last_key=last_key,
                elapsed_sec=time.time() - start_ts,
            )

    @staticmethod
    def _build_index_kline_row(trade_date, ts_code, name, row) -> tuple:
        """构造 kline_index 行元组（open/high/low/close/volume/amount）。"""
        open_ = IFindProvider.safe_float(row.get("open"))
        high = IFindProvider.safe_float(row.get("high"))
        low = IFindProvider.safe_float(row.get("low"))
        close = IFindProvider.safe_float(row.get("close"))
        volume = IFindProvider.safe_float(row.get("volume"))
        amount = IFindProvider.safe_float(row.get("amount"))
        return (
            trade_date, ts_code, name,
            open_ or 0.0, high or 0.0, low or 0.0, close or 0.0,
            int(volume) if volume else 0,
            amount or 0.0,
            0,  # advance_count（iFind 不提供）
            0,  # decline_count
            "ifind",
            1,  # quality_flag
        )

    # ============== money_flow 能力 ==============

    def _fetch_money_flow(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """拉取资金流向数据，写入 c1_market.money_flow。

        使用 THS_iwencai（i问财）自然语言查询。
        逐日查询 "{date} 主力资金流向" 获取全市场资金流数据。

        i问财返回中文字段，映射到 schema：
            股票代码 -> symbol（转 sh/sz 前缀格式）
            收盘价 -> close
            涨跌幅 -> pct_change
            主力净流入-净额 -> main_net_inflow
            主力净流入-净占比 -> main_net_inflow_pct
            超大单净流入-净额 -> super_large_net_inflow
            ...（以此类推）

        Args:
            payload: 下载请求
            policy: 调用策略

        Yields:
            FetchResult: 每日一批
        """
        from iFinDPy import THS_iwencai

        last_key = payload.end.strftime("%Y-%m-%d")
        start_ts = time.time()

        # 逐日查询
        current = payload.start
        while current <= payload.end:
            date_cn = current.strftime("%Y年%m月%d日")
            date_iso = current.strftime("%Y-%m-%d")

            try:
                raw = self._call_with_policy(
                    THS_iwencai, policy,
                    f"{date_cn} 主力资金流向 超大单 大单 中单 小单 收盘价 涨跌幅",
                    "stock",
                )
            except Exception as e:
                self._log.warning(f"THS_iwencai 调用失败 {date_cn}: {e}")
                current += datetime.timedelta(days=1)
                continue

            # 检查错误码
            is_error, code, msg = self._check_ifind_error(raw)
            if is_error:
                if code in (-4318, -4309):
                    yield FetchResult(
                        table=self._MONEY_FLOW_TABLE,
                        columns=self._MONEY_FLOW_COLUMNS,
                        rows=[], last_key=date_iso,
                        elapsed_sec=time.time() - start_ts,
                        error=f"iFind配额耗尽: {code}",
                    )
                    return
                self._log.warning(f"money_flow {date_cn} iFind错误: {code} {msg}")
                current += datetime.timedelta(days=1)
                continue

            # 解析 i问财返回结果
            rows = self._parse_iwencai_money_flow(raw, date_iso)
            if rows:
                yield FetchResult(
                    table=self._MONEY_FLOW_TABLE,
                    columns=self._MONEY_FLOW_COLUMNS,
                    rows=rows, last_key=date_iso,
                    elapsed_sec=time.time() - start_ts,
                )
                start_ts = time.time()

            current += datetime.timedelta(days=1)

    def _parse_iwencai_money_flow(
        self, raw, date_iso: str
    ) -> list[tuple]:
        """解析 i问财资金流向返回结果。

        i问财返回 dict 格式：
            {
                'tables': [{
                    'table': {
                        '股票代码': ['600000.SH', ...],
                        '主力净流入-净额': [...],
                        ...
                    }
                }]
            }

        字段名中文->英文映射（模糊匹配，支持多种变体）。
        """
        if not isinstance(raw, dict) or "tables" not in raw:
            self._log.warning(f"money_flow i问财返回格式异常: {type(raw)}")
            return []

        try:
            table_data = raw["tables"][0]["table"]
        except (IndexError, KeyError, TypeError):
            self._log.warning("money_flow i问财返回无 table 数据")
            return []

        # 获取股票代码列表
        codes = self._find_column(table_data, ["股票代码", "thscode", "THSCODE"])
        if not codes:
            self._log.warning("money_flow i问财返回无股票代码列")
            return []

        # 字段映射（模糊匹配）
        col_map = {
            "close": ["收盘价:不复权", "收盘价", "close"],
            "pct_change": ["涨跌幅:前复权", "涨跌幅"],
            "main_net_inflow": ["主力资金流向", "主力净流入-净额", "主力净流入"],
            "main_net_inflow_pct": ["主力净流入-净占比", "主力净流入占比"],
            "super_large_net_inflow": ["特大单净额", "超大单净流入-净额", "超大单净流入"],
            "super_large_net_inflow_pct": ["超大单净流入-净占比", "超大单净流入占比"],
            "large_net_inflow": ["dde大单净额", "大单净流入-净额", "大单净流入"],
            "large_net_inflow_pct": ["大单净流入-净占比", "大单净流入占比"],
            "medium_net_inflow": ["中单净额", "中单净流入-净额", "中单净流入"],
            "medium_net_inflow_pct": ["中单净流入-净占比", "中单净流入占比"],
            "small_net_inflow": ["小单净额", "小单净流入-净额", "小单净流入"],
            "small_net_inflow_pct": ["小单净流入-净占比", "小单净流入占比"],
        }

        # 提取各列数据
        col_data = {}
        for schema_key, candidates in col_map.items():
            col_data[schema_key] = self._find_column(table_data, candidates)

        rows = []
        n = len(codes)
        for i in range(n):
            ts_code = str(codes[i])
            symbol = self._ts_code_to_money_flow_symbol(ts_code)
            if not symbol:
                continue

            def get_val(key, idx):
                vals = col_data.get(key)
                if not vals or idx >= len(vals):
                    return None
                return self.safe_float(vals[idx])

            rows.append((
                date_iso,
                symbol,
                get_val("close", i) or 0.0,
                get_val("pct_change", i) or 0.0,
                get_val("main_net_inflow", i) or 0.0,
                get_val("main_net_inflow_pct", i) or 0.0,
                get_val("super_large_net_inflow", i) or 0.0,
                get_val("super_large_net_inflow_pct", i) or 0.0,
                get_val("large_net_inflow", i) or 0.0,
                get_val("large_net_inflow_pct", i) or 0.0,
                get_val("medium_net_inflow", i) or 0.0,
                get_val("medium_net_inflow_pct", i) or 0.0,
                get_val("small_net_inflow", i) or 0.0,
                get_val("small_net_inflow_pct", i) or 0.0,
                "ifind_iwencai",
            ))

        return rows

    # ============== edb_data 能力（宏观经济数据库） ==============

    # EDB 默认指标列表（104个核心宏观指标，覆盖7大类）
    # 来源：iFind EDB宏观经济数据库（77,909个指标中筛选策略高价值核心指标）
    # 命名规则：M=宏观(月频为主) / L=利率(日频为主) / G=全球宏观(日频) / S=其他
    # 可通过 payload.extra["indices"] 覆盖；配额5万条/周（每周一重置）
    _EDB_DEFAULT_INDICES = [
        # ---- 财政政策类（6个，月频）----
        "M002982045",  # 国家财政赤字:当月值
        "M001624993",  # 一般公共预算收入:税收收入:当月值
        "M003014407",  # 税收收入:国内增值税:当月值
        "M005658971",  # 债券市场发行债券:国债:当月值
        "M005658972",  # 债券市场发行债券:地方政府债券:当月值
        "M005116408",  # 地方政府专项债券:新增:当月值
        # ---- 参考利率类（17个，日频为主）----
        "L001619604",  # 中债国债到期收益率:10年
        "L001618296",  # 中债国债到期收益率:1年
        "L002959797",  # 中债国开债到期收益率:10年
        "L002959789",  # 中债国开债到期收益率:1年
        "L003009233",  # 中债中短期票据到期收益率(AAA):10年
        "L001618023",  # 中债中短期票据到期收益率(AAA):1年
        "L004421938",  # 中债商业银行二级资本债(AAA-):10年
        "L004421929",  # 中债商业银行二级资本债(AAA-):1年
        "L020452548",  # 中债证券公司永续次级债(AAA-):10年
        "L020452539",  # 中债证券公司永续次级债(AAA-):1年
        "L001619089",  # 固定利率国债:发行利率:3个月
        "L001619090",  # 固定利率国债:发行利率:6个月
        "L001618148",  # 固定利率国债:发行利率:1年
        "L001619092",  # 固定利率国债:发行利率:10年
        "L003018725",  # 固定利率地方政府债:发行利率:5年
        "M005418622",  # LPR:1年
        "M024933257",  # LPR:5年
        # ---- 拆借利率类（9个，日频）----
        "M002816448",  # Shibor:隔夜
        "M002816449",  # Shibor:1周
        "M002816452",  # Shibor:3月
        "M002816453",  # Shibor:6月
        "M002816455",  # Shibor:1年
        "L001619370",  # IBO001
        "L001619053",  # IBO007
        "L004109441",  # DIBO001
        "L004109442",  # DIBO007
        # ---- 宏观货币类（8个，月频）----
        "M004891015",  # 社会融资规模增量:当月值
        "M004891020",  # 社会融资规模存量:期末值
        "M004891021",  # 社会融资规模存量:期末同比
        "M003146166",  # 金融机构:新增人民币贷款:中长期:当月值
        "M001625226",  # M0(流通中货币):同比
        "M001625224",  # M1(货币):同比
        "M001625222",  # M2(货币和准货币):同比
        "M019977046",  # 货币乘数:期末值
        # ---- 回购利率类（8个，日频）----
        "L004109429",  # R001
        "L001618739",  # DR001
        "L004369613",  # GC001(加权平均)
        "L004109430",  # R007
        "L001619493",  # DR007
        "L004369617",  # GC007(加权平均)
        "M004369945",  # 成交量:银行间质押式回购
        "M005880925",  # 成交量:R001
        # ---- 央行资产负债表类（9个，月频）----
        "M012670723",  # 货币当局:负债:政府存款
        "M012670708",  # 货币当局:资产:国外资产:外汇
        "M012670713",  # 货币当局:资产:对其他存款性公司债权
        "M012670719",  # 货币当局:储备货币:其他存款性公司存款
        "M004371436",  # 货币当局:储备货币:非金融机构存款
        "M012670718",  # 货币当局:储备货币:货币发行
        "M002859222",  # 金融机构:人民币存款余额:非金融企业
        "M002859221",  # 金融机构:人民币存款余额:住户
        "M004030792",  # 金融机构:政府存款:机关团体存款
        # ---- 利率互换类（5个，日频）----
        "L001619014",  # 利率互换:FR007:1年
        "L001619145",  # 利率互换:FR007:5年
        "L004381280",  # 利率互换:FR007:10年
        "L001619147",  # 利率互换:3M SHIBOR:1年
        "L002895990",  # 利率互换:3M SHIBOR:5年
        # ---- 海外利率/汇率类（6个，日频）----
        "M017661944",  # 即期汇率:USD/CNY
        "G002600886",  # 美国:名义美元指数:广义
        "L015211683",  # 美国国债收益率曲线:2年
        "L015211687",  # 美国国债收益率曲线:10年
        "L015211689",  # 美国国债收益率曲线:30年
        "G002600763",  # 美国:联邦基金利率
        # ---- 央行操作类（15个）----
        "M002816548",  # 逆回购:7日:回购利率
        "M002816549",  # 逆回购:7日:回购金额
        "M002816550",  # 逆回购:14日:回购利率
        "L015211397",  # 货币净投放量
        "M004211453",  # MLF:操作利率:1年
        "M036089917",  # MLF:投放金额:当月值
        "M004026834",  # MLF:余额
        "M036089923",  # 中央国库现金管理:投放金额:当月值
        "M004202910",  # PSL:期末值
        "M004083914",  # PSL:利率
        "M003523109",  # SLF:余额
        "M004198292",  # SLF:操作金额:合计
        "M004369941",  # SLF:操作利率:1个月
        "M036089940",  # 公开市场国债买卖:净投放金额:当月值
        "M025698822",  # 买断式逆回购:操作量:当月值
        # ---- 银行存单类（17个，日频为主）----
        "L004428052",  # 中债商业银行同业存单到期收益率(AAA):3月
        "L004428053",  # 中债商业银行同业存单到期收益率(AAA):6月
        "L004428055",  # 中债商业银行同业存单到期收益率(AAA):1年
        "M005658976",  # 债券市场发行债券:同业存单:当月值
        "M005658983",  # 债券市场托管余额:同业存单
        "M020086858",  # 大额存单:发行利率:3个月
        "M020086861",  # 大额存单:发行利率:6个月
        "M020086863",  # 大额存单:发行利率:1年
        "L004365967",  # 固定利率同业存单:发行利率:3个月
        "L004365968",  # 固定利率同业存单:发行利率:6个月
        "L004365970",  # 固定利率同业存单:发行利率:1年
        "L004365980",  # 固定利率同业存单:发行利率(城商行):1年
        "L004365975",  # 固定利率同业存单:发行利率(股份制银行):1年
        "L017493155",  # 固定利率同业存单发行利率(国有银行):1年
        "L004365985",  # 固定利率同业存单:发行利率(农商行):1年
        "L017493160",  # 固定利率同业存单发行利率(外资银行):1年
        "L017493173",  # 固定利率同业存单发行利率(民营银行):1年
        # ---- 票据贴现类（2个，日频）----
        "M021397974",  # 转贴(国股贴)半年国股
        "M021397968",  # 直贴半年国股
        # ---- 其他因素类（2个）----
        "S005098105",  # 新成立基金份额:货币市场基金
        "S004369831",  # 银行理财产品预期年收益率:人民币:全市场:1年
    ]

    def _fetch_edb_data(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """拉取宏观经济数据库（EDB）指标，写入 c1_market.edb_data。

        使用 THS_EDBQuery(indicator_codes, start_date, end_date) 获取宏观指标序列。
        指标代码从 payload.extra["indices"] 获取，缺省用 _EDB_DEFAULT_INDICES。

        表 schema: (report_date, indicator_code, indicator_name,
                    indicator_value, data_source)

        Args:
            payload: 下载请求，extra["indices"] 可指定指标代码列表
            policy: 调用策略

        Yields:
            FetchResult: 每个指标一批
        """
        table = payload.table or "c1_market.edb_data"
        columns = [
            "report_date", "indicator_code", "indicator_name",
            "indicator_value", "data_source",
        ]

        extra = payload.extra or {}
        indices = extra.get("indices") or self._EDB_DEFAULT_INDICES
        if not indices:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=0.0, error="指标列表为空",
            )
            return

        start_str = payload.start.strftime("%Y-%m-%d")
        end_str = payload.end.strftime("%Y-%m-%d")
        last_key = end_str
        batch_rows: list[tuple] = []
        start_ts = time.time()

        # 逐指标查询（THS_EDBQuery 每次查一个指标序列）
        for ind_code in indices:
            df, fatal_code = self._query_edb_indicator(
                ind_code, start_str, end_str, policy,
            )
            # 配额耗尽 → yield error 并 return
            if fatal_code is not None:
                yield FetchResult(
                    table=table, columns=columns, rows=[],
                    last_key=last_key,
                    elapsed_sec=time.time() - start_ts,
                    error=f"iFind配额耗尽: {fatal_code}",
                )
                return
            if df is None or len(df) == 0:
                continue

            # 逐行解析并累积
            for idx, row in df.iterrows():
                parsed = self._parse_edb_row(idx, row, ind_code)
                if parsed is not None:
                    batch_rows.append(parsed)
                    if len(batch_rows) >= self._BATCH_SIZE:
                        yield FetchResult(
                            table=table, columns=columns,
                            rows=batch_rows[:], last_key=last_key,
                            elapsed_sec=time.time() - start_ts,
                        )
                        batch_rows.clear()
                        start_ts = time.time()

        if batch_rows:
            yield FetchResult(
                table=table, columns=columns,
                rows=batch_rows[:], last_key=last_key,
                elapsed_sec=time.time() - start_ts,
            )

    def _query_edb_indicator(
        self, ind_code: str, start_str: str, end_str: str, policy: "SourcePolicy",
    ) -> tuple:
        """查询单个 EDB 指标并转 DataFrame（降低 _fetch_edb_data 复杂度）。

        Args:
            ind_code: 指标代码
            start_str: 开始日期
            end_str: 结束日期
            policy: 调用策略

        Returns:
            (df, fatal_code) 二元组。fatal_code 非 None 表示配额耗尽（调用方应中止）；
            df 为 None 表示该指标跳过（错误或无数据）。
        """
        from iFinDPy import THS_EDBQuery, THS_Trans2DataFrame

        try:
            raw = self._call_with_policy(
                THS_EDBQuery, policy,
                ind_code, start_str, end_str,
            )
        except Exception as e:
            self._log.warning(f"THS_EDBQuery 调用失败: {e}")
            return (None, None)

        # 检查错误码
        is_error, code, msg = self._check_ifind_error(raw)
        if is_error:
            if code in (-4318, -4309):
                return (None, code)
            self._log.warning(f"EDB iFind错误: {code} {msg}")
            return (None, None)

        # 解析返回结果（尝试 DataFrame 转换）
        try:
            df = THS_Trans2DataFrame(raw)
        except Exception as e:
            self._log.warning(f"THS_Trans2DataFrame 失败: {e}")
            return (None, None)
        return (df, None)

    def _parse_edb_row(self, idx, row, ind_code: str):
        """解析 EDB DataFrame 单行为元组（降低 _fetch_edb_data 复杂度）。

        Args:
            idx: DataFrame 行索引
            row: DataFrame 行
            ind_code: 指标代码

        Returns:
            (report_date, ind_code, ind_name, ind_value, "ifind") 元组；
            日期无效时返回 None。
        """
        report_date = self._extract_date(idx, row)
        if not report_date:
            return None
        # 指标值：尝试指标代码列或 'value' 列
        ind_value = None
        for key in (ind_code, "value", "指标值", "valueData"):
            v = row.get(key)
            if v is not None:
                ind_value = self.safe_float(v)
                break
        # 指标名称：尝试 'name' / 'ths_edb_name' 列
        ind_name = ""
        for key in ("name", "ths_edb_name", "指标名称", "indicator_name"):
            v = row.get(key)
            if v is not None:
                ind_name = str(v)
                break
        return (report_date, ind_code, ind_name, ind_value, "ifind")

    # ============== industry_class_suppl 能力（同花顺板块分类） ==============

    def _fetch_industry_class_suppl(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """拉取同花顺行业分类，写入 c3_fundamental.industry_class_suppl。

        使用 THS_iwencai（i问财）批量查询全部 A 股的申万行业和同花顺行业分类。
        单次 API 调用即可获取全部股票的行业信息（替代 THS_BasicData 逐股查询）。
        表 schema: (symbol, industry_sw, industry_zsi, industry_level, data_source)
        - industry_sw ← 所属申万行业（如 "银行--股份制银行Ⅱ--股份制银行Ⅲ"）
        - industry_zsi ← 所属同花顺行业（如 "银行-银行-股份制银行"）

        Args:
            payload: 下载请求（symbols 忽略，i问财全市场查询）
            policy: 调用策略

        Yields:
            FetchResult: 每 500 行一批
        """
        from iFinDPy import THS_iwencai

        table = payload.table or "c3_fundamental.industry_class_suppl"
        columns = ["symbol", "industry_sw", "industry_zsi", "industry_level", "data_source"]

        today_str = datetime.date.today().strftime("%Y-%m-%d")
        last_key = today_str
        start_ts = time.time()

        # 单次 i问财查询获取全部 A 股行业分类
        try:
            raw = self._call_with_policy(
                THS_iwencai, policy,
                "全部A股 申万行业 同花顺行业", "stock",
            )
        except Exception as e:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=time.time() - start_ts,
                error=f"THS_iwencai 调用失败: {e}",
            )
            return

        # 检查错误码
        is_error, code, msg = self._check_ifind_error(raw)
        if is_error:
            if code in (-4318, -4309):
                yield FetchResult(
                    table=table, columns=columns, rows=[], last_key=last_key,
                    elapsed_sec=time.time() - start_ts,
                    error=f"iFind配额耗尽: {code}",
                )
                return
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=time.time() - start_ts,
                error=f"i问财错误: {code} {msg}",
            )
            return

        # 解析 i问财返回的表格
        batch_rows: list[tuple] = []
        try:
            tables = raw.get("tables", []) if isinstance(raw, dict) else []
            if not tables:
                yield FetchResult(
                    table=table, columns=columns, rows=[], last_key="",
                    elapsed_sec=time.time() - start_ts,
                    error="i问财返回空表格",
                )
                return
            tbl_data = tables[0].get("table", {})
            codes = tbl_data.get("股票代码", [])
            sw_list = tbl_data.get("所属申万行业", [])
            ths_list = tbl_data.get("所属同花顺行业", [])

            for i, ts_code in enumerate(codes):
                symbol = self._ts_code_to_symbol(ts_code)
                sw = str(sw_list[i]) if i < len(sw_list) else ""
                ths = str(ths_list[i]) if i < len(ths_list) else ""
                batch_rows.append((symbol, sw, ths, 0, "ifind"))

                if len(batch_rows) >= self._BATCH_SIZE:
                    yield FetchResult(
                        table=table, columns=columns,
                        rows=batch_rows[:], last_key=last_key,
                        elapsed_sec=time.time() - start_ts,
                    )
                    batch_rows.clear()
                    start_ts = time.time()
        except Exception as e:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=time.time() - start_ts,
                error=f"i问财结果解析失败: {e}",
            )
            return

        if batch_rows:
            yield FetchResult(
                table=table, columns=columns,
                rows=batch_rows[:], last_key=last_key,
                elapsed_sec=time.time() - start_ts,
            )

    def _query_symbol_industries(
        self, ts_code: str, today_str: str, policy: "SourcePolicy",
    ) -> tuple[str, str, str | None]:
        """查询单只股票的申万/中证行业分类（降低 _fetch_industry_class_suppl 复杂度）。

        Args:
            ts_code: 标的代码
            today_str: 今日日期字符串
            policy: 调用策略

        Returns:
            (industry_sw, industry_zsi, fatal_error) 三元组。
            fatal_error 非 None 且含"配额"时表示配额耗尽需中止。
        """
        from iFinDPy import THS_BasicData, THS_Trans2DataFrame

        industry_sw = ""
        industry_zsi = ""
        fatal_error = None

        for ind_name, col_target in [
            ("ths_the_sw_industry", "sw"),
            ("ths_the_zs_industry", "zsi"),
        ]:
            try:
                raw = self._call_with_policy(
                    THS_BasicData, policy,
                    ts_code, ind_name, f"{today_str},100",
                )
            except Exception as e:
                self._log.warning(f"THS_BasicData 调用失败: {e}")
                fatal_error = str(e)
                break

            is_error, code, msg = self._check_ifind_error(raw)
            if is_error:
                if code in (-4318, -4309):
                    fatal_error = f"iFind配额耗尽: {code}"
                    break
                # -209 表示不支持该指标，跳过
                if code == -209:
                    continue
                self._log.warning(f"行业分类 iFind错误: {code} {msg}")
                continue

            try:
                df = THS_Trans2DataFrame(raw)
                if df is not None and len(df) > 0:
                    val = df.iloc[0].get(ind_name)
                    if val is not None:
                        if col_target == "sw":
                            industry_sw = str(val)
                        else:
                            industry_zsi = str(val)
            except Exception as e:
                self._log.warning(f"THS_Trans2DataFrame 失败: {e}")

        return industry_sw, industry_zsi, fatal_error

    # ============== concept_sector 能力（概念板块列表） ==============

    # 概念板块表列顺序
    _CONCEPT_SECTOR_COLUMNS = ["sector_code", "sector_name", "data_source"]
    _CONCEPT_SECTOR_TABLE = "c1_market.concept_sector"

    def _fetch_concept_sector(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """拉取概念板块列表，写入 c1_market.concept_sector。

        使用 THS_iwencai（i问财）查询"概念板块"，获取全市场股票的概念板块归属，
        然后解析"所属概念"字段提取唯一概念板块名称。

        THS_BasicData/THS_DataPool 不支持直接获取概念板块列表（返回 -209 参数错误），
        i问财是唯一可用的接口。

        表 schema: (sector_code, sector_name, data_source)
        - sector_code: 概念板块名称（i问财不返回独立代码，用名称作代码）
        - sector_name: 概念板块名称
        - data_source: "ifind_iwencai"

        Args:
            payload: 下载请求（symbols 忽略，全市场查询）
            policy: 调用策略

        Yields:
            FetchResult: 一批（概念板块列表通常约 200-400 个）
        """
        from iFinDPy import THS_iwencai

        table = payload.table or self._CONCEPT_SECTOR_TABLE
        columns = self._CONCEPT_SECTOR_COLUMNS
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        start_ts = time.time()

        try:
            raw = self._call_with_policy(
                THS_iwencai, policy,
                "概念板块 代码 名称", "stock",
            )
        except Exception as e:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=time.time() - start_ts,
                error=f"THS_iwencai 调用失败: {e}",
            )
            return

        # 检查错误码
        is_error, code, msg = self._check_ifind_error(raw)
        if is_error:
            if code in (-4318, -4309):
                yield FetchResult(
                    table=table, columns=columns, rows=[], last_key=today_str,
                    elapsed_sec=time.time() - start_ts,
                    error=f"iFind配额耗尽: {code}",
                )
                return
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=today_str,
                elapsed_sec=time.time() - start_ts,
                error=f"iFind错误: {code} {msg}".strip(),
            )
            return

        # 解析 i问财返回，提取唯一概念板块名称
        rows = self._parse_concept_sectors(raw)
        if rows:
            yield FetchResult(
                table=table, columns=columns,
                rows=rows, last_key=today_str,
                elapsed_sec=time.time() - start_ts,
            )
        else:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=today_str,
                elapsed_sec=time.time() - start_ts,
                error="概念板块列表为空（i问财返回无所属概念列）",
            )

    def _parse_concept_sectors(self, raw) -> list[tuple]:
        """解析 i问财概念板块返回，提取唯一概念板块名称。

        i问财返回 dict 格式：
            {'tables': [{'table': {'股票代码': [...], '所属概念': [...]}}]}

        "所属概念"字段为分号分隔的概念板块名称列表，如：
            "融资融券;深股通;小金属概念;黄金概念"

        Returns:
            (sector_code, sector_name, "ifind_iwencai") 元组列表，按名称排序
        """
        if not isinstance(raw, dict) or "tables" not in raw:
            self._log.warning("concept_sector i问财返回格式异常")
            return []

        try:
            table_data = raw["tables"][0]["table"]
        except (IndexError, KeyError, TypeError):
            self._log.warning("concept_sector i问财返回无 table 数据")
            return []

        # 查找"所属概念"列
        concept_col = self._find_column(table_data, ["所属概念", "概念板块", "概念"])
        if not concept_col:
            self._log.warning("concept_sector i问财返回无'所属概念'列")
            return []

        # 提取唯一概念板块名称
        unique_sectors: set[str] = set()
        for concepts_str in concept_col:
            if not concepts_str or not isinstance(concepts_str, str):
                continue
            # 分号分隔的概念板块名称
            for name in concepts_str.split(";"):
                name = name.strip()
                if name:
                    unique_sectors.add(name)

        # 转为元组列表，按名称排序
        rows = [
            (name, name, "ifind_iwencai")
            for name in sorted(unique_sectors)
        ]
        self._log.info(f"concept_sector 提取到 {len(rows)} 个概念板块")
        return rows

    # ============== realtime_snapshot 能力（实时行情快照） ==============

    # 实时快照表列顺序
    _REALTIME_SNAPSHOT_COLUMNS = [
        "snapshot_time", "symbol", "open", "high", "low",
        "close", "volume", "amount", "data_source",
    ]
    _REALTIME_SNAPSHOT_TABLE = "c1_market.realtime_snapshot"
    # THS_RealtimeQuotes 指标（分号分隔，支持多指标）
    _REALTIME_INDICATORS = "ths_open;ths_high;ths_low;ths_close;ths_volume;ths_amount"

    def _fetch_realtime_snapshot(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """拉取实时行情快照，写入 c1_market.realtime_snapshot。

        使用 THS_RealtimeQuotes(thscode, jsonIndicator) 获取实时 OHLCV 数据。
        非交易时段返回 -4001（无数据），属正常行为。

        表 schema: (snapshot_time, symbol, open, high, low, close, volume, amount, data_source)

        Args:
            payload: symbols 为 ts_code 列表（如 ["000001.SZ","600000.SH"]）；
                     None 时通过 THS_DataPool 获取全部A股。
            policy: 调用策略

        Yields:
            FetchResult: 每批一个
        """
        from iFinDPy import THS_RealtimeQuotes

        table = payload.table or self._REALTIME_SNAPSHOT_TABLE
        columns = self._REALTIME_SNAPSHOT_COLUMNS

        symbols = payload.symbols
        if not symbols:
            symbols = self._get_all_a_share_codes(policy)
        if not symbols:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=0.0, error="无法获取标的清单（symbols 为空且 THS_DataPool 失败）",
            )
            return

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        batch_rows: list[tuple] = []
        start_ts = time.time()
        last_key = now_str

        # 逐批查询（THS_RealtimeQuotes 支持逗号分隔多标的，但为避免超限分批处理）
        chunk_size = 50
        for i in range(0, len(symbols), chunk_size):
            chunk = symbols[i:i + chunk_size]
            codes_str = ",".join(chunk)

            rows, fatal_error = self._query_realtime_chunk(
                codes_str, policy,
            )
            # 配额耗尽 → yield error 并 return
            if fatal_error:
                yield FetchResult(
                    table=table, columns=columns, rows=[],
                    last_key=last_key,
                    elapsed_sec=time.time() - start_ts,
                    error=fatal_error,
                )
                return

            # 为每行补充 snapshot_time 和 symbol
            for row in rows:
                batch_rows.append(row)

            if len(batch_rows) >= self._BATCH_SIZE:
                yield FetchResult(
                    table=table, columns=columns,
                    rows=batch_rows[:], last_key=last_key,
                    elapsed_sec=time.time() - start_ts,
                )
                batch_rows.clear()
                start_ts = time.time()

        if batch_rows:
            yield FetchResult(
                table=table, columns=columns,
                rows=batch_rows[:], last_key=last_key,
                elapsed_sec=time.time() - start_ts,
            )

    def _query_realtime_chunk(
        self, codes_str: str, policy: "SourcePolicy",
    ) -> tuple[list[tuple], str | None]:
        """查询单批实时行情并解析为行元组（降低 _fetch_realtime_snapshot 复杂度）。

        Args:
            codes_str: 逗号分隔的 ts_code 字符串（如 "000001.SZ,600000.SH"）
            policy: 调用策略

        Returns:
            (rows, fatal_error) 二元组。fatal_error 非 None 表示配额耗尽或致命错误；
            rows 为解析后的元组列表，每行格式：
            (snapshot_time, symbol, open, high, low, close, volume, amount, "ifind_realtime")
        """
        from iFinDPy import THS_RealtimeQuotes

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            raw = self._call_with_policy(
                THS_RealtimeQuotes, policy,
                codes_str, self._REALTIME_INDICATORS,
            )
        except Exception as e:
            self._log.warning(f"THS_RealtimeQuotes 调用失败: {e}")
            return ([], None)

        # 检查错误码
        is_error, code, msg = self._check_ifind_error(raw)
        if is_error:
            if code in (-4318, -4309):
                return ([], f"iFind配额耗尽: {code}")
            # -4001 表示无数据（非交易时段），不视为致命错误
            if code == -4001:
                self._log.info("THS_RealtimeQuotes 返回 -4001（非交易时段无数据）")
                return ([], None)
            self._log.warning(f"realtime_snapshot iFind错误: {code} {msg}")
            return ([], None)

        # 解析返回结果
        rows = self._parse_realtime_quotes(raw, now_str, codes_str)
        return (rows, None)

    def _parse_realtime_quotes(
        self, raw, now_str: str, codes_str: str,
    ) -> list[tuple]:
        """解析 THS_RealtimeQuotes 返回为行元组列表。

        THS_RealtimeQuotes 返回 dict 格式：
            {'tables': [{'table': {
                'thscode': ['000001.SZ', ...],
                'ths_open': [10.5, ...],
                'ths_high': [...],
                ...
            }}]}

        Args:
            raw: iFind 返回值
            now_str: 快照时间字符串
            codes_str: 原始请求的代码字符串（用于回退取代码）

        Returns:
            元组列表，每行 (snapshot_time, symbol, open, high, low, close, volume, amount, "ifind_realtime")
        """
        if not isinstance(raw, dict) or "tables" not in raw:
            return []

        try:
            table_data = raw["tables"][0]["table"]
        except (IndexError, KeyError, TypeError):
            return []

        # 获取股票代码列表
        codes = self._find_column(table_data, ["thscode", "THSCODE", "股票代码"])
        if not codes:
            # 回退：用请求的 codes_str 拆分
            codes = codes_str.split(",")
        n = len(codes)

        # 提取各指标列
        col_map = {
            "open": ["ths_open", "open", "开盘价"],
            "high": ["ths_high", "high", "最高价"],
            "low": ["ths_low", "low", "最低价"],
            "close": ["ths_close", "close", "收盘价"],
            "volume": ["ths_volume", "volume", "成交量"],
            "amount": ["ths_amount", "amount", "成交额"],
        }
        col_data = {}
        for schema_key, candidates in col_map.items():
            col_data[schema_key] = self._find_column(table_data, candidates)

        rows = []
        for i in range(n):
            ts_code = str(codes[i])
            symbol = self._ts_code_to_symbol(ts_code)

            open_val = self._get_list_val(col_data, "open", i)
            high_val = self._get_list_val(col_data, "high", i)
            low_val = self._get_list_val(col_data, "low", i)
            close_val = self._get_list_val(col_data, "close", i)
            volume_val = self._get_list_val(col_data, "volume", i)
            amount_val = self._get_list_val(col_data, "amount", i)

            rows.append((
                now_str, symbol,
                open_val, high_val, low_val, close_val,
                int(volume_val) if volume_val else None,
                amount_val,
                "ifind_realtime",
            ))

        return rows

    # ============== 辅助方法 ==============

    @staticmethod
    def _get_list_val(col_data: dict, key: str, idx: int) -> float | None:
        """从字典中按键取列表值并安全转 float。

        Args:
            col_data: 列数据字典 {key: [val1, val2, ...]}
            key: 列键名
            idx: 列表索引

        Returns:
            float 值或 None
        """
        vals = col_data.get(key)
        if not vals or idx >= len(vals):
            return None
        return IFindProvider.safe_float(vals[idx])

    @staticmethod
    def _ts_code_to_symbol(ts_code: str) -> str:
        """ts_code 转纯代码：'000001.SZ' -> '000001'。

        Args:
            ts_code: iFind 标的代码，格式 'XXXXXX.SZ/SH/BJ'。

        Returns:
            点号前的部分；输入为空则返回空串。
        """
        if not ts_code:
            return ""
        return ts_code.split(".")[0]

    @staticmethod
    def safe_float(v) -> float | None:
        """安全转 float，失败或 NaN 返回 None。

        Args:
            v: 待转换值（str/float/int/None 等）。

        Returns:
            float 值或 None。
        """
        if v is None:
            return None
        try:
            f = float(v)
        except (TypeError, ValueError):
            return None
        # NaN 视为 None
        if f != f:
            return None
        return f

    def _check_ifind_error(self, raw) -> tuple[bool, int | None, str]:
        """检查 iFind 返回值是否含错误码。

        iFind 错误返回通常为 dict，含 errorcode/errcode 等键。
        常见错误码：
            -4318 / -4309: 月度配额耗尽
            -201: 通用失败

        Args:
            raw: THS_BasicData 的返回值。

        Returns:
            (is_error, code, msg): 是否错误 / 错误码 / 错误消息。
        """
        if not isinstance(raw, dict):
            return (False, None, "")

        # 兼容多种错误码键名
        code = None
        for key in ("errorcode", "errcode", "error_code", "code"):
            if key in raw:
                try:
                    code = int(raw[key])
                except (TypeError, ValueError):
                    code = raw[key]
                break

        if code is None:
            return (False, None, "")

        # 错误消息
        msg = ""
        for key in ("errmsg", "errormsg", "error_msg", "message", "msg"):
            if key in raw:
                msg = str(raw[key])
                break

        # 负数错误码视为错误
        if isinstance(code, int) and code < 0:
            return (True, code, msg)
        # 字符串形态的负数错误码
        if isinstance(code, str) and code.strip().startswith("-"):
            try:
                return (True, int(code), msg)
            except ValueError:
                pass

        return (False, code, msg)

    # ---- 新能力辅助方法 ----

    def _get_all_a_share_codes(self, policy: "SourcePolicy") -> list[str]:
        """获取全部A股 ts_code 列表（iFind 格式，如 "600000.SH"）。

        优先使用 THS_DataPool（中证全指 000985.SH 成分股），
        失败时回退到 ClickHouse c1_market.stock_list 表（list_status='L'）。

        Args:
            policy: 调用策略

        Returns:
            ts_code 列表；失败返回空列表
        """
        # 策略1: THS_DataPool
        codes = self._get_a_share_codes_from_datapool(policy)
        if codes:
            return codes

        # 策略2: ClickHouse stock_list fallback
        self._log.info("THS_DataPool 不可用，回退到 ClickHouse stock_list")
        return self._get_a_share_codes_from_ch()

    def _get_a_share_codes_from_datapool(self, policy: "SourcePolicy") -> list[str]:
        """通过 THS_DataPool 获取 A 股清单（中证全指成分股）。"""
        from iFinDPy import THS_DataPool

        today_str = datetime.date.today().strftime("%Y-%m-%d")
        try:
            raw = self._call_with_policy(
                THS_DataPool, policy,
                "index", f"{today_str};000985.SH",
                "date:Y,thscode:Y",
            )
        except Exception as e:
            self._log.warning(f"THS_DataPool 获取A股清单失败: {e}")
            return []

        # THS_DataPool 返回 dict: {'tables': [{'table': {'THSCODE': [...]}}]}
        if not isinstance(raw, dict) or "tables" not in raw:
            self._log.warning(f"THS_DataPool 返回格式异常: {type(raw)}")
            return []

        # 检查 errorcode（-4001=no data 等错误码）
        err_code = raw.get("errorcode", 0)
        if err_code != 0:
            self._log.warning(f"THS_DataPool 错误: code={err_code} msg={raw.get('errmsg', '')}")
            return []

        try:
            if not raw["tables"]:
                return []
            table_data = raw["tables"][0]["table"]
            # 尝试多种键名
            for key in ("THSCODE", "thscode", "股票代码", "code"):
                if key in table_data:
                    return list(table_data[key])
        except (IndexError, KeyError, TypeError) as e:
            self._log.warning(f"THS_DataPool 解析失败: {e}")

        return []

    def _get_a_share_codes_from_ch(self) -> list[str]:
        """从 ClickHouse c1_market.stock_list 获取在册 A 股 ts_code。

        过滤 list_status='L'（上市中），排除退市股。
        """
        from zephyr.data import ch_writer as _chw

        out = _chw.query(self.SQL_STOCK_LIST_BY_STATUS)
        if not out.strip():
            self._log.warning("ClickHouse stock_list 查询为空")
            return []
        codes = [line.strip() for line in out.split("\n") if line.strip()]
        self._log.info(f"从 stock_list 获取 {len(codes)} 只在册 A 股")
        return codes

    @staticmethod
    def _extract_date(idx, row) -> str:
        """从 DataFrame 行提取日期字符串 "YYYY-MM-DD"。

        THS_Trans2DataFrame 返回的 DataFrame index 可能是：
        - pandas Timestamp
        - datetime 对象
        - 字符串 "2025-06-01"

        也可能在 row 的 "time" 列中。

        Returns:
            "YYYY-MM-DD" 字符串；无法提取返回空串
        """
        # 优先从 index 取
        if idx is not None:
            if hasattr(idx, "strftime"):
                return idx.strftime("%Y-%m-%d")
            s = str(idx)
            # 取前10位 "YYYY-MM-DD"
            if len(s) >= 10 and s[4] == "-":
                return s[:10]

        # 从 row 的 time/日期 列取
        for key in ("time", "日期", "date", "trade_date"):
            v = row.get(key) if hasattr(row, "get") else None
            if v is not None:
                if hasattr(v, "strftime"):
                    return v.strftime("%Y-%m-%d")
                s = str(v)
                if len(s) >= 10 and s[4] == "-":
                    return s[:10]

        return ""

    @staticmethod
    def _find_column(table_data: dict, candidates: list[str]):
        """在 i问财返回的 table dict 中按候选键名列表查找列数据。

        i问财返回的列名带日期后缀（如 "主力资金流向[20250704]"），
        先精确匹配，再前缀匹配（startswith），返回第一个找到的列数据。

        Returns:
            列数据（list）或 None
        """
        if not isinstance(table_data, dict):
            return None
        for key in candidates:
            if key in table_data:
                return table_data[key]
        # 前缀匹配（i问财字段名带 [日期] 后缀）
        for key in candidates:
            for actual_key in table_data:
                if isinstance(actual_key, str) and actual_key.startswith(key):
                    return table_data[actual_key]
        return None

    @staticmethod
    def _ts_code_to_money_flow_symbol(ts_code: str) -> str:
        """ts_code 转 money_flow 表的 symbol 格式。

        "600000.SH" -> "sh600000"
        "000001.SZ" -> "sz000001"
        "830001.BJ" -> "bj830001"

        Returns:
            小写交易所前缀 + 6位代码；无法识别返回空串
        """
        if not ts_code or "." not in ts_code:
            return ""
        code, _, suffix = ts_code.partition(".")
        suffix_lower = suffix.lower()
        if suffix_lower in ("sh", "sz", "bj"):
            return f"{suffix_lower}{code}"
        return ""

    # ============== sector_meta 能力（同花顺881二级行业板块） ==============

    def _fetch_sector_meta(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """拉取同花顺881二级行业板块信息，写入 c1_market.sector_meta。

        通过 THS_WC 问财接口查询881二级行业板块的：
        - 板块代码(sector_code)、板块名称(sector_name)
        - 成分股数量(constituent_num)
        - 总股本(total_share)、流通股本(float_share)
        - 总市值(total_mv)、流通市值(float_mv)

        每日盘后更新，trade_date 为当日。
        """
        from iFinDPy import THS_WC

        table = "c1_market.sector_meta"
        columns = [
            "sector_code", "trade_date", "sector_name", "sector_type",
            "constituent_num", "total_share", "float_share",
            "total_mv", "float_mv",
        ]
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        t0 = time.time()

        # 问财查询：同花顺881二级行业板块
        query = "同花顺二级行业板块 总市值 流通市值 成分股数量 总股本 流通A股"
        try:
            raw = self._call_with_policy(
                THS_WC, policy,
                "同花顺二级行业板块",
                "总市值,流通市值,成份股个数,总股本,流通A股",
                "",
            )
        except Exception as e:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=today_str,
                elapsed_sec=time.time() - t0, error=str(e),
            )
            return

        is_error, code, msg = self._check_ifind_error(raw)
        if is_error:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=today_str,
                elapsed_sec=time.time() - t0,
                error=f"iFind错误: {code} {msg}",
            )
            return

        # 解析问财返回结果
        rows: list[tuple] = []
        try:
            tables = raw.get("tables", []) if isinstance(raw, dict) else []
            if tables:
                tbl = tables[0].get("table", {})
                sector_codes = tbl.get("thscode", [])
                sector_names = self._extract_wencai_column(tbl, ["板块名称", "名称", "sector_name"])
                total_mv = self._extract_wencai_column(tbl, ["总市值", "ths_total_mv_index"])
                float_mv = self._extract_wencai_column(tbl, ["流通市值", "ths_float_mv_index"])
                constituent_num = self._extract_wencai_column(tbl, ["成份股个数", "成分股数量", "ths_constituent_num_index"])
                total_share = self._extract_wencai_column(tbl, ["总股本", "ths_total_shares_index"])
                float_share = self._extract_wencai_column(tbl, ["流通A股", "ths_float_a_share_index"])

                for i, sc in enumerate(sector_codes):
                    def _safe_get(lst, idx):
                        if lst and idx < len(lst):
                            return lst[idx]
                        return None
                    rows.append((
                        str(sc),
                        today_str,
                        str(_safe_get(sector_names, i) or ""),
                        "同花顺二级行业",
                        int(self.safe_float(_safe_get(constituent_num, i)) or 0),
                        self.safe_float(_safe_get(total_share, i)) or 0.0,
                        self.safe_float(_safe_get(float_share, i)) or 0.0,
                        self.safe_float(_safe_get(total_mv, i)) or 0.0,
                        self.safe_float(_safe_get(float_mv, i)) or 0.0,
                    ))
        except Exception as e:
            self._log.warning(f"sector_meta 解析失败: {e}")

        self._log.info(f"sector_meta: {len(rows)} 行")
        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=today_str, elapsed_sec=time.time() - t0,
        )

    @staticmethod
    def _extract_wencai_column(table_data: dict, candidates: list[str]) -> list:
        """从问财返回的table数据中提取列值。

        Args:
            table_data: 问财返回的 table 字典
            candidates: 候选列名列表

        Returns:
            列数据列表，未找到返回空列表
        """
        if not isinstance(table_data, dict):
            return []
        for key in candidates:
            if key in table_data:
                return table_data[key]
        # 前缀匹配
        for key in candidates:
            for actual_key in table_data:
                if isinstance(actual_key, str) and key in actual_key:
                    return table_data[actual_key]
        return []
