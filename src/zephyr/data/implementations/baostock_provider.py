# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.baostock_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] baostock SDK (bs.login/bs.logout/bs.query_history_k_data_plus/bs.query_hs300_stocks/bs.query_trade_date)
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] thread_local 登录模型——每线程独立 bs.login()；数据滞后约1周；匿名访问无需token
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] fetch 异常->yield FetchResult(error=str)；未登录->RuntimeError
# [TESTS] tests/zephyr/data/test_providers.py::TestBaostockProvider
# [A_module] module_id=MOD-GOV-baostock_provider | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: FetchPayload(table/symbols/start/end) + capability 路由键 + SourcePolicy(降级策略)
# I2: baostock SDK(bs.login/thread_local 登录态/query_history_k_data_plus/query_hs300_stocks/query_trade_date)
# A1: fetch 路由分派(capability→_fetch_index_constituent/_fetch_trade_calendar/_fetch_kline_daily/_fetch_kline_daily_delisted)
# A2: _fetch_kline_daily 主表口径=不复权(adjustflag=3，#196：对齐 miniQMT 主口径，防 ReplacingMergeTree 同键 raw/qfq 跑序漂移)
# A3: 退市股回填链(_fetch_delisted_universe→_kline_span_map 缺口探测→_fetch_one_delisted_kline 逐标的补缺)
# O1: Iterator[FetchResult](CH 表行；fetch 异常->yield FetchResult(error=str))
# [/ALGO_FLOW]
"""Baostock 数据源 Provider 实现（MOD-L00-004 §4.3）。

封装 baostock SDK，继承 IngestProviderBase。
- 匿名访问（bs.login() 无需 token）
- **thread_local 登录模型**：每线程独立 bs.login()，结束时 bs.logout()
- 数据滞后约 1 周（last_key < today-7 时标记 stale）
- 当前能力：index_constituent（沪深300成分股）/ trade_calendar（交易日历）

关键设计：
- 用 threading.local() 存储每线程的登录态
- connect() 为当前线程登录；fetch() 前确认当前线程已登录
- disconnect() 登出当前线程
"""

from __future__ import annotations

import datetime
import logging
import threading
import time
from typing import Iterator

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

# Phase 5: 表名从 business_data_categories.yaml 真源派生（裁定 #ARCH-CH-024）
_TBL_INDEX_CONSTITUENT = get_registry().table("market_index_constituent")
_TBL_TRADE_CALENDAR = get_registry().table("market_trade_calendar")
_TBL_KLINE_DAILY = get_registry().table("market_kline_daily")
# JOB-084 SQL（§5.160.2 SQL 集中化：裸 SQL 字面量禁入方法体，NO-BARE-SQL gate）
_SQL_KLINE_SPAN = (
    "SELECT symbol, min(trade_date), max(trade_date) FROM {table} WHERE symbol IN ({symbols}) GROUP BY symbol"
)


def _bs_code_to_symbol(bs_code: str) -> str:
    """baostock 代码（sh.600000/sz.000001）→ 项目 canonical（600000.SH/000001.SZ）。

    #ARCH-DATA-015：index_constituent 表 symbol_canonical MATERIALIZED 列依赖
    '代码.交易所大写' 格式推导，小写前缀格式会导致派生列为空串。
    """
    code = (bs_code or "").strip()
    if "." in code:
        exch, num = code.split(".", 1)
        return f"{num}.{exch.upper()}"
    return code


class BaostockProvider(IngestProviderBase):
    """Baostock 免费数据源 Provider。

    匿名访问、thread_local 登录模型。每线程独立 bs.login() 会话。
    已知问题：数据滞后约 1 周。
    """

    source_name: str = "baostock"
    meta: IngestProviderMeta = IngestProviderMeta(
        name="baostock",
        display_name="BaoStock 免费",
        auth_type="anonymous",
        requires_process=False,
        thread_safety="thread_local",
        rate_limit_default=60,
        capabilities=[
            # 治本修复#ARCH-CAP-NULL-SYMBOLS-001（2026-07-23）：
            # baostock 的 index_constituent/trade_calendar 均为全量查询接口
            # （bs.query_hs300_stocks / bs.query_trade_dates 不接受 symbols 参数），
            # 显式声明 supports_symbols_null=True 消除 WARN。
            CapabilityContract("index_constituent", supports_symbols_null=True),
            CapabilityContract("trade_calendar", supports_symbols_null=True),
            CapabilityContract("kline_daily", supports_symbols_null=False),
            # JOB-084（2026-08-16）：退市股历史 K 线回填——universe 由
            # bs.query_stock_basic(status=0) 自含解析，无需外部 symbols
            CapabilityContract("kline_daily_delisted", supports_symbols_null=True),
        ],
        known_issues=["数据滞后约1周", "需thread_local登录"],
    )

    def __init__(self):
        super().__init__()
        # 线程局部存储：每线程独立的登录态
        self._tls = threading.local()

    # ---- 公共属性（R5: 消除测试私有访问） ----

    @property
    def tls(self) -> threading.local:
        """线程局部存储（只读暴露，供测试验证 per-thread 登录态）。"""
        return self._tls

    # ---- 生命周期 ----

    def connect(self) -> None:
        """建立连接：为当前线程登录 baostock。"""
        self._ensure_login()
        self._connected = True
        self._log.info("Baostock 已连接（thread_local 登录）")

    def _ensure_login(self) -> None:
        """确保当前线程已登录 baostock（若未登录则登录）。"""
        if not getattr(self._tls, "logged_in", False):
            import baostock as bs

            result = bs.login()
            if result.error_code != "0":
                # #ARCH-DATA-015: 登录失败（如 10001011 IP黑名单）时 baostock 库不释放
                # 底层 socket，filterwarnings=error 下泄漏的 ResourceWarning 会被放大为
                # 测试 ExceptionGroup；失败路径显式 logout 关闭 socket。
                try:
                    bs.logout()
                except Exception:  # noqa: BLE001 — 清理动作不掩盖原始错误
                    pass
                raise RuntimeError(f"baostock login failed: {result.error_code} {result.error_msg}")
            self._tls.logged_in = True
            self._tls.bs = bs
            self._log.debug("baostock 线程 %s 已登录", threading.current_thread().name)

    def health_check(self) -> bool:
        """探活：尝试 import baostock + 登录。"""
        try:
            import baostock  # noqa: F401

            self._ensure_login()
            return True
        except ImportError as e:
            self._log.warning(f"Baostock 探活失败（baostock 未安装）: {e}")
            return False
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"Baostock 探活失败: {e}")
            return False

    def disconnect(self) -> None:
        """断开连接：登出当前线程的 baostock 会话。"""
        if getattr(self._tls, "logged_in", False):
            try:
                self._tls.bs.logout()
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.warning(f"baostock logout 异常: {e}")
            self._tls.logged_in = False
            self._tls.bs = None
        self._connected = False
        self._log.info("Baostock 已断开")

    # ---- 拉取入口 ----

    def fetch(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """按 payload.extra["capability"] 路由到具体获取方法。"""
        # 确保当前线程已登录
        try:
            self._ensure_login()
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error=f"baostock login failed: {e}",
            )
            return

        capability = (payload.extra or {}).get("capability")
        if capability == "index_constituent":
            yield from self._fetch_index_constituent(payload, policy)
        elif capability == "trade_calendar":
            yield from self._fetch_trade_calendar(payload, policy)
        elif capability == "kline_daily":
            yield from self._fetch_kline_daily(payload, policy)
        elif capability == "kline_daily_delisted":
            yield from self._fetch_kline_daily_delisted(payload, policy)
        else:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error=f"unsupported capability: {capability}",
            )

    # ---- 沪深300成分股 ----

    def _fetch_index_constituent(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """获取沪深300成分股（bs.query_hs300_stocks）。

        baostock API 变更：返回 3 列（updateDate/code/code_name），无 weight 列。
        #ARCH-DATA-015：列名对齐 index_constituent 表 schema（08-10 SCD-2 重建后
        旧列名 update_date/code/code_name 与表零交集，write_result 过滤后只剩
        weight 一列静默空写——300 行丢失的病根）。weight 无数据源置 0（同 miniqmt 口径）。
        """
        bs = self._tls.bs
        table = payload.table or _TBL_INDEX_CONSTITUENT
        columns = ["trade_date", "index_code", "symbol", "weight", "action", "data_source"]
        t0 = time.time()
        try:
            rs = self._call_with_policy(bs.query_hs300_stocks, policy)
            rows: list[tuple] = []
            while rs.error_code == "0" and rs.next():
                item = rs.get_row_data()
                # API 变更后返回 3 列: updateDate, code(sh.600000), code_name
                rows.append((item[0], "000300.SH", _bs_code_to_symbol(item[1]), 0, "", "baostock"))
            self._log.info(f"沪深300成分股获取完成，{len(rows)} 行")
            yield FetchResult(
                table=table,
                columns=columns,
                rows=rows,
                last_key=datetime.date.today().isoformat(),
                elapsed_sec=time.time() - t0,
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"沪深300成分股获取失败: {e}")
            yield FetchResult(
                table=table,
                columns=columns,
                rows=[],
                last_key="",
                elapsed_sec=time.time() - t0,
                error=str(e),
            )

    # ---- 交易日历 ----

    def _fetch_trade_calendar(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """获取交易日历（bs.query_trade_dates）。

        baostock API 变更：方法名 query_trade_date → query_trade_dates（加 s）。
        返回 2 列: calendar_date, is_trading_day。
        #ARCH-DATA-015：列名对齐 trade_calendar 表 schema（exchange/cal_date/is_open/
        pretrade_date；旧列名 calendar_date/is_trading_day 与表零交集静默空写）。
        pretrade_date=上一开市日（首个开市日取自身）。
        """
        bs = self._tls.bs
        table = payload.table or _TBL_TRADE_CALENDAR
        columns = ["exchange", "cal_date", "is_open", "pretrade_date"]
        t0 = time.time()
        try:
            start = payload.start.isoformat() if payload.start else "2010-01-01"
            end = payload.end.isoformat() if payload.end else datetime.date.today().isoformat()
            rs = self._call_with_policy(bs.query_trade_dates, policy, start_date=start, end_date=end)
            rows: list[tuple] = []
            last_open: str | None = None
            while rs.error_code == "0" and rs.next():
                item = rs.get_row_data()
                # API 变更后返回 2 列: calendar_date(item[0]), is_trading_day(item[1])
                cal_date, is_open = item[0], int(item[1]) if item[1] else 0
                rows.append(("SSE", cal_date, is_open, last_open or cal_date))
                if is_open:
                    last_open = cal_date
            self._log.info(f"交易日历获取完成，{len(rows)} 行")
            yield FetchResult(
                table=table,
                columns=columns,
                rows=rows,
                last_key=end,
                elapsed_sec=time.time() - t0,
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"交易日历获取失败: {e}")
            yield FetchResult(
                table=table,
                columns=columns,
                rows=[],
                last_key="",
                elapsed_sec=time.time() - t0,
                error=str(e),
            )

    # ---- 日K线（备选降级源）----

    def _fetch_kline_daily(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """获取日K线（bs.query_history_k_data_plus）。

        作为日K线降级源使用，写入 kline_daily 主表。数据滞后约1周。
        #196 修复（2026-08-19）：口径强制不复权（adjustflag=3，对齐主口径
        miniQMT 不复权）——此前 adjustflag=2 前复权写主表，ReplacingMergeTree
        同键后写覆盖先写致 raw/qfq 混杂，且 qfq 随分红漂移不可复现（P0）。
        """
        bs = self._tls.bs
        table = payload.table or _TBL_KLINE_DAILY
        # #219 列名对齐 kline_daily schema（真源 schemas/categories/market_kline_daily.py）：
        # 此前透传 baostock 原始列名 date/code——写层 write_result 按列名交集过滤后
        # 仅剩 6 价格列，date/code 被丢弃 → CH 侧键列落 DEFAULT 产 symbol=''/
        # trade_date=1970-01-01 垃圾键行。映射 date→trade_date、code→symbol；
        # symbol 值由 baostock 小写前缀格式（sh.600000）转纯数字（600000，对齐
        # miniqmt 主写口径与表 MATERIALIZED exchange 派生规则，保证 ReplacingMergeTree
        # 同键 (symbol, trade_date) 去重）；补 data_source='Baostock'（同
        # _fetch_kline_daily_delisted 链）；adj_factor 由表 DEFAULT 1 填充（#196
        # 不复权口径）。CH 存量垃圾行清洗留 Owner 窗口，本修复只防新增。
        columns = [
            "trade_date", "symbol", "open", "high", "low", "close",
            "volume", "amount", "data_source",
        ]
        t0 = time.time()
        symbols = payload.symbols or ["sh.600000"]
        start = payload.start.isoformat() if payload.start else "2020-01-01"
        end = payload.end.isoformat() if payload.end else datetime.date.today().isoformat()

        for code in symbols:
            try:
                rs = self._call_with_policy(
                    bs.query_history_k_data_plus,
                    policy,
                    code=code,
                    fields="date,code,open,high,low,close,volume,amount",
                    start_date=start,
                    end_date=end,
                    frequency="d",
                    adjustflag="3",  # 不复权（#196：写 kline_daily 主表必须对齐 miniQMT 主口径；1=后复权 2=前复权 3=不复权）
                )
                rows: list[tuple] = []
                while rs.error_code == "0" and rs.next():
                    item = rs.get_row_data()
                    # item: [date, code(sh.600000), open..amount]（全 str）；
                    # #219：code 取 "." 后纯数字段作 symbol（无 "." 原样，幂等）
                    symbol6 = str(item[1]).split(".")[-1] if len(item) > 1 else ""
                    rows.append((item[0], symbol6, *item[2:], "Baostock"))
                if rows:
                    yield FetchResult(
                        table=table,
                        columns=columns,
                        rows=rows,
                        last_key=end,
                        elapsed_sec=time.time() - t0,
                    )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.warning(f"baostock K线 {code} 获取失败: {e}")
                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=[],
                    last_key="",
                    elapsed_sec=time.time() - t0,
                    error=str(e),
                )

    # ---- JOB-084：退市股历史 K 线回填（DS-002 幸存者偏差治理）----

    # A 股板块前缀（baostock 代码为小写交易所前缀；北交所 baostock 无覆盖——
    # tushare 对照实证退市北交所 5 只，known gap 留 registry evidence）
    _DELISTED_A_PREFIXES = ("sh.60", "sh.68", "sz.00", "sz.30")
    # 覆盖判定余量：已覆盖 [ipo+10d, out-10d] 即视为完整（防边界毛刺反复重抓）
    _SPAN_MARGIN_DAYS = 10

    @staticmethod
    def _iso_or_none(s) -> datetime.date | None:
        """'YYYY-MM-DD' 字符串 → date，脏值返回 None。"""
        try:
            return datetime.date.fromisoformat(str(s or "").strip()[:10])
        except (ValueError, TypeError):
            return None

    def _fetch_delisted_universe(self, bs, policy: SourcePolicy) -> list[tuple]:
        """bs.query_stock_basic → 退市 A 股 universe [(code_bs, code6, ipoDate, outDate)]。

        过滤：type=='1'（股票）& status=='0'（退市）& A 股板块前缀
        （B股/基金/债券/指数排除；2026-08-16 实证 status=0 全类型 1179 行）。
        """
        rs = self._call_with_policy(bs.query_stock_basic, policy)
        out: list[tuple] = []
        if rs is None or getattr(rs, "error_code", "?") != "0":
            self._log.warning(f"query_stock_basic 失败: {getattr(rs, 'error_msg', '?')}")
            return out
        while rs.next():
            row = rs.get_row_data()
            if len(row) < 6:
                continue
            code_bs, _, ipo_d, out_d, typ, status = row[:6]
            if typ != "1" or status != "0":
                continue
            if not code_bs.startswith(self._DELISTED_A_PREFIXES):
                continue
            out.append((code_bs, code_bs.split(".")[1], str(ipo_d), str(out_d)))
        return out

    def _kline_span_map(self, _chr, table: str, codes6: list[str]) -> dict[str, tuple]:
        """kline_daily 已覆盖区间 {code6: (min_date, max_date)}（增量跳过依据）。"""
        if not codes6:
            return {}
        in_list = ",".join(f"'{c}'" for c in codes6)
        try:
            tsv = _chr.query(_SQL_KLINE_SPAN.format(table=table, symbols=in_list))
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"kline_daily 覆盖区间查询失败（降级全量抓取）: {e}")
            return {}
        spans: dict[str, tuple] = {}
        for line in (tsv or "").strip().split("\n"):
            parts = line.split("\t")
            if len(parts) != 3:
                continue
            lo, hi = self._iso_or_none(parts[1]), self._iso_or_none(parts[2])
            if lo and hi:
                spans[parts[0]] = (lo, hi)
        return spans

    @staticmethod
    def _map_delisted_kline_rows(rows: list[list], code6: str) -> list[tuple]:
        """baostock K线行 → kline_daily 表行（INSERT_COLUMNS 列序）。

        fields: date,code,open,high,low,close,preclose,volume,amount,turn,pctChg。
        不复权（adjustflag=3，对齐 kline_daily 主口径=miniQMT 不复权；既有 baostock
        fallback 的 adjustflag=2 前复权为历史不一致，不扩散到本能力）→ adj_factor=1。
        退市整理期末端 volume/amount/turn/pctChg 可空（实证 000005 末日）→ 0 兜底；
        close 空 → 丢行（价格缺失无撮合价值）。
        """
        out: list[tuple] = []
        for r in rows:
            if len(r) < 11:
                continue
            date_s, _, o, h, lo, cl, pre, vol, amt, turn, pct = r[:11]
            if not cl:
                continue
            close = round(float(cl), 4)
            preclose = float(pre) if pre else 0.0
            high = round(float(h), 4) if h else close
            low = round(float(lo), 4) if lo else close
            open_ = round(float(o), 4) if o else close
            amplitude = round((high - low) / preclose * 100, 4) if preclose > 0 else 0.0
            change = round(close - preclose, 4) if preclose > 0 else 0.0
            out.append(
                (
                    date_s,
                    code6,
                    open_,
                    high,
                    low,
                    close,
                    int(float(vol)) if vol else 0,
                    round(float(amt), 2) if amt else 0.0,
                    amplitude,
                    round(float(pct), 4) if pct else 0.0,
                    change,
                    round(float(turn), 4) if turn else 0.0,
                    1,  # adj_factor：不复权
                    "A_share",
                    "Baostock",
                    1,  # quality_flag：正常
                )
            )
        return out

    def _is_span_covered(self, span, ipo: datetime.date | None, out_d: datetime.date | None) -> bool:
        """已覆盖 [ipo+margin, out-margin] 即视为完整（防边界毛刺反复重抓）。"""
        if not span or not ipo or not out_d:
            return False
        margin = datetime.timedelta(days=self._SPAN_MARGIN_DAYS)
        return span[0] <= ipo + margin and span[1] >= out_d - margin

    def _fetch_one_delisted_kline(
        self, bs, policy: SourcePolicy, code_bs: str, code6: str, ipo_d: str, out_d: str
    ) -> list[tuple]:
        """单只退市股 [ipoDate, outDate] 全历史 K 线抓取+映射（失败记 warning 返回 []）。

        adjustflag=3 不复权：对齐 kline_daily 主口径（miniQMT 不复权）。
        """
        try:
            rs = self._call_with_policy(
                bs.query_history_k_data_plus,
                policy,
                code=code_bs,
                fields="date,code,open,high,low,close,preclose,volume,amount,turn,pctChg",
                start_date=ipo_d or "1990-01-01",
                end_date=out_d or datetime.date.today().isoformat(),
                frequency="d",
                adjustflag="3",
            )
            raw: list[list] = []
            while rs is not None and rs.error_code == "0" and rs.next():
                raw.append(rs.get_row_data())
            return self._map_delisted_kline_rows(raw, code6)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"退市股 K线 {code_bs} 获取失败: {e}")
            return []

    def _fetch_kline_daily_delisted(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """退市股历史 K 线回填（JOB-084，DS-002 幸存者偏差治理），写入 kline_daily。

        universe：bs.query_stock_basic(type=1 股票 & status=0 退市) A 股前缀过滤，
        自含解析不跨源。窗口：每股 [ipoDate, outDate] 全历史（2026-08-16 实证
        sz.000005 → 8146 根 1990-12-19~2024-04-26 退市日）。增量：symbol 已覆盖
        [ipo+10d, out-10d] 即跳过（月度 monthly_static 幂等刷新只抓新退市股）；
        同键 ReplacingMergeTree 替换幂等。单股失败记 warning 继续（汇总日志计数）。
        """
        bs = self._tls.bs
        table = payload.table or _TBL_KLINE_DAILY
        columns = [
            "trade_date",
            "symbol",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "amount",
            "amplitude",
            "pct_change",
            "change",
            "turnover",
            "adj_factor",
            "market_type",
            "data_source",
            "quality_flag",
        ]
        t0 = time.monotonic()
        universe = self._fetch_delisted_universe(bs, policy)
        if not universe:
            yield FetchResult(
                table=table,
                columns=columns,
                rows=[],
                last_key="",
                elapsed_sec=time.monotonic() - t0,
                error="退市股 universe 解析为空（query_stock_basic 失败或无退市股）",
            )
            return

        from zephyr.data import ch_reader as _chr

        spans = self._kline_span_map(_chr, table, [u[1] for u in universe])
        n_done = n_skip = n_empty = 0
        for code_bs, code6, ipo_d, out_d in universe:
            if self._is_span_covered(spans.get(code6), self._iso_or_none(ipo_d), self._iso_or_none(out_d)):
                n_skip += 1
                continue
            rows = self._fetch_one_delisted_kline(bs, policy, code_bs, code6, ipo_d, out_d)
            if not rows:
                n_empty += 1
                continue
            n_done += 1
            yield FetchResult(
                table=table,
                columns=columns,
                rows=rows,
                last_key=out_d,
                elapsed_sec=time.monotonic() - t0,
            )
        self._log.info(
            f"kline_daily_delisted: universe {len(universe)} 只 → 回填 {n_done} 只 "
            f"/ 跳过已覆盖 {n_skip} / 无数据或失败 {n_empty}（{time.monotonic() - t0:.1f}s）"
        )
